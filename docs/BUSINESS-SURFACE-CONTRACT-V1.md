---
document_id: BUSINESS-SURFACE-CONTRACT-V1
version: 1
date: 2026-03-15
status: locked
phase: D2 contract
issue: "#7"
---

# Business Surface Contract v1

> Purpose: lock the thin D2 object model and planned API surface for dashboard, projects, clients, and decisions so the next packets can replace placeholders without inventing a second product or a mini-CRM.
>
> Runtime source of truth: `src/intelli/schemas/business.py`
>
> Spec grounding:
> - `YOLO1/docs/execution/intelli-studio-north-star-plan.md`
> - `YOLO1/docs/execution/decision-surface-spec.md`
> - `YOLO1/docs/execution/studio-north-star.md`

## 1. Scope

This contract defines four D2 objects:

| Object | Kind | Why it exists |
|---|---|---|
| `Project` | persisted business wrapper | buyer-visible work container over runs, bundles, and decisions |
| `Client` | persisted business wrapper | lightweight commercial context linked to projects |
| `Decision` | persisted buyer-facing judgment record | what was decided, why, and what evidence points at it |
| `DashboardSummary` | derived read model | one response that lets Overview stop being placeholder framing |

The contract is deliberately thin. It is not a CRM port, portfolio-management system, or compliance engine.

## 2. Locked model boundaries

### 2.1 `Project`

Minimum durable fields:

- `id`
- `name`
- `objective`
- `status`
- optional `client_id`
- `created_by`, `created_at`, `updated_at`

Minimum read-model slices allowed on project responses:

- optional `client`
- optional `primary_bundle`
- `last_activity_at`
- `active_run_count`
- `bundle_count`
- `research_pack_count`
- `decision_count`
- `stale_decision_count`
- optional `recent_decisions`

Rule: `Project` is the main business wrapper. It is where buyer-facing work gets organized. Do not add task trees, resource planning, or delivery workflows in D2.

### 2.2 `Client`

Minimum durable fields:

- `id`
- `name`
- optional `description`
- `status`
- `created_by`, `created_at`, `updated_at`

Minimum read-model slices allowed on client responses:

- `project_count`
- `active_project_count`
- `decision_count`
- `last_activity_at`
- optional `recent_projects`

Rule: `Client` is a lightweight wrapper over analysis work. Contacts, deals, pipeline stages, sync jobs, retention policy editors, and account hierarchy stay out of D2.

### 2.3 `Decision`

Minimum durable fields:

- `id`
- `project_id`
- `title`
- `decision`
- `rationale`
- `status`
- `citations`
- `linked_artifacts`
- `stale`
- optional `stale_reason`
- `created_by`, `created_at`, `updated_at`

Rules:

- `Decision` is project-scoped.
- `Decision` is buyer-facing.
- `citations` and `linked_artifacts` are thin reference lists in D2, not first-class evidence entities yet.
- stale/degradation is visible in the model now, but D4 owns richer invalidation behavior.

### 2.4 `DashboardSummary`

`DashboardSummary` is not a new persisted entity. It is a derived aggregate response.

It must be able to drive:

- top-line counts
- active runs
- workflow activity
- recent bundle changes
- recent research packs
- key projects
- recent decisions
- attention items

Rule: the dashboard summary is computed from existing run/session/pointer/notebook activity plus thin business records. Do not add a separate analytics subsystem for D2.

## 3. Planned endpoint registry

These routes are locked by contract but not implemented in this packet.

| Method | Path | Request body | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/v1/dashboard/summary` | — | `DashboardSummaryResponse` | derived aggregate only |
| `GET` | `/api/v1/projects` | — | `ProjectListResponse` | summary-friendly list |
| `POST` | `/api/v1/projects` | `ProjectCreate` | `ProjectResponse` | thin create only |
| `GET` | `/api/v1/projects/{project_id}` | — | `ProjectResponse` | may embed `recent_decisions` |
| `PATCH` | `/api/v1/projects/{project_id}` | `ProjectUpdate` | `ProjectResponse` | shallow edits only |
| `GET` | `/api/v1/clients` | — | `ClientListResponse` | summary-friendly list |
| `POST` | `/api/v1/clients` | `ClientCreate` | `ClientResponse` | thin create only |
| `GET` | `/api/v1/clients/{client_id}` | — | `ClientResponse` | may embed `recent_projects` |
| `PATCH` | `/api/v1/clients/{client_id}` | `ClientUpdate` | `ClientResponse` | shallow edits only |
| `GET` | `/api/v1/decisions` | — | `DecisionListResponse` | filterable by `project_id`, `status`, `stale` |
| `POST` | `/api/v1/decisions` | `DecisionCreate` | `DecisionResponse` | thin evidence refs only |
| `GET` | `/api/v1/decisions/{decision_id}` | — | `DecisionResponse` | buyer-facing detail |
| `PATCH` | `/api/v1/decisions/{decision_id}` | `DecisionUpdate` | `DecisionResponse` | shallow edits only |

Notes:

- list routes return list wrappers rather than raw arrays
- list wrappers carry `items`, `total`, `limit`, and `offset`
- detail routes may embed thin related-object slices instead of adding nested routes
- nested routes like `/projects/{id}/decisions` are optional, not required for MVP

## 4. Non-goals

Out of scope for this contract and the immediate follow-on packet:

- full CRM or PM port
- contact records, opportunities, pipeline stages, or account hierarchy
- deep workflow linkage, task trees, or enterprise portfolio management
- decision compliance workflows, approval orchestration, or evidence graph semantics
- fake dashboard cards with placeholder copy
- a second shell or imported local CRM product

## 5. Successor expectations

`#8` should implement persistence and real endpoints for `Project`, `Client`, and `DashboardSummary` using this exact shape unless the contract is deliberately revised.

`#9` should use this contract to replace Overview, Projects, Clients, and Decisions placeholders with real buyer-facing surfaces.

Decision evidence seriousness grows later:

- D2: thin references visible now
- D4: first-class citations, direct evidence opening, and richer stale/degradation behavior
