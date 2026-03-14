---
document_id: PLATFORM-FRAMING
version: 1
date: 2026-02-19
status: CRITICAL — Strategic anchor for all NYQST implementation work
model: opus
references:
  - PRD-ADR-DIGEST: docs/analysis/PRD-ADR-VISION-DIGEST.md
  - DEC-REG: docs/plans/DECISION-REGISTER.md
  - DEP-ANALYSIS: docs/plans/DEPENDENCY-ANALYSIS.md
  - BL: docs/plans/BACKLOG.md
  - PLATFORM-GROUND-TRUTH: docs/analysis/PLATFORM-GROUND-TRUTH.md
  - AGENTIC-SYSTEM: docs/analysis/AGENTIC-SYSTEM.md
---

# Platform Framing: Reconciling the PRD Vision with the Superagent Parity Plan

**Purpose:** This document permanently resolves the apparent conflict between the Cognitive ERP product vision (PRD-ADR-DIGEST) and the Superagent parity implementation plan. It establishes the three-layer architecture model that governs all implementation sequencing, reframes existing decisions in platform-primitive terms, and provides the reuse matrix connecting horizontal platform capabilities to vertical domain modules.

**Audience:** Developer teams who need to understand WHY they are building what they are building. Every scope decision, feature cut, and priority trade-off should reference this document.

---

## 1. The Apparent Conflict

Two planning threads exist for this project, and at first glance they describe different products.

**Thread A -- The PRD Vision (PRD-ADR-DIGEST).** The PRD defines a "Cognitive ERP" for regulated mid-cap enterprise. It names domain modules: PropSygnal (CRE intelligence), Debt & Credit MVP (covenant monitoring, DSCR/LTV calculation, lender pack generation), RegSygnal (regulatory monitoring). It specifies a ~$200k/year price point, a Lease Critical Date wedge strategy, and success metrics anchored in extraction accuracy (95%+), calculation accuracy (100%), and institutional trust. The product serves investment analysts, asset managers, compliance officers, and portfolio managers. Architecture principles demand immutable artifacts, deterministic calculation engines, provenance on every output, and agents operating within defined policy boundaries.

**Thread B -- The Superagent Parity Plan (BL, DEP-ANALYSIS, DEC-REG).** The Superagent parity plan describes building a research orchestrator with parallel agent fan-out (LangGraph Send()), structured multi-format deliverables (reports, websites, slides, documents), web search tools (Brave/Jina via MCP), a GML markup system with a healer pipeline, streaming progress UI, billing/quotas, and citation tracking. The backlog (BL) contains 22 items with a 7-week critical path.

**The surface reading:** One thread says "build a platform for lease covenant monitoring in regulated enterprise." The other says "build a research assistant that generates websites and slides." These look like different products with incompatible priorities.

**They are not in conflict.** They describe the same system viewed from different layers of abstraction. The PRD describes what customers see and buy. The Superagent parity plan describes the horizontal platform capabilities that every domain module needs to function. The research orchestrator is not the product. It is the test harness that proves the platform primitives work.

---

## 2. The Resolution: Three-Layer Architecture

The insight that resolves the conflict:

> The Superagent parity work builds PLATFORM PRIMITIVES. The Research Module is the TEST HARNESS that proves those primitives work. Domain modules (Lease Critical Dates, Debt MVP, PropSygnal, RegSygnal) then RUN ON that proven platform.

Every primitive built for "research" becomes infrastructure that all domain modules inherit without reimplementation. The architecture is three layers deep.

### Layer 1 -- Platform Primitives

These are the ten horizontal capabilities that every module consumes. The Superagent parity plan builds and proves all ten through the research module.

**1. Agentic Runtime.** LangGraph orchestrator with StateGraph, Send() fan-out for dynamic parallel agent dispatch, supervisor/coordinator pattern, child run tracking via `parent_run_id`, and AsyncPostgresSaver checkpointing. Governed by ADR-003 (Virtual Team Architecture) and ADR-005 (Agent Runtime Framework). This is the execution engine for all agent-driven work across all modules.

**2. GENUI (Generative UI).** The NYQST Markup AST (BL-004), GML tag system with 18 node types, healer/fixer pipeline (DEC-040), rehype-to-JSX rendering, ReportRenderer (BL-009), WebsitePreview (BL-010), and the `<answer>` wrapper format (DEC-022). Enables LLM-generated structured output that renders consistently across all formats and all modules.

**3. MCP Tool Layer.** Model Context Protocol as the universal agent-tool interface (ADR-008). Namespaced `{domain}.{resource}.{action}` convention. Session-scoped dynamic discovery. Execution pipeline: validate, policy check, execute, log to run ledger, return. Hot-swappable -- domain modules register their own tools into the same namespace system without modifying the execution pipeline.

**4. Document Management.** Content-addressed artifacts (SHA-256 PK, immutable), manifests (tree snapshots), pointers (mutable HEAD references with full history), sessions, and projects. The substrate kernel is fully implemented and battle-tested. Storage backends: S3/MinIO with configurable storage class. Entity_type taxonomy classifies artifacts across all modules.

**5. Provenance & Citation.** Source tracking from extraction through rendering. Entity/citation substrate (BL-016) stores source references as artifacts. Citation IDs link output nodes to source entities. `REFERENCES_FOUND` events trigger async entity creation. The SourcesPanel and CitationAwareText components already exist in the frontend. Designed for URL-level granularity (research) and span-level granularity (extraction) from the start.

**6. Context Engineering.** Data briefs (BL-022), scratchpads, contextual corpus assembly, and knowledge inheritance across sessions. Token window management, memory, summarisation, RAG context injection. Sessions inherit context from project/objective hierarchy (ADR-006). The context primitive is domain-agnostic -- schema, inheritance, and injection mechanisms are shared.

**7. LLM Integration.** Currently ChatOpenAI (langchain-openai) with `base_url` override for model routing. Config-driven model selection. Multi-provider strategy mandated by PRD constraint #23 (no single provider dependency). LiteLLM or equivalent abstraction layer for hot-swap. Budget enforcement embedded in LangGraph state. Different model tiers for different node roles (orchestrator vs. worker).

**8. Reactive State & Streaming.** Dual-stream architecture (DEC-021): chat content via AI SDK Data Stream Protocol, run lifecycle events via PG LISTEN/NOTIFY SSE. Zustand stores for client state (auth, conversation, workbench, run). SSE endpoints: `GET /streams/runs/{run_id}` and `GET /streams/activity`. RunEvent lifecycle tracks every state transition. All fully implemented and production-ready.

**9. Agent Management.** Graph definitions, node configurations, tool registries. Four policy templates: exploratory, standard, regulated, audit_critical (ADR-009). ApprovalRequest model for human-in-the-loop. `APPROVAL_REQUESTED/GRANTED/DENIED` events already in RunEventType. Governance records in the run ledger. Backend v1 establishes the primitive; client-facing management UI follows.

**10. Billing & Metering.** Run cost tracking (`cost_cents` and `token_usage` fields on Run model). Stripe integration (BL-012, ported from okestraai/DocuIntelli). Quota enforcement middleware (BL-013). Subscription and usage_records tables in migration 0005. Per-run cost attribution with session and project scoping. The metering primitive is shared; pricing logic is configurable per deployment model.

### Layer 2 -- Domain Modules

These are vertical products that run ON Layer 1 primitives. Each module combines domain-specific agents, domain-specific MCP tools, domain-specific schemas, and domain-specific UI. The heavy infrastructure is inherited.

| Module | Status | Description |
|--------|--------|-------------|
| **Research Module** | v1 -- the test harness | Multi-format research deliverables. Exercises all 10 primitives. The proof that the platform works. |
| **Lease Critical Dates** | PRD V1 wedge | Lease extraction, date detection, break options, notice periods, event calendar, deadline alerts. The commercial entry point. |
| **Debt MVP** | Q2 2026 | Rent roll extraction, covenant calculations (DSCR, LTV, ICR), lender pack generation, covenant risk alerting. |
| **PropSygnal** | Post-Debt MVP | CRE market intelligence, comparable transactions, deal screening, investment memo generation. |
| **RegSygnal** | Post-Debt MVP | Regulatory change detection, requirement extraction, cross-regulation mapping, compliance gap analysis. |

### Layer 3 -- Enterprise Shell

Cross-cutting concerns required for enterprise deployment. These wrap the platform for production use by regulated organisations.

- **SSO/OIDC/SAML** -- enterprise identity provider integration, replacing JWT + API key for enterprise customers
- **RBAC/ABAC** -- role-based and attribute-based access control beyond current scope model
- **Multi-tenant isolation** -- data partitioning, tenant-scoped queries, cross-tenant protection
- **Data residency / GDPR** -- configurable data location, retention policies, right-to-deletion
- **Audit trails** -- enterprise-grade audit beyond the run ledger (admin access, config changes, user management)
- **Compliance governance** -- policy enforcement, approval chains, regulatory reporting
- **Enterprise billing** -- annual contracts, invoicing, capacity-based pricing, cost center attribution
- **Notification service** -- email alerts, webhook integrations, configurable notification rules for operational triggers

---

## 3. Platform Primitive to Module Reuse Matrix

This matrix shows which platform primitives each domain module requires. Every module consumes all ten Layer 1 primitives. The bottom three rows are Layer 2 extensions -- capabilities needed by subsets of domain modules but NOT part of Superagent parity work.

| Primitive | Research | Lease CDs | Debt MVP | PropSygnal | RegSygnal |
|-----------|----------|-----------|----------|------------|-----------|
| Agentic Runtime | ✓ | ✓ | ✓ | ✓ | ✓ |
| GENUI | ✓ | ✓ | ✓ | ✓ | ✓ |
| MCP Tools | ✓ | ✓ | ✓ | ✓ | ✓ |
| Document Mgmt | ✓ | ✓ | ✓ | ✓ | ✓ |
| Provenance | ✓ | ✓ | ✓ | ✓ | ✓ |
| Context Eng. | ✓ | ✓ | ✓ | ✓ | ✓ |
| LLM Integration | ✓ | ✓ | ✓ | ✓ | ✓ |
| Streaming | ✓ | ✓ | ✓ | ✓ | ✓ |
| Agent Mgmt | ✓ | ✓ | ✓ | ✓ | ✓ |
| Billing | ✓ | ✓ | ✓ | ✓ | ✓ |
| Deterministic Calc | — | — | ✓ | ✓ | — |
| Event Engine | — | ✓ | ✓ | — | ✓ |
| Doc Processing | partial | ✓ | ✓ | — | ✓ |

**Reading the matrix:**

- The top ten rows are universal. Cutting any of them affects all five modules. These are non-negotiable.
- The bottom three rows are domain-readiness extensions built in Phase 3. Cutting one affects specific modules only.
- "partial" for Research/Doc Processing: the research module handles user-uploaded files for RAG context but does not require the full Docling/OCR/DocIR pipeline that lease and financial documents demand.
- Deterministic Calc, Event Engine, and Doc Processing are NOT part of the Superagent parity work. They are built after the platform layer is proven and before domain modules ship.

**Scope decision rule:** When evaluating whether to cut or defer a backlog item, check this matrix. If the item maps to a top-ten primitive, cutting it affects all modules downstream. If it maps to a bottom-three extension, the impact is scoped to specific modules.

---

## 4. Why Research Module Is the Right Test Harness

The decision to build research before any other domain module is strategic, not accidental.

**It exercises ALL 10 platform primitives simultaneously.** No other module touches every primitive in a single end-to-end flow. A research run starts with a user query (context engineering), decomposes it into subtasks (agentic runtime), dispatches parallel agents that call web search and scraping tools (MCP tool layer), accumulates findings (context engineering), generates structured reports with citations (GENUI + provenance), stores outputs as immutable artifacts (document management), streams progress to the UI (reactive state), tracks costs (billing), and operates within policy boundaries (agent management) using configurable LLM providers (LLM integration). One flow validates the entire platform layer.

**It has the most complex orchestration.** Superagent.com runs 13+ parallel workstreams with 23+ numbered subagent tasks (AGENTIC-SYSTEM). If the Send() fan-out pattern works at this scale for research, it works for the simpler parallelism that domain modules require (parallel lease extraction, parallel covenant calculation).

**It uses every deliverable type.** Report, Website, Slides, Document. The GENUI primitive must handle all four. Domain modules use subsets -- Lease CDs produces reports and documents, Debt MVP produces reports and Excel exports -- but the rendering infrastructure is proven across all formats first.

**It stress-tests streaming, citations, and document management.** Real-time progress for 13+ parallel workstreams. Citation binding across dozens of web sources. Multi-artifact document storage for website bundles. These are the hardest integration points, and research exercises all of them under load.

**If it works for research, it works for simpler domain modules.** Lease Critical Date extraction is structurally simpler than multi-format research orchestration -- fewer parallel agents, fewer deliverable types, fewer citation sources. A platform proven under the harder case is reliable under the easier one.

**Superagent.com is the ONLY reference implementation we can study.** It is a working product with observable behaviour -- task decomposition patterns, progress state transitions, output formats, error handling. No equivalent reference implementation exists for lease extraction or covenant monitoring. Building against an observable reference reduces design risk.

---

## 5. What Superagent Parity Does NOT Build

Clarity about scope boundaries prevents feature creep and misallocated effort.

**Domain-specific extraction.** Lease term extraction, rent review date detection, covenant value identification, regulatory requirement decomposition -- these are Layer 2 domain module concerns. The platform provides the agentic runtime, MCP tool interface, and provenance system. Domain modules provide the extraction logic, schemas, and validation rules.

**Deterministic calculation engines.** DSCR = NOI / Debt Service. LTV = Loan Balance / Property Value. These must produce identical results from identical inputs, every time. They are Layer 2 extensions with a fundamentally different accuracy guarantee (100%, not probabilistic). The platform provides the execution container; the calculation engines are domain-specific code with exhaustive deterministic test suites.

**Event-driven monitoring.** Calendar triggers (lease break dates), deadline calculations (notice periods), regulatory change alerts, covenant breach warnings. These require an event engine -- a persistent scheduler with configurable rules, lead times, and notification channels. This is a Layer 2 extension built in Phase 3, not a Superagent parity concern.

**SSO/RBAC/multi-tenant isolation.** Enterprise identity integration (OIDC/SAML), role-based access control beyond current scopes, hard multi-tenant data partitioning. These are Layer 3 enterprise shell concerns. The current JWT + API key system (DEC-038) is sufficient for platform development and internal use.

**Schema-first codegen.** Deferred. Not in scope for any current phase.

---

## 6. Decision Reframing

Key decisions from the DECISION-REGISTER (DEC-REG) were originally framed in terms of "Superagent features" or "internal tool scope." Reframed in platform-primitive terms, their strategic significance becomes clear.

| Decision | Old Frame (Research Tool) | New Frame (Platform Primitive) |
|----------|--------------------------|-------------------------------|
| DEC-001 (v1 scope) | "Build research features" | "Prove 10 platform primitives via research module" |
| DEC-012 (extend ResearchAssistantGraph) | "Enhance the research graph" | "Build the agentic runtime using research as first consumer" |
| DEC-013 (Send() fan-out) | "Research needs parallel tasks" | "Platform runtime needs dynamic parallelism -- all modules will use it" |
| DEC-015 (JSON AST) | "Research reports need structured output" | "GENUI primitive needs a universal markup format -- all modules will render through it" |
| DEC-025 (per-run billing) | "Charge for research runs" | "Billing primitive meters ALL module activity uniformly" |
| DEC-032 to DEC-046 (Search via MCP) | "Research needs web search" | "MCP Tool Layer is hot-swappable -- domain modules plug in their own tools" |

The reframe does not change the decisions. It changes how they are evaluated. A decision that looks optional when framed as "research feature" becomes non-negotiable when framed as "platform primitive that five modules depend on."

---

## 7. Implementation Sequence Implication

Each phase maps to the layer model. The sequence is driven by dependency, not preference.

**Wave 0-1: Build platform primitives.** This is what appears externally as "Superagent parity." Migration 0005 (document management, billing tables), RunEvent schema extensions (streaming, agentic runtime), NYQST Markup AST (GENUI), DeliverableStore (streaming client state), DataBrief schema (context engineering), web research tools (MCP tools). These items have zero dependencies on each other and execute in full parallel. They establish the contracts that all subsequent work builds against.

**Wave 2-3: Complete research module as integration test.** Research orchestrator graph with Send() fan-out (agentic runtime), report/website/slides generation pipelines (GENUI), meta-reasoning node (runtime quality layer), clarification flow (agent management HITL), data brief integration (context engineering). The orchestrator is the critical path bottleneck -- it validates the Send() pattern that every domain module depends on. Frontend integration (PlanViewer, ReportRenderer, WebsitePreview, SourcesPanel, RunTimeline, progress overlay) completes the proof. After this wave, all ten Layer 1 primitives are built, tested, and integrated.

**Post-v1: Lease Critical Dates module plugs into proven platform.** Document processing pipeline (Docling, OCR, DocIR), event management engine (calendar, deadlines, alerts), and the domain-specific extraction agents, MCP tools, and schemas. This module does not rebuild the platform. It configures domain-specific components that run on Layer 1.

**Q2 2026: Debt MVP, then PropSygnal, RegSygnal follow.** Each subsequent module is thinner than the last. The platform is proven. The domain-readiness extensions (deterministic calculation engine, enhanced event engine) are built once and shared.

---

## 8. Risks of NOT Framing This Way

Without the platform-first framing, the following failure modes become likely.

**Research-specific code that does not generalise.** If the team believes it is "building a research tool," it will make research-specific implementation choices -- hardcoded deliverable types, research-specific event schemas, web-search-specific tool interfaces. These choices create technical debt the moment the next module arrives. Domain modules would need to fork or reimagine the same capabilities differently.

**Domain modules re-implement the same primitives.** Without a shared platform layer, each module team builds its own streaming system, its own document storage approach, its own citation mechanism, and its own billing integration. Five modules means five implementations of the same infrastructure, each with different bugs, different APIs, and different operational characteristics.

**No shared quality bar across modules.** If primitives are not abstracted, there is no single place to enforce provenance requirements, immutability guarantees, or audit completeness. Each module defines its own standard. Enterprise customers encounter inconsistent behaviour across modules.

**Each module team reinvents streaming, citations, and document management.** These are the hardest integration points. Getting SSE streaming right, getting citation binding correct, getting content-addressed storage reliable -- each of these is a multi-week engineering effort. Doing it once in the platform layer and proving it through research is dramatically cheaper than doing it separately in each domain module.

**The PRD vision becomes unreachable.** The Cognitive ERP is not five separate products. It is one platform with five domain modules. Without the shared platform layer, the "one platform" aspiration degrades into five loosely coupled tools that happen to share a login page. The strategic value -- cross-module intelligence, unified provenance, shared context -- evaporates.

---

## 9. Success Criteria for Platform Primitives

Each Layer 1 primitive should be evaluated by a single question:

> **Can a NEW domain module use this primitive WITHOUT modifying platform code?**

If yes, the primitive is properly abstracted. If a new domain module requires changes to the agentic runtime, GENUI renderer, MCP execution pipeline, document storage kernel, provenance system, context engine, LLM integration layer, streaming infrastructure, agent management framework, or billing metering -- the primitive is not yet a primitive. It is still a research-specific implementation that needs further abstraction.

Concretely, the Lease Critical Dates module should be buildable by:

1. Defining domain-specific agent graphs (using the existing LangGraph runtime and Send() pattern)
2. Registering domain-specific MCP tools (into the existing namespace and execution pipeline)
3. Defining domain-specific Pydantic schemas (for extraction results, confidence scores, event rules)
4. Adding domain-specific UI components (using existing GENUI rendering, SourcesPanel, RunTimeline)
5. Configuring domain-specific policy templates (selecting from existing exploratory/standard/regulated/audit_critical)
6. Emitting domain-specific RunEvents (into the existing streaming infrastructure)
7. Storing domain-specific artifacts (in the existing content-addressed kernel with domain-specific entity_types)

None of these steps should require modifying the platform primitives themselves. If they do, the primitive is incomplete and must be generalised before the domain module proceeds.

---

## Source References

| Reference ID | Document | Relevance |
|--------------|----------|-----------|
| PRD-ADR-DIGEST | `docs/analysis/PRD-ADR-VISION-DIGEST.md` | Product vision, domain modules, success metrics, constraints |
| DEC-REG | `docs/plans/DECISION-REGISTER.md` | All 47 locked decisions referenced in Section 6 |
| DEP-ANALYSIS | `docs/plans/DEPENDENCY-ANALYSIS.md` | Critical path, execution waves, dependency chains |
| BL | `docs/plans/BACKLOG.md` | 22 backlog items mapped to platform primitives |
| PLATFORM-GROUND-TRUTH | `docs/analysis/PLATFORM-GROUND-TRUTH.md` | Technical baseline -- what exists today in the dev platform |
| AGENTIC-SYSTEM | `docs/analysis/AGENTIC-SYSTEM.md` | Superagent orchestration analysis -- the reference implementation |

---

*This document is the authoritative strategic framing for all NYQST implementation work. When evaluating scope changes, feature cuts, or priority adjustments, consult the Primitive to Module Reuse Matrix (Section 3) and the success criteria (Section 9). The research module is the means; the platform primitives are the end. Every implementation decision should be evaluated against the question: "Does this build a reusable platform primitive, or does it build a research-specific feature?" If the latter, it must be refactored before it ships.*
