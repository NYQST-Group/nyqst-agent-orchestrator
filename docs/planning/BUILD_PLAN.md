# Build Plan: Platform Foundation → MVP

**Date:** 2026-01-26
**Status:** Draft
**Inputs:** ADRs 001–009, PLATFORM_FOUNDATION.md, PLATFORM_REFERENCE_DESIGN.md, INDEX_CONTRACT.md, external tool research (Docling, LlamaIndex, Tavily/Perplexity)

---

## 1. Approach: Epics vs Chains

We assessed two ways to decompose the remaining work:

- **Epic View** — component-oriented: "build the Index Service, then build the Agent Runtime, then..."
- **Chain View** — flow-oriented: "make upload→search work end-to-end, then make agent→audit work end-to-end, then..."

### Assessment

| Criterion | Epic View | Chain View |
|-----------|-----------|------------|
| **Completeness** | Covers every component; nothing missed | May miss components that don't sit on a user-visible flow |
| **Testability** | Acceptance is per-component (unit-level) | Acceptance is per-flow (integration-level) |
| **Parallelism** | Easy to assign epics to different people | Hard to parallelize — chains cross all components |
| **Integration risk** | High — components built in isolation may not integrate | Low — every deliverable proves integration |
| **Prioritization** | Unclear which epic matters most | Clear — chains are ordered by user value |
| **Interconnection handling** | Poor — misses the "wiring" between components | Native — wiring IS the chain |

### Verdict: Chain-First, Epic-Tracked

The system is too interconnected for pure epic decomposition. Components don't deliver value in isolation — an Index Service with no agent calling it and no UI showing results is shelf-ware.

**We use chains as the build sequence** (what to build, in what order) **and epics as the tracking mechanism** (what work remains within each chain). Each chain decomposes into the epics it touches.

---

## 2. The Five Chains

These are ordered by dependency. Each chain builds on the previous one.

### Chain 1: Upload → Discoverable

**Value:** A user uploads a document and can search it.

```
User uploads file
  → Artifact stored (content-addressed, S3)
    → Manifest created (immutable tree)
      → Pointer advanced (mutable HEAD)
        → Auto-index triggered (Docling parse → chunk → embed → store)
          → Search returns results with citations
            → UI shows search results with source links
```

**Components touched:** ArtifactService, ManifestService, PointerService, IndexService (new), Docling pipeline, OpenSearch/pgvector, REST API, UI (upload + search)

**What exists today:** Substrate chain works (upload → manifest → pointer). RAG demo works (index + search). Auto-indexing triggers on pointer advance.

**What's missing:**
- Unified `IndexService` behind contract (currently split across `RagService` + `opensearch_chunks.py`)
- Docling integration upgraded from text-only to full DocIR (tables, structure, metadata)
- Chunking strategy using Docling's `HybridChunker` (structure-aware) instead of naive character splitting
- UI: file upload component connected to substrate API
- UI: search results panel with citation links back to artifacts

**Acceptance test:**
```
1. POST /api/v1/artifacts — upload a 20-page CRE lease PDF with tables
2. POST /api/v1/manifests — create manifest referencing the artifact
3. PUT /api/v1/pointers/{id}/advance — advance pointer to new manifest
4. WAIT — auto-index run completes (poll /api/v1/runs/{id} → status=completed)
5. Verify: run ledger contains step events for each artifact processed
6. POST /api/v1/index/search — "what is the annual rent escalation?"
   → Returns chunks with artifact_sha256 + page number + section heading
7. UI: Navigate to Research page → see search bar → execute query → see results
   with clickable source links that open the artifact viewer at the cited location
```

---

### Chain 2: Agent → Auditable Work

**Value:** An agent executes a multi-step workflow and every action is recorded.

```
Agent creates run via MCP
  → Executes steps (tool calls, LLM calls, retrieval)
    → Each step logged to run ledger (append-only)
      → Agent produces artifacts, creates manifest
        → Agent advances pointer (publishes output)
          → UI shows run timeline with all events
            → User can inspect any step, see inputs/outputs
```

**Components touched:** MCP run_tools (wire handlers), LangGraph runtime, RunService, LedgerService, SSE streaming, UI (run viewer)

**What exists today:** RunService + LedgerService are complete. MCP substrate tools are wired. SSE streaming works via PostgreSQL NOTIFY.

**What's missing:**
- MCP run_tools: handlers defined but **not wired** into MCP server (stub `register()`)
- LangGraph agent graph: no graph definitions exist yet (empty `agents/graphs/`)
- Agent tool execution pipeline: tools need to auto-log to ledger
- UI: run timeline component (event list with expandable payloads)
- UI: SSE subscription for real-time run updates

**Acceptance test:**
```
1. Agent (via MCP) calls create_run → run_id returned, status=pending
2. Agent calls start_run → status=running, run_started event in ledger
3. Agent calls substrate tools (list_pointers, checkout_manifest)
   → tool_call_started + tool_call_completed events auto-logged
4. Agent calls search via knowledge tools
   → retrieval_query + retrieval_result events logged
5. Agent creates new manifest + advances pointer
   → manifest_created + pointer_moved events logged
6. Agent calls complete_run → status=completed
7. GET /api/v1/runs/{id}/events → ordered event stream, all steps visible
8. UI: Run page shows timeline → click any event → see full payload
9. UI: Events appear in real-time via SSE during execution
```

---

### Chain 3: Research Session → Deep Investigation

**Value:** A user starts a research session, and an agent conducts deep research using both internal documents and external web sources.

```
User opens Research module
  → Session created (scoped to project + mounted resources)
    → User asks research question
      → Agent plans research strategy (fast vs deep)
        → Agent searches internal corpus (Index Service)
          → Agent searches external sources (Tavily API)
            → Agent synthesizes findings with citations
              → Findings stored as artifacts (evidence chain)
                → UI shows research notebook with sources + synthesis
```

**Components touched:** Session model (new), Agent runtime (LangGraph), IndexService, external search (Tavily), LLM synthesis, ArtifactService (store findings), UI (research notebook)

**What exists today:** RAG search works. No session model. No external search integration. No research agent graph.

**What's missing:**
- Session database model + API (ADR-006)
- Research agent graph (LangGraph): plan → search internal → search external → synthesize
- Tavily integration for web search (API key + client wrapper)
- Evidence artifact format: structured JSON with source URL/artifact ref, excerpt, relevance score
- Research notebook UI: question → sources panel → synthesis panel → evidence trail
- Session persistence: return to research session, see previous questions + findings

**External tool integration — Tavily:**
- REST API for web search, optimized for LLM consumption
- Returns clean extracted content (not raw HTML)
- Supports `search_depth: "basic"` (fast) and `"advanced"` (deep, more sources)
- `include_domains` / `exclude_domains` for source filtering
- `include_raw_content: true` for full page text
- Cost: ~$0.001/basic search, ~$0.005/advanced search
- Integration point: MCP tool `research.web.search` wrapping Tavily API

**External tool integration — Perplexity (alternative/complement):**
- Perplexity Sonar API provides search-grounded LLM responses
- Returns answer + citations in one call (no separate search → synthesize steps)
- Models: `sonar` (fast, 127k context), `sonar-pro` (more thorough), `sonar-deep-research` (multi-step)
- `sonar-deep-research` runs autonomous research (multiple searches, reasoning) — takes ~30-90s
- `search_recency_filter`: "day", "week", "month" for time-scoped results
- Cost: sonar ~$1/1M tokens, sonar-pro ~$3-15/1M tokens
- Integration point: MCP tool `research.web.perplexity` as deep research option
- Key difference vs Tavily: Perplexity is search+synthesize combined; Tavily is search-only (you control synthesis)

**Decision: Use both.** Tavily for agent-controlled search (agent decides what to search, how to combine). Perplexity Sonar for "deep research" mode where user wants comprehensive autonomous investigation.

**Acceptance test:**
```
1. POST /api/v1/sessions — create research session for Project X
2. Session has mounted pointers (project's document bundles)
3. User asks: "What are typical lease escalation clauses in Class A office?"
4. Agent searches internal corpus → finds relevant clauses from uploaded leases
5. Agent searches Tavily → finds market data and legal references
6. Agent synthesizes: answer with internal + external citations
7. Findings stored as artifact (JSON with evidence chain)
8. Manifest updated, pointer advanced
9. UI: Research notebook shows question, sources (internal highlighted differently
   from external), synthesis, and evidence trail
10. User closes browser, returns later → session restored, all findings visible
```

---

### Chain 4: Document Processing → Structured Knowledge

**Value:** Complex documents (CRE leases, reports with tables) are parsed into structured, searchable knowledge — not just flat text.

```
User uploads complex PDF (tables, figures, multi-column)
  → Docling processes with appropriate tier (fast/standard/deep)
    → DocIR artifact created (structured JSON alongside raw PDF)
      → HybridChunker creates structure-aware chunks
        → Chunks indexed with structural metadata (section, page, table ref)
          → Search returns results with structural context
            → UI shows results with document structure navigation
```

**Components touched:** Docling pipeline (upgrade), DocIR artifact format, HybridChunker integration, IndexService (structural metadata), UI (document viewer with structure nav)

**What exists today:** Docling text extraction works. Naive 2000-char chunking. No DocIR storage. No structural metadata in index.

**What's missing:**
- Docling pipeline upgrade: enable `do_cell_matching`, table structure extraction, section hierarchy
- DocIR artifact: store `DoclingDocument` JSON as a sibling artifact to the raw PDF
- Manifest entries: raw PDF + DocIR JSON as paired entries with metadata linking them
- HybridChunker: replace naive splitting with Docling's `HybridChunker` (token-aware, structure-preserving)
- Chunk metadata: section headings, page numbers, table references, bounding boxes
- Index enrichment: structural facets in OpenSearch (filter by section, page range, element type)
- UI: document viewer showing parsed structure (outline, table extraction, figure extraction)

**Docling integration architecture (from research):**

```python
# Pipeline configuration per tier
TIER_CONFIGS = {
    "fast": PdfPipelineOptions(
        do_ocr=False,                    # skip OCR for digital PDFs
        do_table_structure=False,        # skip table parsing
        images_scale=1.0,
    ),
    "standard": PdfPipelineOptions(
        do_ocr=True,                     # enable OCR
        do_table_structure=True,         # enable table extraction
        table_structure_options=TableStructureOptions(
            mode=TableFormerMode.FAST,   # fast table model
            do_cell_matching=True,
        ),
    ),
    "deep": PdfPipelineOptions(
        do_ocr=True,
        do_table_structure=True,
        table_structure_options=TableStructureOptions(
            mode=TableFormerMode.ACCURATE,  # accurate table model
            do_cell_matching=True,
        ),
        do_code_enrichment=True,
        do_formula_enrichment=True,
        do_picture_classification=True,
    ),
}

# Chunking (replaces naive 2000-char split)
from docling.chunking import HybridChunker

chunker = HybridChunker(
    tokenizer=OpenAITokenizer(model="text-embedding-3-small"),
    max_tokens=512,        # matches embedding model window
    merge_peers=True,      # merge adjacent small chunks with same heading
)
chunks = list(chunker.chunk(dl_doc=docling_document))

# Each chunk carries structural metadata:
# - chunk.meta.headings  (section hierarchy)
# - chunk.meta.page      (page number)
# - chunk.meta.origin    (table/text/figure)
# - chunk.meta.captions  (figure/table captions)
```

**DocIR storage pattern:**

```
Manifest entry for a processed document:
  /raw/lease-agreement.pdf        → artifact_sha256: abc123...  (original file)
  /docir/lease-agreement.json     → artifact_sha256: def456...  (DoclingDocument JSON)
  /meta/lease-agreement.yaml      → artifact_sha256: ghi789...  (extraction metadata)
```

**Acceptance test:**
```
1. Upload a CRE lease PDF with: cover page, TOC, body text, 3 tables (rent schedule,
   escalation terms, maintenance obligations), 2 figures (floor plan, site map)
2. Process with "standard" tier
3. Verify DocIR artifact created alongside raw PDF in manifest
4. Verify DocIR contains: structured sections, 3 TableItem objects with cell data,
   2 PictureItem objects, correct reading order
5. Verify chunks created with structural metadata (section headings, page refs)
6. Search: "rent escalation schedule" → returns table chunk with table data,
   not just surrounding text
7. Search: "maintenance obligations" → returns section with correct heading hierarchy
8. UI: Document viewer shows outline (clickable sections), extracted tables
   (rendered as HTML tables), and figure thumbnails
```

---

### Chain 5: Governed Workflow → Trusted Output

**Value:** Agent work that requires human oversight follows policy-driven approval gates, building trust incrementally.

```
Project configured with "standard" trust level
  → Agent completes analysis, proposes promotion (bundle → corpus)
    → Policy Engine checks gate rules
      → Gate required: creates ApprovalRequest
        → LangGraph interrupt pauses agent
          → UI shows approval panel (context, evidence, proposed changes)
            → Human reviews and approves/rejects
              → Decision recorded in run ledger
                → Agent resumes (or halts on rejection)
                  → Output promoted to corpus
```

**Components touched:** PolicyEngine (new), ApprovalRequest model (new), LangGraph interrupt integration, RunService (decision events), UI (approval panel + notification)

**What exists today:** Run ledger supports approval event types. LangGraph in dependencies. No policy engine. No approval UI.

**What's missing:**
- Policy Engine service (`services/governance/policy_engine.py`)
- Policy template model (DB) with predefined templates (exploratory/standard/regulated/audit_critical)
- ApprovalRequest model (DB) + API endpoints
- GovernanceNode for LangGraph (checks policy → creates approval → interrupts)
- LangGraph interrupt/resume wiring for approval flows
- UI: ApprovalPanel (render approval context, evidence, approve/reject/modify buttons)
- UI: Notification badge for pending approvals
- Run ledger events: `human.approval.requested`, `human.approval.recorded`

**Acceptance test:**
```
1. Configure project with "standard" policy template
2. Agent completes research, creates output manifest
3. Agent attempts pointer promote (bundle → corpus via advance_pointer)
4. Policy Engine detects gate rule: "substrate.pointer.promote" requires approval
5. ApprovalRequest created with context (what's being promoted, evidence summary)
6. LangGraph interrupt fires — agent execution pauses
7. UI: Notification appears → click → ApprovalPanel shows:
   - What: "Promote research bundle 'Q4 Lease Analysis' to corpus"
   - Evidence: 12 source documents, 3 research runs, synthesis artifact
   - Proposed changes: pointer target moves from manifest A to manifest B
8. Human clicks "Approve" with comment "Looks good, verified sources"
9. Decision recorded: run ledger event with approver, timestamp, comment
10. LangGraph resumes → pointer advanced → corpus updated
11. Run ledger shows complete chain: proposal → gate → approval → execution
```

---

## 3. Epic Decomposition (Per Chain)

Each chain breaks into the epics it touches. An epic may appear in multiple chains — that's the interconnection. The chain tells you WHEN to build it; the epic tells you WHAT to build.

### Epic Map

| Epic ID | Epic Name | Chains | ADR | Status |
|---------|-----------|--------|-----|--------|
| **E-IDX-01** | Unify IndexService behind contract | C1, C3 | ADR-004 | Not started |
| **E-IDX-02** | Index profiles (docs.default) | C1, C4 | ADR-004 | Not started |
| **E-IDX-03** | Structural metadata in index | C4 | ADR-004 | Not started |
| **E-DOC-01** | Docling pipeline upgrade (tiers) | C1, C4 | ADR-007 | Not started |
| **E-DOC-02** | DocIR artifact storage | C4 | ADR-007 | Not started |
| **E-DOC-03** | HybridChunker integration | C1, C4 | ADR-007 | Not started |
| **E-AGT-01** | Wire MCP run_tools handlers | C2 | ADR-008 | Not started |
| **E-AGT-02** | LangGraph agent graph (research) | C2, C3 | ADR-005 | Not started |
| **E-AGT-03** | Tool auto-logging to run ledger | C2 | ADR-005, ADR-008 | Not started |
| **E-SES-01** | Session database model + API | C3, C5 | ADR-006 | Not started |
| **E-SES-02** | Session context injection for agents | C3 | ADR-006 | Not started |
| **E-RES-01** | Tavily web search integration | C3 | — | Not started |
| **E-RES-02** | Perplexity Sonar deep research | C3 | — | Not started |
| **E-RES-03** | Evidence artifact format | C3 | — | Not started |
| **E-GOV-01** | Policy Engine service | C5 | ADR-009 | Not started |
| **E-GOV-02** | ApprovalRequest model + API | C5 | ADR-009 | Not started |
| **E-GOV-03** | LangGraph governance node | C5 | ADR-009 | Not started |
| **E-UI-01** | File upload + artifact viewer | C1, C4 | — | Partial (pages exist) |
| **E-UI-02** | Search results panel | C1, C3 | — | Not started |
| **E-UI-03** | Run timeline viewer | C2 | — | Not started |
| **E-UI-04** | SSE real-time updates | C2 | — | Not started |
| **E-UI-05** | Research notebook | C3 | — | Not started |
| **E-UI-06** | Document structure viewer | C4 | — | Not started |
| **E-UI-07** | Approval panel + notifications | C5 | — | Not started |
| **E-UI-08** | Session persistence + restore | C3, C5 | — | Not started |

### What Falls Out: Shared Epics

Several epics appear in multiple chains. These are the **integration seams** — build them well and multiple chains light up:

| Shared Epic | Chains | Why It's Critical |
|-------------|--------|-------------------|
| E-IDX-01 (Unified IndexService) | C1, C3 | Every search — internal or research — goes through this. Build once, used everywhere. |
| E-DOC-01 (Docling tiers) | C1, C4 | Controls document quality. C1 uses "fast" tier; C4 uses "deep". Same pipeline, different config. |
| E-DOC-03 (HybridChunker) | C1, C4 | Replaces naive chunking everywhere. C1 gets better search; C4 gets structural chunks. Both benefit. |
| E-AGT-02 (LangGraph graph) | C2, C3 | The research agent IS the agent runtime proof. Build it for C3, C2 gets proven infrastructure. |
| E-SES-01 (Session model) | C3, C5 | Sessions scope agent work AND governance. Build for research, governance gets scoping free. |
| E-UI-02 (Search results) | C1, C3 | Same component shows internal search (C1) and research results (C3). |

**Key insight:** The five shared epics (IndexService, Docling, HybridChunker, LangGraph, Session) are the **backbone**. Build these right and the chains compose naturally. Build them wrong and every chain breaks independently.

---

## 4. Build Sequence

Based on chain dependencies and shared epic analysis:

### Phase A: Chain 1 — Upload → Discoverable

**Goal:** User uploads a document, it gets indexed, search returns results in the UI.

| Order | Epic | Work |
|-------|------|------|
| A.1 | E-IDX-01 | Refactor: create `IndexService` interface wrapping current `RagService` + `opensearch_chunks.py`. Implement `ingest(target, profile, mode)` and `search(query, scope, profile)` from INDEX_CONTRACT.md |
| A.2 | E-DOC-01 | Upgrade Docling pipeline: configure `PdfPipelineOptions` with "standard" tier defaults. Enable OCR + table structure. |
| A.3 | E-DOC-03 | Replace naive 2000-char chunking with `HybridChunker(max_tokens=512, merge_peers=True)`. Wire chunk metadata (headings, page, origin) into index records. |
| A.4 | E-IDX-02 | Create `docs.default` index profile. Configure chunking, embedding model, hybrid search weights. |
| A.5 | E-UI-01 | Upload component: file picker → POST /artifacts → create manifest → advance pointer. Show upload progress + indexing status. |
| A.6 | E-UI-02 | Search panel: query input → POST /index/search → render results with artifact ref, page number, section heading, relevance score. Click result → opens artifact. |

**Exit criteria:** The Chain 1 acceptance test passes end-to-end.

### Phase B: Chain 2 — Agent → Auditable Work

**Goal:** An agent runs a workflow and every step is visible in the UI.

| Order | Epic | Work |
|-------|------|------|
| B.1 | E-AGT-01 | Wire MCP `run_tools.py` register function. Connect tool handlers to RunService + LedgerService. |
| B.2 | E-AGT-03 | Add auto-logging middleware: every MCP tool call emits `tool_call_started` + `tool_call_completed` to run ledger automatically. |
| B.3 | E-AGT-02 | Create first LangGraph agent graph: a simple "research assistant" that calls substrate tools + search. Prove checkpoint/resume works. |
| B.4 | E-UI-03 | Run timeline: fetch /runs/{id}/events → render as vertical timeline. Expandable event cards showing payload. |
| B.5 | E-UI-04 | SSE subscription: connect to /streams?channels=run_events → update timeline in real-time as events arrive. |

**Exit criteria:** The Chain 2 acceptance test passes. Run events stream live to UI.

### Phase C: Chain 3 — Research Session → Deep Investigation

**Goal:** User conducts research using internal documents + web sources, with session persistence.

| Order | Epic | Work |
|-------|------|------|
| C.1 | E-SES-01 | Session model: `sessions` table, CRUD API endpoints, session-to-run linkage. |
| C.2 | E-SES-02 | Session context injection: when agent starts in a session, mounted pointers + KBs are injected into LangGraph state. Agent tools are scoped to session mounts. |
| C.3 | E-RES-01 | Tavily integration: `TavilySearchTool` MCP tool. Wraps Tavily API with `search_depth`, `include_domains`, result normalization. Auto-logs to run ledger. |
| C.4 | E-RES-02 | Perplexity integration: `PerplexityResearchTool` MCP tool. Wraps Sonar API for deep research mode. Returns answer + citations. Auto-logs to run ledger. |
| C.5 | E-RES-03 | Evidence artifact format: JSON schema for research findings. Fields: source (internal/external), URL/artifact_ref, excerpt, relevance_score, confidence. Store as artifact, include in manifest. |
| C.6 | E-AGT-02+ | Extend research agent graph: plan → search internal (IndexService) → search external (Tavily) → synthesize (LLM) → store findings (artifacts). Support "fast" (Tavily basic + synthesis) and "deep" (Perplexity sonar-deep-research) modes. |
| C.7 | E-UI-05 | Research notebook: left panel (conversation), right panel (sources with internal/external badges), evidence trail, session restore on return. |
| C.8 | E-UI-08 | Session persistence: on page load, check for active session for this project/module. If found, restore. If not, create new. |

**Exit criteria:** The Chain 3 acceptance test passes. User can research, leave, return, and see full history.

### Phase D: Chain 4 — Document Processing → Structured Knowledge

**Goal:** Complex documents produce structured, navigable knowledge.

| Order | Epic | Work |
|-------|------|------|
| D.1 | E-DOC-01+ | Add "deep" Docling tier: `TableFormerMode.ACCURATE`, formula enrichment, picture classification. Tier selection based on document metadata or user choice. |
| D.2 | E-DOC-02 | DocIR storage: after Docling conversion, serialize `DoclingDocument` JSON as a sibling artifact. Manifest entries pair raw file + DocIR + metadata. |
| D.3 | E-IDX-03 | Structural facets in index: store section headings, page numbers, element type (text/table/figure) as filterable fields in OpenSearch. Support filtered search ("tables only", "section X only"). |
| D.4 | E-UI-06 | Document viewer: outline panel (from DocIR sections), table renderer (from DocIR TableItems), figure gallery (from DocIR PictureItems). Click outline → scroll to section. |

**Exit criteria:** The Chain 4 acceptance test passes. Tables are searchable as structured data.

### Phase E: Chain 5 — Governed Workflow → Trusted Output

**Goal:** Agent actions requiring oversight go through policy-driven approval gates.

| Order | Epic | Work |
|-------|------|------|
| E.1 | E-GOV-01 | Policy Engine: `PolicyEngine` service evaluates action + context against gate rules. Returns gate decision (auto/approve/review/notify). Seed predefined templates. |
| E.2 | E-GOV-02 | ApprovalRequest model + API: DB table, `POST /approvals` (create), `GET /approvals` (list pending), `POST /approvals/{id}/decide` (approve/reject). |
| E.3 | E-GOV-03 | LangGraph GovernanceNode: before governed actions, checks PolicyEngine. If gate required, creates ApprovalRequest, triggers `interrupt_before`. On resume, checks decision. |
| E.4 | E-UI-07 | Approval panel: renders ApprovalContext (summary, evidence, proposed changes). Approve/reject/modify buttons. Comment field for rationale. Notification badge for pending approvals. |

**Exit criteria:** The Chain 5 acceptance test passes. Approval decisions appear in run ledger.

---

## 5. Interconnection Matrix

This is what makes the system "hyper-connected." Each cell shows what Component A provides to Component B.

| → Consumes / Produces ↓ | ArtifactService | ManifestService | PointerService | IndexService | RunService | LedgerService | SessionService | PolicyEngine | LangGraph | Docling | UI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **ArtifactService** | — | validates refs | — | content for indexing | — | — | — | — | — | — | upload/download |
| **ManifestService** | ref counts | — | target resolution | index targets | input/output manifests | — | — | — | — | — | manifest browser |
| **PointerService** | — | points to manifests | — | triggers auto-index | — | — | mounted pointers | gate actions | — | — | pointer list |
| **IndexService** | fetches content | fetches entries | resolves pointers | — | creates index runs | logs search events | scoped to session | — | tool for agents | receives DocIR | search results |
| **RunService** | — | — | — | — | — | logs all events | run.session_id | — | creates/manages runs | — | run list/detail |
| **LedgerService** | — | — | — | — | appends events | — | — | approval events | — | — | event stream (SSE) |
| **SessionService** | — | — | mounts pointers | scopes search | links runs | — | — | policy template | thread_id | — | session restore |
| **PolicyEngine** | — | — | — | — | — | — | reads policy | — | interrupt trigger | — | approval panel |
| **LangGraph** | — | — | — | calls search | manages lifecycle | — | bound to session | checked before actions | — | — | agent interaction |
| **Docling** | reads content | — | — | produces chunks | logged as tool call | — | — | — | called by agent | — | — |

---

## 6. External Tool Integration Summary

### Docling (Document Processing)

**Role:** Primary document parser. Converts PDF/DOCX/PPTX → DoclingDocument (structured IR).

**Integration point:** `src/intelli/services/knowledge/document_converter.py` (upgrade existing)

**Key capabilities to use:**
- `StandardPdfPipeline` with tier-based `PdfPipelineOptions`
- `HybridChunker` for structure-aware chunking (replaces naive splitting)
- `DoclingDocument.model_dump_json()` for DocIR artifact storage
- `docling-serve` (optional): microservice mode for offloading heavy parsing

**Not using (yet):**
- `docling-mcp`: We build our own MCP tools wrapping Docling
- `docling-operator`: K8s deployment is premature
- VLM pipeline: Granite-Docling is promising but adds model management complexity
- Audio/ASR pipeline: Not in scope for CRE document processing

### LlamaIndex

**Role:** NOT primary framework. We use LangGraph for orchestration and our own IndexService for search. However, LlamaIndex has two useful pieces:

1. **`DoclingReader` + `DoclingNodeParser`**: Structure-aware document loading that understands DoclingDocument format. Could be used inside our IndexService as an alternative chunking strategy.
2. **Index abstractions**: If we later need graph-based retrieval (knowledge graphs over CRE entities), LlamaIndex's `KnowledgeGraphIndex` is more mature than building from scratch.

**Integration point:** Optional dependency, not core path. Evaluate when knowledge graph retrieval is needed (F5: Knowledge & Domain module).

**Decision:** Defer. Docling's own `HybridChunker` + our `IndexService` contract covers current needs. LlamaIndex adds dependency weight without clear current benefit.

### Tavily

**Role:** Web search API for research agents. Returns clean, LLM-optimized content.

**Integration point:** `src/intelli/mcp/tools/research_tools.py` (new)

**Key capabilities:**
- `search(query, search_depth="basic"|"advanced", include_domains=[], max_results=10)`
- Returns: `title`, `url`, `content` (extracted text), `score`
- `include_raw_content=True` for full page text
- Fast: ~1-2s per search

**Usage pattern:**
```python
# MCP tool: research.web.search
async def tavily_search(query: str, depth: str = "basic", domains: list[str] = []) -> dict:
    client = TavilyClient(api_key=settings.tavily_api_key)
    results = client.search(query, search_depth=depth, include_domains=domains)
    # Auto-log to run ledger
    await ledger.log_tool_call(run_id, "tavily_search", {"query": query}, results)
    return results
```

### Perplexity Sonar

**Role:** Search-grounded LLM for deep research. Returns synthesized answer + citations.

**Integration point:** `src/intelli/mcp/tools/research_tools.py` (alongside Tavily)

**Key capabilities:**
- `sonar`: Fast search-grounded answers (~3-5s)
- `sonar-pro`: More thorough, multiple searches (~10-15s)
- `sonar-deep-research`: Autonomous multi-step research (~30-90s)
- All return `citations[]` with URLs
- `search_recency_filter` for time-scoped results

**Usage pattern:**
```python
# MCP tool: research.web.deep_research
async def perplexity_research(query: str, mode: str = "sonar") -> dict:
    client = OpenAI(api_key=settings.perplexity_api_key, base_url="https://api.perplexity.ai")
    response = client.chat.completions.create(
        model=mode,  # "sonar" | "sonar-pro" | "sonar-deep-research"
        messages=[{"role": "user", "content": query}],
    )
    # Extract citations from response
    # Auto-log to run ledger
    return {"answer": response.choices[0].message.content, "citations": response.citations}
```

**Tavily vs Perplexity decision matrix:**

| Scenario | Use | Why |
|----------|-----|-----|
| Agent needs raw search results to reason over | Tavily | Agent controls synthesis |
| User wants quick factual lookup | Perplexity sonar | Faster, cheaper, answer included |
| User wants comprehensive research report | Perplexity sonar-deep-research | Autonomous multi-step investigation |
| Agent needs to search + filter specific domains | Tavily | Domain filtering support |
| Need to search + combine with internal results | Tavily + IndexService | Agent merges sources |

---

## 7. UI Chain Map

How each UI component connects to the backend chains:

### Existing UI Pages → Chain Mapping

| UI Page | File | Chain | Backend Integration |
|---------|------|-------|---------------------|
| `ResearchPage.tsx` | `ui/src/pages/ResearchPage.tsx` | C3 | Session API + research agent + search results |
| `NotebooksPage.tsx` | `ui/src/pages/NotebooksPage.tsx` | C1, C4 | Pointer list (bundles) + upload + document viewer |
| `NotebookPage.tsx` | `ui/src/pages/NotebookPage.tsx` | C1, C4 | Single document view + search + DocIR structure |
| `AnalysisPage.tsx` | `ui/src/pages/AnalysisPage.tsx` | C2 (future) | Run viewer + agent interaction |
| `DecisionsPage.tsx` | `ui/src/pages/DecisionsPage.tsx` | C5 | Approval queue + decision history |
| `OverviewPage.tsx` | `ui/src/pages/OverviewPage.tsx` | All | Dashboard: recent sessions, pending approvals, active runs |

### New UI Components Needed (by chain)

**Chain 1 (Upload → Discoverable):**
```
FileUploadDialog          → POST /artifacts + create manifest + advance pointer
SearchBar                 → POST /index/search (with scope = mounted pointers)
SearchResultCard          → Render: title, excerpt, source badge, page ref, score
SearchResultsList         → Paginated list of SearchResultCards
ArtifactViewer            → Download + render artifact (PDF viewer, text viewer)
IndexingStatusBadge       → Poll run status for auto-index runs
```

**Chain 2 (Agent → Auditable Work):**
```
RunTimeline               → Vertical timeline of RunEvents
RunEventCard              → Expandable card: event type icon, timestamp, payload
RunStatusBadge            → Status chip (pending/running/completed/failed)
LiveRunIndicator          → Pulsing dot + SSE connection for active runs
RunDetailPanel            → Full run metadata + event stream + input/output manifests
```

**Chain 3 (Research Session → Deep Investigation):**
```
ResearchNotebook          → Left: conversation thread. Right: sources panel
SourceCard                → Source with badge (internal/external), excerpt, confidence
EvidenceTrail             → Linked chain: question → sources → synthesis → artifact
ResearchModeToggle        → Fast (Tavily basic) vs Deep (Perplexity sonar-deep)
SessionRestoreBanner      → "Continue previous session?" on page load
```

**Chain 4 (Document → Structured Knowledge):**
```
DocumentOutline           → Tree view from DocIR section hierarchy
TableRenderer             → HTML table from DocIR TableItem data
FigureGallery             → Thumbnails from DocIR PictureItems
StructuredSearchFilter    → Filter by: element type, section, page range
DocumentProcessingStatus  → Tier indicator + processing progress
```

**Chain 5 (Governed Workflow → Trusted Output):**
```
ApprovalPanel             → Context + evidence + approve/reject/modify
ApprovalNotificationBadge → Count of pending approvals in nav
ApprovalHistoryList       → Past decisions with outcome + rationale
PolicyIndicator           → Current trust level badge on session/project
```

### UI Data Flow

```
Zustand Stores (client state)
├── auth-store.ts         → JWT token, current user
├── session-store.ts      → Active session, mounted resources (NEW)
├── search-store.ts       → Current query, results, filters (NEW)
├── run-store.ts          → Active runs, event streams (NEW)
└── approval-store.ts     → Pending approvals, decisions (NEW)

TanStack Query (server state cache)
├── useArtifacts()        → GET /artifacts
├── useManifests()        → GET /manifests
├── usePointers()         → GET /pointers
├── useRuns()             → GET /runs
├── useRunEvents(id)      → GET /runs/{id}/events
├── useSession(id)        → GET /sessions/{id} (NEW)
├── useSearch(query)      → POST /index/search (NEW)
├── useApprovals()        → GET /approvals (NEW)
└── mutations for all POST/PUT/DELETE operations

SSE Subscriptions
├── useRunStream(runId)   → /streams?channels=run_events&run_id=X
└── useApprovalStream()   → /streams?channels=approvals
```

---

## 8. What Fell Out

### From the Epic View (things Chains missed):

1. **MCP tool registration cleanup** — run_tools handlers are defined but not wired. This is invisible from chain perspective but is a technical blocker for Chain 2.
2. **Database migrations** — new models (Session, ApprovalRequest, PolicyTemplate) need Alembic migrations. Chains don't surface this infrastructure work.
3. **Configuration management** — new API keys (Tavily, Perplexity), new env vars, new config fields. Epics make this explicit; chains assume it.
4. **Error handling patterns** — what happens when Docling hangs (known issue, needs timeout), when Tavily rate-limits, when OpenSearch is down. Chains show happy path; epics can include resilience stories.

### From the Chain View (things Epics missed):

1. **The "always-on indexing" trigger is the critical integration seam** — epic decomposition would build IndexService and PointerService independently. The chain reveals that the `auto_index_manifest` background task in `pointers.py` is where they connect, and it's fragile (no retry, no dead letter).
2. **Session scoping is a cross-cutting concern, not a feature** — epic view puts "Session" in one epic. Chain view shows sessions touch IndexService (scope search), PolicyEngine (trust level), LangGraph (thread binding), and UI (restore). It's not one epic; it's a capability that must be wired into 4 other systems.
3. **The DocIR-to-chunk-to-index pipeline is a single data flow** — epics would have "Docling upgrade", "chunking", "index metadata" as separate items. The chain shows they're one pipeline where output format of step N must match input format of step N+1. Build them together or integration breaks.
4. **Evidence artifacts are the lingua franca of research** — not obvious from component decomposition, but the chain shows that research findings (internal search results + external search results + synthesis) must be stored as structured artifacts to enable "return to topic" and governance review. This isn't an IndexService concern or an AgentService concern — it's a data format decision that crosses both.

### The Hybrid: What We Actually Do

1. **Build in chain order** (A→B→C→D→E) because each chain proves integration
2. **Track by epic** because each epic has clear "done" criteria and can be assigned
3. **Test by chain acceptance** because that's the only test that proves the system works
4. **Prioritize shared epics** (IndexService, Docling, HybridChunker, Sessions, LangGraph) because they unblock multiple chains

---

## 9. Dependency Graph (What Blocks What)

```
                    ┌─────────────────────┐
                    │ E-IDX-01            │
                    │ Unified IndexService │
                    └──────┬──────────────┘
                           │
              ┌────────────┼────────────────┐
              │            │                │
    ┌─────────▼──┐  ┌──────▼─────┐  ┌───────▼──────┐
    │ E-DOC-01   │  │ E-IDX-02   │  │ E-DOC-03     │
    │ Docling    │  │ Index      │  │ HybridChunker│
    │ tiers      │  │ profiles   │  │              │
    └─────────┬──┘  └──────┬─────┘  └───────┬──────┘
              │            │                │
              └────────────┼────────────────┘
                           │
                    ┌──────▼──────────────┐
                    │ CHAIN 1 COMPLETE    │
                    │ Upload→Discoverable │
                    └──────┬──────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
    ┌─────────▼──┐  ┌──────▼─────┐     │
    │ E-AGT-01   │  │ E-AGT-03   │     │
    │ Wire MCP   │  │ Auto-log   │     │
    │ run_tools  │  │ middleware  │     │
    └─────────┬──┘  └──────┬─────┘     │
              │            │            │
              └─────┬──────┘            │
                    │                   │
              ┌─────▼────────┐          │
              │ E-AGT-02     │          │
              │ LangGraph    │          │
              │ agent graph  │          │
              └─────┬────────┘          │
                    │                   │
              ┌─────▼────────────┐      │
              │ CHAIN 2 COMPLETE │      │
              │ Agent→Auditable  │      │
              └─────┬────────────┘      │
                    │                   │
              ┌─────▼────────┐   ┌──────▼─────┐
              │ E-SES-01     │   │ E-RES-01   │
              │ Session model│   │ Tavily     │
              └─────┬────────┘   └──────┬─────┘
                    │                   │
              ┌─────▼────────┐   ┌──────▼─────┐
              │ E-SES-02     │   │ E-RES-02   │
              │ Context      │   │ Perplexity │
              │ injection    │   └──────┬─────┘
              └─────┬────────┘          │
                    │            ┌──────▼─────┐
                    │            │ E-RES-03   │
                    │            │ Evidence   │
                    │            │ format     │
                    │            └──────┬─────┘
                    │                   │
                    └─────┬─────────────┘
                          │
                    ┌─────▼────────────┐
                    │ CHAIN 3 COMPLETE │
                    │ Research Session  │
                    └─────┬────────────┘
                          │
              ┌───────────┼────────────┐
              │           │            │
    ┌─────────▼──┐ ┌──────▼─────┐ ┌───▼──────────┐
    │ E-DOC-02   │ │ E-IDX-03   │ │ E-GOV-01     │
    │ DocIR      │ │ Structural │ │ Policy Engine│
    │ storage    │ │ metadata   │ └───┬──────────┘
    └─────────┬──┘ └──────┬─────┘     │
              │           │      ┌────▼─────────┐
              └─────┬─────┘      │ E-GOV-02     │
                    │            │ Approval API │
              ┌─────▼──────────┐ └────┬─────────┘
              │ CHAIN 4        │      │
              │ COMPLETE       │ ┌────▼─────────┐
              │ Structured KB  │ │ E-GOV-03     │
              └────────────────┘ │ Governance   │
                                 │ Node         │
                                 └────┬─────────┘
                                      │
                                ┌─────▼──────────┐
                                │ CHAIN 5        │
                                │ COMPLETE       │
                                │ Governed Work  │
                                └────────────────┘
```

**Critical path:** E-IDX-01 → E-DOC-03 → Chain 1 → E-AGT-02 → Chain 2 → E-SES-01 → Chain 3

**Parallel tracks (can run alongside critical path):**
- UI components (E-UI-*) can be built with mock data ahead of backend
- Tavily + Perplexity integrations (E-RES-01, E-RES-02) are independent of IndexService
- Policy Engine (E-GOV-01) can be designed while Chains 1-3 are being built
- DocIR storage (E-DOC-02) can be built alongside Chain 3

---

## 10. Risk Register

| Risk | Impact | Chain | Mitigation |
|------|--------|-------|------------|
| Docling hangs on certain PDFs | Blocks document processing | C1, C4 | `document_timeout=120s`, fallback to text-only extraction |
| OpenSearch unavailable | Blocks all search | C1, C3 | pgvector fallback (already in codebase), health check in startup |
| Tavily rate limiting | Degrades research | C3 | Cache results by query hash (TTL 1h), queue with backoff |
| Perplexity deep research takes >90s | Poor UX | C3 | Show progress indicator, allow cancellation, fallback to sonar (fast) |
| LangGraph checkpoint size grows unbounded | Memory/DB pressure | C2, C3 | Prune checkpoints for closed sessions, configurable retention |
| Policy Engine false positives | Approval fatigue | C5 | Start with "exploratory" (no gates), opt-in to stricter levels |
| HybridChunker token counting mismatch | Bad chunk boundaries | C1, C4 | Use same tokenizer as embedding model (text-embedding-3-small) |
| Session state loss on server restart | Lost work context | C3 | Sessions in DB (not memory), LangGraph threads in PostgreSQL checkpointer |
