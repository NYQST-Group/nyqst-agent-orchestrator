---
document_id: DEC-REG
version: 2
date: 2026-02-19
---

# Decision Register — Superagent Parity Project

This document captures all locked decisions, provisional choices, and open questions for the Superagent parity build on `nyqst-intelli-230126`. It is derived from analysis and planning documents completed during the reverse-engineering phase (2026-02-16).

---

## Part 1: References Index

| REF-ID | Path | Summary | Key Outputs |
|--------|------|---------|-------------|
| REF-001 | `docs/analysis/SYSTEM-ARCHITECTURE.md` | Full reverse-engineering of Superagent's frontend architecture, routes, API surface, streaming protocol, entity model, and agent orchestration inferred from JS bundles and network traffic. Covers confirmed vs. speculated with confidence levels. | 18 GML tags catalog; 22 streaming event types; REST endpoint map; entity type taxonomy (REPORT, SLIDES, WEBSITE, DOCUMENT, CODE); auth model (Ory Kratos + OIDC) |
| REF-002 | `docs/analysis/AGENTIC-SYSTEM.md` | Deep analysis of Superagent's orchestration mechanics — plan decomposition, parallel dispatch, task lifecycle state machine, fan-in aggregation, meta-reasoning, tool registry, and error propagation. Covers both confirmed evidence and inferred implementation patterns. | PlanSet/Plan/PlanTask linked-list model; fan-out Send() pattern; task states (QUEUED/PROCESSING/DONE/FAILED); meta-reasoning trigger; 12+ parallel subagent evidence |
| REF-003 | `docs/analysis/QUALITY-METHODS.md` | Analysis of what makes Superagent outputs high quality — structured output schemas, the GML tag system as prompt constraints, citation binding, the 7-stage healer/fixer pipeline for website generation, and Plotly/Lottie library choices. Separates artifact output quality from site UI engineering quality. | GML healer algorithm description; 7-stage website pipeline; report progress states; chart library list (Plotly, Recharts, Lottie, GSAP); citation quality patterns |
| REF-004 | `docs/analysis/PLATFORM-GROUND-TRUTH.md` | Authoritative ground-truth read of the actual `nyqst-intelli-230126` codebase, correcting false assumptions made by prior Kiro analysis. Documents all 16 tables, 11 API routers, 4 migrations, the real LangGraph implementation, and existing capabilities. | Corrected assumption list; 4-migration history (next is 0005); ResearchAssistantGraph implementation details; RunEventType complete enum; capability status table (what works today vs. what is missing) |
| REF-005 | `docs/analysis/CHAT-EXPORT-ANALYSIS.md` | Analysis of a captured Superagent chat export (run ID `5988fe2c`), revealing `deliverable_type` placement on user messages, `<answer>` XML wrapper format, co-generation pattern (WEBSITE + companion REPORT), async entity creation, and pricing model. | 9 actionable build items; Discovery 1–7 (co-generation, deliverable_type on user message, pricing, public URL patterns, UTM attribution, Ory Kratos auth, ephemeral plan sets); feature flags list |
| REF-006 | `docs/analysis/TECHNICAL-DEEP-DIVE.md` | Verbatim extraction of GML healer algorithm, all 10 chart Zod schemas, the complete 22-event streaming protocol Zod schemas, PlanSet data model, citation buffering state machine, and HSLA color palette. All sourced directly from minified JS bundles. | GML width constraint table; healer pseudocode; 10 chart type schemas (Python Pydantic equivalents); NDJSON envelope format; citation buffering state machine; HSLA palette (6 colors) |
| REF-007 | `docs/plans/PROJECT-BRIEF.md` | Master project brief defining what we are building, where all information is stored, architecture summary, locked user decisions, and key technical choices. Primary reference document for all agents entering the project. | v1 feature scope table; deferred features list; locked user decisions table; 6-phase delivery plan; cross-reference guide to all docs |
| REF-008 | `docs/plans/OBJECTIVES.md` | Defines 4 project objectives (OBJ-1 through OBJ-4), the three-layer analysis methodology (Product / Agents / Quality), agent dispatch protocol by tier (haiku/sonnet/opus), and revision cycle standards. | OBJ-1 through OBJ-4 with deliverables; three-layer decomposition framework; agent tier dispatch rules |
| REF-009 | `docs/plans/BACKLOG.md` | 22 backlog items (BL-001 through BL-022) with priorities, dependencies, and effort estimates. Includes a Tradeoffs Log capturing explicit architectural tradeoffs made during planning. | BL-001–BL-022 with dependency graph; Tradeoffs Log (6 entries); interaction point cross-references |
| REF-010 | `docs/plans/INTERACTION-POINTS.md` | Registry of all external services, internal services, data boundaries, user-facing boundaries, and explicitly NOT-replicating services. Includes rationale for each exclusion. | EXT-001–EXT-009 external services; INT-001–INT-005 internal services; DB-001–DB-007 data boundaries; 7-row "Not Replicating" table |
| REF-011 | `docs/plans/IMPLEMENTATION-PLAN.md` | Detailed week-by-week implementation plan across 4 phases (0–3 documented in full). Contains architectural decision table (AD-1 through AD-7), dependency graph, assumption validation table, and open questions requiring user input. | AD-1–AD-7 architectural decisions; phase-by-phase task lists with code stubs; assumption validation table (17 rows); 5 open questions |
| REF-012 | `docs/plans/2026-02-16-MAPPING-01-RESEARCH-ORCHESTRATOR.md` | Definitive mapping of Superagent's research orchestrator to the intelli LangGraph architecture. Grounds each Superagent behavior in real intelli code paths. | Planner node design; fan-out Send() mapping; fan-in aggregation; meta-reasoning node placement |
| REF-013 | `docs/plans/2026-02-16-MAPPING-02-DELIVERABLES-ARTIFACTS.md` | Definitive mapping of Superagent's 6 deliverable types (REPORT, SLIDES, WEBSITE, DOCUMENT, CODE, DATA) to intelli's Artifact/Manifest/Pointer content-addressed kernel. | Deliverable type → Artifact mapping; NYQST Markup AST node types (18); Manifest tree structure for website bundles |
| REF-014 | `docs/plans/2026-02-16-MAPPING-03-UI-MODULES.md` | Definitive mapping of Superagent's UI components to intelli's React frontend. Identifies 7 new components needed, components reusable as-is, and components explicitly NOT needed for v1. | New components list (PlanViewer, DeliverableSelector, ReportRenderer, WebsitePreview, SlidesPreview, Enhanced SourcesPanel, Enhanced RunTimeline); v1 exclusion table |
| REF-015 | `docs/plans/2026-02-16-MAPPING-04-BILLING-TESTING.md` | Definitive mapping of Superagent's billing model to intelli's data model, and the testing strategy (philosophy, test pyramid, contract/integration/E2E breakdown). Includes revised delivery phases grounded in actual codebase. | Stripe port plan from okestraai/DocuIntelli; test pyramid (contract/integration/E2E); CI strategy; revised phase checklist |

---

## Part 2: Decision Register

### 2A: Scope Decisions

| DEC-ID | Decision | Date | Rationale | Source | Status |
|--------|----------|------|-----------|--------|--------|
| DEC-001 | v1 includes: Research orchestrator, Report deliverable, Website deliverable, Slides deliverable, Document deliverable (PDF/DOCX), Billing & quotas, Document upload + RAG, Deliverable selector UI, Plan viewer + enhanced timeline UI | 2026-02-16 | User-approved scope covering core Superagent parity features for an internal tool | REF-007, REF-009 | Locked |
| DEC-002 | Deferred to v2: Scheduled tasks / automations, Content library / curated reports, Browser agent (Playwright automation), Public share system, Replay bar, Push notifications | 2026-02-16 | Reduces v1 complexity; these features are peripheral to core research+deliverable value | REF-007, REF-014 | Locked |
| DEC-003 | Meta-reasoning node (BL-017) is included in v1 despite 30–60s latency cost | 2026-02-16 | Quality improvement is dramatic; latency is acceptable for deep research workflows | REF-009 (Tradeoffs Log) | Locked |
| DEC-004 | Clarification flow: implement schema now (BL-002), defer full pause/resume UI to v1.5 | 2026-02-16 | Schema is needed regardless; AsyncPostgresSaver checkpoint is available for free; full UI is complex | REF-011 (AD-6) | Locked |
| DEC-005 | Feature flags to implement in v1: `websiteDeliverableEnabled`, `documentDeliverableEnabled`, `fileUploadEnabled`, `enhancedReportEnabled`, `multiSectionReportStreamingEnabled` | 2026-02-16 | Chat export confirmed Superagent uses these flags; deferred flags (`customReportTemplateUIEnabled`, `editableReportUIEnabled`, `tableOfContentsUIEnabled`) are out of scope | REF-005 | Locked |

### 2B: Architecture Decisions

| DEC-ID | Decision | Date | Rationale | Source | Status |
|--------|----------|------|-----------|--------|--------|
| DEC-010 | Architecture style: Pragmatic vertical (Superagent-style), not meta-architecture | 2026-02-16 | Internal tool; direct vertical slices are faster to build and easier to reason about | REF-007 | Locked |
| DEC-011 | Framework: React + Vite + FastAPI (not Next.js) | 2026-02-16 | Internal tool — no SSR, no social previews, no SEO requirement | REF-007 | Locked |
| DEC-012 | LangGraph: Extend `ResearchAssistantGraph` (do not replace or start fresh) | 2026-02-16 | Existing graph has 3 nodes, tool loop, and AsyncPostgresSaver; replacing would discard working code | REF-004, REF-011 | Locked |
| DEC-013 | Fan-out strategy: Dynamic `Send()` per plan task (not fixed N workers) | 2026-02-16 | Mirrors Superagent's numbered-task pattern; more flexible, scales with plan complexity | REF-011 (AD-7) | Locked |
| DEC-014 | Plan storage: Store plans as RunEvents (no new database tables for plans) | 2026-02-16 | Run ledger is already append-only with SSE; avoids schema proliferation | REF-007, REF-009 | Locked |
| DEC-015 | Markup format: JSON AST (NYQST Markup AST), not raw HTML tags. **Note: Split into DEC-015a (backend JSON AST) and DEC-015b (frontend rehype-to-JSX). See DEC-043.** | 2026-02-16 | Easier to validate, heal, render across targets, and export to different formats | REF-007 | Locked |
| DEC-015a | Backend: MarkupDocument JSON AST (Pydantic models) for report generation, storage, and transport between nodes. This is the structured data format for BL-004/BL-005. | 2026-02-19 | Backend nodes need a validated, serialisable intermediate representation for report sections. | REF-007, DEC-015 | Locked |
| DEC-015b | Frontend: rehype-to-JSX pipeline for GML rendering. Skip JSON AST intermediate layer on the frontend — parse GML HTML directly via unified/rehype stack. See DEC-043. | 2026-02-19 | Frontend does not need to reconstruct the AST; direct HTML-to-React rendering is simpler and faster. | DEC-015, DEC-043 | Locked |
| DEC-016 | Entity/citation model: Extend `Artifact` with `entity_type` field (no new entity table) | 2026-02-16 | Avoids schema proliferation; content-addressed kernel is already flexible enough | REF-009 (Tradeoffs Log BL-016) | Locked |
| DEC-017 | Async entity creation: Decoupled from main response stream via arq background worker | 2026-02-16 | Chat export confirmed Superagent does post-processing async; `has_async_entities_in_progress` flag required | REF-005, REF-004 | Locked |
| DEC-018 | SSE streaming: Extend existing `streams.py` (PG LISTEN/NOTIFY) — do not introduce new mechanism | 2026-02-16 | Existing production-ready SSE infrastructure; adding new mechanism would duplicate work | REF-004, REF-011 | Locked |
| DEC-019 | Next migration number is 0005 (four migrations already exist: 0001–0004) | 2026-02-16 | Corrects prior Kiro assumption that only 3 migrations existed | REF-004 | Locked |
| DEC-020 | Chat UI streaming: AI SDK Data Stream Protocol (not NDJSON) | 2026-02-16 | Already working in intelli with `@assistant-ui/react`; NDJSON is Superagent-specific, not needed | REF-014 | Locked |
| DEC-021 | Two parallel SSE streams: chat (AI SDK) + run events (platform PG LISTEN/NOTIFY SSE) | 2026-02-16 | Clean separation: chat content via AI SDK, run lifecycle events via existing platform SSE | REF-014 | Locked |
| DEC-022 | Response format: LLM output wrapped in `<answer>...</answer>` XML; deliverables referenced via `<gml-*>` web component tags inside the wrapper | 2026-02-16 | Chat export confirmed this exact format; system prompt must enforce it | REF-005 | Locked |
| DEC-023 | `deliverable_type` belongs on the user `Message` (not on the `Conversation`) | 2026-02-16 | Chat export confirmed: user messages carry the deliverable type; AI messages have null | REF-005 | Locked |
| DEC-024 | Co-generation: WEBSITE deliverable automatically generates a companion REPORT artifact | 2026-02-16 | Chat export confirmed both `gml-ViewWebsite` and `gml-ViewReport` appear in the same response | REF-005 | Locked |
| DEC-025 | Billing unit: 1 run = 1 AI generation message; reads are free; retries tracked via `retry_attempts` field without double-billing | 2026-02-16 | Confirmed from chat export pricing data ($20/mo = 200 runs, $0.50/run overage) | REF-005 | Locked |

### 2C: Technology Choices

| DEC-ID | Decision | Date | Rationale | Source | Status |
|--------|----------|------|-----------|--------|--------|
| DEC-030 | PDF export: Server-side with weasyprint (not client-side, not reportlab, not headless browser) | 2026-02-16 | More control; no browser dependency; consistent output; CSS-driven markdown→HTML→PDF pipeline | REF-009 (Tradeoffs Log BL-019), REF-011 (AD-4) | Locked |
| DEC-031 | Slides format: reveal.js HTML bundle (not JSON deck AST, not PPTX) | 2026-02-16 | Consistent with web artifact pattern; no new library; stores as Manifest of file Artifacts | REF-011 (AD-3) | Locked |
| DEC-032 | Web search: Brave Search API (not Tavily, not SerpAPI). **Superseded by DEC-046 (MCP-based search). Brave remains the default provider but is now hot-swappable.** | 2026-02-16 | Generous free tier; no JS rendering required; sufficient for research workloads | REF-011 (AD-1), REF-010 (EXT-001) | Locked |
| DEC-033 | Web scraping: Jina Reader API (not Firecrawl) | 2026-02-16 | Simpler API; cheaper; sufficient capability; avoids Firecrawl external dependency | REF-010 | Locked |
| DEC-034 | v0.app code generation: NOT replicating; use direct LLM code generation instead | 2026-02-16 | Avoids external dependency; more control over output format | REF-009 (Tradeoffs Log), REF-010 | Locked |
| DEC-035 | Website deploy target v1: iframe preview only (no Vercel/Cloudflare/S3 deployment in v1) | 2026-02-16 | Reduces v1 complexity; deploy infrastructure is a post-v1 concern | REF-011 (AD-5) | Locked |
| DEC-036 | Billing code: Port from `okestraai/DocuIntelli` (working Stripe integration exists) | 2026-02-16 | Avoids reimplementing Stripe from scratch; source repo is public | REF-007, REF-015 | Locked |
| DEC-037 | Analytics/observability: Use existing Langfuse (not PostHog) | 2026-02-16 | Langfuse already wired in intelli; no need for a second observability layer | REF-010 | Locked |
| DEC-038 | Auth: Use existing intelli auth (JWT + API keys) — NOT replicating Ory Kratos | 2026-02-16 | Intelli auth is already fully implemented; changing auth for an internal tool is unnecessary risk | REF-010 | Locked |
| DEC-039 | Financial/market data: Data connector pattern (user configures their own API keys/sources) — NOT replicating FactSet | 2026-02-16 | FactSet is proprietary and expensive; connector pattern is more flexible | REF-009 (Tradeoffs Log), REF-010 | Locked |
| DEC-040 | GML healer: Implement as Pydantic validator + AST repair logic in Python (port from JS healer algorithm) | 2026-02-16 | Direct port of confirmed verbatim healer logic from JS bundle; Pydantic equivalents fully designed | REF-006 | Locked |
| DEC-041 | Chat frontend: `@assistant-ui/react` for chat UI (actively migrated as of 2026-02-05 commit) | 2026-02-16 | Already in-progress migration; existing CitationAwareText, SourcesPanel, RunTimeline components reused | REF-014, REF-004 | Locked |
| DEC-042 | LiteLLM multi-provider hot-swap: Stay OpenAI-only for v1. Add LiteLLM as proxy layer for cost tracking via Langfuse callbacks. Do NOT add langchain-anthropic. base_url override supports proxy routing if needed. | 2026-02-19 | Cost tracking benefit is independent of which LLM providers are used. LiteLLM proxies all calls uniformly. | OQ-001, REF-024 | Locked |
| DEC-043 | GML renders in separate ReportPanel using rehype-to-JSX pipeline. GML content arrives via node_report_preview_done SSE event, stored in ReportStore Zustand slice, rendered outside @assistant-ui/react Thread. New npm deps: unified, rehype-parse, rehype-react. | 2026-02-19 | @assistant-ui/react Thread should not parse GML. Separate rendering path matches Superagent's architecture. | OQ-005, REF-023 | Locked |
| DEC-044 | Website deliverable: iframe-only for v1 demos. No unauthenticated /website/[id] route. | 2026-02-19 | Confirms DEC-035. Reduces v1 complexity. | OQ-003, REF-020 | Locked |
| DEC-045 | Observability: Langfuse self-hosted (MIT) + budget enforcement in LangGraph state. Token accumulator + conditional edge to END node. $2/run hard limit. LiteLLM auto-feeds cost data to Langfuse. Langfuse REST API for billing data export. NOT LangSmith (proprietary SaaS). | 2026-02-19 | Budget enforcement must be in-graph (no observability tool can halt a running graph). Langfuse is MIT-licensed, self-hosted, already wired. | OQ-004, REF-024 | Locked |
| DEC-046 | Web search via MCP protocol: hot-swap Brave/Tavily/future providers without code changes. Tools registered as MCP resources. Supersedes DEC-032 (which locked Brave specifically). | 2026-02-19 | MCP protocol abstraction means provider changes are config-only. Aligns with ADR-008 (MCP as THE tool protocol). | REF-010, REF-020 | Locked |
| DEC-047 | Clarification UI deferred to v1.5. v1 delivers: schema (BL-002 CLARIFICATION_NEEDED/RECEIVED events), backend pause/resume via AsyncPostgresSaver, text-only "This run needs your input" banner. No ClarificationPrompt.tsx rich UI in v1. | 2026-02-19 | Rich clarification UI is complex; schema + basic banner is sufficient for v1. | OQ-007, REF-020 | Locked |
| DEC-048 | Chart library: Plotly.js (via react-plotly.js). NOT Recharts. Neither is currently installed in the platform. Plotly chosen because Recharts cannot render candlestick charts needed for financial data (CRE, Debt MVP). Superagent also uses Plotly per REF-003. | 2026-02-19 | Financial domain requires candlestick/waterfall charts. Plotly supports all 10 GML chart schemas. Bundle size (~3MB) is acceptable for an enterprise internal tool. | REF-003, REF-017, REF-023 | Locked |
| DEC-049 | Graph development: LangSmith Studio (free tier) for LangGraph debugging. graph.get_graph().draw_mermaid() for zero-effort visualization. No visual graph editor — graph-as-code is the only viable approach (no OSS editor supports Send() fan-out). LangGraph Builder explicitly blocks parallel node execution. | 2026-02-19 | REF-025 confirms no viable visual editor. Hand-authored Python graph code with LangSmith Studio debug is the standard LangGraph workflow. | REF-025 | Locked |
| DEC-050 | LLM structured output: Use LangChain with_structured_output(PydanticModel) for all JSON-producing nodes (planner, synthesis, report sections, DataBrief). Free-form output only for website HTML generation. | 2026-02-19 | Without enforcement, LLMs produce invalid JSON 5-15% of the time. At 13 parallel subagents, probability of at least one failure per run is ~50-85%. | REF-020 (DG-3) | Locked |
| DEC-051 | DB sessions in parallel Send() nodes: each node creates new AsyncSession from shared async_sessionmaker, scoped to node function lifetime. expire_on_commit=False required. Do NOT share sessions across parallel nodes. | 2026-02-19 | SQLAlchemy AsyncSession is not thread-safe. Sharing across LangGraph Send() coroutines causes MissingGreenlet errors. | REF-020 (DG-5, AR-1), REF-017 (LIB-08) | Locked |
| DEC-052 | Migration 0005 split into 3 independent migrations: 0005a (artifact entity_type + tags columns), 0005b (message extensions — 7 new columns), 0005c (billing tables — subscriptions, usage_records). Each can land and be tested independently. | 2026-02-19 | Monolithic migration touching 3+ tables is high risk. Independent migrations prevent cross-track merge conflicts and allow independent validation. | REF-020 (DG-6, AR-3) | Locked |

### 2D: Testing Strategy

| DEC-ID | Decision | Date | Rationale | Source | Status |
|--------|----------|------|-----------|--------|--------|
| DEC-070 | Testing philosophy: Real LLM calls, minimal mocking; contract + integration + E2E pyramid | 2026-02-16 | Get to production looking good then refine; mocking LLMs produces false confidence | REF-007, REF-015 | Locked |
| DEC-071 | CI budget control: Use `max_tokens=2000` and fast models (haiku/gpt-4o-mini) for integration test LLM calls | 2026-02-16 | Prevents runaway CI costs while preserving real-LLM contract | REF-015 | Locked |
| DEC-072 | CI cadence: Contract tests on every push; integration tests on PR merge; E2E weekly or on release tags | 2026-02-16 | Balances coverage frequency against cost and speed | REF-015 | Locked |

### 2E: Not Replicating

| DEC-ID | Decision | Date | Rationale | Source | Status |
|--------|----------|------|-----------|--------|--------|
| DEC-060 | NOT replicating: v0.app (use direct LLM code gen) | 2026-02-16 | External dependency; direct LLM generation gives more control | REF-009, REF-010 | Locked |
| DEC-061 | NOT replicating: Firecrawl (use Jina Reader API) | 2026-02-16 | Simpler, cheaper, sufficient | REF-010 | Locked |
| DEC-062 | NOT replicating: FactSet (use data connector pattern) | 2026-02-16 | Proprietary, expensive; users bring their own data sources | REF-010 | Locked |
| DEC-063 | NOT replicating: Ory Kratos (use existing intelli auth) | 2026-02-16 | No need to change auth for an internal tool | REF-010 | Locked |
| DEC-064 | NOT replicating: PostHog (use existing Langfuse) | 2026-02-16 | Already have observability | REF-010 | Locked |
| DEC-065 | NOT replicating: Sanity CMS content library (defer to v2) | 2026-02-16 | Content library explicitly deferred to v2 | REF-010 | Locked |
| DEC-066 | NOT replicating: OneSignal push notifications (defer to v2) | 2026-02-16 | Desktop/internal tool — push notifications not needed | REF-010, REF-014 | Locked |
| DEC-067 | NOT replicating: OTEL trace viewer (use existing Langfuse) | 2026-02-16 | Langfuse provides equivalent observability | REF-014 | Locked |

---

## Part 3: Open Questions (All Resolved)

All open questions from the initial planning phase have been resolved as of 2026-02-19.

| OQ-ID | Question | Resolution | Resolved By |
|-------|----------|------------|-------------|
| OQ-001 | **LLM provider for orchestrator (AD-2)**: Add `langchain-anthropic` to use Claude 3.5 Sonnet for planner and meta-reasoning nodes, or stay OpenAI-only with gpt-4o? | **Resolved.** Stay OpenAI-only for v1. Add LiteLLM as proxy layer for cost tracking via Langfuse callbacks. Do NOT add langchain-anthropic. | DEC-042 |
| OQ-002 | **Slides viewer component**: Should `WebsitePreview.tsx` be reused for slides rendering, or does a dedicated `gml-ViewSlides` tag and component need to be defined? | **Resolved.** Reuse iframe approach for slides (per DEC-044 pattern). `gml-ViewPresentation` renders a link card in Phase 1/2. | DEC-044 pattern |
| OQ-003 | **Website public URL in v1 (AD-5)**: Is iframe-only preview sufficient for v1, or must `/website/[id]` as an unauthenticated route also land in v1? | **Resolved.** iframe-only for v1 demos. No unauthenticated `/website/[id]` route. Duplicate of DEC-035. | DEC-044 |
| OQ-004 | **LLM cost budget per research run**: What is the acceptable per-run cost ceiling? | **Resolved.** Langfuse self-hosted (MIT) + budget enforcement in LangGraph state. Token accumulator + conditional edge to END node. $2/run hard limit. | DEC-045 |
| OQ-005 | **`hydrated_content` rendering in ChatPanel**: Does `@assistant-ui/react` handle `<gml-*>` web components, or is a custom renderer needed? | **Resolved.** GML renders in separate ReportPanel using rehype-to-JSX pipeline, outside @assistant-ui/react Thread. | DEC-043 |
| OQ-006 | **Web search provider confirmation (AD-1)**: Brave Search confirmed, or still evaluating? | **Resolved.** Confirmed via MCP protocol abstraction — Brave is the default provider but is now hot-swappable. Duplicate of DEC-032/DEC-046. | DEC-046 |
| OQ-007 | **Clarification flow UI timing**: Should the full clarification UI be pulled forward into Phase 3? | **Resolved.** Deferred to v1.5. v1 delivers schema + basic "This run needs your input" banner only. | DEC-047 |

---

## Revision Log

| Date | Author | Change |
|------|--------|--------|
| 2026-02-18 | Agent (claude-sonnet-4-6) | Initial version created from analysis of REF-001 through REF-015 |
| 2026-02-19 | Agent (claude-opus-4-6) | v2: Added DEC-042–DEC-052 (technology choices). Split DEC-015 into DEC-015a/015b. Superseded DEC-032 with DEC-046. Renumbered testing decisions DEC-050/051/052 → DEC-070/071/072 to resolve ID collision. Resolved all 7 open questions (OQ-001–OQ-007). |
