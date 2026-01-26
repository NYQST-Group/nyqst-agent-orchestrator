# ADR-004: Index Service Architecture

**Status:** Proposed
**Date:** 2026-01-26
**Deciders:** Mark Forster, Engineering Team
**PRD Reference:** [03_PLATFORM.md - Indexing/Diffing Service](../prd/03_PLATFORM.md), [06_ARCHITECTURE.md - Index Service](../prd/06_ARCHITECTURE.md)

---

## Context

NYQST treats indexing as a **substrate capability** — every artifact, manifest, run event, and domain object should be searchable without any module owning the indexing strategy. The platform needs a unified Index Service that supports:

1. **Multiple retrieval modes**: keyword (BM25), semantic (dense embeddings), hybrid (fusion + reranking), faceted metadata filtering, and trace search over run events.
2. **Profile-based abstraction**: Modules select profiles (`docs.default`, `docs.citation_strict`, `runs.trace_search`), not chunking parameters or reranking knobs. Profiles are the IP boundary.
3. **Always-on triggering**: Indexing fires automatically on pointer advance — no "Index" button in the UI.
4. **Incremental efficiency**: Manifest diffs (Merkle-like hash DAGs) drive change detection; chunk-hash caching avoids redundant embedding compute.
5. **Swappable backends**: The contract must survive a migration from pgvector to OpenSearch to Qdrant without rewriting product logic.

Today's code has two partial implementations:
- `RagService` (pgvector) — stores chunks + embeddings in PostgreSQL; used by `/api/v1/rag`.
- `opensearch_client.py` / `opensearch_chunks.py` — OpenSearch integration for hybrid search when `INDEX_BACKEND=opensearch`.
- `auto_index.py` — thin orchestration facade that wraps `RagService` and emits run ledger events.

These need to be unified behind a single contract.

---

## Decision

Adopt a **contract-first, profile-driven Index Service** with pluggable backends.

### Architecture

```
Modules / Agents
       │
       ▼
┌─────────────────────────────┐
│     Index Service Contract   │  ← Stable API surface
│  ingest() / search() / explain()
└──────────┬──────────────────┘
           │
    ┌──────▼──────┐
    │ Profile      │  ← Binds strategy (chunking, embedding, reranking)
    │ Registry     │     to a named profile with version
    └──────┬──────┘
           │
    ┌──────▼──────────────────┐
    │  Backend Adapter Layer   │
    │  ┌─────────┐ ┌────────┐ │
    │  │pgvector │ │OpenSrch│ │  ← Swappable at deployment time
    │  └─────────┘ └────────┘ │
    │  ┌─────────┐ ┌────────┐ │
    │  │ Qdrant  │ │ Vespa  │ │  ← Future backends
    │  └─────────┘ └────────┘ │
    └─────────────────────────┘
```

### Contract Surface

```python
# Ingest
async def ingest(
    target: str,          # manifest_sha256 or pointer_id
    profile: str,         # e.g. "docs.default"
    mode: str = "incremental",  # "incremental" | "rebuild"
) -> IngestResult

# Search
async def search(
    query: str,
    scope: SearchScope,   # pointer_ids, project_id, or global
    profile: str,
    top_k: int = 10,
    filters: dict | None = None,
) -> list[SearchResult]   # Returns references (doc_id + offsets + scores), not plaintext

# Explain
async def explain(
    result: SearchResult,
) -> ExplainResult        # Why this result matched (scores, features, profile info)
```

### Profile Model

Each profile is a versioned configuration object:

```python
IndexProfile(
    name="docs.citation_strict",
    version="1.0",
    chunking=ChunkingStrategy(method="semantic", max_tokens=512, overlap=64),
    embedding=EmbeddingConfig(model="text-embedding-3-small", dimensions=1536, provider="openai"),
    retrieval=RetrievalConfig(method="hybrid", bm25_weight=0.3, semantic_weight=0.7),
    reranker=RerankerConfig(model="cohere-rerank-v3", top_n=5) | None,
    filters=FilterConfig(required_fields=["source_type", "confidence"]),
)
```

Profiles are registered in the Schema Registry (ADR future) and versioned. Profile changes trigger re-indexing where necessary.

### Triggering Model

1. **Pointer advance** → `auto_index.py` schedules `ingest(pointer_id, profile, "incremental")`
2. **Manifest diff** determines which artifacts are new/changed/removed
3. **Chunk-hash cache** skips re-embedding unchanged content
4. **Run ledger** records every ingest operation (profile, backend, timing, stats)

### LangChain / LangGraph Split

- **LangChain** (inside Index Service): provides parsers, splitters, embeddings, retrievers, rerankers as implementation details behind profiles.
- **LangGraph** (orchestration): runs indexing as a workflow (fan-out across artifacts, retries, checkpoints) and runs agentic RAG workflows that call Index Service via MCP.
- **LangSmith** (optional): developer tracing for retrieval quality debugging. Run ledger remains canonical for audit.

---

## Options Considered

### Option 1: Unified pgvector Only

**Description:** Use PostgreSQL pgvector for all search (BM25 via tsvector + semantic via pgvector).

**Pros:**
- Single infrastructure dependency
- Transactional consistency with metadata
- Simpler operations

**Cons:**
- pgvector has limited ANN performance at scale (>1M vectors)
- No native BM25 ranking quality comparable to Lucene-based engines
- Missing advanced features (faceting, aggregations, multi-tenancy sharding)
- Vendor lock to PostgreSQL extension ecosystem

### Option 2: OpenSearch Primary with pgvector Fallback (Selected)

**Description:** Use OpenSearch as the primary search backend for production (BM25 + kNN + hybrid). Keep pgvector as a lightweight fallback for development and small deployments.

**Pros:**
- OpenSearch provides production-grade hybrid search (BM25 + kNN + reranking)
- Scales independently from PostgreSQL
- Rich faceting, aggregations, and multi-tenant index patterns
- pgvector fallback means zero external dependencies for dev/small setups
- Backend selectable via `INDEX_BACKEND` config (already implemented)

**Cons:**
- Two code paths to maintain (OpenSearch + pgvector)
- Additional infrastructure component in production
- Eventually-consistent indexing (vs transactional pgvector)

### Option 3: Dedicated Vector DB (Qdrant/Milvus) + Search Engine

**Description:** Separate vector DB for embeddings, separate search engine for keyword/faceted search.

**Pros:**
- Best-in-class for each concern
- Qdrant/Milvus optimized for high-throughput ANN

**Cons:**
- Three infrastructure components (Postgres + vector DB + search engine)
- More complex query federation
- Premature optimization before scale demands it

---

## Decision Rationale

Option 2 (OpenSearch primary, pgvector fallback) was chosen because:

1. **Already implemented**: Both backends exist in code. The adapter pattern is partially in place via `INDEX_BACKEND` config selection.
2. **Appropriate for current scale**: OpenSearch handles hybrid search well at the 10K-1M document scale NYQST targets initially.
3. **Dev simplicity**: pgvector fallback means developers can run the full stack with just PostgreSQL.
4. **Upgrade path clear**: If vector throughput demands exceed OpenSearch, the contract allows adding Qdrant/Vespa without product code changes.
5. **Profile abstraction**: The contract-first approach means backend choice is invisible to modules and agents.

---

## Consequences

### Positive

- Modules never interact with search backends directly — only via profiles
- Always-on indexing ensures content is discoverable without user action
- Incremental indexing via manifest diffs keeps compute costs low
- Backend swappable without product code changes
- Every index operation is auditable via run ledger

### Negative

- Two backend implementations to maintain (OpenSearch + pgvector)
- Profile versioning adds complexity (re-index on profile change)
- Eventually-consistent search results (OpenSearch refresh interval)

### Risks

- **Risk:** Profile proliferation makes the system hard to reason about
  - **Mitigation:** Start with 3-4 profiles (`docs.default`, `docs.citation_strict`, `runs.trace_search`, `projects.cross_project`); add only when a module demonstrates the need
- **Risk:** OpenSearch adds operational burden
  - **Mitigation:** Use managed OpenSearch (AWS) in production; Docker Compose for dev; defer cluster tuning until scale forces it
- **Risk:** Chunk-hash cache grows unbounded
  - **Mitigation:** Tie cache entries to manifest references; prune when artifacts have zero reference count

---

## Implementation Notes

1. **Unify `RagService` and `opensearch_chunks.py`** behind a single `IndexService` class that delegates to the configured backend adapter.
2. **Profile registry**: Store profiles as JSON in the database (or config files initially). Each profile is immutable once published; changes create new versions.
3. **Ingest pipeline** (inside LangGraph workflow):
   - Resolve target (pointer → manifest → artifact list)
   - Diff against last indexed manifest
   - Fan-out: parse → chunk → embed per artifact (parallel)
   - Write to backend
   - Emit run ledger events (profile, backend, stats)
4. **Search pipeline**:
   - Accept query + scope + profile
   - Delegate to backend adapter
   - Return references (not plaintext) with scores
   - Explain endpoint returns scoring breakdown
5. **Multi-provider embeddings**: Bind embedding model to profile (not global config). This allows different profiles to use different embedding models as needed.

---

## Related ADRs

- [ADR-001: Data Model Strategy](./001-data-model-strategy.md) — Index Service indexes domain-first models
- [ADR-002: Code Generation Strategy](./002-code-generation-strategy.md) — Index Service contract types flow through code generation
- ADR-005: Agent Runtime & Framework — Agents use Index Service via MCP tools
- ADR-008: MCP Tool Architecture — Index Service exposed as MCP tools for agents

---

## References

- [PLATFORM_REFERENCE_DESIGN.md §4 — Index Service](../PLATFORM_REFERENCE_DESIGN.md)
- [INDEX_CONTRACT.md](../INDEX_CONTRACT.md)
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [pgvector](https://github.com/pgvector/pgvector)
- [LangChain Retrievers](https://python.langchain.com/docs/modules/data_connection/retrievers/)
