# Dify RAG/Knowledge Base System -- Clean-Room Requirements Document

**Source analysis**: `~/nyqst-dify/upstream-dify/api/` (Dify open-source, Python/Flask)
**Date**: 2026-02-01
**Purpose**: Architecture extraction for independent reimplementation

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Document Ingestion Pipeline](#2-document-ingestion-pipeline)
3. [File Format Support and Extraction](#3-file-format-support-and-extraction)
4. [Text Cleaning](#4-text-cleaning)
5. [Chunking Strategies](#5-chunking-strategies)
6. [Embedding Provider Abstraction](#6-embedding-provider-abstraction)
7. [Embedding Cache Layer](#7-embedding-cache-layer)
8. [Vector Store Abstraction](#8-vector-store-abstraction)
9. [Keyword Index (Full-Text)](#9-keyword-index-full-text)
10. [Index Types and Document Structure Models](#10-index-types-and-document-structure-models)
11. [Data Models and Relationships](#11-data-models-and-relationships)
12. [Retrieval Strategies](#12-retrieval-strategies)
13. [Reranking Subsystem](#13-reranking-subsystem)
14. [Metadata Filtering on Retrieval](#14-metadata-filtering-on-retrieval)
15. [RAG Integration with Chat/Completion](#15-rag-integration-with-chatcompletion)
16. [Dataset/Knowledge Base Management](#16-datasetkknowledge-base-management)
17. [External Knowledge Sources](#17-external-knowledge-sources)
18. [Multimodal Support](#18-multimodal-support)
19. [Configuration Options and Trade-offs](#19-configuration-options-and-trade-offs)
20. [Libraries and Dependencies](#20-libraries-and-dependencies)
21. [Reimplementation Requirements Summary](#21-reimplementation-requirements-summary)

---

## 1. System Overview

Dify's RAG system is a multi-layer knowledge base engine with the following core flow:

```
Upload/Crawl -> Extract -> Clean -> Chunk -> Embed -> Index (Vector + Keyword)
                                                          |
Query -> Embed Query -> Retrieve (Vector/Keyword/Hybrid) -> Rerank -> Context Injection -> LLM
```

Key architectural patterns:
- **Factory pattern** everywhere: vector stores, index processors, keyword backends, rerankers
- **Strategy pattern** for retrieval methods, chunking modes, reranking approaches
- **Two-tier caching**: PostgreSQL for document embeddings, Redis for query embeddings
- **Async processing**: Celery task queue drives indexing; retrieval uses ThreadPoolExecutor
- **Multi-tenant**: every entity scoped by `tenant_id`
- **Three index structure types**: paragraph (flat), QA (question-answer pairs), parent-child (hierarchical)

### Key File Locations

| Component | Path (relative to `api/`) |
|-----------|--------------------------|
| Data models | `models/dataset.py` |
| Extractors | `core/rag/extractor/` |
| Splitters | `core/rag/splitter/` |
| Cleaner | `core/rag/cleaner/clean_processor.py` |
| Embedding | `core/rag/embedding/` |
| Vector stores | `core/rag/datasource/vdb/` |
| Keyword stores | `core/rag/datasource/keyword/` |
| Index processors | `core/rag/index_processor/` |
| Retrieval | `core/rag/retrieval/` and `core/rag/datasource/retrieval_service.py` |
| Reranking | `core/rag/rerank/` |
| Post-processing | `core/rag/data_post_processor/` |
| Docstore | `core/rag/docstore/dataset_docstore.py` |
| Indexing runner | `core/indexing_runner.py` |
| Service layer | `services/dataset_service.py`, `services/knowledge_service.py` |

---

## 2. Document Ingestion Pipeline

The ingestion pipeline follows a strict phase model. Each phase updates the `Document.indexing_status` column and a corresponding timestamp.

### Pipeline Phases

```
waiting -> parsing -> cleaning -> splitting -> indexing -> completed
                                                  |
                                                error (any phase)
```

**Status transitions tracked**: `processing_started_at`, `parsing_completed_at`, `cleaning_completed_at`, `splitting_completed_at`, `completed_at`.

### Orchestration

The `IndexingRunner.run()` method drives the pipeline:

1. **Extract** (`index_processor.extract()`): Dispatches to format-specific extractor based on file extension. Returns `list[Document]` where each Document has `page_content` (string) and `metadata` (dict).

2. **Transform** (`index_processor.transform()`): Applies cleaning rules, then splits into chunks. Assigns each chunk a UUID `doc_id` and a content hash `doc_hash`. For parent-child mode, also generates child chunks.

3. **Save segments** (`_load_segments()`): Persists each chunk as a `DocumentSegment` row in PostgreSQL via `DatasetDocumentStore.add_documents()`. For hierarchical mode, also persists `ChildChunk` rows.

4. **Load** (`index_processor.load()`): Embeds chunks and inserts into vector store (high_quality mode) or keyword index (economy mode).

### Pause/Resume Support

Documents can be paused mid-indexing (`is_paused` flag). The indexing runner checks for pause after each batch of segments and raises `DocumentIsPausedError`.

### Requirements for Reimplementation

- R-INGEST-1: Implement a state machine for document indexing status with timestamps per phase.
- R-INGEST-2: Each phase must be independently resumable (idempotent on retry).
- R-INGEST-3: Support pause/resume at segment batch granularity.
- R-INGEST-4: Track `word_count`, `tokens`, `indexing_latency` per document.
- R-INGEST-5: Support batch processing of multiple documents per run.

---

## 3. File Format Support and Extraction

The `ExtractProcessor` class dispatches to format-specific extractors based on file extension. There are two ETL modes controlled by `dify_config.ETL_TYPE`:

### ETL Mode: "Unstructured" (richer format support)

| Extension | Extractor | Library |
|-----------|-----------|---------|
| `.pdf` | `PdfExtractor` | Custom (likely pdfplumber or PyMuPDF) |
| `.xlsx`, `.xls` | `ExcelExtractor` | openpyxl |
| `.md`, `.markdown`, `.mdx` | `UnstructuredMarkdownExtractor` (auto) or `MarkdownExtractor` (custom) | unstructured API |
| `.htm`, `.html` | `HtmlExtractor` | beautifulsoup4 |
| `.docx` | `WordExtractor` | python-docx |
| `.doc` | `UnstructuredWordExtractor` | unstructured API |
| `.csv` | `CSVExtractor` | csv stdlib |
| `.msg` | `UnstructuredMsgExtractor` | unstructured API |
| `.eml` | `UnstructuredEmailExtractor` | unstructured API |
| `.ppt` | `UnstructuredPPTExtractor` | unstructured API |
| `.pptx` | `UnstructuredPPTXExtractor` | unstructured API |
| `.xml` | `UnstructuredXmlExtractor` | unstructured API |
| `.epub` | `UnstructuredEpubExtractor` | unstructured API |
| (other) | `TextExtractor` | chardet for encoding |

### ETL Mode: "Dify" (built-in only, no Unstructured API)

Supports: PDF, Excel, Markdown, HTML, DOCX, CSV, EPUB, and plain text.

### Data Source Types

- **upload_file**: File uploaded via API/UI, stored in blob storage
- **notion_import**: Notion pages via `NotionExtractor`
- **website_crawl**: Web pages via Firecrawl, WaterCrawl, or Jina Reader

### Extractor Base Interface

All extractors implement `BaseExtractor.extract() -> list[Document]`.

### Requirements for Reimplementation

- R-EXTRACT-1: Implement a dispatcher that routes by file extension to format-specific extractors.
- R-EXTRACT-2: Support at minimum: PDF, DOCX, Markdown, HTML, CSV, Excel, plain text.
- R-EXTRACT-3: Support auto-detection of file encoding (chardet/cchardet).
- R-EXTRACT-4: Optional: Unstructured API integration for extended formats (PPT, EML, MSG, DOC, XML, EPUB).
- R-EXTRACT-5: Support Notion and web crawl data sources as separate extraction paths.
- R-EXTRACT-6: All extractors produce `list[Document(page_content, metadata)]`.

---

## 4. Text Cleaning

The `CleanProcessor` applies configurable pre-processing rules before chunking:

### Built-in Rules

1. **Always applied** (hardcoded):
   - Remove invalid control characters (`\x00-\x08`, `\x0B`, `\x0C`, `\x0E-\x1F`, `\x7F`, BOM markers)
   - Normalize `<|` and `|>` to `<` and `>`

2. **Configurable** (per `pre_processing_rules` list):
   - `remove_extra_spaces`: Collapse 3+ newlines to 2, collapse multiple whitespace chars to one space
   - `remove_urls_emails`: Remove email addresses and URLs, but preserve Markdown image/link syntax

### Requirements for Reimplementation

- R-CLEAN-1: Always strip control characters and Unicode BOM.
- R-CLEAN-2: Support togglable rules for extra space removal and URL/email removal.
- R-CLEAN-3: URL removal must preserve Markdown image and link syntax (placeholder-based approach).

---

## 5. Chunking Strategies

### Processing Rule Modes

Three modes: `automatic`, `custom`, `hierarchical`.

### Splitter Architecture

Two splitter classes, both character-count based (not token-count, despite the parameter name):

1. **`EnhanceRecursiveCharacterTextSplitter`**: Used for automatic mode. Extends a LangChain-style `RecursiveCharacterTextSplitter`. Uses a character-length function (not tokenizer) for chunk sizing.

2. **`FixedRecursiveCharacterTextSplitter`**: Used for custom/hierarchical modes. First splits on a user-defined separator (e.g., `\n\n`), then recursively splits oversized chunks using fallback separators: `["\n\n", ".", ". ", " ", ""]`.

### Automatic Mode

Fixed parameters from `DatasetProcessRule.AUTOMATIC_RULES`:
- Separator: `\n`
- Max tokens: 500 (characters)
- Chunk overlap: 50

### Custom Mode

User-configurable:
- `separator`: Primary delimiter (supports `\n` escape)
- `max_tokens`: Chunk size in characters (range: 50 to `INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH`)
- `chunk_overlap`: Overlap between chunks in characters

Fallback separators: `["\n\n", ".", ". ", " ", ""]`

### Hierarchical Mode (Parent-Child)

Two sub-modes controlled by `parent_mode`:

1. **`paragraph`**: Parent chunks split by user rules (same as custom mode), then each parent is further split into child chunks using `subchunk_segmentation` rules.

2. **`full-doc`**: Entire document is one parent, split into child chunks. Only child chunks are embedded and indexed in vector store. Parent content is returned at retrieval time.

### Chunk Metadata

Each chunk receives:
- `doc_id`: UUID v4 (unique per chunk)
- `doc_hash`: SHA-256 of content (for deduplication)
- `document_id`: FK to parent Document
- `dataset_id`: FK to Dataset

### Requirements for Reimplementation

- R-CHUNK-1: Implement recursive character splitter with configurable primary separator and fallback chain.
- R-CHUNK-2: Support automatic mode with sensible defaults (500 char chunks, 50 overlap).
- R-CHUNK-3: Support custom mode with user-defined separator, chunk size, overlap.
- R-CHUNK-4: Support hierarchical parent-child chunking with both paragraph and full-doc parent modes.
- R-CHUNK-5: Assign UUID and content hash to every chunk.
- R-CHUNK-6: Character-based length function (not token-based) for chunk sizing.
- R-CHUNK-7: Strip leading punctuation from chunk starts after splitting.

---

## 6. Embedding Provider Abstraction

### Interface

`Embeddings` (abstract base class) defines four methods:

```
embed_documents(texts: list[str]) -> list[list[float]]
embed_query(text: str) -> list[float]
embed_multimodal_documents(docs: list[dict]) -> list[list[float]]
embed_multimodal_query(doc: dict) -> list[float]
```

### Provider Resolution

Embedding model is resolved via `ModelManager.get_model_instance()` which loads the configured provider (OpenAI, Cohere, local models, etc.) based on:
- `dataset.embedding_model_provider` (e.g., "openai")
- `dataset.embedding_model` (e.g., "text-embedding-3-small")
- `dataset.tenant_id` (for API key resolution)

### Normalization

All embeddings are L2-normalized before storage: `vector / np.linalg.norm(vector)`. NaN vectors are rejected.

### Batching

Embeddings are computed in batches controlled by `ModelPropertyKey.MAX_CHUNKS` (from model schema). There is also an outer batch of 1000 documents in `Vector.create()`.

### Requirements for Reimplementation

- R-EMBED-1: Define abstract embedding interface with document, query, and multimodal variants.
- R-EMBED-2: Support pluggable embedding providers via model registry.
- R-EMBED-3: L2-normalize all embedding vectors before storage.
- R-EMBED-4: Reject NaN vectors gracefully.
- R-EMBED-5: Support batched embedding calls with configurable batch size.

---

## 7. Embedding Cache Layer

Two-tier caching strategy:

### Tier 1: Database Cache for Document Embeddings

The `Embedding` model stores precomputed embeddings:
- **Key**: `(model_name, provider_name, hash)` -- unique constraint
- **Value**: Serialized float list in binary column
- **Scope**: Permanent (no TTL)
- **Lookup**: Before embedding a text, compute SHA-256 hash, query for existing embedding
- **Purpose**: Avoid re-embedding identical content across documents/datasets

### Tier 2: Redis Cache for Query Embeddings

- **Key**: `{provider}_{model}_{text_hash}`
- **Value**: Base64-encoded numpy float array
- **TTL**: 600 seconds (10 minutes), refreshed on hit
- **Purpose**: Cache repeated queries within a session

### Requirements for Reimplementation

- R-CACHE-1: Implement persistent embedding cache keyed by (provider, model, content_hash).
- R-CACHE-2: Implement volatile query embedding cache with short TTL (e.g., 10 minutes).
- R-CACHE-3: Content hash should use SHA-256 or equivalent.
- R-CACHE-4: Cache lookup must happen before any API call to embedding provider.

---

## 8. Vector Store Abstraction

### Interface

`BaseVector` defines the contract:

```
create(texts, embeddings)         -- Initial bulk insert
add_texts(documents, embeddings)  -- Incremental add
text_exists(id) -> bool           -- Check existence by doc_id
delete_by_ids(ids)                -- Delete specific vectors
delete_by_metadata_field(key, value)  -- Delete by metadata filter
search_by_vector(query_vector, **kwargs) -> list[Document]  -- Similarity search
search_by_full_text(query, **kwargs) -> list[Document]      -- Full-text search
delete()                          -- Drop entire collection
```

### Factory Pattern

`Vector` class wraps `BaseVector` and handles:
1. Embedding model instantiation
2. Collection name generation: `{prefix}_{dataset_id_normalized}_Node`
3. Provider selection from config or dataset's stored `index_struct_dict`
4. Batched embedding + insertion (1000 docs per batch)

### Supported Vector Stores (30+)

| Category | Stores |
|----------|--------|
| Purpose-built | Qdrant, Milvus, Weaviate, Chroma, Upstash |
| PostgreSQL-based | pgvector, pgvecto-rs, OpenGauss |
| Elasticsearch-based | Elasticsearch, Elasticsearch-JA (Japanese), OpenSearch |
| Cloud-managed | Tencent, Baidu, Alibaba Cloud MySQL, AnalyticDB, VikingDB, Huawei Cloud |
| SQL-based | TiDB Vector, Oracle, MatrixOne, OceanBase/SeekDB, IRIS |
| Others | Couchbase, Lindorm, TableStore, ClickZetta, Relyt |
| Hybrid | TiDB-on-Qdrant (managed Qdrant with TiDB auth) |

### Collection Management

- `DatasetCollectionBinding` tracks which collection a dataset uses
- Collection names are generated from dataset ID
- Redis cache key `vector_indexing_{collection_name}` caches collection existence

### Metadata Stored per Vector

Standard attributes: `["doc_id", "dataset_id", "document_id", "doc_hash"]`

### Requirements for Reimplementation

- R-VEC-1: Define abstract vector store interface with create, add, delete, search_by_vector, search_by_full_text.
- R-VEC-2: Implement factory that selects backend from configuration.
- R-VEC-3: Support at minimum: pgvector, Qdrant, and one Elasticsearch variant.
- R-VEC-4: Store standard metadata (doc_id, dataset_id, document_id, doc_hash) with every vector.
- R-VEC-5: Support collection-per-dataset isolation.
- R-VEC-6: Implement duplicate detection via `text_exists()` before insertion.
- R-VEC-7: Cache collection existence in Redis to avoid repeated existence checks.

---

## 9. Keyword Index (Full-Text)

### Architecture

Keyword search uses Jieba (Chinese word segmentation library) for keyword extraction and a keyword table stored in PostgreSQL or file storage.

### Components

- `Keyword` factory class (parallel to `Vector`)
- `JiebaKeywordTableHandler`: extracts keywords from text using Jieba with stopword filtering
- `DatasetKeywordTable` model: stores inverted index as JSON (`keyword -> set[node_ids]`)

### Storage Options

- **database**: JSON blob in `dataset_keyword_tables.keyword_table` column
- **file**: Stored at `keyword_files/{tenant_id}/{dataset_id}.txt` in blob storage (for large tables)

### When Used

- Economy indexing technique (no embedding model required)
- As the keyword component of hybrid search

### Requirements for Reimplementation

- R-KW-1: Implement keyword extraction (can substitute Jieba with language-appropriate tokenizer).
- R-KW-2: Maintain inverted index mapping keywords to chunk IDs.
- R-KW-3: Support keyword-only search as a zero-cost retrieval option (no embedding model needed).

---

## 10. Index Types and Document Structure Models

### Index Structure Types

Three `doc_form` values determine processing and retrieval behavior:

| Type | `doc_form` Value | Description |
|------|-----------------|-------------|
| **Paragraph** | `text_model` | Flat chunking. Each chunk independently embedded and indexed. |
| **QA** | `qa_model` | Each segment has both `content` (question) and `answer`. Context returned as `question: ... answer: ...`. |
| **Parent-Child** | `hierarchical_model` | Two-level hierarchy. Child chunks are embedded and indexed. Parent content returned at retrieval time. |

### Index Technique Types

| Technique | Description |
|-----------|-------------|
| **high_quality** | Embeddings + vector store. Supports semantic, full-text, and hybrid search. |
| **economy** | Keyword-only. No embedding model needed. Only keyword search. |

### Index Processor Factory

`IndexProcessorFactory(index_type)` returns the appropriate processor:
- `text_model` -> `ParagraphIndexProcessor`
- `qa_model` -> `QAIndexProcessor`
- `hierarchical_model` -> `ParentChildIndexProcessor`

Each processor implements: `extract()`, `transform()`, `load()`, `clean()`, `retrieve()`, `index()`.

### Requirements for Reimplementation

- R-IDX-1: Support at minimum paragraph (flat) index structure.
- R-IDX-2: Support parent-child hierarchical structure with full-doc and paragraph parent modes.
- R-IDX-3: Support QA index structure (question + answer pairs).
- R-IDX-4: Support both high_quality (vector) and economy (keyword-only) indexing techniques.
- R-IDX-5: Implement index processor factory pattern for extensibility.

---

## 11. Data Models and Relationships

### Entity Relationship Diagram (Logical)

```
Tenant (tenant_id)
  |
  +-- Dataset (knowledge base)
  |     |-- name, description, permission, provider
  |     |-- indexing_technique (high_quality | economy)
  |     |-- embedding_model, embedding_model_provider
  |     |-- retrieval_model (JSON: search_method, top_k, etc.)
  |     |-- collection_binding_id -> DatasetCollectionBinding
  |     |-- chunk_structure (text_model | qa_model | hierarchical_model)
  |     |
  |     +-- Document (source file/page)
  |     |     |-- data_source_type (upload_file | notion_import | website_crawl)
  |     |     |-- data_source_info (JSON: file_id, URL, etc.)
  |     |     |-- indexing_status, enabled, archived
  |     |     |-- doc_form (text_model | qa_model | hierarchical_model)
  |     |     |-- doc_metadata (JSON: user-defined metadata fields)
  |     |     |-- dataset_process_rule_id -> DatasetProcessRule
  |     |     |
  |     |     +-- DocumentSegment (chunk)
  |     |     |     |-- content, answer (for QA), position
  |     |     |     |-- index_node_id (UUID, used as vector store ID)
  |     |     |     |-- index_node_hash (content hash)
  |     |     |     |-- keywords (JSON), word_count, tokens
  |     |     |     |-- hit_count, enabled, status
  |     |     |     |
  |     |     |     +-- ChildChunk (for hierarchical)
  |     |     |     |     |-- content, position
  |     |     |     |     |-- index_node_id, index_node_hash
  |     |     |     |
  |     |     |     +-- SegmentAttachmentBinding -> UploadFile (images)
  |     |     |
  |     |     +-- DatasetProcessRule
  |     |           |-- mode (automatic | custom | hierarchical)
  |     |           |-- rules (JSON: pre_processing_rules, segmentation, etc.)
  |     |
  |     +-- DatasetKeywordTable (inverted index)
  |     +-- DatasetMetadata (custom metadata field definitions)
  |     +-- DatasetMetadataBinding (metadata values per document)
  |     +-- DatasetPermission (user-level access)
  |     +-- DatasetQuery (query log)
  |
  +-- Embedding (cache: model_name, hash, provider_name -> embedding blob)
  +-- DatasetCollectionBinding (provider_name, model_name -> collection_name)
  +-- AppDatasetJoin (links apps to knowledge bases)
```

### Key Design Patterns in Models

1. **Soft delete + archive**: Documents have `enabled`, `archived`, `disabled_at` fields
2. **Hit counting**: `DocumentSegment.hit_count` incremented on retrieval
3. **Position ordering**: Both segments and child chunks have `position` for ordering
4. **Dual ID system**: `id` (PK, UUID) vs `index_node_id` (vector store reference)
5. **Content hashing**: `index_node_hash` for change detection during re-indexing

### Requirements for Reimplementation

- R-MODEL-1: Implement Dataset, Document, DocumentSegment, ChildChunk as core entities.
- R-MODEL-2: Support JSON metadata on documents for user-defined fields.
- R-MODEL-3: Track indexing status with phase-level timestamps.
- R-MODEL-4: Maintain hit count per segment for analytics.
- R-MODEL-5: Support soft delete (enabled/disabled) and archival.
- R-MODEL-6: Dual ID: internal UUID primary key + vector-store-facing index_node_id.
- R-MODEL-7: Content hash per segment for incremental re-indexing.

---

## 12. Retrieval Strategies

### Retrieval Methods

Four methods defined in `RetrievalMethod`:

| Method | Vector Search | Full-Text Search | Requires Embedding |
|--------|:---:|:---:|:---:|
| `semantic_search` | Yes | No | Yes |
| `full_text_search` | No | Yes | Yes (for store) |
| `hybrid_search` | Yes | Yes | Yes |
| `keyword_search` | No | No (keyword table) | No |

### Retrieval Service Architecture

`RetrievalService.retrieve()` orchestrates retrieval:

1. Spawns search threads using `ThreadPoolExecutor` (configurable `RETRIEVAL_SERVICE_EXECUTORS`)
2. For hybrid search: runs semantic and full-text in parallel, then merges and deduplicates
3. Deduplication strategy: by `doc_id` for Dify documents (keep highest score), by content for external
4. Score threshold filtering: optional minimum score cutoff

### Multi-Dataset Retrieval

`DatasetRetrieval` supports two strategies:

1. **Single retrieval**: Uses LLM router (function-call or ReAct) to select the most relevant dataset, then retrieves from it alone.

2. **Multiple retrieval**: Queries all datasets in parallel (one thread per dataset), then optionally reranks across datasets if `reranking_enable` and `dataset_count > 1`.

### Result Format

Results come back as `list[Document]` where each Document has metadata including `score`, `doc_id`, `document_id`, `dataset_id`.

For parent-child indexes, child chunks are retrieved from the vector store, then their parent segments are looked up and returned with child chunk details attached.

### Requirements for Reimplementation

- R-RET-1: Support four retrieval methods: semantic, full-text, hybrid, keyword.
- R-RET-2: Hybrid search must run vector and full-text in parallel, deduplicate, then rerank.
- R-RET-3: Support multi-dataset retrieval with both single (LLM-routed) and multiple (parallel) strategies.
- R-RET-4: Score threshold filtering as optional configuration.
- R-RET-5: For parent-child indexes, retrieve child chunks then resolve parent segments.
- R-RET-6: Thread-pool-based parallel retrieval with configurable concurrency.
- R-RET-7: Document deduplication by doc_id (keep highest score).

---

## 13. Reranking Subsystem

### Rerank Modes

Two modes in `RerankMode`:

1. **`reranking_model`**: Uses an external rerank model (Cohere, Jina, etc.) via `ModelManager`. The model scores each document against the query and returns relevance scores.

2. **`weighted_score`**: Combines vector similarity score with keyword (TF-IDF/BM25) score using configurable weights: `score = vector_weight * vector_score + keyword_weight * keyword_score`.

### Weighted Score Implementation

- **Keyword scoring**: TF-IDF with cosine similarity. Uses Jieba for keyword extraction.
- **Vector scoring**: Reuses the existing similarity score from vector search (if available), or computes cosine similarity between query embedding and document embedding.
- **Weight configuration**: `vector_weight` + `keyword_weight` (should sum to 1.0). Presets: "semantic_first", "keyword_first", "customized".

### Post-Processing Pipeline

`DataPostProcessor` chains:
1. Reranking (model-based or weighted)
2. Reordering (`ReorderRunner` -- optional, for diversity)

### When Reranking Happens

- **Semantic search**: Optional reranking with model after vector retrieval
- **Full-text search**: Optional reranking with model after full-text retrieval
- **Hybrid search**: Always reranks after merging vector + full-text results
- **Multi-dataset**: Reranks across all datasets when `dataset_count > 1`

### Requirements for Reimplementation

- R-RERANK-1: Support model-based reranking via pluggable rerank model providers.
- R-RERANK-2: Support weighted-score reranking combining vector similarity and keyword TF-IDF.
- R-RERANK-3: Weighted scoring weights must be user-configurable.
- R-RERANK-4: Apply score threshold after reranking.
- R-RERANK-5: Apply top_n truncation after reranking.
- R-RERANK-6: Optional reorder step for diversity.

---

## 14. Metadata Filtering on Retrieval

### Metadata Architecture

- `DatasetMetadata`: Defines custom metadata fields per dataset (name, type: string/number/time)
- `DatasetMetadataBinding`: Links metadata fields to documents
- `Document.doc_metadata`: JSON column storing actual metadata values
- Built-in fields: `document_name`, `uploader`, `upload_date`, `last_update_date`, `source`

### Filtering Modes

Three modes:

1. **`disabled`**: No metadata filtering
2. **`manual`**: User specifies filter conditions in app config
3. **`automatic`**: LLM generates filter conditions from the query (few-shot prompting)

### Supported Comparison Operators

`contains`, `not contains`, `start with`, `end with`, `is`/`=`, `is not`/`!=`, `empty`, `not empty`, `before`/`<`, `after`/`>`, `<=`/`>=`, `in`, `not in`

### Logical Operators

Conditions combined with `and` or `or`.

### Implementation

Metadata filtering happens at the SQL level (PostgreSQL JSON operators on `doc_metadata`), producing a `document_ids_filter` list that is passed to the vector store's search methods. The vector store then filters results to only include vectors from those documents.

For external knowledge bases, the `MetadataCondition` object is passed to the external API.

### Automatic Metadata Filtering

Uses an LLM (configurable model) with few-shot prompts to extract filter conditions from the user query. The LLM receives the list of available metadata field names and returns a JSON structure with field name, value, and comparison operator.

### Requirements for Reimplementation

- R-META-1: Support custom metadata field definitions per dataset (string, number, time types).
- R-META-2: Support metadata values per document.
- R-META-3: Support manual metadata filter conditions with 12+ comparison operators.
- R-META-4: Support logical combination (AND/OR) of filter conditions.
- R-META-5: Filter at SQL level to produce document ID whitelist, passed to vector search.
- R-META-6: Optional: LLM-driven automatic metadata filter extraction from queries.
- R-META-7: Support built-in metadata fields (document name, uploader, dates, source).

---

## 15. RAG Integration with Chat/Completion

### Context Injection

`DatasetRetrieval.retrieve()` is the main entry point from chat/completion flows. It:

1. Takes the user query and dataset config
2. Runs retrieval (single or multiple strategy)
3. Formats results into `DocumentContext(content, score)` list
4. Sorts by score descending
5. Joins all content with `\n` separator
6. Returns the concatenated context string for injection into the LLM prompt

### QA Format Handling

For QA-model segments: context formatted as `"question:{content} answer:{answer}"`

### Citation and Source Tracking

When `show_retrieve_source` is enabled:
- Each result produces a `RetrievalSourceMetadata` object with: dataset_id, dataset_name, document_id, document_name, data_source_type, segment_id, score, content
- In dev mode: also includes hit_count, word_count, segment_position, index_node_hash
- Source list is ordered by score and given sequential position numbers

### Hit Count Tracking

After retrieval, `_on_retrieval_end()` asynchronously (in a separate thread) batch-updates `DocumentSegment.hit_count` for all retrieved segments.

### Query Logging

Every retrieval logs to `DatasetQuery` table: dataset_id, query content, source app, user info.

### Vision/Multimodal Context

When `vision_enabled`, segment attachments (images) are resolved and returned as `File` objects alongside the text context, for multimodal LLMs.

### Trace/Observability

Integrates with `TraceQueueManager` for distributed tracing of retrieval operations.

### Requirements for Reimplementation

- R-RAG-1: Return context as sorted, newline-joined string of chunk contents.
- R-RAG-2: Support QA format with question/answer pairs.
- R-RAG-3: Support citation metadata for source attribution.
- R-RAG-4: Async hit count update after retrieval.
- R-RAG-5: Query logging per dataset per retrieval operation.
- R-RAG-6: Optional multimodal context (image attachments).

---

## 16. Dataset/Knowledge Base Management

### Permission Model

Three levels:
- `only_me`: Only the creator can access
- `all_team_members`: All team members can access
- `partial_members`: Specific users via `DatasetPermission` table

### CRUD Operations

Managed via `DatasetService` and `KnowledgeService`:
- Create dataset with indexing technique, embedding model, retrieval model config
- Add/remove documents
- Enable/disable individual documents and segments
- Archive documents
- Re-index documents (re-run the pipeline)

### App Integration

`AppDatasetJoin` links datasets to apps. A dataset can be used by multiple apps.

### Tags

Datasets can be tagged via the generic `Tag`/`TagBinding` system (type="knowledge").

### API Access

`Dataset.enable_api` controls whether the dataset is accessible via API.

### Requirements for Reimplementation

- R-MGMT-1: Support three permission levels (owner-only, all-team, partial).
- R-MGMT-2: Support document lifecycle: add, enable, disable, archive, re-index.
- R-MGMT-3: Support dataset-to-app linking (many-to-many).
- R-MGMT-4: Support tagging for organization.

---

## 17. External Knowledge Sources

Datasets with `provider="external"` delegate retrieval to an external API:

- `ExternalKnowledgeApis`: Stores API name, endpoint URL, credentials
- `ExternalKnowledgeBindings`: Links external knowledge to a dataset
- At retrieval time, calls the external endpoint with query and retrieval parameters
- Results are wrapped as `Document(provider="external")` with metadata

### Requirements for Reimplementation

- R-EXT-1: Support external knowledge base integration via configurable API endpoints.
- R-EXT-2: Unify external results with internal results in the retrieval pipeline.

---

## 18. Multimodal Support

### Image Handling in Chunks

- During chunking, Markdown images (`![alt](url)`) are detected in chunk content
- Image URLs are resolved to `UploadFile` records
- `SegmentAttachmentBinding` links segments to their image attachments
- `AttachmentDocument` carries image metadata for vector embedding

### Multimodal Embedding

- `dataset.is_multimodal` flag enables multimodal indexing
- `embed_multimodal_documents()`: Base64-encodes images and sends to multimodal embedding model
- `search_by_file()`: Embeds a query image and searches by vector similarity

### Image Queries

`QueryType.IMAGE_QUERY` supports image-based retrieval alongside text queries.

### Requirements for Reimplementation

- R-MM-1: Detect and extract Markdown images from chunk content.
- R-MM-2: Link image attachments to segments.
- R-MM-3: Optional: Support multimodal embedding and image-based retrieval.

---

## 19. Configuration Options and Trade-offs

### Key Configuration Parameters

| Parameter | Location | Effect |
|-----------|----------|--------|
| `VECTOR_STORE` | env/config | Default vector store backend |
| `ETL_TYPE` | env/config | "Dify" (built-in) or "Unstructured" (API) |
| `INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH` | env/config | Max chunk size limit |
| `RETRIEVAL_SERVICE_EXECUTORS` | env/config | Thread pool size for retrieval |
| `CHILD_CHUNKS_PREVIEW_NUMBER` | env/config | Preview limit for hierarchical chunks |
| `VECTOR_INDEX_NAME_PREFIX` | env/config | Collection name prefix |
| `ATTACHMENT_IMAGE_FILE_SIZE_LIMIT` | env/config | Max image size in MB |
| `ATTACHMENT_IMAGE_DOWNLOAD_TIMEOUT` | env/config | Timeout for downloading external images |

### Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Character-count chunking (not tokens) | Simpler but less accurate for token-limited LLMs |
| Database embedding cache (permanent) | No eviction -- grows unbounded over time |
| Redis query cache (10min TTL) | Fast but cold start on restart |
| Thread-based parallelism (not async) | Simpler but GIL-limited for CPU-bound work |
| Jieba for keyword extraction | Excellent for Chinese, less effective for other languages |
| Collection-per-dataset | Clean isolation but multiplies vector store collections |
| JSON metadata in Document column | Flexible but limited query performance vs dedicated columns |

---

## 20. Libraries and Dependencies

| Library | Purpose |
|---------|---------|
| SQLAlchemy | ORM, PostgreSQL access |
| Flask | Web framework |
| Celery | Async task queue for indexing |
| Redis | Query embedding cache, collection existence cache |
| NumPy | Vector normalization, cosine similarity |
| Jieba | Chinese keyword extraction |
| chardet | File encoding detection |
| Pydantic | Data validation (Rule, KnowledgeConfig, etc.) |
| unstructured (optional) | Extended file format parsing |
| python-docx | DOCX extraction |
| openpyxl | Excel extraction |
| beautifulsoup4 | HTML extraction |
| httpx | HTTP client for web crawling |

---

## 21. Reimplementation Requirements Summary

### Priority 1 (Core Pipeline)

| ID | Requirement | Complexity |
|----|------------|------------|
| R-INGEST-1..5 | Stateful ingestion pipeline with phases | Medium |
| R-EXTRACT-1..6 | File extraction dispatcher (PDF, DOCX, MD, HTML, CSV, TXT minimum) | Medium |
| R-CLEAN-1..3 | Text cleaning with configurable rules | Low |
| R-CHUNK-1..7 | Recursive character splitter with custom/auto/hierarchical modes | Medium |
| R-EMBED-1..5 | Embedding provider abstraction with batching and normalization | Medium |
| R-CACHE-1..4 | Two-tier embedding cache (persistent + volatile) | Low |
| R-VEC-1..7 | Vector store abstraction with at least one backend | Medium |
| R-MODEL-1..7 | Core data models (Dataset, Document, Segment, ChildChunk) | Medium |

### Priority 2 (Retrieval)

| ID | Requirement | Complexity |
|----|------------|------------|
| R-RET-1..7 | Four retrieval methods with parallel execution | High |
| R-RERANK-1..6 | Model-based and weighted reranking | Medium |
| R-RAG-1..6 | Context injection, citation, hit tracking | Medium |
| R-KW-1..3 | Keyword index for economy mode | Low |

### Priority 3 (Advanced)

| ID | Requirement | Complexity |
|----|------------|------------|
| R-IDX-1..5 | Three index structure types | Medium |
| R-META-1..7 | Metadata filtering with 12+ operators | Medium |
| R-MGMT-1..4 | Dataset management, permissions, tagging | Medium |
| R-EXT-1..2 | External knowledge base integration | Low |
| R-MM-1..3 | Multimodal support | High |

### Key Architectural Decisions for Reimplementation

1. **Use Oracle Autonomous DB** as converged backend for both vector store and relational data (replaces PostgreSQL + dedicated vector DB).
2. **Replace Jieba** with a language-agnostic keyword extraction approach (or use Oracle Text for full-text search).
3. **Replace Celery** with a lighter task runner or Oracle AQ for async indexing.
4. **Replace Redis embedding cache** with Oracle in-memory or application-level LRU cache.
5. **Consider token-based chunking** instead of character-based for better LLM context utilization.
6. **Implement MCP tool interface** over the retrieval layer for integration with MCP-based agents.
