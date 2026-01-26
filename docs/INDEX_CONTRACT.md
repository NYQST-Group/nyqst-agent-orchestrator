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

## Where LangGraph / LangChain / LangSmith fit

To avoid inventing a custom agentic stack, use these tools *behind* the contract:

- **LangChain** (inside the Index Service) provides the RAG/indexing primitives:
  - parsing/loading, splitting, embeddings
  - retrievers + rerankers (hybrid and multi-stage retrieval)
  - integrations with search/vector backends

  The platform still owns the “IP boundary”: LangChain components are wired into **profiles**, not exposed as user-visible knobs.

- **LangGraph** is an orchestration/runtime layer, not the index itself:
  - use it to run indexing workflows (fan-out, retries, checkpoints) as **runs**
  - use it to run agentic RAG workflows that call the Index Service + MCP tools
  - do **not** treat LangGraph memory/stores as the enterprise Index Service (those are for per-thread memory/resume, not global search over corpora)

- **LangSmith** is optional developer tooling (tracing + evals):
  - helpful for debugging and regression testing indexing/retrieval quality
  - does not replace the platform run ledger (ledger remains canonical for audit/export)

## Multi-provider considerations (embeddings + rerankers)

The index inevitably depends on models (embeddings, and optionally rerankers). To keep this enterprise-ready:
- Bind model/provider choice to **profiles** (not user-visible knobs).
- Support multiple providers via a **ModelRouter** that can select per-tenant/per-profile providers (OpenAI/Anthropic/Azure/etc.), with policy constraints.
- Emit run ledger fields/hashes for:
  - embedding model id + dimensions + provider
  - reranker model id + provider (if used)
  - profile id + version
  - index backend id + version

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
