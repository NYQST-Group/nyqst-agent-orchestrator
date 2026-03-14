---
document_id: CONSISTENCY-AUDIT-PLANS
version: 1
date: 2026-02-19
scope: docs/plans/
auditor: claude-sonnet-4-6
inputs:
  - docs/plans/LIBRARY-REFERENCE.md
  - docs/plans/DEPENDENCY-ANALYSIS.md
  - docs/plans/DECISION-REGISTER.md
  - docs/plans/GIT-ISSUES-STRUCTURE.md
  - docs/plans/STRATEGIC-REVIEW.md
  - docs/plans/IMPLEMENTATION-PLAN.md
  - docs/analysis/LANGSMITH-COST-EVAL-RESEARCH.md
  - docs/analysis/GML-RENDERING-ANALYSIS.md
  - docs/analysis/GRAPH-EDITOR-RESEARCH.md
---

# Consistency Audit: Planning Documents

This audit cross-references all six planning documents plus three analysis documents completed after the planning documents were written. It identifies contradictions, stale references, unclosed decisions, and corrections that have not been propagated.

---

## Part 1: Inconsistency Matrix

| # | Doc A | Doc B | Inconsistency | Severity | Resolution |
|---|-------|-------|---------------|----------|------------|
| I-01 | LIBRARY-REFERENCE (LIB-13: Plotly.js) | IMPLEMENTATION-PLAN (Sections 3.6, file manifest) | LIBRARY-REFERENCE documents Plotly.js with full patterns and install commands. IMPLEMENTATION-PLAN section 3.6 says "Chart rendering: recharts" and the file manifest entry adds "recharts (if absent)" to package.json. GIT-ISSUES BL-009 acceptance criteria states "CHART nodes render as Recharts charts." These are different libraries with incompatible APIs and data formats. | BLOCKING | STRATEGIC-REVIEW (C-1) identified this and recommended Recharts for v1. GML-RENDERING-ANALYSIS confirms `react-plotly.js / plotly.js` for `gml-chartcontainer`. The two analyses give conflicting recommendations. A single decision must be locked and propagated to all four documents. See I-01 note below. |
| I-02 | DEPENDENCY-ANALYSIS (BL-003: Wave 0 standalone) | GIT-ISSUES (BL-003: Blocked By BL-001) | DEPENDENCY-ANALYSIS explicitly corrects BL-003: Brave/Jina wrappers have zero platform dependencies and should be built in Wave 0. GIT-ISSUES still lists `Blocked By: BL-001` without qualification. IMPLEMENTATION-PLAN places BL-003 in Phase 1 (Weeks 3-5). | HIGH | DEPENDENCY-ANALYSIS is correct. BL-003 standalone tools belong in Wave 0. GIT-ISSUES and IMPLEMENTATION-PLAN must be updated to split BL-003 into standalone (Wave 0) and integration-wiring (Wave 2). |
| I-03 | DEPENDENCY-ANALYSIS (BL-022: design has no deps) | GIT-ISSUES (BL-022: Blocked By BL-001) | DEPENDENCY-ANALYSIS corrects BL-022: the DataBrief schema design must precede BL-001, not depend on it. The listed dependency is directionally backwards for the design portion. GIT-ISSUES still shows `Blocked By: BL-001`. | HIGH | DEPENDENCY-ANALYSIS is correct. BL-022 design goes in Wave 0. GIT-ISSUES blocked-by field must be corrected. The distinction between design (no deps) and integration (requires BL-001) should be noted in the issue body. |
| I-04 | DEPENDENCY-ANALYSIS (BL-008 weakly depends on BL-015) | GIT-ISSUES (BL-008: Blocked By None, Blocks None) | DEPENDENCY-ANALYSIS adds BL-015 as a dependency of BL-008 because BL-008 writes to `useDeliverableStore()`. GIT-ISSUES lists BL-008 with no blocked-by and no blocks relationships. | MEDIUM | Update GIT-ISSUES BL-008 to add `Blocked By: BL-015` (weak, but both are Wave 0/trivial items). BL-015 should add `Blocks: BL-008` to its issue. |
| I-05 | DEPENDENCY-ANALYSIS (BL-012 needs Migration 0005) | GIT-ISSUES (BL-012: Blocked By None) | DEPENDENCY-ANALYSIS explicitly adds Migration 0005 as a dependency of BL-012 (billing tables are created there). GIT-ISSUES BL-012 shows `Blocked By: None (independent track; billing tables land in migration 0005 during Phase 0)` — the parenthetical acknowledges the dependency but the field says None. | MEDIUM | GIT-ISSUES BL-012 `Blocked By` should read: `Migration 0005 (billing tables)`. The parenthetical is inconsistent with the field value. |
| I-06 | DEPENDENCY-ANALYSIS (BL-016 needs Migration 0005 + BL-005 soft-dep) | GIT-ISSUES (BL-016: Blocked By BL-002, BL-005) | GIT-ISSUES BL-016 lists `Blocked By: BL-002, BL-005` — this is partially correct (BL-005 is a soft dep for citation binding) but omits Migration 0005, which is a hard dependency for the entity_type and tags columns. | MEDIUM | GIT-ISSUES BL-016 `Blocked By` should be: `BL-002, Migration 0005` (hard deps), with BL-005 noted as a soft dependency for the citation-binding integration step only. |
| I-07 | DEPENDENCY-ANALYSIS (BL-005/006/018 need Migration 0005) | GIT-ISSUES and IMPLEMENTATION-PLAN | None of the GIT-ISSUES entries for BL-005, BL-006, or BL-018 list Migration 0005 as a blocked-by dependency. IMPLEMENTATION-PLAN dependency diagram does not show Migration 0005 as a precondition for these items. | HIGH | GIT-ISSUES entries for BL-005, BL-006, and BL-018 must add `Migration 0005` to their `Blocked By` fields. The IMPLEMENTATION-PLAN dependency diagram should be updated accordingly. |
| I-08 | DEPENDENCY-ANALYSIS (Wave model: 7 weeks parallel) | GIT-ISSUES (Milestones: 13-14 week sequential phases) | DEPENDENCY-ANALYSIS concludes the minimum duration is 7 weeks (parallel) or 10-11 weeks (realistic). GIT-ISSUES milestone dates span: M0 (2026-03-14) through M4 (2026-05-30) — approximately 13 weeks from today (2026-02-19). The milestone structure reflects a sequential phase model, not the parallel-track model from DEPENDENCY-ANALYSIS. STRATEGIC-REVIEW (C-8) flagged this explicitly. | HIGH | The STRATEGIC-REVIEW recommended replacing the sequential phase model with the parallel-track model from DEPENDENCY-ANALYSIS as the primary execution plan. The milestones should be recalibrated to reflect parallel execution. This does not require changing the milestone names, only their dates and the assignment of items across milestones. |
| I-09 | DEPENDENCY-ANALYSIS (BL-015 in Wave 0) | GIT-ISSUES (BL-015 in M3: Frontend) | BL-015 (DeliverableStore) has no dependencies and belongs in Wave 0 per DEPENDENCY-ANALYSIS. GIT-ISSUES assigns it to `phase:3-frontend` and Milestone M3. Similarly, BL-008 (DeliverableSelector) is Wave 0 or Wave 1 but is assigned to M3. | MEDIUM | BL-015 and BL-008 can and should start in Week 1. Their milestone assignment to M3 is an artifact of "all frontend in Phase 3" waterfall thinking, which the DEPENDENCY-ANALYSIS explicitly rejected. Phase labels should be updated to reflect actual wave assignment. |
| I-10 | IMPLEMENTATION-PLAN (Critical path: BL-022 after BL-001) | DEPENDENCY-ANALYSIS (BL-022 precedes BL-001) | IMPLEMENTATION-PLAN dependency graph shows `BL-022 (Data Brief, design only — state field) ◄─ BL-001`, placing BL-022 as dependent on BL-001. The stated critical path in IMPLEMENTATION-PLAN is `BL-002 → BL-001 → BL-022 → ...`. DEPENDENCY-ANALYSIS shows BL-022 design must feed INTO BL-001, reversing this relationship. | HIGH | The IMPLEMENTATION-PLAN dependency diagram arrow on BL-022 is backwards. It should be `BL-022d → BL-001` (BL-022 design is an input to BL-001, not an output). The critical path in IMPLEMENTATION-PLAN must be corrected. |
| I-11 | DECISION-REGISTER (OQ-001 through OQ-007: all Open) | STRATEGIC-REVIEW (OQ-001–007: all recommended for resolution) | DECISION-REGISTER Part 3 shows all seven open questions as unresolved. STRATEGIC-REVIEW Section 8 provides explicit recommended resolutions for all seven. These resolutions have not been written back into DECISION-REGISTER as locked decisions. | HIGH | Seven new locked decisions must be added to DECISION-REGISTER Part 2. See Part 2 of this audit for the specific decision text. |
| I-12 | DECISION-REGISTER (DEC-037: use existing Langfuse) | LANGSMITH-COST-EVAL-RESEARCH (Recommends Langfuse self-hosted with LiteLLM) | DEC-037 says "Use existing Langfuse (not PostHog)" — this is a correct decision but was made on the basis that "Langfuse already wired in intelli." LANGSMITH-COST-EVAL-RESEARCH confirms Langfuse self-hosted as correct and adds critical implementation detail: LiteLLM as the cost-tracking layer, Langfuse callback handler pattern, and the fact that budget enforcement must be implemented in LangGraph state (not by Langfuse). DEC-037 as written does not capture these implementation specifics. | MEDIUM | DEC-037 should be augmented with: (a) Langfuse + LiteLLM is the cost-tracking mechanism; (b) budget enforcement is implemented in LangGraph state via token accumulator pattern, NOT by Langfuse; (c) the Langfuse REST API is the source for billing data export. This is an enrichment, not a contradiction. |
| I-13 | DECISION-REGISTER (DEC-015: JSON AST for markup format) | GML-RENDERING-ANALYSIS (Skip JSON AST; use rehype-to-JSX) | DEC-015 says "Markup format: JSON AST (NYQST Markup AST), not raw HTML tags." GML-RENDERING-ANALYSIS Section 4 explicitly recommends: "Do not implement the JSON AST layer for Phase 1 or 2. Use the rehype-to-JSX approach matching Superagent's architecture." The analysis identifies the JSON AST layer as an additional serialisation pass that is not necessary and not what Superagent uses for the GML rendering pipeline. | HIGH | DEC-015 conflates two different things: (a) the backend MarkupDocument Pydantic model for report generation (BL-004, BL-005 — this JSON AST is correct and needed) and (b) the frontend GML rendering pipeline, where a JSON AST intermediate layer is NOT needed. DEC-015 should be split or clarified: MarkupDocument JSON AST applies to report generation; the GML viewer uses rehype-to-JSX directly. |
| I-16 | DECISION-REGISTER (OQ-005: open, "custom renderer may be needed") | GML-RENDERING-ANALYSIS (resolved: separate ReportPanel, not blocking @assistant-ui) | OQ-005 asks whether `@assistant-ui/react` can handle `<gml-*>` web components and whether a custom renderer is needed. GML-RENDERING-ANALYSIS resolves this: the GML content (from `node_report_preview_done` event) is rendered in a separate `ReportPanel` component outside the `Thread`. The GML parser uses `unified + rehype-parse + rehype-react`. `@assistant-ui/react` is NOT expected to parse GML — the two rendering paths are separate. | HIGH | OQ-005 is resolved by GML-RENDERING-ANALYSIS. The answer is Pattern B (Separate Report Panel). This must be added to DECISION-REGISTER as a locked decision (DEC-043 or similar). The framing of OQ-005 was based on a false premise (that GML content would flow through @assistant-ui message parts). |
| I-14 | GML-RENDERING-ANALYSIS (gml-chartcontainer uses react-plotly.js) | IMPLEMENTATION-PLAN / GIT-ISSUES (Recharts) | GML-RENDERING-ANALYSIS summary table shows `gml-chartcontainer` needs `react-plotly.js / plotly.js`. The underlying GML rendering analysis follows Superagent's actual implementation. IMPLEMENTATION-PLAN and GIT-ISSUES BL-009 specify Recharts. | BLOCKING | This is the same chart library conflict as I-01 but now surfaces from a third document. GML-RENDERING-ANALYSIS is based on direct analysis of Superagent's JS bundle. Superagent uses Plotly. The question is whether to match Superagent (Plotly) or optimize for bundle size (Recharts). This must be locked once. |
| I-15 | GRAPH-EDITOR-RESEARCH (No visual editor; graph-as-code) | No contradiction in planning docs, but adds new constraint | GRAPH-EDITOR-RESEARCH confirms no viable visual editor supports Send() fan-out. LangGraph Builder explicitly cannot generate parallel-node graphs. This means the development workflow for BL-001 is purely code-based with LangSmith Studio for debugging. This is consistent with existing decisions but had not been explicitly confirmed. | INFO | No action required in planning docs. Confirm in BL-001 technical notes that LangSmith Studio (free) is the debug tool, and no visual editor is expected. |

**Note on I-01/I-14 (Chart Library)**: The conflict exists between STRATEGIC-REVIEW (recommends Recharts for v1 based on bundle size) and GML-RENDERING-ANALYSIS (recommends react-plotly.js based on Superagent's actual implementation). Both documents were written after LIBRARY-REFERENCE. The resolution must be made by the user/lead and then propagated to all affected documents. Arguments for each side: Recharts (lighter, React-native, sufficient for 5 v1 chart types per SC-3); Plotly (matches Superagent exactly, supports all 10 chart types, `react-plotly.js` wrapper is established). STRATEGIC-REVIEW also recommends limiting v1 to 5 chart types, which makes Recharts more viable. This audit flags it but does not resolve it.

---

## Part 2: Open Questions — Status After Later Research

All seven open questions in DECISION-REGISTER are listed as unresolved. The STRATEGIC-REVIEW (written same day) provided recommended resolutions. LANGSMITH-COST-EVAL-RESEARCH and GML-RENDERING-ANALYSIS (written 2026-02-19) add further evidence.

| OQ-ID | Prior Status | Resolution Source | Recommended Lock |
|-------|-------------|-------------------|-----------------|
| OQ-001 | Open: LiteLLM multi-provider vs OpenAI-only | STRATEGIC-REVIEW recommends OpenAI-only for v1 (gpt-4o for orchestrator, gpt-4o-mini for workers). LANGSMITH-COST-EVAL-RESEARCH adds: if LiteLLM is used as a proxy layer, multi-provider support comes "for free" via Langfuse callbacks without adding langchain-anthropic. The cost tracking benefit of LiteLLM is independent of which providers are used. | Lock as: Stay OpenAI-only for v1. Do NOT add langchain-anthropic. The `base_url` override in the existing platform supports proxy routing if needed. LiteLLM can be added as a proxy layer without changing LLM provider. |
| OQ-002 | Open: Reuse WebsitePreview for slides vs dedicated SlidesPreview component | STRATEGIC-REVIEW recommends: reuse WebsitePreview (iframe). Slides = `<gml-ViewWebsite type="slides">` with a prop. GML-RENDERING-ANALYSIS confirms: `gml-viewpresentation` maps to `GmlViewPresentation` (Phase 3, deferred embedded mode). | Lock as: Reuse iframe approach. `gml-viewpresentation` renders a link card in Phase 1/2; embedded reveal.js deferred to Phase 3. No dedicated SlidesPreview component for v1. |
| OQ-003 | Open: iframe-only vs add unauthenticated `/website/[id]` route | STRATEGIC-REVIEW recommends: iframe-only for v1. DEC-035 already locked this — the OQ is redundant with an existing locked decision. | Lock as: iframe-only. Already covered by DEC-035. Close OQ-003 as duplicate of DEC-035. |
| OQ-004 | Open: gpt-4o-mini default for workers vs gpt-4o for all | STRATEGIC-REVIEW recommends: gpt-4o-mini for fan-out workers, gpt-4o for planner/synthesis/meta-reasoning only. LANGSMITH-COST-EVAL-RESEARCH confirms this is the standard cost-control pattern. | Lock as: gpt-4o-mini for all worker nodes; gpt-4o for planner, synthesis, and meta-reasoning (BL-017). Budget ceiling: $2.00/run hard limit via token accumulator in LangGraph state. |
| OQ-005 | Open: @assistant-ui/react handles gml-* or custom renderer needed? | GML-RENDERING-ANALYSIS (2026-02-19) resolves this definitively. GML content arrives via `node_report_preview_done` SSE event (separate from message_delta). It is stored in a ReportStore Zustand slice and rendered in a dedicated `ReportPanel` component outside the Thread. The GML parser is `unified + rehype-parse + rehype-react`. @assistant-ui/react does NOT touch GML content. | Lock as: Separate ReportPanel (Pattern B from GML-RENDERING-ANALYSIS). GML rendering pipeline: GML string → rehype-parse → HAST → healer → rehype-react → React tree. @assistant-ui/react renders chat message text only. New dependencies: `unified`, `rehype-parse`, `rehype-react`. Add these to LIBRARY-REFERENCE. |
| OQ-006 | Open: Brave Search API key confirmed? | STRATEGIC-REVIEW says: "Brave Search confirmed. Proceed." DEC-032 already locks Brave Search. OQ-006 is redundant with DEC-032. | Lock as: confirmed. Close OQ-006 as duplicate of DEC-032. |
| OQ-007 | Open: Pull clarification UI into Phase 3 vs keep deferred to v1.5 | STRATEGIC-REVIEW recommends: keep deferred. Schema + backend checkpoint in v1; minimal text-input banner UI only. | Lock as: Clarification UI deferred to v1.5. v1 delivers schema (BL-002 CLARIFICATION_NEEDED/RECEIVED events), backend pause/resume via AsyncPostgresSaver, and a text-only "This run needs your input" banner. No ClarificationPrompt.tsx rich UI in v1. |

---

## Part 3: Stale Claims

These are specific claims in planning documents that have been superseded or corrected by later research. Each entry includes the document, the stale claim, and what replaces it.

### SC-01: IMPLEMENTATION-PLAN "Background jobs: arq + Redis — Available"

- **Document**: IMPLEMENTATION-PLAN.md, "What We Get For Free" table
- **Stale claim**: `"Background jobs: arq + Redis | core/jobs.py, docker-compose redis | Available"`
- **What replaces it**: STRATEGIC-REVIEW (DG-2, A1) flags this as Assumption A1 with "High" probability of being wrong. The platform has arq + Redis wired in `jobs.py` but whether a worker process with `WorkerSettings` actually runs in production is unverified. "Available" overstates confidence.
- **Required action**: Change to `"Available (unverified — worker process must be confirmed operational before Wave 1 starts)"`. Add verification task to Phase 0 checklist.

### SC-02: DECISION-REGISTER DEC-015 (GML markup format: JSON AST)

- **Document**: DECISION-REGISTER, DEC-015
- **Stale claim**: "Markup format: JSON AST (NYQST Markup AST), not raw HTML tags"
- **What replaces it**: GML-RENDERING-ANALYSIS establishes that the GML rendering pipeline does NOT use a JSON AST intermediate layer. The pipeline is `GML string → rehype-parse → HAST → healer → rehype-react`. The JSON AST (NYQST Markup Document) is the backend report generation format (BL-004/BL-005), not the frontend GML rendering format. These are two different things sharing a name.
- **Required action**: Split DEC-015 into (a) DEC-015a: Report generation uses MarkupDocument JSON AST (Pydantic backend model, BL-004); (b) DEC-015b: Frontend GML rendering uses rehype-to-JSX pipeline without JSON AST intermediate layer.

### SC-03: DECISION-REGISTER OQ-005 framing

- **Document**: DECISION-REGISTER, OQ-005
- **Stale claim**: The question asks "Does [ChatPanel.tsx / @assistant-ui/react] already handle HTML containing `<gml-*>` web components embedded in `<answer>` wrappers, or is a custom renderer needed?"
- **What replaces it**: GML-RENDERING-ANALYSIS shows the question has a false premise. GML content does NOT flow through the @assistant-ui/react message renderer at all. It arrives on a separate SSE event (`node_report_preview_done`), is stored separately, and rendered in a separate `ReportPanel`. The answer is: neither (A) nor (B) as framed — GML rendering is a completely separate component tree.
- **Required action**: Close OQ-005. Add new locked decision (suggested DEC-043): "GML rendering pathway: ReportPanel + GmlRenderer, separate from @assistant-ui/react Thread. Rendering pipeline: unified + rehype-parse + rehype-react."

### SC-04: IMPLEMENTATION-PLAN critical path direction for BL-022

- **Document**: IMPLEMENTATION-PLAN.md, Dependency Graph and Critical Path comment
- **Stale claim**: `"BL-022 (Data Brief, design only — state field) ◄─ BL-001"` and critical path listed as `BL-002 → BL-001 → BL-022 → BL-017 → BL-003 → ...`
- **What replaces it**: DEPENDENCY-ANALYSIS explicitly corrects this. BL-022 design must come BEFORE BL-001 (DataBrief schema defines state fields that BL-001 needs). The arrow is backwards. The critical path comment placing BL-022 after BL-001 in the chain is wrong.
- **Required action**: IMPLEMENTATION-PLAN dependency diagram must flip the BL-022 arrow to `BL-022d → BL-001`. The critical path description must remove BL-022 from the post-BL-001 chain.

### SC-05: GIT-ISSUES BL-016 arq claim

- **Document**: GIT-ISSUES-STRUCTURE.md, BL-016 Technical Notes
- **Stale claim**: `"Async job in: src/intelli/core/jobs.py (arq + Redis already configured)"`
- **What replaces it**: STRATEGIC-REVIEW (C-6) flags this: "already configured" implies it works, but PLATFORM-GROUND-TRUTH says "wired but background job definitions in jobs.py" — ambiguous and possibly boilerplate only. STRATEGIC-REVIEW Assumption A1 rates this as "High" probability of being wrong.
- **Required action**: Change to `"Async job in: src/intelli/core/jobs.py — verify arq worker is operational before implementing (see Phase 0 validation checklist)"`.

### SC-06: LIBRARY-REFERENCE missing three libraries needed by GML rendering

- **Document**: LIBRARY-REFERENCE.md
- **Stale claim**: The library catalog is complete for the implementation.
- **What replaces it**: GML-RENDERING-ANALYSIS identifies three npm packages needed for GML rendering that are not in LIBRARY-REFERENCE: `unified`, `rehype-parse`, `rehype-react`. These are direct dependencies of the GmlRenderer implementation.
- **Required action**: Add three new entries to LIBRARY-REFERENCE: LIB-18 `unified`, LIB-19 `rehype-parse`, LIB-20 `rehype-react`. Install commands: `npm install unified rehype-parse rehype-react`.

### SC-07: DECISION-REGISTER DEC-040 (GML healer: Pydantic validator)

- **Document**: DECISION-REGISTER, DEC-040
- **Stale claim**: "GML healer: Implement as Pydantic validator + AST repair logic in Python (port from JS healer algorithm)"
- **What replaces it**: GML-RENDERING-ANALYSIS confirms the GML healer runs in the FRONTEND (TypeScript), not in the backend (Python). The healer is a HAST (Hypertext Abstract Syntax Tree) walker that repairs GML tag nesting errors in the rehype pipeline. A Python Pydantic healer is still needed for the backend MarkupDocument (BL-004), but the GML frontend healer is a separate TypeScript implementation.
- **Required action**: Split DEC-040 into: (a) DEC-040a: Backend MarkupDocument healer — Python/Pydantic for server-side JSON AST repair (BL-004); (b) DEC-040b: Frontend GML healer — TypeScript/HAST walker in the rehype pipeline, ported from the JS algorithm in TECHNICAL-DEEP-DIVE.md. Both are needed.

---

## Part 4: Items Requiring Update

Ordered by priority: BLOCKING items first, then HIGH, then MEDIUM.

### Priority 1: BLOCKING — Must resolve before implementation code is written

**1A. Lock chart library decision and propagate to all affected documents.**

The chart library conflict (I-01, I-14) is present in four documents with conflicting answers. Before BL-004 (Markup AST schema), BL-005 (report generation), BL-009 (ReportRenderer), and BL-019 (export) are started, this must be resolved. The chart node schema in MarkupDocument must match whichever library is chosen.

Documents to update after the decision:
- LIBRARY-REFERENCE: If Recharts, replace LIB-13 Plotly.js section with Recharts documentation. If Plotly, keep LIB-13 and update IMPLEMENTATION-PLAN + GIT-ISSUES to match.
- IMPLEMENTATION-PLAN: Section 3.6, chart rendering line, and file manifest entry.
- GIT-ISSUES: BL-009 acceptance criteria ("CHART nodes render as Recharts charts" or "...as Plotly charts").
- DECISION-REGISTER: Add locked decision DEC-042: Chart library for v1.

**1B. Close all seven open questions in DECISION-REGISTER.**

Add the following to DECISION-REGISTER Part 2 as locked decisions, using the resolutions from Part 2 of this audit:

| New DEC-ID | Resolves | Decision Text |
|-----------|----------|--------------|
| DEC-042 | OQ-001 | LLM provider: OpenAI-only for v1. gpt-4o for planner/synthesis/meta-reasoning, gpt-4o-mini for fan-out workers. No langchain-anthropic dependency added. |
| DEC-043 | OQ-002, OQ-005 | GML rendering: separate ReportPanel + GmlRenderer using unified + rehype-parse + rehype-react pipeline. Slides viewer reuses iframe approach; gml-viewpresentation renders link card in Phase 1/2. |
| DEC-044 | OQ-003 | Website public URL: iframe-only for v1. (Closes as duplicate of DEC-035.) |
| DEC-045 | OQ-004 | LLM cost budget: gpt-4o-mini for workers, gpt-4o for orchestrator nodes. Hard budget ceiling $2.00/run via token accumulator in LangGraph state. |
| DEC-046 | OQ-006 | Brave Search confirmed as web search provider. (Closes as duplicate of DEC-032.) |
| DEC-047 | OQ-007 | Clarification UI: deferred to v1.5. v1 delivers schema + backend + text-only banner. No rich UI. |

Also add:
- Split DEC-015 into DEC-015a (backend MarkupDocument AST) and DEC-015b (frontend GML uses rehype-to-JSX).
- Split DEC-040 into DEC-040a (backend Python/Pydantic healer) and DEC-040b (frontend TypeScript/HAST healer).
- Update DEC-037 to add: budget enforcement via LangGraph state token accumulator; Langfuse REST API as billing data source; LiteLLM as cost-tracking proxy.

### Priority 2: HIGH — Correct before Wave 0 starts

**2A. GIT-ISSUES: Correct dependency fields for six items.**

| Issue | Current Blocked By | Correct Blocked By |
|-------|-------------------|--------------------|
| BL-003 | BL-001 | None (standalone tools); BL-001 for integration wiring only — note in body |
| BL-005 | BL-001, BL-004 | BL-001, BL-004, Migration 0005 |
| BL-006 | BL-001 | BL-001, Migration 0005 |
| BL-008 | None | BL-015 (weak dependency) |
| BL-012 | None | Migration 0005 (billing tables) |
| BL-016 | BL-002, BL-005 | BL-002, Migration 0005 (hard); BL-005 soft dep for citation binding only |
| BL-018 | BL-001 | BL-001, Migration 0005 |
| BL-022 | BL-001 | None (design portion); BL-001 for integration wiring only |

**2B. GIT-ISSUES: Correct phase/milestone assignments for Wave 0 items.**

BL-015 and BL-008 have no dependencies and should start in Week 1 (Wave 0). Their current assignment to `phase:3-frontend` and M3 is incorrect. Update:
- BL-015: change phase label to `phase:0-foundation`, milestone to M0 or a "Wave 0" milestone.
- BL-008: change phase label to `phase:0-foundation`, milestone to M0.

**2C. IMPLEMENTATION-PLAN: Correct BL-022 dependency arrow direction.**

In the dependency graph section, flip `BL-022 (Data Brief, design only — state field) ◄─ BL-001` to `BL-022d → BL-001`. Update the critical path description to remove BL-022 from the post-BL-001 sequential chain.

**2D. LIBRARY-REFERENCE: Add three missing frontend libraries for GML rendering.**

Add entries for `unified` (LIB-18), `rehype-parse` (LIB-19), `rehype-react` (LIB-20) following the same pattern as existing entries. Install command: `npm install unified rehype-parse rehype-react`. These are needed for GmlRenderer (OQ-005 resolution).

### Priority 3: MEDIUM — Correct before Phase 1 starts

**3A. DECISION-REGISTER: Enrich DEC-037 with Langfuse implementation specifics.**

Append to DEC-037 rationale: "LiteLLM is used as the cost-tracking proxy layer — Langfuse captures cost automatically via LiteLLM callback. Budget enforcement is NOT provided by Langfuse and must be implemented in LangGraph state (token accumulator pattern). Billing data export uses Langfuse REST API (GET /api/v1/traces filtered by user_id and date range)."

**3B. GIT-ISSUES BL-016: Correct arq operational claim.**

In BL-016 Technical Notes, change "arq + Redis already configured" to "arq + Redis wired in jobs.py — verify worker is operational before implementing (Phase 0 validation item)".

**3C. IMPLEMENTATION-PLAN "What We Get For Free": Downgrade arq confidence.**

In the capability table, change `"Available"` for arq background jobs to `"Available (worker process operational status unverified)"`.

**3D. GIT-ISSUES and IMPLEMENTATION-PLAN: Add Phase 0 validation checklist as mandatory.**

STRATEGIC-REVIEW Section 8 recommends adding a "Week 1 Validation Checklist" with six verification tasks that must pass before Wave 1 starts:
1. arq worker operational (enqueue + execute round-trip)
2. Send() prototype with async DB writes (3-node fan-out, no deadlocks)
3. GmlRenderer spike (rehype pipeline renders one GML string)
4. WeasyPrint system dependencies installed and functional
5. Brave Search API key active and rate limit confirmed
6. Existing test suite green after ResearchState extension (BL-001a)

Add this checklist to IMPLEMENTATION-PLAN Phase 0 and as a GIT-ISSUES epic or milestone gate.

---

## Part 5: Summary of Document Health

| Document | Overall Status | Issues Found | Critical |
|----------|---------------|--------------|---------|
| LIBRARY-REFERENCE | Needs update | Missing 3 libraries (rehype stack); chart library conflict | Yes (chart conflict) |
| DEPENDENCY-ANALYSIS | Authoritative | No inconsistencies; corrections not propagated to other docs | No |
| DECISION-REGISTER | Needs significant update | 7 open questions unclosed; 2 decisions need splitting; 1 needs enrichment | Yes (OQs unclosed) |
| GIT-ISSUES-STRUCTURE | Needs update | 8 blocked-by fields wrong; 2 milestone assignments wrong; 1 stale arq claim | Yes (deps wrong) |
| STRATEGIC-REVIEW | Authoritative | Correctly identifies all major issues; recommendations not yet acted on | No |
| IMPLEMENTATION-PLAN | Needs minor update | BL-022 arrow backwards; chart library conflict; arq confidence overstated | Yes (BL-022, chart) |

DEPENDENCY-ANALYSIS and STRATEGIC-REVIEW are the most reliable documents. They were written last and explicitly audit the earlier documents. Their corrections must be the source of truth when updating all other documents.

---

## Revision Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-19 | Agent (claude-sonnet-4-6) | Initial audit — cross-referenced 6 planning docs + 3 analysis docs |
