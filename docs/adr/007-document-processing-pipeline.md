# ADR-007: Document Processing Pipeline

**Status:** Proposed
**Date:** 2026-01-26
**Deciders:** Mark Forster, Engineering Team
**PRD Reference:** [03_PLATFORM.md - Document Processing Pipeline](../prd/03_PLATFORM.md), [06_ARCHITECTURE.md - Document Intelligence](../prd/06_ARCHITECTURE.md)

---

## Context

NYQST ingests documents from diverse sources (PDFs, DOCX, HTML, scanned images, spreadsheets) and needs to convert them into a canonical intermediate representation (DocIR) that downstream modules depend on. The platform needs:

1. **Multi-format support**: PDF (native + scanned), DOCX, XLSX, HTML, plain text, images, and email (.eml/.msg).
2. **Canonical IR**: A single intermediate representation (DocIR) that all downstream modules consume — analysis, indexing, evidence extraction, claims.
3. **Tiered processing**: Not all documents need the same level of processing. Quick text extraction for basic search vs. full layout analysis with table extraction for analysis workflows.
4. **Parser swappability**: Parser technology evolves rapidly (Docling, Unstructured, LlamaParse, Marker). The platform must not be coupled to any single parser.
5. **Quality evaluation**: Document processing quality directly affects downstream trust. Parsing quality must be measurable and improvable.
6. **Provenance**: Every DocIR output must trace back to source bytes (page, block, span offsets) for citation and evidence anchoring.

Today's codebase has:
- `Docling 2.10.0+` in `pyproject.toml` — primary parser dependency
- `src/intelli/services/docir/` — empty placeholder package
- `src/intelli/services/knowledge/rag_service.py` — basic text chunking (2000 char / 200 overlap) for RAG
- Reference Design §6 — specifies DocIR canonical format and adapter pattern

The current RAG service does simple text extraction and chunking. It does not produce structured DocIR with block types, table models, or span offsets.

---

## Decision

Adopt a **tiered document processing pipeline** with a canonical DocIR format and pluggable parser adapters.

### DocIR Canonical Format

DocIR is the platform's intermediate representation for all parsed documents:

```python
DocIR(
    source_artifact_sha256: str,          # Provenance: which artifact was parsed
    parser: str,                          # Which parser produced this ("docling-v2", "unstructured-v1")
    parser_version: str,
    tier: str,                            # "fast" | "standard" | "deep"

    pages: list[Page],
    metadata: dict,                       # Title, author, dates, language, etc.
)

Page(
    page_number: int,
    width: float | None,                  # Layout geometry (optional)
    height: float | None,
    blocks: list[Block],
)

Block(
    block_type: BlockType,                # "heading" | "paragraph" | "table" | "figure" | "list" | "code" | "footer" | "header"
    level: int | None,                    # Heading level (h1=1, h2=2, etc.)
    text: str,                            # Extracted text content
    spans: list[Span],                    # Character-level spans for evidence anchoring
    table: TableModel | None,             # Structured table (if block_type == "table")
    bbox: BoundingBox | None,             # Layout position (optional, for PDF/image sources)
    confidence: float | None,             # Parser confidence for this block (0.0-1.0)
)

Span(
    start: int,                           # Character offset in block text
    end: int,
    label: str | None,                    # Optional semantic label ("entity", "citation", "number")
    source_page: int,
    source_bbox: BoundingBox | None,      # Back-reference to source layout position
)

TableModel(
    rows: list[list[Cell]],
    headers: list[str] | None,
    caption: str | None,
)
```

DocIR is stored as an **artifact** (JSON, content-addressed) linked to the source artifact via the manifest. This means DocIR outputs are immutable, versioned, and auditable.

### Processing Tiers

| Tier | Use Case | Parser Strategy | Output |
|------|----------|-----------------|--------|
| **Fast** | Quick search indexing, chat context | Text extraction only; minimal structure | Blocks (paragraph-level), no table model, no layout |
| **Standard** | Document management, research | Full block extraction with headings, paragraphs, lists, tables | Full DocIR with table model, no layout geometry |
| **Deep** | Analysis, evidence anchoring, claims | Full extraction + layout analysis + OCR + confidence scoring | Full DocIR with layout geometry, confidence scores, span-level provenance |

Tier selection is driven by:
- Module context (research may use "standard"; analysis uses "deep")
- Index profile requirements (search indexing uses "fast")
- User/policy override (regulated workflows may mandate "deep")

### Parser Adapter Pattern

```
Document Artifact (PDF/DOCX/etc.)
         │
         ▼
┌────────────────────┐
│  Parser Dispatcher  │  ← Selects adapter based on media_type + tier
└────────┬───────────┘
         │
    ┌────▼────┐  ┌──────────┐  ┌───────────┐  ┌────────┐
    │ Docling  │  │Unstructd │  │LlamaParse │  │ Marker │
    │ Adapter  │  │ Adapter  │  │  Adapter  │  │Adapter │
    └────┬────┘  └────┬─────┘  └─────┬─────┘  └───┬────┘
         │            │              │              │
         └────────────▼──────────────▼──────────────┘
                      │
               ┌──────▼──────┐
               │  DocIR JSON  │  ← Canonical output (stored as artifact)
               └─────────────┘
```

Each adapter:
- Accepts a source artifact (bytes + media_type)
- Produces a `DocIR` object
- Is versioned independently
- Reports parsing confidence and any warnings

The dispatcher selects the adapter based on:
1. Media type (e.g., `application/pdf` → Docling or LlamaParse)
2. Tier (fast/standard/deep)
3. Configuration (which adapters are enabled, preference order)
4. Fallback chain (if primary adapter fails, try secondary)

### Pipeline as LangGraph Workflow

Document processing runs as a LangGraph workflow for orchestration benefits:

```
[Receive artifact] → [Select adapter] → [Parse] → [Validate DocIR] → [Store DocIR artifact]
                                           │                              │
                                           └── retry on failure           └── trigger indexing
```

This gives us:
- Checkpointing (large documents can be resumed)
- Streaming progress to UI
- Run ledger events for audit
- Retry logic for transient failures

---

## Options Considered

### Option 1: Docling-Only

**Description:** Use Docling as the sole document parser for all formats and tiers.

**Pros:**
- Single dependency, simpler code
- Docling handles PDF, DOCX, XLSX, HTML, images
- Open source, actively maintained
- Good table extraction quality

**Cons:**
- Single point of failure if Docling has quality issues for a format
- No competitive pressure for quality improvement
- Missing some formats (email, specialized)

### Option 2: Tiered Pipeline with Adapter Pattern (Selected)

**Description:** Define a canonical DocIR format with pluggable parser adapters. Start with Docling as the primary adapter; add others as quality demands.

**Pros:**
- Parser technology can evolve without changing downstream code
- Different parsers can excel at different formats
- Competitive evaluation between parsers drives quality
- DocIR provides a stable contract for all consumers
- Tiers avoid over-processing for simple use cases

**Cons:**
- More initial design work (DocIR schema, adapter interface)
- Must maintain adapter implementations
- DocIR schema may need evolution as requirements emerge

### Option 3: External Parsing Service (API-based)

**Description:** Use external parsing APIs (LlamaParse, Adobe Extract, Azure Document Intelligence) as the primary processing path.

**Pros:**
- Best-in-class quality for complex documents
- No local compute for parsing
- Handles edge cases (handwriting, complex layouts)

**Cons:**
- External dependency and latency
- Cost per document at scale
- Data residency concerns (documents leave the platform)
- Vendor lock-in

---

## Decision Rationale

Option 2 (Tiered Pipeline with Adapter Pattern) was chosen because:

1. **DocIR as contract**: Downstream modules (indexing, analysis, evidence, claims) depend on a stable IR, not parser-specific formats. This is the same "contract-first" pattern used throughout the platform.
2. **Docling as starting point**: Docling is already in dependencies and handles the common cases. Adding adapters later is additive, not disruptive.
3. **Tiers save compute**: Not every document needs deep layout analysis. Quick text extraction for search indexing should be fast and cheap.
4. **Quality evolution**: When a parser produces poor results for a format, we can add or swap an adapter without touching downstream code.
5. **Provenance by design**: DocIR's span model enables evidence anchoring from day one. This is foundational for the trust primitives (EvidenceSpan, Claim, ClaimSupportLink).

---

## Consequences

### Positive

- Downstream modules have a stable, rich intermediate representation
- Parser swapping is a configuration change, not a code change
- Tiered processing optimizes compute cost vs. quality
- Full provenance from DocIR spans to source bytes
- Quality is measurable (compare adapter outputs for the same document)

### Negative

- DocIR schema design requires upfront investment
- Must maintain at least one adapter (Docling) with quality parity
- DocIR JSON artifacts add storage overhead (mitigated by content-addressing deduplication)

### Risks

- **Risk:** DocIR schema insufficient for future document types (e.g., CAD drawings, video transcripts)
  - **Mitigation:** DocIR is extensible via metadata and custom block types. Evolution creates new schema versions, not breaking changes.
- **Risk:** Docling quality degrades or project becomes unmaintained
  - **Mitigation:** Adapter pattern means we can swap to Unstructured, LlamaParse, or Marker without downstream changes.
- **Risk:** Tier selection becomes complex with many combinations
  - **Mitigation:** Default tier is "standard" for all modules. Override only when demonstrably needed.

---

## Implementation Notes

1. **DocIR schema**: Define as Pydantic models in `src/intelli/schemas/docir.py`. Register the JSON Schema in the Schema Registry.
2. **Adapter interface**: `DocParser` abstract base class with `parse(artifact_bytes, media_type, tier) -> DocIR` method. Implementations in `src/intelli/services/docir/adapters/`.
3. **Docling adapter**: Primary adapter in `src/intelli/services/docir/adapters/docling_adapter.py`. Maps Docling's `DocumentConverter` output to DocIR format.
4. **Storage**: DocIR JSON is stored as an artifact (content-addressed). The manifest entry links source artifact to DocIR artifact (`path: "docir/{source_sha256}.json"`).
5. **Index integration**: When Index Service ingests a manifest, it checks for DocIR artifacts. If present, it chunks based on DocIR blocks (respecting headings and paragraphs) rather than naive character splitting.
6. **Migration from RagService**: Gradually replace `RagService.index_manifest`'s inline text extraction with the DocIR pipeline. The existing chunking logic becomes a consumer of DocIR.

---

## Related ADRs

- [ADR-001: Data Model Strategy](./001-data-model-strategy.md) — DocIR stored as domain-first artifacts
- ADR-004: Index Service Architecture — Index Service consumes DocIR for intelligent chunking
- ADR-005: Agent Runtime & Framework — Document processing runs as LangGraph workflow
- ADR-008: MCP Tool Architecture — Document processing tools exposed via MCP

---

## References

- [PLATFORM_REFERENCE_DESIGN.md §6 — Document Processing](../PLATFORM_REFERENCE_DESIGN.md)
- [Docling Documentation](https://ds4sd.github.io/docling/)
- [Unstructured.io](https://unstructured.io/)
- [LlamaParse](https://docs.llamaindex.ai/en/stable/llama_cloud/llama_parse/)
