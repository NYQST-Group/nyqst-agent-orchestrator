# Index Contract (v0)

This platform treats **indexing as a substrate capability**, not a feature of a single module.

The goal is simple: **everything becomes searchable** (primitive + advanced), and every module/agent can use that capability without knowing internal strategies (chunking/reranking/etc. are IP).

## Scope

The index covers (at minimum):
- Artifacts (files/blobs) + extracted text representations (DocIR/text)
- Manifests (immutable trees) and pointers (mutable HEADs)
- Runs + run ledger events (audit history, tool calls, retrieval traces)
- Projects/clients (as they are introduced)

## Core principles

- **Versioned inputs**: indexing targets immutable versions (`manifest_sha256`), not mutable concepts (“the notebook”).
- **Incremental by default**: manifests are Merkle-like trees of artifact hashes; manifest diffs drive incremental indexing.
- **Profiles, not knobs**: modules choose an **index profile** (e.g. `docs.default`), but chunking, hybrid fusion, reranking, etc. are not exposed.
- **Explainable & auditable**: indexing emits runs + ledger events (what happened, with what config, when).
- **Swappable backend**: the contract stays stable while the engine can evolve (pgvector → OpenSearch/Qdrant/Vespa/etc.).

## Contract surface (conceptual)

### Ingest

`ingest(target, profile, mode)`

Targets:
- `pointer_id` (preferred for UI modules)
- `manifest_sha256` (preferred for governance/reproducibility)

Modes:
- `incremental` (default)
- `rebuild` (admin / troubleshooting)

### Retrieve

`search(query, scope, profile)` → returns references (not plaintext)

- Returns `doc_id` + offsets (byte/line) + scores + metadata.
- A separate loader fetches the exact spans (from artifact storage or, later, a local connector).

### Answer / RAG (optional consumer)

“Answering” is just one consumer of retrieval:
- modules may use retrieval for navigation, linking, clustering, similarity, dedupe, etc.
- agents may use retrieval via MCP/tools

## Triggering model (always-on)

Indexing is triggered by substrate events:
- Artifact upload → manifest created → pointer advanced → ingest scheduled
- Connectors/scrapers → new artifacts/manifests → ingest scheduled
- Periodic jobs are allowed, but should be additive (health, drift checks, compaction)

## Profile ownership

Each module must define:
- **How the index makes it “game changing good”** (what tasks become fast/automatic)
- Which profiles it uses (defaults + optional agent-invoked profiles)
- What “levels of care” require stricter evidence constraints / citation mode

## Demo implementation note

In this repo today, “Index Ingest” uses OpenSearch (BM25 + vector) when `INDEX_BACKEND=opensearch`.
The legacy pgvector store remains as a fallback.
