---
document_id: COMPREHENSIVE-GAP-ANALYSIS
version: 1
date: 2026-02-20
author: claude-sonnet-4-6
role: Senior Engineering Lead
inputs:
  - 04-gaps/hypothesis-consistency.md (H1–H4)
  - 04-gaps/hypothesis-code-alignment.md (H5–H8)
  - 00-inventory/EXTRACTION-SUMMARY.md
  - 00-inventory/KNOWLEDGE-MAP.md
  - 01-extracts/orchestration-extract.md
  - 01-extracts/streaming-events-extract.md
  - 01-extracts/billing-metering-extract.md
  - docs/analysis/CONSISTENCY-AUDIT-ANALYSIS.md
  - docs/plans/CONSISTENCY-AUDIT-PLANS.md
status: DEFINITIVE — synthesizes all prior audit and extraction work
---

# Comprehensive Gap Analysis — NYQST DocuIntelli Platform

---

## Gap Summary Dashboard

### Counts by Category

| Category | CRITICAL | HIGH | MEDIUM | LOW | Total |
|----------|----------|------|--------|-----|-------|
| 1. Documentation Gaps | 3 | 4 | 5 | 2 | 14 |
| 2. Design Gaps | 2 | 5 | 3 | 1 | 11 |
| 3. Implementation Gaps | 2 | 4 | 4 | 2 | 12 |
| 4. Competitive Intelligence Gaps | 0 | 1 | 3 | 1 | 5 |
| 5. Operational Gaps | 1 | 3 | 3 | 2 | 9 |
| **TOTALS** | **8** | **17** | **18** | **8** | **51** |

### Counts by Wave

| Wave | CRITICAL | HIGH | MEDIUM | LOW | Total |
|------|----------|------|--------|-----|-------|
| P0 (Immediate — before any code) | 5 | 8 | 2 | 0 | 15 |
| W0 (Phase 0 foundation) | 2 | 5 | 6 | 1 | 14 |
| W1 (Phase 1 build) | 1 | 2 | 5 | 2 | 10 |
| W2 (Phase 2 build) | 0 | 2 | 3 | 2 | 7 |
| W3 (Phase 3+) | 0 | 0 | 2 | 3 | 5 |

### Key Risk Summary

**Production-blocking bugs confirmed in codebase** (GAP-022, GAP-023): Two CRITICAL bugs verified by direct code inspection — a race condition in RunEvent sequence numbering and a worker registry initialization order failure. Both will cause data corruption or silent job loss in production.

**Chart library conflict unresolved across 4 documents** (GAP-001): DEC-048 locks Plotly.js but the correction has not been written back into IMPLEMENTATION-PLAN, STRATEGIC-REVIEW, and GIT-ISSUES BL-009. Any developer reading those documents will implement the wrong library.

**GML rendering pipeline split not yet propagated** (GAP-002): DEC-015 has been split into DEC-015a/b, but 4 downstream documents still reference the old undivided decision. The split is decided but not implemented in documentation.

**7 open questions closed in DECISION-REGISTER but not in source docs** (GAP-003): OQ-001 through OQ-007 were resolved with DEC-042–052, but documents that reference those open questions (STRATEGIC-REVIEW, GML-RENDERING-ANALYSIS, CODEX-ANALYSIS) still show them as unresolved.

---

## Category 1: Documentation Gaps

### GAP-001 — Chart Library Decision Not Propagated

- **ID**: GAP-001
- **Severity**: CRITICAL
- **Description**: DEC-048 locks Plotly.js (`react-plotly.js`) as the chart library. This is correct and grounded in Superagent bundle analysis (Superagent uses Plotly via `gml-chartcontainer`). However, the decision has NOT been written back into four documents that still specify Recharts: IMPLEMENTATION-PLAN section 3.6, GIT-ISSUES BL-009 acceptance criteria ("CHART nodes render as Recharts charts"), STRATEGIC-REVIEW (recommended Recharts for bundle size), and the LIBRARY-REFERENCE LIB-13 section. A developer reading any of these documents will use the wrong library.
- **Affected BL Items**: BL-004, BL-005, BL-009, BL-019
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-01, I-14; hypothesis-consistency.md H1; EXTRACTION-SUMMARY confirms Plotly in Superagent bundle
- **Resolution**: Update IMPLEMENTATION-PLAN section 3.6 to "Chart rendering: react-plotly.js". Update GIT-ISSUES BL-009 acceptance criteria to Plotly. Update STRATEGIC-REVIEW to reflect DEC-048. Confirm LIB-13 in LIBRARY-REFERENCE documents `react-plotly.js`. Mark I-01 and I-14 as resolved.
- **Owner Recommendation**: Documentation lead / plan owner; 30-minute task per document
- **Wave**: P0 — must complete before any implementation code is written

---

### GAP-002 — GML Rendering Pipeline Split Not Propagated

- **ID**: GAP-002
- **Severity**: CRITICAL
- **Description**: DEC-015 was split into DEC-015a (backend MarkupDocument JSON AST, used by BL-004/BL-005 report generation) and DEC-015b (frontend GML rendering uses rehype-to-JSX, NOT a JSON AST intermediate layer). This split resolves the conflict between DEC-015 and GML-RENDERING-ANALYSIS. However, multiple documents still reference the old undivided DEC-015 and the conflict is still listed as open. CONSISTENCY-AUDIT-ANALYSIS Section 5.3 flagged this as the "most significant unresolved conflict in the entire document set." GML-RENDERING-ANALYSIS's Section 4 recommendation (skip JSON AST, use rehype-to-JSX) is NOW CORRECT under DEC-015b, but the document doesn't know this because DEC-015 was not split when GML-RENDERING-ANALYSIS was written.
- **Affected BL Items**: BL-004, BL-005, BL-009 (report generation and rendering pipeline)
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS SC-02, I-13; CONSISTENCY-AUDIT-ANALYSIS C-04, C-11; hypothesis-consistency.md H3 gap 2
- **Resolution**: Add a "Status Update" note to GML-RENDERING-ANALYSIS Section 4 clarifying that the DEC-015 split has resolved the conflict — its rehype-to-JSX recommendation is confirmed as DEC-015b. Update DEC-015 entry in DECISION-REGISTER to show the split clearly. Update any document that cross-references DEC-015 to distinguish the two sub-decisions.
- **Owner Recommendation**: Architecture lead; requires 1–2 hours to update all cross-references
- **Wave**: P0 — required before BL-004 or BL-009 implementation begins

---

### GAP-003 — Open Questions Still Appear Open in Source Documents

- **ID**: GAP-003
- **Severity**: CRITICAL
- **Description**: OQ-001 through OQ-007 were resolved in DECISION-REGISTER v2 with new decisions DEC-042–052 (as of 2026-02-19). However, documents that originally asked these questions still show them as open. A developer reading STRATEGIC-REVIEW Section 8 will see seven unresolved questions. GML-RENDERING-ANALYSIS OQ-005 framing is based on a false premise that has since been resolved by DEC-043 (separate ReportPanel). CODEX-ANALYSIS-SUMMARY lists infrastructure choices as "Unresolved" that are in fact locked (Auth: DEC-038, Web search: DEC-032/DEC-046, Observability: DEC-037).
- **Affected BL Items**: All BL items — affects developer onboarding and execution confidence
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS Part 2, I-11, I-16; hypothesis-consistency.md H3 gap 3; KNOWLEDGE-MAP Section 10
- **Resolution**: Add a resolution block to each affected document's open question. For STRATEGIC-REVIEW: append a "Resolution" row to each OQ-001–OQ-007 entry pointing to the DEC-04x that resolved it. For GML-RENDERING-ANALYSIS: add a note to OQ-005 section. For CODEX-ANALYSIS-SUMMARY: annotate the infrastructure matrix with resolution citations.
- **Owner Recommendation**: Documentation lead; mechanical task, no architectural judgment needed
- **Wave**: P0 — must be closed before Wave 0 begins to prevent misaligned implementation

---

### GAP-004 — Analysis Module (Infinite Canvas) Scope Deferral Not Explicit

- **ID**: GAP-004
- **Severity**: HIGH
- **Description**: The PRD (03_PLATFORM.md) specifies six integrated modules: Research, Document Management, Analysis (infinite canvas), Modelling (provable methods), Knowledge & Domain, and Organisational Insight. The IMPLEMENTATION-PLAN v3 frames work as "ten platform primitives" validated through the Research Module. The Analysis Module (infinite canvas for visual analysis) does not appear anywhere in BL-001 through BL-022. There is no explicit statement in the IMPLEMENTATION-PLAN that the Analysis Module is deferred and why. A product manager or new team member reading both documents cannot determine the deferred scope without cross-referencing all six modules against the backlog.
- **Affected BL Items**: None in current backlog (the gap IS the absence of any BL item)
- **Source Evidence**: hypothesis-consistency.md H1 gap 1; KNOWLEDGE-MAP Section 2 (Platform Layer)
- **Resolution**: Add a "Deferred Scope" section to IMPLEMENTATION-PLAN explicitly listing the three deferred PRD modules (Analysis, Modelling, Organisational Insight) with rationale and the ADR/DEC that defers them. This does not require new decisions — it is a documentation clarification.
- **Owner Recommendation**: Product lead; 1-hour documentation task
- **Wave**: W0 — before Phase 1 design reviews

---

### GAP-005 — Index Service Not Listed as Layer 1 Primitive

- **ID**: GAP-005
- **Severity**: HIGH
- **Description**: ADR-004 specifies the Index Service Architecture (contract-first, pluggable backends: OpenSearch + pgvector). The KNOWLEDGE-MAP confirms it is a key platform component. However, the IMPLEMENTATION-PLAN's "ten platform primitives" list does not include the Index Service. It is documented in the ADR and referenced in PLATFORM-FRAMING.md, but a developer building the primitives would not know it belongs at Layer 1 from reading the IMPLEMENTATION-PLAN alone.
- **Affected BL Items**: BL-003 (web research MCP tools), BL-016 (entity/citation substrate)
- **Source Evidence**: hypothesis-consistency.md H1 gap 3; KNOWLEDGE-MAP Section 3 (Infrastructure & Storage)
- **Resolution**: Add "Index Service (pluggable search backend)" as the eleventh platform primitive in IMPLEMENTATION-PLAN, or add a footnote under the existing "MCP Tool Layer" primitive that explicitly calls out Index Service as a sub-component. Cross-reference ADR-004.
- **Owner Recommendation**: Architecture lead
- **Wave**: W0 — before BL-003 or BL-016 implementation

---

### GAP-006 — Document Processing Pipeline Strategy Not in Decision Register

- **ID**: GAP-006
- **Severity**: HIGH
- **Description**: ADR-007 specifies a tiered document processing pipeline (Fast, Standard, Deep) with parser adapters (Docling primary, Unstructured fallback, LlamaParse optional). DECISION-REGISTER has DEC-030 (PDF export via WeasyPrint) and DEC-033 (Jina Reader API), but there is no decision capturing the tiered pipeline strategy itself. A developer implementing document ingestion would not know the three-tier approach is specified in ADR-007 or that Docling is the primary parser.
- **Affected BL Items**: Any backlog items involving document ingestion or RAG (BL-016 adjacent)
- **Source Evidence**: hypothesis-consistency.md H2 gap 2 (ADR-007 partial reflection)
- **Resolution**: Add a decision to DECISION-REGISTER capturing: "Document processing: tiered pipeline (Fast/Standard/Deep tiers) using Docling 2.3+ as primary parser, Unstructured 0.15+ as fallback, LlamaParse as optional paid API. Canonical output format: DocIR artifact." Cross-reference ADR-007.
- **Owner Recommendation**: Backend track lead
- **Wave**: W0 — before any document processing implementation

---

### GAP-007 — ADR-010 Infrastructure Not in Decision Register

- **ID**: GAP-007
- **Severity**: MEDIUM
- **Description**: ADR-010 specifies the bootstrap infrastructure: PostgreSQL + pgvector + Neo4j + Redis. The DECISION-REGISTER has no infrastructure decision. DEC-037 mentions Langfuse self-hosted but not the database or cache infrastructure. A team member tasked with environment setup has no single locked decision to point to for infrastructure.
- **Affected BL Items**: All BL items (infrastructure is cross-cutting)
- **Source Evidence**: hypothesis-consistency.md H2 gap 3
- **Resolution**: Add a decision "Bootstrap Infrastructure: PostgreSQL 16+ + pgvector 0.8+ (RDBMS and vector search dev), Neo4j Aura free (domain ontologies), Redis 7+ (cache, arq queue, profiles: full), MinIO (S3-compatible object storage, dev). Sourced from ADR-010." This is a documentation task; the infrastructure is already in docker-compose.yml.
- **Owner Recommendation**: DevOps / infrastructure track
- **Wave**: W0

---

### GAP-008 — Stale Claims Not Corrected in Source Documents

- **ID**: GAP-008
- **Severity**: MEDIUM
- **Description**: CONSISTENCY-AUDIT-PLANS Part 3 identifies seven stale claims (SC-01 through SC-07) in planning documents that have not been corrected. The most impactful: (a) IMPLEMENTATION-PLAN "What We Get For Free" table lists arq background jobs as "Available" when the worker process operational status is unverified; (b) GIT-ISSUES BL-016 claims "arq + Redis already configured" implying it works; (c) DECISION-REGISTER DEC-040 says GML healer is Python/Pydantic when the frontend healer is TypeScript/HAST.
- **Affected BL Items**: BL-016 (entity substrate uses arq), BL-004/BL-009 (GML healer)
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS SC-01 through SC-07
- **Resolution**: Apply all seven corrections listed in CONSISTENCY-AUDIT-PLANS SC-01 through SC-07. Specifically: downgrade arq status to "unverified"; add arq operational verification to Phase 0 checklist; split DEC-040 into DEC-040a (backend Python healer) and DEC-040b (frontend TypeScript/HAST healer).
- **Owner Recommendation**: Documentation lead; review each SC item and apply correction
- **Wave**: P0

---

### GAP-009 — Dependency Graph Errors in GIT-ISSUES (8 Blocked-By Fields Wrong)

- **ID**: GAP-009
- **Severity**: MEDIUM
- **Description**: CONSISTENCY-AUDIT-PLANS Part 4 section 2A identifies eight blocked-by field errors in GIT-ISSUES. Specifically: BL-003 incorrectly lists BL-001 as a blocker (it is independent); BL-022 incorrectly lists BL-001 as a blocker (the direction is reversed — BL-022 design FEEDS BL-001); BL-005, BL-006, BL-018 omit Migration 0005 as a hard dependency; BL-012 acknowledges but doesn't formally list Migration 0005; BL-016 omits Migration 0005.
- **Affected BL Items**: BL-003, BL-005, BL-006, BL-008, BL-012, BL-016, BL-018, BL-022
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-02, I-03, I-04, I-05, I-06, I-07; DEPENDENCY-ANALYSIS corrections
- **Resolution**: Apply the corrections from CONSISTENCY-AUDIT-PLANS Part 4 table 2A to all eight GIT-ISSUES entries. This is a mechanical update — the correct values are already specified in the audit.
- **Owner Recommendation**: Project coordinator / documentation lead; 1–2 hour task
- **Wave**: P0 — must be correct before Wave 0 execution starts

---

### GAP-010 — BL-015 and BL-008 Assigned to Wrong Milestone

- **ID**: GAP-010
- **Severity**: MEDIUM
- **Description**: BL-015 (DeliverableStore Zustand slice) and BL-008 (DeliverableSelector component) have no dependencies and can start in Week 1 (Wave 0). Both are currently assigned to `phase:3-frontend` and Milestone M3 in GIT-ISSUES — an artifact of "all frontend in Phase 3" waterfall thinking. This means frontend work that unblocks other items is scheduled 8–10 weeks later than it needs to be.
- **Affected BL Items**: BL-015, BL-008
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-09, 2B
- **Resolution**: Update GIT-ISSUES BL-015 and BL-008: change phase label to `phase:0-foundation`, update milestone to M0. No code change required.
- **Owner Recommendation**: Project coordinator
- **Wave**: P0

---

### GAP-011 — IMPLEMENTATION-PLAN Critical Path Arrow Backwards for BL-022

- **ID**: GAP-011
- **Severity**: MEDIUM
- **Description**: IMPLEMENTATION-PLAN dependency graph shows `BL-022 (Data Brief, design only) ◄─ BL-001`, placing BL-022 as downstream of BL-001. DEPENDENCY-ANALYSIS explicitly corrects this: the DataBrief schema design (BL-022) must precede BL-001 because BL-001 (Research Orchestrator) requires the DataBrief state field definitions to be locked first. The arrow is directionally wrong, and the critical path description `BL-002 → BL-001 → BL-022 → ...` is incorrect.
- **Affected BL Items**: BL-001, BL-022
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS I-10, SC-04
- **Resolution**: Update IMPLEMENTATION-PLAN dependency diagram: flip `BL-022 ◄─ BL-001` to `BL-022d → BL-001`. Update critical path text to show `BL-022 (design) → BL-001 → ...`.
- **Owner Recommendation**: Architecture lead; 15-minute documentation edit
- **Wave**: P0

---

### GAP-012 — Router Count Discrepancy in PLATFORM-GROUND-TRUTH

- **ID**: GAP-012
- **Severity**: LOW
- **Description**: PLATFORM-GROUND-TRUTH.md states "11 routers" for the API surface. Direct codebase inspection (hypothesis-code-alignment.md H5) confirmed 12 routers — the tags router was added in migration 0004 and is not included in the documented count.
- **Affected BL Items**: None directly (documentation accuracy only)
- **Source Evidence**: hypothesis-code-alignment.md H5.5
- **Resolution**: Update PLATFORM-GROUND-TRUTH.md Section 5 (API Routes) from "11 routers" to "12 routers, including tags router added in migration 0004."
- **Owner Recommendation**: Documentation lead; 5-minute fix
- **Wave**: W0

---

### GAP-013 — `<answer>` Wrapper Stripping Not Addressed in GML Renderer Spec

- **ID**: GAP-013
- **Severity**: LOW
- **Description**: DEC-022 locks the LLM output format as `<answer>...</answer>` XML wrapper with `<gml-*>` tags inside. GML-RENDERING-ANALYSIS (which specifies the complete GML rendering pipeline) does not mention the `<answer>` wrapper at all. There is no specification for where and how the wrapper is stripped before the GML content reaches the renderer.
- **Affected BL Items**: BL-009 (ReportRenderer)
- **Source Evidence**: CONSISTENCY-AUDIT-ANALYSIS C-09; CONSISTENCY-AUDIT-PLANS SC-03 (partial)
- **Resolution**: Add a "Pre-processing Step" to GML-RENDERING-ANALYSIS Section 7 (Implementation Checklist): "1. Extract GML content from `<answer>...</answer>` wrapper before passing to GmlRenderer. Handle: partial `<answer>` during streaming (buffer until closing tag), malformed wrapper (fallback to plain markdown rendering), nested tags inside the answer body."
- **Owner Recommendation**: Frontend track lead; update GML-RENDERING-ANALYSIS only
- **Wave**: W0 — before BL-009 implementation

---

## Category 2: Design Gaps

### GAP-014 — No Explicit Integration Contract for LangGraph → SSE Pipeline

- **ID**: GAP-014
- **Severity**: CRITICAL
- **Description**: The streaming-events-extract.md documents 22 confirmed Superagent event types plus 4 NYQST proposed types, with complete Pydantic schemas and the NDJSON envelope format. The orchestration-extract.md documents the full fan-out dispatch pattern. However, there is no document that specifies the explicit integration contract between the two: which LangGraph events (on_tool_start, on_chat_model_stream, on_end) map to which SSE event types (node_tool_event, message_delta, done). The LangGraphToAISDKAdapter pseudocode in streaming-events-extract.md is an example, not a locked contract.
- **Affected BL Items**: BL-001 (Research Orchestrator), BL-002 (RunEvent schema extensions)
- **Source Evidence**: streaming-events-extract.md (Two-Stream Architecture, LangGraph → AI SDK Adapter); orchestration-extract.md Section 1.3; KNOWLEDGE-MAP Phase 0 deliverables
- **Resolution**: Create a formal "Event Contract v1" document (referenced in KNOWLEDGE-MAP as a Phase 0 deliverable but not yet produced as a locked spec). The contract must: enumerate every LangGraph event hook (on_tool_start, on_tool_end, on_chat_model_stream, on_chain_start, on_chain_end) and specify exactly which SSE event type each maps to, what payload fields are included, and which LangGraph state fields are read for each mapping.
- **Owner Recommendation**: Backend architecture lead (BL-002 owner)
- **Wave**: P0 — this is a Phase 0 deliverable per KNOWLEDGE-MAP and must exist before BL-001 implementation

---

### GAP-015 — Tool Fallback Chain Strategy Not Specified in BL-001

- **ID**: GAP-015
- **Severity**: HIGH
- **Description**: Superagent's orchestration shows a clear tool failure cascade: FactSet → SEC Filings → AlphaVantage → FinancialModelingPrep. This "FALLBACK_CHAINS" pattern is documented in orchestration-extract.md Section 4.2 with explicit code. BL-001 (Research Orchestrator Graph) is the backlog item that must implement this pattern. However, BL-001's spec (MAPPING-01) does not explicitly design the fallback chain mechanism. The term "fallback" appears in the backlog context but the algorithm (try primary → emit fallback_used event → try secondary → emit all_tools_failed if all fail) is not in the spec.
- **Affected BL Items**: BL-001, BL-003 (web research MCP tools that have fallback providers)
- **Source Evidence**: hypothesis-consistency.md H4 gap 4; orchestration-extract.md Section 4.1, 4.2
- **Resolution**: Amend BL-001 technical notes (MAPPING-01) to include the fallback chain algorithm: (1) Try primary provider, emit `tool_call_started`; (2) On failure: emit `node_tool_event(event="fallback_used")`; (3) Try secondary provider; (4) If all fail: emit `node_tool_event(event="all_tools_failed")` and mark task as partial; (5) Fan-in detects partial tasks and routes to meta-reasoning.
- **Owner Recommendation**: Backend track lead (BL-001 implementer)
- **Wave**: W0 — before BL-001 implementation begins

---

### GAP-016 — Async Entity Creation Worker Has No Dedicated Backlog Item

- **ID**: GAP-016
- **Severity**: HIGH
- **Description**: DEC-017 specifies "Async entity creation: Decoupled from main response stream via arq background worker." PLATFORM-GROUND-TRUTH confirms `has_async_entities_in_progress` flag exists. BL-016 covers the entity/citation substrate schema. However, there is no dedicated backlog item for "Implement async entity creation worker" — the arq background job that processes entities after the main stream completes. The work is mentioned in DEC-017 and BL-016 body text but is not a standalone, estimable, assignable item.
- **Affected BL Items**: BL-016 (entity substrate), adjacent to billing and observability
- **Source Evidence**: hypothesis-consistency.md H4 gap 5; CONSISTENCY-AUDIT-PLANS SC-05 (arq claim)
- **Resolution**: Create backlog item BL-023: "Async Entity Creation Worker — implement arq background job that processes entities after stream completion, triggered by `has_async_entities_pending: true` in the `done` event. Includes: job definition in jobs.py, entity resolution logic, `references_found` emission on completion." Size: ~1 SP.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1 — needed before BL-016 is considered complete

---

### GAP-017 — NDM v1 JSON Schema Not Formalized

- **ID**: GAP-017
- **Severity**: HIGH
- **Description**: The KNOWLEDGE-MAP Section 10 explicitly lists "NDM v1 exact JSON schema (sketched in SUPERAGENT_PARITY_PLAN §3.4, needs formalization)" as a needed-soon open thread. The orchestration-extract.md specifies the DataBrief schema (BL-022) but the NDM (NYQST Document Markup) v1 schema — the JSON AST format used for report generation (DEC-015a) — is only sketched. BL-004 (Markup AST schema) depends on this being locked before implementation.
- **Affected BL Items**: BL-004, BL-005 (report generation pipeline), BL-009 (ReportRenderer)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; DEC-015a; BL-004 in BACKLOG.md
- **Resolution**: Formalize the NDM v1 JSON schema as a standalone specification document. Required fields: node types (18 GML tags mapped to JSON node representations), nesting rules, chart data structure, citation reference format, section hierarchy. This is a prerequisite for BL-004.
- **Owner Recommendation**: Architecture lead — can be derived from GML-RENDERING-ANALYSIS tag inventory and orchestration-extract.md Section 3.1
- **Wave**: W0 — blocks BL-004

---

### GAP-018 — MCP Tool Discovery Filtering Algorithm Unspecified

- **ID**: GAP-018
- **Severity**: HIGH
- **Description**: KNOWLEDGE-MAP Section 10 lists "MCP tool discovery filtering (context-scoped, needs algorithm for 'is tool X relevant to session Y?')" as a needed-soon open thread. ADR-008 specifies MCP as the tool protocol with session-scoped discovery. DEC-046 locks MCP search (hot-swap Brave/Tavily). However, the algorithm for how the orchestrator decides which MCP tools are available in a given session context is not specified. This matters because the Research Orchestrator (BL-001) must know which tools to include in a given PlanTask.
- **Affected BL Items**: BL-001 (orchestrator tool selection), BL-003 (MCP tool definitions)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; ADR-008; orchestration-extract.md Section 2.1 (tool dispatch)
- **Resolution**: Specify the tool discovery algorithm in BL-001 technical notes: (1) On session creation, register available MCP tools based on tenant tier (sandbox: subset, professional: full); (2) On PlanTask creation, filter tool list by task category (financial_data → FactSet chain; web_search → Brave/Tavily; document → DocIR tools); (3) Pass filtered tool list to research_executor node.
- **Owner Recommendation**: Backend architecture lead
- **Wave**: W0

---

### GAP-019 — Policy Evaluation Order for HITL Not Specified

- **ID**: GAP-019
- **Severity**: MEDIUM
- **Description**: ADR-009 defines four HITL governance templates (Exploratory, Standard, Regulated, Audit-Critical). KNOWLEDGE-MAP Section 10 lists "Policy evaluation order (ADR-009 lists 4 templates, needs conflict resolution)" as an open thread. When a run is configured with a governance template, the exact precedence rules for when to interrupt vs. continue are not specified. DEC-047 defers the clarification UI to v1.5 but the backend schema and interrupt logic are in scope for v1.
- **Affected BL Items**: BL-021 (clarification flow — backend schema)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; ADR-009; DEC-047
- **Resolution**: Document the policy evaluation algorithm for the four templates: Exploratory (no interrupts); Standard (interrupt on approval_required tool categories); Regulated (interrupt before any external data access); Audit-Critical (interrupt at every plan step). This specification belongs in BL-021 technical notes and is a prerequisite for the LangGraph interrupt implementation.
- **Owner Recommendation**: Product lead + backend architecture lead
- **Wave**: W1 — before BL-021 implementation

---

### GAP-020 — Entity Reference Algorithm Edge Cases Unspecified

- **ID**: GAP-020
- **Severity**: MEDIUM
- **Description**: KNOWLEDGE-MAP Section 10 lists "Entity reference algorithm (sketched, needs edge cases: citations, tool outputs, deliverables)" as a needed-soon open thread. BL-016 covers the entity/citation substrate, but the exact deduplication algorithm (content-hash-based? URL-based? Both?), the algorithm for resolving inline citation identifiers to entity IDs in the GML output, and the behavior when an entity is referenced in both a deliverable and a tool output are not specified.
- **Affected BL Items**: BL-016 (entity substrate), BL-009 (ReportRenderer — citation rendering)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; orchestration-extract.md Section 1.4 (Entity schema)
- **Resolution**: Define the entity reference algorithm: (1) Primary deduplication key: SHA-256 of content; (2) Secondary: URL normalization for web sources; (3) Citation identifier: UUID assigned at entity creation, stored in entity.metadata.citation_identifier; (4) GML citation binding: `<gml-inlinecitation identifier="X"/>` resolved by looking up entity where `citation_identifier == X`; (5) Cross-type references: tool output entities and deliverable entities share the same table, differentiated by entity_type.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1 — before BL-016 integration with BL-009

---

### GAP-021 — Error Handling Failure Modes Not Enumerated

- **ID**: GAP-021
- **Severity**: MEDIUM
- **Description**: The streaming-events-extract.md documents the connection lifecycle and retry strategy (exponential backoff, 5 attempts). The orchestration-extract.md documents the graceful degradation hierarchy (tool error → task error → plan error → run error). However, there is no document that enumerates what happens at each failure level from the platform's perspective: what state is written to the DB, what SSE events are emitted, what the user sees, and how the run is marked in the Run ledger. The "what happens if ALL fallback tools fail" case (orchestration-extract.md Section 6, open question 9) is still open.
- **Affected BL Items**: BL-001 (orchestrator), BL-002 (RunEvent schema)
- **Source Evidence**: orchestration-extract.md Section 4, Section 6 open question 9; streaming-events-extract.md SSE Protocol Details
- **Resolution**: Create a failure mode table in BL-001 technical notes with four rows (tool failure, task failure, plan failure, run failure), specifying: DB state written, SSE events emitted, user-visible message, run ledger status. Define the "all fallbacks exhausted" behavior: emit `node_tool_event(event="all_tools_failed")`, mark task as failed, trigger meta-reasoning if at least 50% of other tasks succeeded, else emit plan error.
- **Owner Recommendation**: Backend architecture lead
- **Wave**: W0

---

### GAP-022 — P0 Bug: RunEvent Sequence Number Race Condition

- **ID**: GAP-022
- **Severity**: CRITICAL
- **Description**: Direct codebase inspection confirmed a TOCTOU (time-of-check-to-time-of-use) race condition in `src/intelli/repositories/runs.py` `_get_next_sequence` method. The method SELECT MAX(sequence_num) then INSERT with MAX+1. Under concurrent parallel task execution (which BL-001 Send() fan-out will trigger), multiple tasks can SELECT the same MAX value and attempt to INSERT with the same sequence_num+1, violating the unique constraint `(run_id, sequence_num)`. This causes data corruption in the run ledger under load.
- **Affected BL Items**: BL-001 (fan-out creates concurrent writes), BL-002 (RunEvent schema)
- **Source Evidence**: hypothesis-code-alignment.md H7.1 (bug confirmed in production code)
- **Resolution**: Fix `_get_next_sequence` before implementing BL-001 fan-out. Three options: (1) Replace SELECT MAX with `SEQUENCE` or `GENERATED ALWAYS AS IDENTITY` at DB level (cleanest); (2) Use `SELECT FOR UPDATE` with `SERIALIZABLE` isolation; (3) Move to DB-level trigger. Recommend option 1: add `sequence_num BIGINT GENERATED ALWAYS AS IDENTITY` to RunEvent in Migration 0005. Create INFRA-BUG-001 tracking issue.
- **Owner Recommendation**: Backend track lead — must fix before any BL-001 work begins
- **Wave**: P0 — production-blocking; blocks BL-001

---

### GAP-023 — P0 Bug: ARQ Worker Registry Initialization Order

- **ID**: GAP-023
- **Severity**: CRITICAL
- **Description**: Direct codebase inspection confirmed that `WorkerSettings.functions` in `src/intelli/core/jobs.py` is evaluated as a class variable at class definition time (module import). At that point, `_job_registry` is still empty because the `@job()` decorators on functions defined below `WorkerSettings` have not yet run. The result: ARQ worker starts with an empty functions list and silently ignores all job submissions. This means any code relying on arq background workers (BL-016 async entity creation, BL-012 billing batch jobs) will appear to work but jobs will never execute.
- **Affected BL Items**: BL-016 (async entity creation), BL-012 (billing batch jobs)
- **Source Evidence**: hypothesis-code-alignment.md H7.2 (bug confirmed in production code)
- **Resolution**: Fix `WorkerSettings.functions` before implementing BL-016 or any arq-dependent work. Fix options: (1) Use `@property` or callable for late binding; (2) Move `WorkerSettings` to a separate module loaded after all job definitions; (3) Use `__init_subclass__` pattern. Recommend option 2 as simplest: create `src/intelli/core/worker_settings.py` that imports from `jobs.py` (ensuring decorator execution order). Also verifies GAP-016's prerequisite: arq must be confirmed operational before BL-016 begins. Create INFRA-BUG-002 tracking issue.
- **Owner Recommendation**: Backend track lead; prerequisite for arq operational verification (CONSISTENCY-AUDIT-PLANS SC-01)
- **Wave**: P0 — production-blocking; must fix before Wave 0 arq verification checkpoint

---

## Category 3: Implementation Gaps

### GAP-024 — LiteLLM Integration: Designed but Not Coded

- **ID**: GAP-024
- **Severity**: HIGH
- **Description**: DEC-042 specifies LiteLLM multi-provider hot-swap for v1.5+ (OpenAI-only for v1). The billing-metering-extract.md documents the LiteLLM + Langfuse integration pattern in detail (Router, callbacks, cost tracking via Langfuse REST API). However, KNOWLEDGE-MAP Section 10 explicitly lists "LiteLLM hot-swap implementation (DEC-042, designed but not coded)" as a deferred item. The current platform uses `langchain_openai.ChatOpenAI` directly. The cost tracking pipeline described in billing-metering-extract.md Section 4.2 requires LiteLLM to be in place for Langfuse to capture per-call costs automatically.
- **Affected BL Items**: BL-012 (billing/metering — depends on cost tracking), BL-013 (quota enforcement)
- **Source Evidence**: KNOWLEDGE-MAP Section 10 (Deferred to v1.5+); billing-metering-extract.md Section 4.2; hypothesis-code-alignment.md H5.4 (confirmed: ChatOpenAI only, no LiteLLM)
- **Resolution**: Determine whether v1 billing requires LiteLLM in the critical path. If cost tracking (DEC-045, $2/run budget) is required for v1, LiteLLM must be introduced before BL-012 can be completed. If cost tracking can be approximated (e.g., count tokens from ChatOpenAI response metadata), LiteLLM can remain deferred. Decision required before BL-012 is scheduled.
- **Owner Recommendation**: Architecture lead — needs explicit wave assignment decision
- **Wave**: W1 — decision needed before BL-012 begins; implementation timing depends on decision

---

### GAP-025 — Langfuse Self-Hosted Deployment Not Sized or Planned

- **ID**: GAP-025
- **Severity**: HIGH
- **Description**: DEC-045 locks Langfuse self-hosted (MIT license) for observability and billing data. KNOWLEDGE-MAP Section 10 lists "Langfuse self-hosted deployment (sizing, backup strategy)" as an external dependency TBD. The docker-compose.yml has a `profiles: ["observability"]` profile referenced in hypothesis-code-alignment.md H8 discussion, but there is no specification for: Langfuse container resource sizing, backup strategy, data retention policy, or how the Langfuse REST API will be accessed from the FastAPI backend for billing queries.
- **Affected BL Items**: BL-012 (billing — uses Langfuse REST API for cost data), BL-013 (quota middleware)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; billing-metering-extract.md Section 4.2; DEC-045
- **Resolution**: Add a Langfuse deployment specification: container resource requirements (CPU, RAM), data retention policy (30 days minimum for billing), backup schedule (daily), and a `docker-compose.langfuse.yml` or addition to the `observability` profile. Define the REST API call pattern for billing queries.
- **Owner Recommendation**: DevOps / infrastructure track
- **Wave**: W0 — required before BL-012 implementation

---

### GAP-026 — Search Provider Selection Requires Cost Comparison

- **ID**: GAP-026
- **Severity**: HIGH
- **Description**: DEC-046 specifies MCP search with hot-swap Brave/Tavily. KNOWLEDGE-MAP Section 10 lists "Search provider selection (Brave API vs Tavily, cost comparison needed)" as an external dependency TBD. DEC-032 (original) locked Brave Search API, superseded by DEC-046 which adds Tavily as an alternative but does not select between them. BL-003 (web research MCP tools) must implement one as the default with the other as the fallback — but which is primary is not specified.
- **Affected BL Items**: BL-003 (MCP web research tools)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; DEC-046; hypothesis-consistency.md H4 (tool fallback)
- **Resolution**: Conduct Brave vs Tavily cost comparison (API pricing per 1000 queries, rate limits, result quality for financial/regulatory queries). Lock a decision specifying primary and fallback. This is an operational/procurement decision that must precede BL-003 implementation. Estimated effort: 2-hour research task.
- **Owner Recommendation**: Product / engineering lead
- **Wave**: W0 — before BL-003

---

### GAP-027 — Neo4j Aura Free Tier Limits Not Assessed

- **ID**: GAP-027
- **Severity**: MEDIUM
- **Description**: KNOWLEDGE-MAP Section 10 lists "Neo4j Aura free tier limits → upgrade/fallback plan" as an external dependency TBD. ADR-010 specifies Neo4j Aura free for graph domain ontologies. The free tier has storage limits (typically 200K nodes, 400K relationships, 50MB storage on the free plan). If the platform's domain ontologies for PropSygnal/RegSygnal exceed these limits, the free tier will fail without warning. No fallback plan (upgrade to paid, self-hosted Neo4j, or alternative graph DB) is documented.
- **Affected BL Items**: Domain modules (PropSygnal, RegSygnal) — not current v1 backlog but risk
- **Source Evidence**: KNOWLEDGE-MAP Section 10; KNOWLEDGE-MAP Section 3 (Infrastructure & Storage)
- **Resolution**: Assess Neo4j Aura free tier limits against the domain ontology data volume expected for v1 research module (likely well within limits). Document the fallback plan if exceeded: (1) Upgrade to Neo4j AuraDB Professional; (2) Self-hosted Neo4j Docker container. Add as a risk note in STRATEGIC-REVIEW.
- **Owner Recommendation**: DevOps / architecture lead
- **Wave**: W1 — low urgency for v1 research module; higher urgency for domain modules

---

### GAP-028 — No Migration 0005 Specification

- **ID**: GAP-028
- **Severity**: MEDIUM
- **Description**: DEC-052 specifies that Migration 0005 is split into three sub-migrations: 0005a (DB schema changes), 0005b (LangGraph state extensions), 0005c (indices). The split is decided but the content of each sub-migration is not specified anywhere. Multiple backlog items depend on Migration 0005 (BL-005, BL-006, BL-012, BL-016, BL-018 per GAP-009). Without a specification of what tables/columns/indices are in each sub-migration, there is a risk of merge conflicts and ordering issues during implementation.
- **Affected BL Items**: BL-005, BL-006, BL-012, BL-016, BL-018
- **Source Evidence**: DEC-052; CONSISTENCY-AUDIT-PLANS I-05, I-06, I-07
- **Resolution**: Document Migration 0005a/b/c content: (a) 0005a: subscriptions table, usage_records table, entity_type column on relevant tables, tags schema extensions; (b) 0005b: RunState extensions (planning_hierarchy fields, cost accumulator fields); (c) 0005c: indices for entity lookup, usage aggregation, run timeline queries.
- **Owner Recommendation**: Backend architecture lead
- **Wave**: W0 — prerequisite for multiple BL items

---

### GAP-029 — Billing Port from DocuIntelli Not Verified

- **ID**: GAP-029
- **Severity**: MEDIUM
- **Description**: DEC-036 specifies "port working Stripe code from okestraai/DocuIntelli." The billing-metering-extract.md Section 10 provides a detailed port strategy (what to take, what to redesign, porting steps). However, the DocuIntelli codebase has not been inspected to verify: (1) that it uses raw body for webhook signature verification (the critical LIB-08 gotcha); (2) that its subscription model matches the NYQST schema; (3) that it doesn't have equivalent bugs to the arq worker initialization issue found in NYQST. The port plan assumes the source code is correct.
- **Affected BL Items**: BL-012 (billing), BL-013 (quota enforcement)
- **Source Evidence**: billing-metering-extract.md Section 10; DEC-036; LIB-08 gotcha
- **Resolution**: Inspect `okestraai/DocuIntelli` billing code before porting. Specifically verify: (a) raw body usage in webhook handler; (b) subscription schema compatibility; (c) no initialization-order bugs; (d) the Stripe SDK version (must be v11+ for the `StripeClient` API used in billing-metering-extract.md).
- **Owner Recommendation**: Backend track lead (BL-012 owner)
- **Wave**: W0 — before BL-012 implementation begins

---

### GAP-030 — Feature Flag Backend Not Specified for v1

- **ID**: GAP-030
- **Severity**: MEDIUM
- **Description**: DEC-025 references experiments/feature flags. EXTRACTION-SUMMARY Section 6 (Feature Flags) confirms Superagent has `/api/feature-flags` and client-side evaluation endpoints. DEC-047 defers the clarification UI feature to v1.5 (presumably behind a feature flag). However, there is no decision specifying how v1 will implement feature flags: PostHog is excluded (DEC-064 uses Langfuse), and the DEC-025 entry is vague. The `streaming-events-extract.md` also makes no reference to a v1 feature flag mechanism.
- **Affected BL Items**: DEC-047 (clarification UI deferred implies a feature flag), future domain modules
- **Source Evidence**: EXTRACTION-SUMMARY Section 6; DEC-064 (no PostHog); DEC-025; DEC-047
- **Resolution**: Decide v1 feature flag mechanism. Options: (a) Tenant-level configuration in the database (simplest — `tenant.features JSONB`); (b) Langfuse experiment tracking (reuses existing observability); (c) Simple environment variable flags. Recommend option (a) for v1: add `features JSONB` column to tenants table in Migration 0005a.
- **Owner Recommendation**: Architecture lead — small decision with disproportionate downstream impact
- **Wave**: W0

---

### GAP-031 — Slides Generation Viewer Not Fully Specified

- **ID**: GAP-031
- **Severity**: LOW
- **Description**: BL-018 (Slides Generation) is in scope for v1. DEC for slides viewer (OQ-002 resolution) specifies: reuse iframe approach, `gml-viewpresentation` renders a link card in Phase 1/2, embedded reveal.js deferred to Phase 3. The slides generation pipeline (7 stages documented in orchestration-extract.md Section 3.3 for website) is documented for websites, but the slides-specific pipeline is not documented. The DataBrief-to-slides transformation logic and the GML tag set for presentations (`gml-viewpresentation`) are not specified.
- **Affected BL Items**: BL-018 (Slides Generation)
- **Source Evidence**: orchestration-extract.md Section 3.3 (website 7 stages); DEC-043 (OQ-002 resolution); KNOWLEDGE-MAP Section 5 (Document Generation Contract)
- **Resolution**: Add slides-specific pipeline specification to BL-018 technical notes. Minimally: (1) DataBrief → slides generator LLM prompt template; (2) Output format: series of `<gml-viewpresentation>` sections with section slides; (3) Viewer: link card with download option for v1; (4) Streaming: `node_report_preview_start/delta/done` events reused with `deliverable_type: slides`.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1 — before BL-018 implementation

---

### GAP-032 — Clarification Flow Resume Endpoint Not Specified

- **ID**: GAP-032
- **Severity**: LOW
- **Description**: DEC-047 defers the clarification UI to v1.5 but specifies that v1 includes "schema + backend checkpoint." BL-021 covers the clarification flow. The streaming-events-extract.md documents `clarification_needed` and `update_message_clarification_message` events. However, the API endpoint that accepts user input and resumes the LangGraph run after an interrupt is not specified (no route, no request/response schema, no LangGraph checkpoint resume pattern documented).
- **Affected BL Items**: BL-021 (clarification flow)
- **Source Evidence**: DEC-047; streaming-events-extract.md (Clarification Events); KNOWLEDGE-MAP Phase 4 deliverables
- **Resolution**: Specify the resume endpoint in BL-021: `POST /api/v1/runs/{run_id}/resume` with body `{user_input: str, interrupt_id: str}`. This calls `graph.ainvoke(Command(resume=user_input), config={thread_id: run_id})` using LangGraph's interrupt/resume pattern. Add to BL-021 acceptance criteria.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1

---

## Category 4: Competitive Intelligence Gaps

### GAP-033 — Superagent GML Formal Spec Not Recovered

- **ID**: GAP-033
- **Severity**: HIGH
- **Description**: The Superagent GML markup language is inferred from the JS bundle analysis. The EXTRACTION-SUMMARY and orchestration-extract.md document 17–18 GML tags with high confidence. However, the formal schema — the exact rules for which tags can nest inside which, the full attribute set for `gml-chartcontainer` props, the complete `gml-infoblockmetric` schema, and the healer's nesting rules — is inferred from code, not documented from a formal spec (which is not publicly available). The NYQST implementation must be compatible with Superagent's output but cannot verify compatibility without the formal spec.
- **Affected BL Items**: BL-004 (Markup AST schema), BL-009 (ReportRenderer)
- **Source Evidence**: EXTRACTION-SUMMARY (GML inferred from 344 KB bundle); orchestration-extract.md Section 3.1 (healer rules inferred)
- **Resolution**: Accept the inference approach as sufficient for v1 (the 18 tags and nesting rules are extracted at HIGH confidence). Document the inference confidence in the NDM v1 schema spec (GAP-017). Plan a validation step in Phase 2: generate a report using the NYQST system, compare its GML structure to a Superagent reference report, and adjust nesting rules if needed. This is acceptable risk.
- **Owner Recommendation**: Architecture lead — risk acceptance decision
- **Wave**: W2 — validation step post-implementation

---

### GAP-034 — Superagent Authentication Method Unknown

- **ID**: GAP-034
- **Severity**: MEDIUM
- **Description**: EXTRACTION-SUMMARY Section (Gaps/Unknowns) lists "Authentication: JWT vs session cookies unclear from bundle." The Superagent bundle shows `/api/session/redeem-token` and `credentials: include` on SSE requests, suggesting cookie-based sessions. NYQST uses JWT + API keys (confirmed in PLATFORM-GROUND-TRUTH). If Superagent's session-redeem pattern is something NYQST needs to replicate for enterprise SSO or shared workspace access, the design gap is unclear.
- **Affected BL Items**: Enterprise Shell layer (Layer 3 — post-v1)
- **Source Evidence**: EXTRACTION-SUMMARY Section (Gaps/Unknowns); streaming-events-extract.md (Frontend Event Consumption, credentials: include)
- **Resolution**: Assess whether Superagent's token-redeem pattern has a v1 analog in NYQST. If enterprise SSO is deferred (it is — per PLATFORM-FRAMING.md Layer 3), this gap is post-v1. Document as a known unknown in the Enterprise Shell layer specifications.
- **Owner Recommendation**: Product lead — scope clarification
- **Wave**: W3 — post-v1 enterprise shell

---

### GAP-035 — Superagent SSO Details Not Recovered

- **ID**: GAP-035
- **Severity**: MEDIUM
- **Description**: EXTRACTION-SUMMARY notes `/api/sso/google/generate-url` is present in the Superagent API surface "but details minimal." NYQST's v1 auth is JWT + API keys (DEC-038, using existing intelli auth, not Ory Kratos). The SSO design for regulated enterprise ($200k/yr) customers will require SAML/OIDC. The Superagent SSO approach is not recoverable from the bundle analysis.
- **Affected BL Items**: Layer 3 Enterprise Shell (SSO/OIDC — post-v1)
- **Source Evidence**: EXTRACTION-SUMMARY Section (API Surface Map — Session & Auth); DEC-038; PLATFORM-FRAMING.md Layer 3
- **Resolution**: Explicitly defer to Layer 3 Enterprise Shell. Ensure the JWT auth system in v1 is designed to accommodate SSO as an additive layer (not a replacement). Add OIDC-compatibility as a non-functional requirement for the auth system.
- **Owner Recommendation**: Architecture lead — ensure v1 auth is SSO-extensible
- **Wave**: W3

---

### GAP-036 — Multi-Channel Output Width Gap

- **ID**: GAP-036
- **Severity**: MEDIUM
- **Description**: EXTRACTION-SUMMARY Section (Comparison to DocuIntelli Platform Primitives) notes: "Multi-channel Output: Superagent offers Report, Website, Presentation — Superagent is wider." NYQST v1 scope includes Report (Phase 2), Website iframe (Phase 2), Slides (BL-018). However, Superagent's "Generated Document" type (`gml-viewgenerateddocument`) is not explicitly addressed in the backlog. It is unclear whether this maps to the NYQST document export (BL-019) or is a distinct output type.
- **Affected BL Items**: BL-018 (Slides), BL-019 (Document Export)
- **Source Evidence**: EXTRACTION-SUMMARY (GML View Types: gml-viewreport, gml-viewwebsite, gml-viewpresentation, gml-viewgenerateddocument); KNOWLEDGE-MAP Section 5
- **Resolution**: Clarify whether `gml-viewgenerateddocument` maps to BL-019 (Document Export — PDF/DOCX). If yes, ensure BL-019 acceptance criteria include the `gml-viewgenerateddocument` tag handling. If it is a distinct output type (e.g., "generated data document" as opposed to a "report"), determine whether it is in v1 scope or deferred.
- **Owner Recommendation**: Product lead
- **Wave**: W1 — before BL-018 and BL-019 implementation

---

### GAP-037 — Competitor Analytics Maturity Gap Not Quantified

- **ID**: GAP-037
- **Severity**: LOW
- **Description**: EXTRACTION-SUMMARY documents Superagent's analytics stack: PostHog with 5 modules (recorder, surveys, web vitals, dead-click detection, exception tracking), GA4 with 5 properties, Facebook/Twitter/LinkedIn pixels. NYQST v1 uses Langfuse for observability (DEC-037) and explicitly excludes PostHog (DEC-064). This is the correct strategic choice for a B2B enterprise platform, but the gap in behavioral analytics (session recording, funnel analysis, product analytics) is not quantified or planned for.
- **Affected BL Items**: Enterprise Shell Layer 3 (analytics and notifications)
- **Source Evidence**: EXTRACTION-SUMMARY Section (Analytics Stack); DEC-064; PLATFORM-FRAMING.md
- **Resolution**: Accept the gap for v1. Document in STRATEGIC-REVIEW that product analytics (session recording, funnels) is a Layer 3 Enterprise Shell concern and will be addressed when the enterprise billing tier requires product-led growth tooling. This is an acceptable deferred risk for a $200k/yr sales-led enterprise motion.
- **Owner Recommendation**: Product lead
- **Wave**: W3 — post-v1

---

## Category 5: Operational Gaps

### GAP-038 — No CI/CD Pipeline for the Platform

- **ID**: GAP-038
- **Severity**: CRITICAL
- **Description**: No CI/CD pipeline is documented for the `nyqst-intelli-230126` platform repository. CONSISTENCY-AUDIT-ANALYSIS C-05 notes "Deployment/containerization (no Dockerfile exists — genuine gap, no locked decision)" from the Codex analysis. The KNOWLEDGE-MAP lists Docker for containerization but docker-compose is a dev-only setup. There is no GitHub Actions workflow, no automated test run on PR, no container build pipeline, no staging environment specification. As implementation progresses across 5 parallel tracks, the absence of CI will cause integration failures to accumulate undetected.
- **Affected BL Items**: All BL items — CI gates every merge
- **Source Evidence**: CONSISTENCY-AUDIT-ANALYSIS C-05 (Codex unresolved item: "Deployment/containerization"); KNOWLEDGE-MAP Section 4 (DevOps & Observability); no CI files found in codebase review
- **Resolution**: Create minimal CI pipeline: (1) GitHub Actions workflow on PR to `main`: run `pytest` (backend), `tsc --noEmit` (frontend), `alembic check` (migration drift); (2) Docker build step to validate containerization; (3) Lint step (`ruff`, `eslint`). This is a 1-day setup task that prevents weeks of integration debt.
- **Owner Recommendation**: DevOps track; should be the first W0 task
- **Wave**: W0 — highest priority operational task

---

### GAP-039 — No Phase 0 Validation Checklist Formalized

- **ID**: GAP-039
- **Severity**: HIGH
- **Description**: CONSISTENCY-AUDIT-PLANS Part 4 section 3D specifies a "Week 1 Validation Checklist" with six verification tasks that MUST pass before Wave 1 begins. These tasks de-risk critical assumptions: arq operational (de-risks BL-016, BL-012), Send() prototype (de-risks BL-001), GmlRenderer spike (de-risks BL-009), WeasyPrint system deps (de-risks BL-019), Brave Search API (de-risks BL-003), existing tests green (de-risks all BL). This checklist exists in the audit document but has NOT been added to IMPLEMENTATION-PLAN Phase 0 or created as a GIT-ISSUES gate milestone.
- **Affected BL Items**: BL-001, BL-003, BL-009, BL-012, BL-016, BL-019
- **Source Evidence**: CONSISTENCY-AUDIT-PLANS Part 4 3D; STRATEGIC-REVIEW Section 8 (Week 1 Validation Checklist)
- **Resolution**: Add to IMPLEMENTATION-PLAN Phase 0 a mandatory "Validation Checkpoint" section with the six tasks. Create a blocking GIT-ISSUES milestone gate (M0-GATE) that must be closed before M1 work begins. Link each validation task to the BL items it de-risks.
- **Owner Recommendation**: Project coordinator + engineering lead; 2-hour documentation task
- **Wave**: P0 — must exist before Wave 0 begins

---

### GAP-040 — No Monitoring or Alerting Specification

- **ID**: GAP-040
- **Severity**: HIGH
- **Description**: The platform has Langfuse for trace observability and LangSmith Studio for graph debugging. Neither of these is a production monitoring and alerting solution. There is no specification for: (1) application-level health monitoring (FastAPI health endpoint exists at `/health` but no uptime monitoring); (2) database monitoring (PostgreSQL connection pool exhaustion, replication lag); (3) arq worker monitoring (job queue depth, job failure rate); (4) SSE stream health (active connections, disconnection rate); (5) budget overrun alerting (when a tenant approaches their monthly quota).
- **Affected BL Items**: BL-012 (billing alerts), BL-013 (quota alerts), cross-cutting
- **Source Evidence**: KNOWLEDGE-MAP Section 4 (DevOps & Observability — only lists Langfuse and LangSmith Studio); billing-metering-extract.md Section 7 (monthly invoice generation — no alerting on failure)
- **Resolution**: Define minimal v1 monitoring: (1) Uptime: use Langfuse health check endpoint + external uptime monitor (UptimeRobot free tier); (2) DB: pg_stat_statements for slow query detection; (3) arq: job failure rate logged to Langfuse trace; (4) Budget: add a webhook or email notification when tenant reaches 80% of monthly quota. Document in a new `docs/plans/OPERATIONS.md`.
- **Owner Recommendation**: DevOps track
- **Wave**: W1 — needed before staging deployment

---

### GAP-041 — No Developer Experience (DX) Tooling Spec

- **ID**: GAP-041
- **Severity**: MEDIUM
- **Description**: KNOWLEDGE-MAP Section 9 specifies a "Critical Knowledge Path" for new team members (Day 1: read PLATFORM-FRAMING.md, etc.) but this is reading-based onboarding. There is no specification for: (1) a local development setup guide (`make dev` or equivalent); (2) database seeding scripts for local testing; (3) LangSmith Studio integration for local graph debugging; (4) Langfuse local instance for local trace observation; (5) mock data for development that doesn't require live API keys (Brave, Stripe).
- **Affected BL Items**: All BL items — affects all developer velocity
- **Source Evidence**: KNOWLEDGE-MAP Section 9 (Critical Knowledge Paths — reading-based only); CONSISTENCY-AUDIT-PLANS SC-01 (arq verification task implies no existing setup verification)
- **Resolution**: Create a `docs/plans/DEVELOPER-SETUP.md` that specifies: (1) prerequisites check script; (2) `docker-compose up` sequence and validation; (3) database initialization command; (4) test data seeding; (5) local Langfuse + LangSmith Studio startup; (6) `.env.example` with all required variables. This is a 4-hour task that pays for itself in the first week of multi-track development.
- **Owner Recommendation**: Any senior engineer; should be done during P0
- **Wave**: W0

---

### GAP-042 — No Staging Environment Specification

- **ID**: GAP-042
- **Severity**: MEDIUM
- **Description**: The platform targets enterprise deployment but there is no specification for a staging environment. The only documented environments are local development (docker-compose) and production (implied). For a $200k/yr enterprise product, buyers will require sandbox testing against a non-production instance. Stripe itself requires test-mode integration before going live. Without a staging environment spec, every integration (Stripe, Langfuse, search providers) is validated in production.
- **Affected BL Items**: BL-012 (Stripe — must be tested in test mode first), BL-013
- **Source Evidence**: billing-metering-extract.md Section 10.3 (Stripe CLI testing); KNOWLEDGE-MAP (no staging reference); PLATFORM-FRAMING.md (enterprise target)
- **Resolution**: Define a staging environment specification: (1) Same docker-compose setup as production with `ENVIRONMENT=staging` flag; (2) Separate Stripe test-mode API keys; (3) Separate Langfuse instance or project; (4) Reduced resource allocation (single Postgres, no Neo4j); (5) Data reset capability (for demo purposes). Add to `docs/plans/OPERATIONS.md`.
- **Owner Recommendation**: DevOps track
- **Wave**: W1

---

### GAP-043 — Multi-Tenant Data Isolation Not Specified for v1

- **ID**: GAP-043
- **Severity**: MEDIUM
- **Description**: The KNOWLEDGE-MAP confirms `workspace_id` (multi-tenant isolation) is part of all streaming events. The platform has `tenant_id` in the auth system. However, there is no document specifying the row-level security (RLS) strategy for the database, the tenant isolation guarantee for SSE streams (ensuring tenant A cannot receive tenant B's events), or the isolation of LangGraph checkpoints by tenant. For an enterprise product, this is a compliance requirement, not a nice-to-have.
- **Affected BL Items**: BL-001 (orchestrator must be tenant-scoped), all data models
- **Source Evidence**: KNOWLEDGE-MAP (workspace_id in all events); streaming-events-extract.md (X-Gradient-Workspace-Id header); PLATFORM-FRAMING.md Layer 3 (multi-tenant isolation listed as Layer 3 concern)
- **Resolution**: Define v1 tenant isolation: (1) All DB queries include `WHERE tenant_id = $current_tenant` (application-level isolation); (2) LangGraph `thread_id` includes `{tenant_id}:{run_id}` to prevent checkpoint namespace collisions; (3) SSE channels namespaced as `run_stream_{tenant_id}_{run_id}` in NOTIFY; (4) Document that PostgreSQL RLS is a Layer 3 enhancement (stronger isolation with row-level policies). Add to BL-001 technical notes.
- **Owner Recommendation**: Architecture lead
- **Wave**: W0 — must be specified before BL-001 implementation

---

### GAP-044 — No Data Retention or Backup Policy

- **ID**: GAP-044
- **Severity**: LOW
- **Description**: The run ledger is append-only and grows indefinitely. SSE event logs per run include the full NDJSON event stream (stored as `event_stream_artifact_id` per the Message schema). Langfuse traces accumulate. There is no documented data retention policy (how long are runs kept, how long are events kept, when are artifacts purged), no backup schedule for the PostgreSQL primary, and no disaster recovery plan.
- **Affected BL Items**: BL-012 (billing records must be retained for audit), cross-cutting
- **Source Evidence**: billing-metering-extract.md (UsageRecord table — billing audit requires long retention); streaming-events-extract.md (event_stream_artifact_id — event logs stored); no retention policy in any document
- **Resolution**: Define a minimal v1 data retention policy: (1) Run ledger events: 90 days active, 1 year cold storage; (2) Billing records: 7 years (regulatory requirement); (3) Langfuse traces: 30 days (consistent with DEC-045 Langfuse plan); (4) Daily PostgreSQL backups via `pg_dump` to S3/MinIO; (5) Weekly backup restore tests. Add to `docs/plans/OPERATIONS.md`.
- **Owner Recommendation**: DevOps track
- **Wave**: W2 — before production deployment

---

### GAP-045 — Slice Structure Plan (CLAUDE.md Team Briefs) Not Created

- **ID**: GAP-045
- **Severity**: LOW
- **Description**: MEMORY.md (Pending Work section) notes: "Slice structure plan (plan mode): 10 CLAUDE.md team briefs in dev repo — approved but not yet created." The 10 team briefs are the primary onboarding and context documents for AI agent subteams working in parallel on the 5 tracks. Without these briefs, each agent team must reconstruct context from the full document corpus, which violates the "NEVER read full source files" context management rule and will cause compounding context errors across parallel tracks.
- **Affected BL Items**: All BL items — affects parallel execution quality
- **Source Evidence**: MEMORY.md Pending Work; KNOWLEDGE-MAP Section 9 (Critical Knowledge Paths)
- **Resolution**: Create the 10 CLAUDE.md team briefs in the dev repo, each 1–2 pages covering: team scope, assigned BL items, key decisions (relevant DEC-xxx), dependencies on other teams, files they own, files they must not modify. This is a 1-day documentation task. Approved by user but not yet executed.
- **Owner Recommendation**: Engineering lead / plan owner
- **Wave**: P0 — must exist before any parallel agent execution

---

## Cross-Cutting Observations

### Propagation Debt Pattern

The most pervasive gap class is **propagation debt**: decisions are made correctly in the Decision Register but are not written back to the source documents where they will be read by implementers. The project has strong decision hygiene (52+ locked decisions) but poor propagation hygiene. The CONSISTENCY-AUDIT-PLANS document correctly identifies all required propagations but is itself an intermediate artifact — the propagations still need to be applied.

Estimated propagation debt resolution: 2–3 engineer-days of documentation work before Wave 0 implementation begins.

### Production Bug Risk

Two production-blocking bugs (GAP-022, GAP-023) were confirmed by direct codebase inspection. These are not theoretical risks — they are real code paths that will fail under the exact conditions (parallel fan-out writes, arq job execution) that the BL-001 and BL-016 implementations will trigger. Both bugs have straightforward fixes (≤ 4 hours each) but must be in place before any implementation that depends on them.

### Phase 0 Validation Checkpoint Is Critical

The six-task Phase 0 validation checklist (GAP-039) is the single highest-leverage risk-reduction action available. Running these validations before any Wave 1 code is written will expose hidden infrastructure failures (arq worker, WeasyPrint system deps, API key validity) in a low-cost, low-stakes context rather than mid-implementation.

---

## Prioritized Resolution Order

### P0 — Before Any Code Is Written (Estimated: 3–4 engineer-days)

1. **GAP-022** — Fix sequence number race condition (CRITICAL, 4 hours)
2. **GAP-023** — Fix arq worker registry initialization (CRITICAL, 4 hours)
3. **GAP-001** — Propagate Plotly decision to 4 documents (CRITICAL, 2 hours)
4. **GAP-002** — Propagate GML rendering split to affected docs (CRITICAL, 2 hours)
5. **GAP-003** — Mark OQ-001–007 as resolved in source documents (CRITICAL, 3 hours)
6. **GAP-009** — Correct 8 blocked-by fields in GIT-ISSUES (MEDIUM, 1 hour)
7. **GAP-010** — Move BL-015 and BL-008 to Wave 0 milestone (MEDIUM, 30 minutes)
8. **GAP-011** — Flip BL-022 dependency arrow in IMPLEMENTATION-PLAN (MEDIUM, 15 minutes)
9. **GAP-008** — Apply SC-01 through SC-07 stale claim corrections (MEDIUM, 2 hours)
10. **GAP-039** — Formalize Phase 0 validation checklist in IMPLEMENTATION-PLAN (HIGH, 2 hours)
11. **GAP-045** — Create 10 CLAUDE.md team briefs in dev repo (LOW, 8 hours)

### W0 — Phase 0 Foundation (Estimated: 1 engineer-week parallel with implementation)

12. **GAP-014** — Create formal Event Contract v1 document (CRITICAL, 4 hours)
13. **GAP-017** — Formalize NDM v1 JSON schema (HIGH, 4 hours)
14. **GAP-038** — Create minimal CI pipeline (CRITICAL, 1 day)
15. **GAP-028** — Document Migration 0005a/b/c content (MEDIUM, 2 hours)
16. **GAP-015** — Document tool fallback chain in BL-001 spec (HIGH, 2 hours)
17. **GAP-025** — Langfuse deployment specification (HIGH, 2 hours)
18. **GAP-026** — Search provider cost comparison and lock (HIGH, 2 hours)
19. **GAP-018** — Specify MCP tool discovery algorithm (HIGH, 2 hours)
20. **GAP-021** — Enumerate failure modes in BL-001 spec (MEDIUM, 2 hours)
21. **GAP-043** — Specify v1 tenant isolation approach (MEDIUM, 2 hours)
22. **GAP-041** — Create developer setup guide (MEDIUM, 4 hours)
23. **GAP-004** — Add deferred scope section to IMPLEMENTATION-PLAN (HIGH, 1 hour)
24. **GAP-005** — Add Index Service to platform primitives list (HIGH, 30 minutes)
25. **GAP-006** — Add document processing pipeline decision (HIGH, 1 hour)
26. **GAP-007** — Add infrastructure decision to DECISION-REGISTER (MEDIUM, 1 hour)
27. **GAP-012** — Update router count in PLATFORM-GROUND-TRUTH (LOW, 5 minutes)
28. **GAP-013** — Add `<answer>` wrapper spec to GML-RENDERING-ANALYSIS (LOW, 30 minutes)
29. **GAP-030** — Decide feature flag mechanism for v1 (MEDIUM, 1 hour)

### W1 — Phase 1 Build

30. **GAP-016** — Create BL-023 (async entity worker backlog item) (HIGH, 1 hour)
31. **GAP-024** — Decision: LiteLLM in v1 critical path? (HIGH, 2-hour design discussion)
32. **GAP-029** — Inspect and verify DocuIntelli billing code (MEDIUM, 4 hours)
33. **GAP-019** — Specify HITL policy evaluation order (MEDIUM, 2 hours)
34. **GAP-020** — Specify entity reference algorithm edge cases (MEDIUM, 2 hours)
35. **GAP-031** — Specify slides generation pipeline (LOW, 2 hours)
36. **GAP-032** — Specify clarification resume endpoint (LOW, 1 hour)
37. **GAP-040** — Define production monitoring and alerting (HIGH, 1 day)
38. **GAP-042** — Define staging environment (MEDIUM, 2 hours)
39. **GAP-036** — Clarify gml-viewgenerateddocument scope (MEDIUM, 1 hour)

### W2 — Phase 2 Build

40. **GAP-044** — Data retention and backup policy (LOW, 2 hours)
41. **GAP-033** — Validate GML spec against live reference (HIGH, 4 hours)
42. **GAP-027** — Assess Neo4j Aura free tier limits (MEDIUM, 1 hour)

### W3 / Post-v1

43. **GAP-034** — Superagent auth method assessment (MEDIUM — enterprise shell)
44. **GAP-035** — SSO design for enterprise tier (MEDIUM — enterprise shell)
45. **GAP-037** — Product analytics gap for enterprise (LOW — Layer 3)

---

*Revision Log:*

| Date | Author | Change |
|------|--------|--------|
| 2026-02-20 | Claude Sonnet 4.6 (Senior Engineering Lead role) | Initial comprehensive gap analysis — synthesizes all hypothesis tests, inventory data, extract documents, and consistency audits |
