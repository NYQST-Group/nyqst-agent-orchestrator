# Issues index

This index groups issues by milestone. Use issues.json for machine import.

## M0 Baseline + P0 fixes
- **EPIC-PLATFORM** — Platform baseline, core primitives, and CI (epic)
- **STORY-PLAT-001** — Baseline dev scripts + validation harness (story)
- **STORY-PLAT-002** — CI: unit/integration/contract/live split + secrets discipline (story)
- **TASK-PLAT-P0-ARQ** — P0: Fix arq worker registration + Redis always-on (task)
- **TASK-PLAT-P0-EVENTSEQ** — P0: Fix RunEvent sequence_num race condition (task)
- **TASK-PLAT-P0-TENANTRUN** — P0: Add tenant_id to runs and propagate (task)

## M1 Contracts locked + UI shell
- **EPIC-CONTRACTS** — Contracts locked (events, apps, bundles, provenance) (epic)
- **EPIC-FE-SHELL** — Frontend shell (navigation, routes, base screens) (epic)
- **STORY-CON-001** — Contract governance: versioning rules + fixtures discipline (story)
- **STORY-CON-005** — Generate TS types from contracts + runtime dev assertions (story)
- **STORY-FE-001** — Implement app shell: routing + left nav + project selector (story)
- **STORY-FE-002** — Apps screens v1 (gallery + detail tabs) fixture-driven (story)
- **STORY-FE-003** — Runs screens v1 (list + run detail timeline) fixture-driven (story)
- **STORY-STREAM-001** — Streaming protocol alignment (NDJSON/SSE), heartbeat, reconnect (story)
- **TASK-CON-002** — Implement run_event schema + fixtures + validators (task)
- **TASK-CON-003** — Implement app + context_pack schemas + fixtures (task)
- **TASK-CON-004** — Implement bundle/version + evidence + insight schemas + fixtures (task)
- **TASK-FE-004** — Integrate mockups route (dev-only) and keep in sync with contracts (task)

## M2 Documents (bundles/versions/ingest/diff)
- **EPIC-DOCUMENTS** — Document management (bundles, versions, ingest, diff) (epic)
- **STORY-DOCS-001** — Backend: bundles + versions data model and migrations (story)
- **STORY-DOCS-002** — Backend: bundle upload API and artifact storage integration (story)
- **STORY-DOCS-003** — Pipeline: ingest runner (parse/normalize/chunk/index) with run logs (story)
- **STORY-DOCS-004** — Pipeline: extraction to structured JSON + evidence spans (story)
- **STORY-DOCS-005** — Diff engine: document diff + extraction diff + impact diff outputs (story)
- **STORY-DOCS-006** — Frontend: Documents screens (bundles list, detail, version compare) (story)

## M3 Studio (notebook + canvas)
- **EPIC-GENUI** — GenUI renderer (component registry, GML, charts) for dynamic outputs (epic)
- **EPIC-STUDIO** — Studio (notebook + infinite canvas) with provenance (epic)
- **STORY-GENUI-001** — GenUI component registry (primitives + composed patterns) (story)
- **STORY-GENUI-002** — GML/rehype pipeline: markdown+tags → React components (story)
- **STORY-GENUI-003** — Chart rendering support (Plotly or chosen lib) + theming (story)
- **STORY-STUDIO-001** — Notebook v1: pages, blocks, and citations (story)
- **STORY-STUDIO-002** — Canvas v1: pan/zoom, blocks, edges, inspector (story)
- **STORY-STUDIO-004** — Pinning: pin app outputs and diffs into canvas + notebook (story)
- **TASK-STUDIO-003** — Canvas persistence v1: save/load layout per project (task)

## M4 Evidence + insights + CRM
- **EPIC-CRM** — CRM entities, relationships, and timelines (epic)
- **EPIC-INTEL** — Evidence + insights + audit-first provenance (epic)
- **STORY-CRM-001** — Backend: CRM entities + relationships tables and API (story)
- **STORY-CRM-002** — Frontend: CRM list + entity detail + timeline + linked items (story)
- **STORY-ENTITY-001** — Entity & citation system (entities, citations, buffers, matching) (story)
- **STORY-INTEL-001** — Backend: evidence model + API + provenance enforcement (story)
- **STORY-INTEL-002** — Backend: insights lifecycle + linkage to evidence/CRM/models (story)
- **STORY-INTEL-003** — Review queue: low confidence and conflicts view + actions (story)
- **TASK-INTEL-004** — Stale propagation engine (doc change → evidence/insight/model stale) (task)

## M5 Apps + agents + context packs
- **EPIC-AGENTS** — Agents + skills + MCP tool system + evals (epic)
- **EPIC-APPS** — Apps system (Dify-style) + context packs + runs (epic)
- **EPIC-DELIVERABLES** — Deliverables pipeline (reports/websites) + co-generation + diff (epic)
- **EPIC-ORCH** — Orchestration & planning (PlanSet, LangGraph, subagents) (epic)
- **STORY-AGENT-001** — Backend: skill registry + permissions + versioning (story)
- **STORY-AGENT-002** — MCP integration: stdio tool runner + sandboxed HTTP (story)
- **STORY-AGENT-003** — Frontend: agent/skills management screens (story)
- **STORY-AGENT-004** — Evals harness: fixed fixtures + regression tests for core apps (story)
- **STORY-APPS-001** — Backend: apps + app_versions + app_runs data model and API (story)
- **STORY-APPS-002** — Frontend: App builder wizard (template → publish) (story)
- **STORY-APPS-003** — App runner v1: start run, stream events, persist outputs (story)
- **STORY-APPS-004** — Triggers v1: schedule + event trigger for apps (story)
- **STORY-DELIV-001** — Deliverable selection UI + artifact persistence (story)
- **STORY-DELIV-002** — Co-generation jobs (website + report) with pending entities flag (story)
- **STORY-ORCH-001** — PlanSet schemas + persistence (Plan, PlanTask linked ordering) (story)
- **STORY-ORCH-002** — LangGraph orchestrator for Research Notebook app (fan-out, structured output) (story)
- **STORY-ORCH-003** — Clarification flow (clarification_needed event → UI prompt → resume) (story)
- **STORY-ORCH-004** — Report preview streaming (delta + done semantics) (story)
- **TASK-APPS-005** — App diff UI: compare v1 vs v2 config (task)

## M6 Models + validation
- **EPIC-MODELS** — Models + validation + impact diffs (epic)
- **STORY-MODEL-001** — Backend: model registry + versioning + field definitions (story)
- **STORY-MODEL-002** — Frontend: model editor (schema + fields + requirements) (story)
- **STORY-MODEL-003** — Validation engine v1: rule evaluation + run logs (story)
- **TASK-MODEL-004** — Impact diff: explain model field changes from doc version diffs (task)

## M7 Dashboards + provenance
- **EPIC-DASH** — Dashboards with provenance drilldowns (epic)
- **STORY-DASH-001** — Backend: dashboards model + API (tiles, queries, provenance) (story)
- **STORY-DASH-002** — Frontend: dashboard builder and runtime + provenance panel (story)

## M8 Workflows + triggers
- **EPIC-WORKFLOWS** — Workflow builder + triggers + schedules (n8n-like) (epic)
- **STORY-WF-001** — Backend: workflow definitions + versioning + API (story)
- **STORY-WF-002** — Workflow runner: node execution + logs + retries (story)
- **STORY-WF-003** — Scheduler/triggers: schedule + event triggers for workflows (story)
- **STORY-WF-004** — Frontend: workflow builder UI (node canvas) + run logs (story)

## M9 Billing + quota
- **EPIC-BILLING** — Billing, subscriptions, usage and quota (epic)
- **STORY-BILL-001** — Billing tables migration (subscriptions, usage_records) (story)
- **STORY-BILL-002** — Usage recording on run completion (story)
- **STORY-BILL-003** — Quota middleware blocks over-limit runs (story)
- **STORY-BILL-004** — Stripe integration + webhook handler (test mode) (story)

## M10 Production hardening
- **EPIC-PROD** — Production hardening (deploy, security, observability, perf) (epic)
- **STORY-PROD-001** — Containerize API + worker (Dockerfiles, entrypoints) (story)
- **STORY-PROD-002** — Observability baseline: structured logs + metrics + traces (story)
- **STORY-PROD-003** — Security baseline: rate limits, payload size limits, SSRF protections (story)
- **STORY-PROD-004** — Backup/restore + retention policy runbook (story)
