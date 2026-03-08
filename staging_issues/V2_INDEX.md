# NYQST issues index (v2)

This folder is the v2 backlog aligned to the provided repo snapshot and Build Guide v5.
Older v1 issues are preserved in `../issues_legacy_v1/`.

## M0-P0

### Epics

- [EPIC-P0](EPIC-P0.md) — P0 repo stabilization and CI hardening

### Stories / tasks

- [P0-001](P0-001.md) — Fix arq WorkerSettings.functions dynamic registration bug
- [P0-002](P0-002.md) — Fix run_event sequence race under concurrent writers
- [P0-003](P0-003.md) — Add tenant_id to Run model and API filtering
- [P0-004](P0-004.md) — Make Redis always-on in dev compose (remove profile gating)
- [P0-005](P0-005.md) — Add GitHub Actions CI for backend + UI (lint, unit tests, minimal integration)

## M1-W0

### Epics

- [EPIC-W0](EPIC-W0.md) — Wave 0 — Orchestrated research harness (planner + fan-out) + run events

### Stories / tasks

- [BL-001](BL-001.md) — Extend ResearchAssistantGraph to planner → fan-out workers → synthesize (orchestrated research)
- [BL-001a](BL-001a.md) — Define orchestrator state, TaskResult, and DataBrief schemas (backend)
- [BL-001b](BL-001b.md) — Implement planner node with deterministic PlanTask IDs and minimal heuristics
- [BL-001c](BL-001c.md) — Implement worker execution using Send() fan-out and structured TaskResult returns
- [BL-001d](BL-001d.md) — Implement fan-in synth node to build DataBrief from TaskResults
- [BL-002](BL-002.md) — Extend RunEvent contract + UI typing for plan/report/citation events
- [BL-002a](BL-002a.md) — Add new RunEventType enum values + payload schemas (backend)
- [BL-002b](BL-002b.md) — Improve SSE stream reliability: resume by last sequence + backoff
- [BL-003](BL-003.md) — Add web research toolset (Brave/Tavily + Jina Reader) with provenance

## M10-REGSYGNAL

### Epics

- [EPIC-REGSYGNAL](EPIC-REGSYGNAL.md) — RegSygnal module (regulatory intelligence, reconciliation, alerts)

### Stories / tasks

- [REG-001](REG-001.md) — Regulatory source ingestion (web feeds, PDFs) into corpus with provenance
- [REG-002](REG-002.md) — Obligation extraction + mapping to internal controls framework
- [REG-003](REG-003.md) — RegSygnal UI: regulatory dashboard, diffs, tasks, and decision linking

## M11-PROPSYGNAL

### Epics

- [EPIC-PROPSYGNAL](EPIC-PROPSYGNAL.md) — PropSygnal module (commercial property signal aggregation and analytics)

### Stories / tasks

- [PROP-001](PROP-001.md) — Asset data model + CRUD (properties, portfolios, KPIs)
- [PROP-002](PROP-002.md) — Signal ingestion: news/market feeds + web research into asset context packs
- [PROP-003](PROP-003.md) — PropSygnal dashboards: KPIs, trends, and cited insights

## M2-W1

### Epics

- [EPIC-W1](EPIC-W1.md) — Wave 1 — GenUI + report rendering + planning UX (PlanViewer + ReportPanel)

### Stories / tasks

- [BL-004](BL-004.md) — Implement GenUI descriptor contracts + base component renderer
- [BL-004a](BL-004a.md) — Create zod schemas for GenUI descriptors + discriminated unions
- [BL-004b](BL-004b.md) — Implement GenUIRenderer + base component set
- [BL-005](BL-005.md) — Build ReportPanel: GML renderer + incremental healing + citation slots
- [BL-005a](BL-005a.md) — Define GML tag set + parsing rules (contract doc + tests)
- [BL-005b](BL-005b.md) — Implement incremental GML parser (client-side)
- [BL-005c](BL-005c.md) — Add backend report healer endpoint (LLM repair) with strict input/output contracts
- [BL-006](BL-006.md) — Stream report preview deltas during run (backend → UI)
- [BL-007](BL-007.md) — PlanSet persistence and API: store plan state and expose to UI
- [BL-007a](BL-007a.md) — Add PlanSet storage (runs.plan_set JSONB + migration) and repository helpers
- [BL-008](BL-008.md) — PlanViewer UI: render PlanSet with live task status updates
- [BL-009](BL-009.md) — Emit Plan events from graph (plan_created/task_updated) and map to UI
- [BL-010](BL-010.md) — Citation binding UI: allow user to bind report claims to evidence
- [BL-011](BL-011.md) — EntityService v0: store all tool outputs as artifacts with stable references

## M3-W2

### Epics

- [EPIC-W2](EPIC-W2.md) — Wave 2 — Deliverables pipelines (report, website, slides, document) + context

### Stories / tasks

- [BL-012](BL-012.md) — Planner prompt library + heuristics (quality improvements)
- [BL-013](BL-013.md) — Deepen Docs/Notebooks integration into research runs (selected notebook as context)
- [BL-014](BL-014.md) — Context management & inheritance (task → app → project → workspace) with background indexing
- [BL-015](BL-015.md) — DeliverableStore + per-message deliverable selection (report / website / slides / document)
- [BL-015a](BL-015a.md) — DB migration: add messages.deliverable_type + backfill from conversation.deliverable_type
- [BL-015b](BL-015b.md) — UI: add DeliverableSelector control and send deliverable_type via AI SDK transport
- [BL-016](BL-016.md) — Entity + citation substrate (DB + APIs) and provenance enforcement
- [BL-017](BL-017.md) — Meta-reasoning node: validate citations, detect low-confidence claims, suggest repairs
- [BL-018](BL-018.md) — Slides deliverable pipeline (Reveal-based) with citations and charts
- [BL-019](BL-019.md) — Document deliverable pipeline (DOCX/PDF) from report + citations
- [BL-019a](BL-019a.md) — Website deliverable pipeline (standalone Next.js or static site) generated from report
- [BL-014a](BL-014a.md) — DB model for ContextPacks + attachments to projects/apps/conversations
- [BL-014b](BL-014b.md) — Indexing jobs for context packs (background embeddings + OpenSearch index updates)
- [BL-014c](BL-014c.md) — Retrieval tools merge context pack results with precedence rules
- [BL-014d](BL-014d.md) — UI: Context manager (create packs, attach to project/app, view indexing status)
- [BL-016a](BL-016a.md) — DB migrations for entities + citations tables + indexes
- [BL-016b](BL-016b.md) — Entity/Citation API endpoints (create, bulk fetch, search) with RBAC
- [BL-016c](BL-016c.md) — UI components for citations (CitationPopover, CitationList, EvidenceViewer integration)
- [BL-016d](BL-016d.md) — Emit references_found and citations_bound events from tools and binder
- [BL-018a](BL-018a.md) — Define slides.json schema and export contract (with citations and assets)
- [BL-018b](BL-018b.md) — Implement Reveal deck renderer (slides.json → HTML) + asset bundling
- [BL-018c](BL-018c.md) — Wire slide generation into arq job and deliverable store
- [BL-019b](BL-019b.md) — Implement DOCX template + generator library (report → docx)
- [BL-019c](BL-019c.md) — Wire document generation into deliverable store and UI download links
- [RAG-001](RAG-001.md) — Hybrid retrieval (vector + keyword) + reranking + metadata filters
- [RAG-002](RAG-002.md) — Knowledge base UI: chunk preview, retrieval test console, and tuning controls

## M4-W3

### Epics

- [EPIC-W3](EPIC-W3.md) — Wave 3 — Polish, integration, and safety rails

### Stories / tasks

- [BL-020](BL-020.md) — Generation overlay UI: unified run progress, plan, citations, and artifacts
- [BL-021](BL-021.md) — Clarification flow (interactive): structured questions when intent/constraints missing
- [BL-022](BL-022.md) — Shared data brief: persist DataBrief and reuse across deliverables

## M5-PLUGINS

### Epics

- [EPIC-PLUGINS](EPIC-PLUGINS.md) — MCP tools, plugins, connectors, and skills registry

### Stories / tasks

- [PLUG-001](PLUG-001.md) — MCP tool registry + discovery service (list, describe, enable by scope)
- [PLUG-002](PLUG-002.md) — Implement MCP knowledge tools (documents, notebooks, web research) and wire into graphs
- [PLUG-003](PLUG-003.md) — Connector framework: credentials, OAuth flows, and ingestion sync jobs
- [PLUG-004](PLUG-004.md) — Plugin/Tools manager UI: list tools, configure connectors, enable per project/app
- [PLUG-005](PLUG-005.md) — Skills registry: package reusable subgraphs with metadata, permissions, and tests
- [PLUG-003a](PLUG-003a.md) — Secrets storage abstraction (encryption at rest + redaction)
- [PLUG-003b](PLUG-003b.md) — Generic OAuth flow endpoints + connector account linking
- [PLUG-003c](PLUG-003c.md) — Implement first production connector (Google Drive or SharePoint) + sync job

## M5-STUDIO

### Epics

- [EPIC-STUDIO](EPIC-STUDIO.md) — Studio surfaces: Projects, Clients/CRM, Decisions, Analysis canvas, Apps/Workflows

### Stories / tasks

- [STUDIO-001](STUDIO-001.md) — Projects: backend model + API + UI list/detail (replace placeholder ProjectsPage)
- [STUDIO-002](STUDIO-002.md) — Clients/CRM: backend model + API + UI list/detail (replace placeholder ClientsPage)
- [STUDIO-003](STUDIO-003.md) — Decisions register: decisions CRUD + citation binding to evidence
- [STUDIO-004](STUDIO-004.md) — Analysis canvas MVP: infinite canvas with persisted nodes and links
- [STUDIO-005](STUDIO-005.md) — Diff viewer: compare artifacts/versions and render semantic diffs
- [STUDIO-006](STUDIO-006.md) — Apps surface (Dify-like): save configured agent workflows and run them
- [STUDIO-007](STUDIO-007.md) — Workflow builder MVP (n8n-like): compose multi-step workflows from skills/tools
- [STUDIO-004a](STUDIO-004a.md) — Select canvas implementation (React Flow vs custom) and build base pan/zoom/drag interactions
- [STUDIO-004b](STUDIO-004b.md) — Canvas persistence API + optimistic sync
- [STUDIO-004c](STUDIO-004c.md) — Implement v1 node types (Note, Artifact, ReportSnippet, ChartPlaceholder, Decision)

## M6-ENTERPRISE

### Epics

- [EPIC-ENTERPRISE](EPIC-ENTERPRISE.md) — Enterprise baseline: SSO, RBAC, audit logs, billing/metering

### Stories / tasks

- [ENT-001](ENT-001.md) — OIDC SSO login flow + workspace membership mapping
- [ENT-002](ENT-002.md) — RBAC/ABAC policy engine enforced across APIs and UI
- [ENT-003](ENT-003.md) — Audit log: expand coverage (runs, docs, tool calls) + admin UI viewer
- [ENT-004](ENT-004.md) — Billing & metering: usage records per tenant (tokens, tools, storage) + Stripe integration
- [ENT-005](ENT-005.md) — Data retention, deletion, and export (GDPR baseline)

## M6-OBS

### Epics

- [EPIC-OBS](EPIC-OBS.md) — Observability, evals, and production readiness

### Stories / tasks

- [OBS-001](OBS-001.md) — Tracing integration (LangSmith + optional Langfuse/OTel) across graphs and tools
- [OBS-002](OBS-002.md) — Metrics + health endpoints (queue depth, latency, error rates, cost)
- [OBS-003](OBS-003.md) — Evals and regression suite wired into CI (golden prompts, output scoring)
- [OBS-004](OBS-004.md) — Load testing and streaming reliability tests (N concurrent runs)

## M7-DOCUINTELLI

### Epics

- [EPIC-DOCUINTELLI](EPIC-DOCUINTELLI.md) — DocuIntelli domain module (document intelligence and corpus analysis)

### Stories / tasks

- [DI-001](DI-001.md) — DocuIntelli foundation: document bundles, versions, and corpus metadata model
- [DI-002](DI-002.md) — DocuIntelli processing pipeline: DocIR extraction and normalized representations
- [BL-023](BL-023.md) — DocuIntelli: cross-framework reconciliation tool (compare/resolve multiple frameworks)
- [BL-024](BL-024.md) — DocuIntelli: mental model prompt library (templated reasoning patterns per framework)
- [BL-025](BL-025.md) — DocuIntelli: dimension discovery agent (derive new dimensions from corpus)
- [BL-026](BL-026.md) — DocuIntelli: pattern library + matcher (detect patterns/anomalies across corpus)
- [BL-027](BL-027.md) — DocuIntelli: process template engine (turn analysis into repeatable workflows)
- [BL-028](BL-028.md) — DocuIntelli: anomaly detection engine (rank gaps, contradictions, outliers)
- [BL-029](BL-029.md) — DocuIntelli: dimensional visualization engine (heatmaps, matrices, timelines) with GenUI
- [BL-030](BL-030.md) — DocuIntelli: corpus comparison agent (compare two corpora or versions)

## M8-LEASECD

### Epics

- [EPIC-LEASECD](EPIC-LEASECD.md) — Lease CD module (commercial property lease cashflow and covenant analysis)

### Stories / tasks

- [LEASECD-001](LEASECD-001.md) — Lease data model + CRUD (lease, parties, dates, rent schedule, options)
- [LEASECD-002](LEASECD-002.md) — Lease extraction skill: parse DocIR blocks into structured lease terms with citations
- [LEASECD-003](LEASECD-003.md) — Deterministic lease calculation engine (cashflows, indexation, scenarios)
- [LEASECD-004](LEASECD-004.md) — Lease CD UI: term review, scenario builder, export to deliverables

## M9-DEBT

### Epics

- [EPIC-DEBT](EPIC-DEBT.md) — Debt module (term sheets, amortization, covenant monitoring)

### Stories / tasks

- [DEBT-001](DEBT-001.md) — Debt instrument data model + CRUD (facilities, tranches, rates, covenants)
- [DEBT-002](DEBT-002.md) — Debt extraction skill: parse DocIR into structured debt terms with citations
- [DEBT-003](DEBT-003.md) — Deterministic debt calculation engine (amortization, interest, covenant ratios)
- [DEBT-004](DEBT-004.md) — Debt dashboards + alerts (exceptions, covenant breaches) with provenance

