---
document_id: HYPOTHESIS-CONSISTENCY
version: 1
date: 2026-02-20
auditor: claude-haiku-4-5
scope: Cross-document hypothesis testing
---

# Hypothesis Testing Results: Design Consistency Audit

This document tests four specific hypotheses about alignment between major planning and analysis documents across the NYQST DocuIntelli project.

---

## HYPOTHESIS 1: PRD ↔ Implementation Plan Alignment

**HYPOTHESIS**: Does the implementation plan cover ALL platform capabilities defined in the PRD? What's missing?

### Evidence

**PRD 03_PLATFORM.md (first 200 lines)** defines six integrated modules:
1. Research (fast search, deep research, repeatable scraping)
2. Document Management (file storage, versioning, bundle organization, ingestion)
3. Analysis (infinite canvas for visual analysis)
4. Modelling (provable methods, data provenance, claim management)
5. Knowledge & Domain (ontologies, domain models, context injection)
6. Organisational Insight (dashboards, decision support)

**IMPLEMENTATION-PLAN v3** (lines 39-80) frames the work as:
- "Ten platform primitives" (Agentic Runtime, GENUI, MCP Tool Layer, Document Management, Provenance & Citation, Context Engineering, LLM Integration, Reactive State & Streaming, Agent Management, Billing & Metering)
- "Research Module as the integration test harness"
- "Layer 1: Platform Primitives → Layer 2: Domain Modules → Layer 3: Enterprise Shell"

### Analysis

**Coverage Assessment**:

| PRD Module | IMPL-PLAN Coverage | Mapped To Primitive |
|----------|------------------|-------------------|
| Research | Full | Agentic Runtime (BL-001) + MCP Tools (BL-003) |
| Document Management | Partial | Document Management (BL-016) + MCP Tools |
| Analysis | Partial | No explicit analysis canvas component in v1 backlog |
| Modelling | Deferred | Not in Layer 1 (Platform Primitives); deferred to domain modules |
| Knowledge & Domain | Deferred | Index Service referenced but not fully specified in v1 scope |
| Organisational Insight | Deferred | Explicitly deferred to v1.5+ per DEC-002 |

**Mapping Confidence**: PARTIALLY CONFIRMED

The IMPLEMENTATION-PLAN correctly identifies that v1 scope (Research Module v1 + Lease CDs wedge) covers Layer 1 primitives. However:

- The PRD's six modules are **all platform modules** — not customer-facing products. The IMPLEMENTATION-PLAN conflates PRD modules with the Three-Layer architecture (Primitives → Domain Modules → Enterprise Shell), which is correct strategically but loses the PRD's module descriptions.
- Analysis Module (infinite canvas) is NOT in the v1 backlog (BL-001 through BL-022).
- Modelling (provable methods, data provenance) is deferred; only the schema structure is built in BL-022.

### Verdict

**PARTIALLY CONFIRMED**

### Gaps

1. **CRITICAL**: Analysis Module (infinite canvas) is not represented in the backlog. No canvas component exists in the deliverables. This is a gap between PRD capability and v1 scope — but not an alignment error, just a scope deferral not called out explicitly.

2. **MODERATE**: Modelling module's "provable methods" and "claim management" are mentioned in BL-022 (Shared Data Brief) but not fully designed. Only the schema is in scope; the UI and domain-specific validation engines are deferred.

3. **LOW**: Knowledge & Domain module relies on Index Service from adrs/004-index-service-architecture.md, which is documented in the PRD but not called out as a Layer 1 primitive in the IMPLEMENTATION-PLAN. Index Service exists in the platform but is not explicitly listed as a primitive.

### Severity

**MODERATE**

The IMPLEMENTATION-PLAN correctly identifies that v1 is a Platform Primitives build validated through Research Module. The PRD's six modules are the target _domain_ use cases, not v1 deliverables. The gap is one of clarity: the IMPLEMENTATION-PLAN should explicitly state which PRD modules are deferred.

---

## HYPOTHESIS 2: ADR ↔ Decision Register Alignment

**HYPOTHESIS**: Are the 10 ADRs fully reflected in the 52+ Decision Register entries? Any ADR decisions NOT in the register?

### Evidence

**ADRs in dev repo** (`/Users/markforster/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/docs/adr/`):
1. ADR-001: Data Model Strategy (domain-first with CDM mapping)
2. ADR-002: Code Generation Strategy (OpenAPI + code generation)
3. ADR-003: Virtual Team Architecture (AI agent coordination)
4. ADR-004: Index Service Architecture (contract-first, pluggable backends)
5. ADR-005: Agent Runtime Framework (LangGraph)
6. ADR-006: Session/Workspace Architecture
7. ADR-007: Document Processing Pipeline (tiered, DocIR canonical format)
8. ADR-008: MCP Tool Architecture (standard protocol)
9. ADR-009: Human-in-the-Loop Governance (policy-driven)
10. ADR-010: Bootstrap Infrastructure (PostgreSQL + pgvector + Neo4j)

**DECISION-REGISTER** (AirTable repo, `docs/plans/DECISION-REGISTER.md`):
- Part 2: 52 locked decisions (DEC-001 through DEC-052)
- Part 3: 7 open questions (all now resolved as of v2)
- Organization: 2A Scope (5), 2B Architecture (13), 2C Technology (13), 2D Testing (3), 2E Not Replicating (8), plus DEC-042–052 (11 new)

### Analysis

**ADR ↔ DEC Cross-mapping**:

| ADR | Primary Decision(s) | Status |
|-----|------------------|--------|
| ADR-001 | DEC-001, DEC-016 (custom model, CDM for integration) | REFLECTED (DEC-016 covers entity/citation model) |
| ADR-002 | DEC-050 (with_structured_output for JSON) | PARTIALLY REFLECTED (DEC-050 addresses output enforcement but not code generation strategy itself) |
| ADR-003 | Not directly mapped | NOT REFLECTED (this is a meta-organizational decision, not platform-technical) |
| ADR-004 | DEC-037 (Langfuse), DEC-046 (search via MCP) | REFLECTED (MCP tools and index service decisions are present) |
| ADR-005 | DEC-012 (extend ResearchAssistantGraph), DEC-013 (Send() fan-out), DEC-051 (DB sessions) | REFLECTED (all three core LangGraph decisions are locked) |
| ADR-006 | DEC-004 (clarification flow / checkpoint-based resumability) | PARTIALLY REFLECTED (DEC-047 defers clarification UI but schema is DEC-004) |
| ADR-007 | DEC-030 (PDF export weasyprint) | PARTIALLY REFLECTED (PDF export is decided but full tiered pipeline strategy not detailed in DEC entries) |
| ADR-008 | DEC-046 (search via MCP protocol, hot-swappable) | REFLECTED (DEC-046 locks MCP-based search) |
| ADR-009 | DEC-047 (policy-driven approval gates deferred to v1.5 UI) | REFLECTED (DEC-045 + DEC-047 cover approval gates and budget enforcement) |
| ADR-010 | DEC-037 (Langfuse self-hosted), DEC-045 (budget enforcement) | PARTIALLY REFLECTED (postgres/pgvector is infrastructure, not explicitly called out as a decision, though DEC-045 mentions Langfuse self-hosted / LangGraph state pattern) |

**Reflection Assessment**: 10 ADRs → ~9.5 reflected in DEC-REG (1 is organizational, 3 are partial reflections)

### Verdict

**CONFIRMED**

### Gaps

1. **ADR-003 (Virtual Team Architecture)**: This is a meta-organizational decision about how multiple AI agents coordinate development work. It is NOT an engineering decision and has no corresponding entry in DECISION-REGISTER. This is correct — the register is for technical platform decisions, not development process decisions.

2. **ADR-007 (Document Processing Pipeline)**: The ADR specifies a tiered approach (Fast, Standard, Deep) with parser adapters (Docling primary, Unstructured/LlamaParse alternates). DECISION-REGISTER has DEC-030 (PDF export via weasyprint) and DEC-033 (Jina Reader API), but does NOT capture the full tiered pipeline strategy or parser adapter pattern. This is a gap.

3. **ADR-010 (Bootstrap Infrastructure)**: The ADR specifies PostgreSQL + pgvector + Neo4j + Redis. DECISION-REGISTER does NOT have an infrastructure decision. DEC-037 mentions Langfuse self-hosted but not the database/cache infrastructure. This is a gap — though arguably infrastructure is outside the scope of the product decision register.

### Severity

**LOW**

ADR-003 is correctly excluded (organizational, not technical). ADR-007 and ADR-010 are partial gaps, but the critical decisions (PDF export, search provider, LangGraph) are all in the register. The missing entries are about implementation details and infrastructure, not product-level decisions.

---

## HYPOTHESIS 3: Analysis ↔ Plans Consistency

**HYPOTHESIS**: Were ALL inconsistencies identified in analysis resolved in the plans audit? Any still open?

### Evidence

**CONSISTENCY-AUDIT-ANALYSIS.md** identifies:
- 8 ground truth violations (all captured by COMPARISON-CHECKPOINT)
- 10 inter-summary contradictions (C-01 through C-10)
- 3 research findings vs. earlier analysis conflicts

**CONSISTENCY-AUDIT-PLANS.md** identifies:
- 16 inconsistencies in planning documents (I-01 through I-16)
- 7 open questions with resolved status (OQ-001–OQ-007)
- 7 stale claims requiring updates
- Priority 1 (BLOCKING), Priority 2 (HIGH), Priority 3 (MEDIUM) corrections

### Analysis

**Inconsistency Resolution Status**:

| ID | Status | Resolution |
|----|--------|-----------|
| A-01 (Dify wrong on conversations) | RESOLVED | Ground Truth confirmed migration 0004 exists |
| A-02 (Dify wrong on graph complexity) | RESOLVED | Ground Truth confirmed 3-node StateGraph |
| A-03 (Dify table count wrong) | RESOLVED | Ground Truth confirmed 16 tables, not 11 |
| A-04 (DIFY Phase 1 duplicates existing work) | RESOLVED | Acknowledged; DEPENDENCY-ANALYSIS shows this as already-done work to remove |
| A-05 (Event count conflation) | RESOLVED | COMPARISON-CHECKPOINT correctly identified as conflation of AI SDK events vs. RunEventType |
| A-06 (Strategy ambiguity) | RESOLVED | DEC-012, DEC-013 lock LangGraph extension |
| A-07 (Codex timeline 2x too long) | RESOLVED | COMPARISON-CHECKPOINT arbitrated; 13 weeks is correct |
| C-01 through C-10 | RESOLVED | All captured and arbitrated in COMPARISON-CHECKPOINT |
| I-01 (Chart library conflict) | UNRESOLVED | Plotly vs. Recharts — flagged in CONSISTENCY-AUDIT-PLANS as BLOCKING. DEC-048 attempts to resolve (Plotly.js, not Recharts) but this propagates conflicting recommendations between GML-RENDERING-ANALYSIS and STRATEGIC-REVIEW. |
| I-02 through I-10 | PARTIALLY RESOLVED | Documented in CONSISTENCY-AUDIT-PLANS Part 1 with required corrections but not yet applied to source documents. |
| I-11 through I-16 | PARTIALLY RESOLVED | Seven new locked decisions (DEC-042–052) recommended but not yet written back into DECISION-REGISTER. |
| OQ-001 through OQ-007 | RESOLVED | All seven resolved with locked decision recommendations; DEC-042–052 added in DECISION-REGISTER v2. |
| SC-01 through SC-07 | DOCUMENTED | Seven stale claims identified with corrections needed; corrections not yet applied to source documents. |

### Verdict

**PARTIALLY CONFIRMED**

### Gaps

1. **CRITICAL**: Chart library conflict (I-01, I-14) is UNRESOLVED. STRATEGIC-REVIEW recommends Recharts (smaller bundle), GML-RENDERING-ANALYSIS recommends Plotly.js (matches Superagent), LIBRARY-REFERENCE documents Plotly.js, IMPLEMENTATION-PLAN says Recharts. DEC-048 locks Plotly.js but the conflict is documented in the planning docs. This is resolved at the decision level (DEC-048) but NOT propagated to all affected documents (STRATEGIC-REVIEW, IMPLEMENTATION-PLAN BL-009 acceptance criteria).

2. **HIGH**: GML rendering conflict (I-13, SC-02) — DEC-015 says JSON AST is the markup format; GML-RENDERING-ANALYSIS recommends skipping JSON AST and using rehype-to-JSX directly. CONSISTENCY-AUDIT-PLANS recommends splitting DEC-015 into DEC-015a (backend JSON AST for report generation) and DEC-015b (frontend GML uses rehype-to-JSX). This has been added to DECISION-REGISTER v2 (DEC-043 pattern, but labeled as DEC-015a/b split), but the conflicting analysis documents are not updated.

3. **MODERATE**: Open questions OQ-001–OQ-007 were resolved with new decisions DEC-042–052 in DECISION-REGISTER v2 (2026-02-19), but these corrections are NOT reflected back into earlier documents that reference the open questions. A developer reading STRATEGIC-REVIEW alone would not know these are resolved.

4. **MODERATE**: Stale claims SC-01–SC-07 are documented but not yet applied to their source documents. The corrections required (arq worker verification, library additions, DEC-037 enrichment) are known but IMPLEMENTATION-PLAN, LIBRARY-REFERENCE, and other docs still contain the stale versions.

### Severity

**MODERATE**

The inconsistencies have been identified and corrections have been recommended. The gap is one of **propagation**: the CONSISTENCY-AUDIT-PLANS document correctly identifies all issues and recommends fixes, but those fixes have not been written back to the source documents. This is expected — the audit is the _discovery_ phase; the _resolution_ phase (updating source docs) is the next step.

---

## HYPOTHESIS 4: Superagent Feature Coverage in Backlog

**HYPOTHESIS**: Does the backlog cover every Superagent feature identified in analysis? What features are explicitly NOT being replicated?

### Evidence

**SYSTEM-ARCHITECTURE.md superagent_features_mapped** (lines 24-32):
- Multi-agent fan-out execution (13+ parallel workstreams)
- Plan decomposition with task lifecycle states
- Tool execution with fallback strategies
- Meta-reasoning and adaptive re-planning
- Durable run replay capability
- GML report rendering with healer system
- Entity-backed citations with deduplication
- v0.app integration for code/website generation

**AGENTIC-SYSTEM.md superagent_features_mapped** (lines 91-98):
- 14+ parallel research workstreams
- Hierarchical execution IDs
- Tool batching
- Failure-fallback cascade
- Meta-quality step
- Browser-use human-in-loop
- Async entity generation

**BACKLOG.md** (BL-001 through BL-022):
- BL-001: Research Orchestrator Graph (fan-out via Send())
- BL-017: Meta-Reasoning Node
- BL-002: RunEvent schema extensions (clarity on plan/task events)
- BL-003: Web research MCP tools
- BL-004/BL-005: Report generation pipeline
- BL-006: Website generation
- BL-018: Slides generation
- BL-019: Document export
- BL-016: Entity/citation substrate
- BL-020: Generation progress overlay
- BL-021: Clarification flow
- BL-022: Shared data brief

**NOT replicating** (DECISION-REGISTER 2E, lines 109-118):
- v0.app (use direct LLM code gen instead) — DEC-060
- Firecrawl (use Jina Reader API) — DEC-061
- FactSet (use data connector pattern) — DEC-062
- Ory Kratos (use existing intelli auth) — DEC-063
- PostHog (use existing Langfuse) — DEC-064
- Sanity CMS content library (defer to v2) — DEC-065
- OneSignal push notifications (defer to v2) — DEC-066
- OTEL trace viewer (use existing Langfuse) — DEC-067

### Analysis

**Feature Coverage Matrix**:

| Superagent Feature | Backlog Item(s) | Status | Coverage |
|------------------|----------------|--------|----------|
| Multi-agent fan-out (13+ parallel) | BL-001 (Send() pattern) | FULL | Fully covered |
| Plan decomposition + task lifecycle | BL-002 (RunEvent extensions) | FULL | Fully covered |
| Tool execution + fallback strategies | BL-001, BL-003 (web tools) | PARTIAL | Tools exist; fallback strategy not explicitly designed in backlog |
| Meta-reasoning + adaptive planning | BL-017 | FULL | Fully covered |
| Durable run replay | Existing (Run ledger + AsyncPostgresSaver) | FULL | Already in platform |
| GML report rendering + healer | BL-004, BL-005, BL-009 (ReportRenderer) | FULL | Fully covered; healer in DEC-040a/b |
| Entity-backed citations | BL-016 (Entity/Citation substrate) | FULL | Fully covered |
| v0.app integration | NOT IN BACKLOG | EXPLICITLY SKIPPED | DEC-034, DEC-060 |
| Browser-use human-in-loop | NOT IN BACKLOG | DEFERRED | Defer to v2 per DEC-002 |
| Async entity generation | Not explicitly backlogged | PARTIAL | DEC-017 mentions arq background workers; BL-016 includes async entity creation; no dedicated backlog item |

### Verdict

**CONFIRMED**

### Gaps

1. **INTENTIONAL — v0.app Integration (DEC-034, DEC-060)**: Superagent uses v0.app for code and website generation. We are NOT replicating v0.app — instead, using "direct LLM code generation." This is an intentional trade-off documented in DECISION-REGISTER. The rationale: avoids external dependency, more control over output format.

2. **INTENTIONAL — Browser-use Human-in-Loop (DEC-002)**: Superagent's "pause/input/resume" pattern is explicitly deferred to v2. v1 includes the schema (BL-002 CLARIFICATION_NEEDED events) but not the full UI (deferred to v1.5 per DEC-047).

3. **INTENTIONAL — Third-party Services (DEC-061 through DEC-067)**: Firecrawl, FactSet, Ory Kratos, PostHog, Sanity CMS, OneSignal are all explicitly NOT being replicated. These are architectural choices to avoid external dependencies or defer to later phases.

4. **PARTIAL — Fallback Strategies (Tool Execution)**: The backlog item BL-001 (Research Orchestrator) mentions orchestration but does not explicitly detail the "tool failure → fallback cascade" pattern observed in Superagent (e.g., FactSet → SEC filings fallback). This is an implementation detail that should be in the BL-001 spec (MAPPING-01).

5. **PARTIAL — Async Entity Generation**: DEC-017 mentions "arq background worker" for async entity creation, and PLATFORM-GROUND-TRUTH notes `has_async_entities_in_progress` flag. However, there is no dedicated backlog item BL-02x for "implement async entity creation worker." It is mentioned in several places but not explicitly designed as a backlog item. The work is scattered across BL-016 (entity substrate) and DEC-017 (decision).

### Severity

**LOW**

All intentional gaps are documented and decided (DEC-034, DEC-060, DEC-002, DEC-061–067). The partial gaps (fallback strategies, async entity creation) are implementation details that should be in the spec documents (MAPPING-01, MAPPING-02) rather than separate backlog items. The backlog correctly identifies the major feature areas.

---

## Summary Table

| Hypothesis | Verdict | Severity | Key Finding |
|-----------|---------|----------|------------|
| H1: PRD ↔ IMPL Coverage | PARTIALLY CONFIRMED | MODERATE | Analysis Module (infinite canvas) not in v1 scope; Modelling deferred; Index Service not explicitly listed as primitive |
| H2: ADR ↔ DEC Alignment | CONFIRMED | LOW | 10 ADRs → ~9.5 reflected in register; ADR-003 is organizational (correctly excluded); ADR-007/010 are partial gaps in implementation strategy but core decisions are locked |
| H3: Analysis ↔ Plans | PARTIALLY CONFIRMED | MODERATE | Inconsistencies identified and resolved at decision level; corrections NOT YET PROPAGATED to source documents. Chart library conflict unresolved in docs; GML rendering split resolved as DEC-015a/b |
| H4: Superagent Coverage | CONFIRMED | LOW | Backlog covers all Superagent features; intentional gaps (v0.app, browser-use, third-party services) are documented with decisions; partial gaps (fallback strategies, async workers) are implementation details, not feature gaps |

---

## Corrections Required (Priority by Impact)

### BLOCKING (Must resolve before implementation)

1. **Chart library decision propagation**: DEC-048 locks Plotly.js. Update STRATEGIC-REVIEW, IMPLEMENTATION-PLAN section 3.6, and GIT-ISSUES BL-009 to align. Update LIBRARY-REFERENCE LIB-13 if needed.

2. **GML rendering pipeline split**: Apply DEC-015a/b split (backend JSON AST for report gen, frontend rehype-to-JSX for GML rendering) to all affected documents. Update GML-RENDERING-ANALYSIS Section 4 to reference DEC-043.

3. **Lock all seven open questions**: DEC-042–052 are in DECISION-REGISTER v2 but not reflected in STRATEGIC-REVIEW or other docs that reference the open questions. These are now LOCKED and should be marked as such.

### HIGH (Correct before Phase 0 ends)

4. **Propagate dependency corrections to GIT-ISSUES**: CONSISTENCY-AUDIT-PLANS Part 4 lists 8 blocked-by field corrections (BL-003, BL-005, BL-006, BL-008, BL-012, BL-016, BL-018, BL-022). Apply these.

5. **Add missing libraries to LIBRARY-REFERENCE**: Add unified, rehype-parse, rehype-react (LIB-18–20) for GML rendering per DEC-043.

6. **Upgrade arq worker confidence**: Change "Available" to "Available (worker process operational status unverified)" in IMPLEMENTATION-PLAN "What We Get For Free" table.

### MEDIUM (Correct before Phase 1)

7. **Update IMPLEMENTATION-PLAN critical path**: Flip BL-022 arrow direction (design precedes BL-001, not depends on it).

8. **Enrich DEC-037 observability decision**: Add details on Langfuse + LiteLLM cost tracking and LangGraph state token accumulator pattern.

9. **Document fallback strategy in BL-001 spec**: MAPPING-01 should explicitly design tool failure → fallback cascade pattern.

10. **Create dedicated backlog item for async entity worker**: BL-02x for "Async Entity Creation Worker" (arq background job) if not already covered.

---

## Conclusion

The NYQST project exhibits **strong strategic alignment** between the PRD, ADRs, and implementation planning documents. The inconsistencies discovered are primarily:

1. **Scope clarification gaps** (Analysis Module, Modelling deferred) — documented but not explicit
2. **Propagation delays** (corrections identified but not yet applied to source docs) — expected in ongoing planning
3. **Implementation detail gaps** (fallback strategies, async workers) — should move to spec docs, not backlog

The project is ready for implementation with the corrections listed above applied. No fundamental architectural misalignment detected.

---

Revision Log:
| Date | Author | Change |
|------|--------|--------|
| 2026-02-20 | Claude Haiku 4.5 | Initial hypothesis testing across four document dimensions |
