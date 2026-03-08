# v4 new issues (generated)

This file converts v4 TODO deltas into explicit issue specs. If an equivalent issue already exists in your tracker, treat these as the canonical acceptance criteria and close as duplicate.

Total new issues in this pack: 45.

## EPIC-BILLING-USAGE

### V4-BILL-001: Billing Portal screen (missing screen #33)

Milestone: M3
Priority: P1
Dependencies: EPIC-BILLING-USAGE, EPIC-ENTERPRISE

UI for plan, usage, invoices and payment method management (embed Stripe portal if adopted).

Acceptance criteria:
- Shows current plan and limits
- Shows usage for current period
- Admin-only access


## EPIC-COLLABORATION

### V4-COLLAB-001: Project sharing model + UI (roles, invites)

Milestone: M3
Priority: P0
Dependencies: EPIC-ENTERPRISE

Enable multi-user access to a project with role-based permissions and invitation flows.

Acceptance criteria:
- Admin can invite users to project and assign role
- UI shows members and roles
- Permissions enforce read/write/execute actions

### V4-COLLAB-002: Comments on evidence and report blocks + @mentions

Milestone: M3
Priority: P1
Dependencies: V4-COLLAB-001, EPIC-NOTIFICATIONS, EPIC-EVIDENCE-INTELLIGENCE, EPIC-REPORT-PIPELINE

Implement commenting with @mentions on evidence items and report blocks; integrate with Notifications.

Acceptance criteria:
- Comments are tenant/project scoped
- Mentions trigger notifications with deep links
- Comment threads support resolve/unresolve

### V4-COLLAB-003: Assignments + due dates + task list

Milestone: M3
Priority: P1
Dependencies: V4-COLLAB-001, EPIC-NOTIFICATIONS

Create lightweight assignments (tasks) for review items, decisions, or signals, with due dates and statuses.

Acceptance criteria:
- Task list view with filters (owner, status, due)
- Due date reminders via Notifications
- Tasks link to target object and evidence

### V4-COLLAB-004: Activity feed (project timeline)

Milestone: M3
Priority: P2
Dependencies: V4-COLLAB-001, EPIC-ORCHESTRATION

Provide a project activity feed: uploads, runs, comments, assignments, exports.

Acceptance criteria:
- Feed is filterable
- Items deep-link to source objects


## EPIC-CONTRACTS / EPIC-PLATFORM-FOUNDATION

### V4-P0-006: Normalize and enforce `entity_type` naming (contracts + DB)

Milestone: M0
Priority: P0
Dependencies: EPIC-CONTRACTS, EPIC-PLATFORM-FOUNDATION

Define canonical `EntityType` enum in contracts and enforce it across API + DB. Backfill existing rows and reject unknown types at boundaries.

Acceptance criteria:
- EntityType enum exists in Pydantic + TS and is used everywhere
- DB constraints/indexes support entity_type queries
- Migration/backfill script normalizes legacy values
- Contract tests fail on unknown entity types


## EPIC-CRM

### V4-INTEG-005: Salesforce integration (integration #34, P1)

Milestone: M5
Priority: P1
Dependencies: EPIC-CRM, EPIC-TOOLS-CONNECTORS

Sync clients/deals and attach reports/decisions back to Salesforce records where permitted.

Acceptance criteria:
- OAuth connection and object mapping
- Basic bidirectional sync for selected fields


## EPIC-DOC-INGESTION

### V4-INTEG-007: Box / Google Drive connectors (integration #34, P1)

Milestone: M5
Priority: P1
Dependencies: EPIC-DOC-INGESTION, EPIC-TOOLS-CONNECTORS

Additional document ingestion connectors for Box and Google Drive.

Acceptance criteria:
- OAuth connections and incremental sync
- Metadata and folder mapping preserved


## EPIC-DOC-INGESTION / EPIC-TOOLS-CONNECTORS

### V4-INTEG-001: SharePoint / OneDrive connector (integration #34, P0)

Milestone: M2
Priority: P0
Dependencies: EPIC-TOOLS-CONNECTORS, EPIC-ENTERPRISE

Implement document ingestion from SharePoint/OneDrive via Microsoft Graph; preserve metadata and permissions mapping.

Acceptance criteria:
- User can connect SharePoint site/library with OAuth admin consent
- Docs ingest with folder paths, created/modified metadata
- Incremental sync supported


## EPIC-DOCS-DX

### V4-DX-001: Documentation pipeline: OpenAPI docs + admin/integration guides

Milestone: M2
Priority: P1
Dependencies: EPIC-CONTRACTS, V4-INFRA-001

Generate and publish API reference docs from OpenAPI plus curated guides for admins and integration developers.

Acceptance criteria:
- Docs build in CI and deploy to a docs site
- OpenAPI is discoverable and versioned
- At least 3 integration playbooks exist (SharePoint, Slack, Yardi/Argus)


## EPIC-ENTERPRISE

### V4-ENT-001: Tenant Admin Panel screen (missing screen #33)

Milestone: M3
Priority: P1
Dependencies: EPIC-ENTERPRISE, EPIC-INFRASTRUCTURE

Admin UI for tenant settings: allowed domains, retention defaults, connector allowlists, feature flags.

Acceptance criteria:
- Settings are tenant-scoped and audited
- Sensitive settings require admin role

### V4-ENT-002: Audit Log Viewer screen (missing screen #33)

Milestone: M3
Priority: P1
Dependencies: EPIC-ENTERPRISE

UI to search/filter/export audit logs.

Acceptance criteria:
- Search by actor, action, time range
- Export to CSV
- Audit events include run/export/key actions at minimum

### V4-ENT-003: API Key Management screen (missing screen #33)

Milestone: M0.5
Priority: P0
Dependencies: EPIC-ENTERPRISE

Create/revoke API keys for connectors and programmatic access; show last used and scoped permissions.

Acceptance criteria:
- Keys are stored securely (hashed at rest) and shown once
- Can revoke and rotate keys
- Audit events recorded for create/revoke

### V4-ENT-004: User Profile / Account Settings screen (missing screen #33)

Milestone: M0
Priority: P1
Dependencies: EPIC-FRONTEND-SHELL

Profile page for name/email/timezone plus links to notification preferences and API keys where allowed.

Acceptance criteria:
- User can update profile fields
- Timezone affects timestamps display

### V4-ENT-005: Team Management screen (missing screen #33)

Milestone: M0
Priority: P0
Dependencies: EPIC-ENTERPRISE, EPIC-FRONTEND-SHELL

Tenant-level team management: invite users, remove users, assign tenant roles, manage pending invites.

Acceptance criteria:
- Admin can invite user by email and assign role
- Pending invites view (resend/revoke)
- Remove/deactivate member
- All actions are audited


## EPIC-ENTERPRISE / EPIC-ORCHESTRATION

### V4-SEC-001: Fix SSE tenant isolation vulnerability (authorization on stream subscription)

Milestone: M0
Priority: P0
Dependencies: EPIC-ENTERPRISE, EPIC-ORCHESTRATION

Ensure run streaming endpoints cannot leak events across tenants. Validate run ownership, enforce tenant_id filters at query level, and add abuse logging.

Acceptance criteria:
- Stream subscription requires auth and checks run belongs to tenant
- DB query for events filters by tenant_id and run_id
- Automated test attempts cross-tenant subscription and fails
- Audit log records stream subscriptions (optional, Beta)


## EPIC-EXPORT

### V4-EX-001: Export engine foundation: template registry + versioning

Milestone: M0.5
Priority: P0
Dependencies: EPIC-CONTRACTS, EPIC-PLATFORM-FOUNDATION

Create a template registry for exports (Excel/PDF/DOCX/PPTX) with versioning and tenant overrides.

Acceptance criteria:
- Templates stored as artifacts with versioning
- Export job references template version explicitly
- Golden test harness supports template rendering tests

### V4-EX-002: Excel template mapping engine + golden-file tests

Milestone: M0.5
Priority: P0
Dependencies: V4-EX-001

Implement deterministic Excel generation using xlsx templates and a mapping layer; add golden-file regression tests.

Acceptance criteria:
- Engine fills templates from structured data model
- Outputs are stable across runs (except timestamps)
- Golden tests run in CI and detect formatting drift

### V4-EX-003: LeaseCD lender pack Excel template v1

Milestone: M0.5
Priority: P0
Dependencies: V4-EX-002, EPIC-LEASE-CD

Design and implement the initial lender pack Excel template for LeaseCD outputs.

Acceptance criteria:
- Template includes summary, cashflow schedule, assumptions, validation warnings
- All numbers trace back to extracted terms and deterministic calculations
- Export includes metadata and version stamp

### V4-EX-004: PDF export pipeline (WeasyPrint) with citations

Milestone: M2
Priority: P1
Dependencies: EPIC-REPORT-PIPELINE, V4-EX-001

Implement PDF export for report artifacts using HTML/CSS rendering; ensure citations are embedded and linkable where possible.

Acceptance criteria:
- PDF export job produces a PDF artifact and status events
- Citations appear as footnotes or inline references
- Works for long reports (pagination and TOC)

### V4-EX-005: Import Wizard screen (missing screen #33)

Milestone: M0.5
Priority: P1
Dependencies: EPIC-FRONTEND-SHELL, EPIC-CONTRACTS

Guide users through importing external spreadsheets/CSVs and mapping columns to schemas (esp. LeaseCD assumptions).

Acceptance criteria:
- Wizard uploads file, previews rows, maps to schema fields
- Validation errors are shown inline
- Imported data is stored as an artifact and linked to a run


## EPIC-FRONTEND-SHELL

### V4-FE-001: Frontend shell: layout + navigation + role-gated sections

Milestone: M0
Priority: P0
Dependencies: EPIC-DESIGN-SYSTEM, EPIC-ENTERPRISE

Implement the base UI shell: header, nav, routing, and role-gated visibility for major areas (Runs, Documents, Evidence, Exports, Admin).

Acceptance criteria:
- Shell loads within authenticated tenant context
- Navigation reflects RBAC roles
- Error/empty/loading states follow Design System patterns

### V4-FE-002: Frontend shell: project/workspace switcher + recents

Milestone: M0
Priority: P1
Dependencies: V4-FE-001

Add a project switcher with recents and search. Required for multi-project enterprise workflows.

Acceptance criteria:
- User can switch projects without hard refresh
- Recent projects list is persisted per user

### V4-FE-003: Runs list + run detail view with streaming panel

Milestone: M0
Priority: P0
Dependencies: EPIC-ORCHESTRATION, V4-P0-008

Provide run list, run detail page, and an integrated streaming progress panel (replaces separate Run Progress epic).

Acceptance criteria:
- Runs list shows status, timestamps, app/agent, owner
- Run detail streams events live and supports resume (cursor)
- User can cancel/stop a run if policy allows

### V4-FE-004: Artifact explorer: list/detail with provenance links

Milestone: M0.5
Priority: P1
Dependencies: EPIC-PLATFORM-FOUNDATION, EPIC-EVIDENCE-INTELLIGENCE

Implement artifact list and detail pages; show provenance (which run created it) and evidence links.

Acceptance criteria:
- Artifacts are tenant/project scoped
- Artifact detail links to run and evidence where available


## EPIC-INFRASTRUCTURE

### V4-INFRA-001: CI/CD pipeline + environment strategy

Milestone: M0
Priority: P0
Dependencies: EPIC-STANDARDS

Implement CI pipeline and establish dev/staging/prod environment configuration, including migrations and secrets handling.

Acceptance criteria:
- CI runs lint/unit/integration tests and blocks merges on failure
- Migrations run safely in staging/prod with rollback strategy
- Secrets are stored in a managed secret store or encrypted env

### V4-INFRA-002: Observability baseline: OTel traces + logs + LLM traces

Milestone: M0.5
Priority: P1
Dependencies: V4-INFRA-001

Add OpenTelemetry traces and structured logs; integrate LLM trace tooling (Langfuse/LangSmith) for run debugging.

Acceptance criteria:
- Traces link run_id across services
- Key dashboards exist (latency, error rate, queue depth)
- LLM traces can be inspected per run

### V4-INFRA-003: Backups + restore drills + DR runbook

Milestone: M3
Priority: P1
Dependencies: V4-INFRA-001

Implement automated backups, restore drills, and DR runbooks (RTO/RPO targets) for Enterprise Beta.

Acceptance criteria:
- Nightly backups verified
- Restore procedure documented and tested quarterly
- RTO/RPO targets agreed and tracked


## EPIC-INFRASTRUCTURE / EPIC-STANDARDS

### V4-SEC-002: Security scanning baseline: SAST/DAST/dependency scanning + SBOM

Milestone: M0.5
Priority: P1
Dependencies: V4-INFRA-001

Add security scanning and SBOM generation to CI; document remediation workflow and SLA.

Acceptance criteria:
- SAST and dependency scanning run in CI
- DAST baseline scan runs against staging
- SBOM generated for releases and stored


## EPIC-KNOWLEDGE-RETRIEVAL

### V4-FE-005: Global Search screen (missing screen #33)

Milestone: M2
Priority: P1
Dependencies: EPIC-KNOWLEDGE-RETRIEVAL, EPIC-FRONTEND-SHELL

Implement global search across documents, evidence, runs, and artifacts with filters.

Acceptance criteria:
- Search returns results across multiple entity types
- Filters by project and type
- Result links deep-link to the correct screen


## EPIC-NOTIFICATIONS

### V4-NOTIF-001: Select and integrate notifications provider (Novu default)

Milestone: M3
Priority: P0
Dependencies: EPIC-INFRASTRUCTURE, EPIC-ORCHESTRATION

Implement the chosen notifications provider integration (Novu) and establish event → notification trigger mapping.

Acceptance criteria:
- Provider deployment exists in staging (self-host) or approved SaaS
- Core event types mapped: run complete/fail, assignment, mention, breach
- Retries/backoff implemented for delivery failures

### V4-NOTIF-002: In-app notification center UI (bell + feed)

Milestone: M3
Priority: P1
Dependencies: V4-NOTIF-001, EPIC-FRONTEND-SHELL

Add in-app notification center UI and APIs to mark read/unread; integrate with provider inbox.

Acceptance criteria:
- Bell icon in shell shows unread count
- Feed supports read/unread and deep-links to target objects

### V4-NOTIF-003: Notification Preferences screen (missing screen #33)

Milestone: M3
Priority: P1
Dependencies: V4-NOTIF-001, EPIC-ENTERPRISE

Allow users to configure per-channel preferences and digests (email/in-app/webhooks).

Acceptance criteria:
- Preferences persisted per user
- Defaults are sensible and tenant-configurable
- Preferences enforced on event delivery

### V4-NOTIF-004: Outbound webhooks for Slack/Teams/PagerDuty (integration #34)

Milestone: M3
Priority: P1
Dependencies: V4-NOTIF-001

Implement outbound notifications to Slack/Teams/PagerDuty via webhooks and/or native APIs; include retry and rate limiting.

Acceptance criteria:
- Webhook destinations are configurable per tenant
- Delivery attempts are logged and retryable
- Can send run-complete and high-severity alert messages


## EPIC-NOTIFICATIONS / EPIC-WORKFLOWS

### V4-INTEG-008: Outlook/Exchange calendar integration (integration #34, P1)

Milestone: M4
Priority: P1
Dependencies: EPIC-NOTIFICATIONS, EPIC-WORKFLOWS

Integrate calendar deadlines (due dates for tasks, covenant deadlines) with Outlook/Exchange via Graph.

Acceptance criteria:
- Can create/update calendar events for assigned tasks (if permitted)
- Two-way sync strategy documented


## EPIC-ONBOARDING

### V4-ONB-001: First-run checklist (tenant + project)

Milestone: M0.5
Priority: P0
Dependencies: EPIC-FRONTEND-SHELL

Implement a guided checklist to reach first successful LeaseCD export: create project → upload docs → run → review → export.

Acceptance criteria:
- Checklist tracks completion state
- Links to correct UI pages
- Can be dismissed and revisited

### V4-ONB-002: Template Gallery screen (missing screen #33)

Milestone: M0.5
Priority: P0
Dependencies: EPIC-APPS, V4-EX-001

Create a Template Gallery for apps, workflows, and export templates; allow 'install into project'.

Acceptance criteria:
- Gallery lists templates with description and version
- Install creates project-local copies
- Templates are role-gated (admin-only install)

### V4-ONB-003: Sample project + sample lease docs package

Milestone: M0.5
Priority: P1
Dependencies: V4-ONB-001, EPIC-LEASE-CD

Provide a seed dataset for demos and training: sample project, sample lease docs, and expected outputs.

Acceptance criteria:
- One-click create sample project
- Sample run produces known outputs and exports


## EPIC-ORCHESTRATION

### V4-P0-007: Define MESSAGE_DELTA semantics and update streaming clients

Milestone: M0
Priority: P0
Dependencies: EPIC-CONTRACTS, EPIC-ORCHESTRATION

Remove ambiguity around MESSAGE_DELTA events: define whether they append/patch, how they reference message_id, and how clients reconstruct full messages deterministically.

Acceptance criteria:
- Contract defines MESSAGE_DELTA fields and deterministic replay rules
- Backend emits delta events that satisfy the contract
- Frontend reconstructs messages correctly from event stream replay
- Regression test replays recorded runs and matches expected transcript

### V4-P0-008: SSE resume/catch-up via cursor (Last-Event-ID) + NDJSON fallback

Milestone: M0
Priority: P0
Dependencies: EPIC-ORCHESTRATION, EPIC-PLATFORM-FOUNDATION

Implement streaming resume so UI can recover from disconnects without reruns. Support `Last-Event-ID` cursor and a bounded catch-up endpoint. Keep NDJSON download as fallback.

Acceptance criteria:
- SSE endpoint accepts cursor and resumes from correct event without cross-tenant leakage
- Catch-up endpoint returns events after cursor in correct order
- UI reconnect logic uses cursor and does not duplicate events
- Works for long runs and large event volumes (bounded paging)


## EPIC-PLATFORM-FOUNDATION

### V4-DATA-001: Trash / Recycle Bin (missing screen #33)

Milestone: M3
Priority: P2
Dependencies: EPIC-PLATFORM-FOUNDATION, EPIC-ENTERPRISE

Implement soft-delete and restore for documents/artifacts; enforce retention purge.

Acceptance criteria:
- User can restore deleted items within retention window
- Purge job deletes permanently and is audited


## EPIC-PROPSYGNAL

### V4-INTEG-006: CoStar Analytics integration spec (integration #34, P1)

Milestone: M6
Priority: P1
Dependencies: EPIC-PROPSYGNAL, EPIC-EXPORT

Define ingestion of market data from CoStar (likely via licensed export/feed) and map into Market KPI schema.

Acceptance criteria:
- Source licensing constraints documented
- Initial import pipeline from an export file


## EPIC-TOOLS-CONNECTORS

### V4-INTEG-004: MRI connector (integration #34, P1)

Milestone: M5
Priority: P1
Dependencies: EPIC-TOOLS-CONNECTORS

Define and implement an MRI integration approach (API or file-based).

Acceptance criteria:
- Documented mapping + initial ingestion POC


## EPIC-TOOLS-CONNECTORS / EPIC-LEASE-CD

### V4-INTEG-002: Argus Enterprise integration spec + file-based bridge (integration #34, P0)

Milestone: M4
Priority: P0
Dependencies: EPIC-EXPORT, EPIC-LEASE-CD

Define and implement the minimum Argus bridge (import/export) using file formats and templates; add API connector later if available.

Acceptance criteria:
- Documented Argus data mapping to LeaseCD and cashflow models
- Deterministic import/export via templates
- Round-trip test with fixture datasets


## EPIC-TOOLS-CONNECTORS / EPIC-PROPSYGNAL

### V4-INTEG-003: Yardi Voyager connector (integration #34, P0)

Milestone: M4
Priority: P0
Dependencies: EPIC-TOOLS-CONNECTORS, EPIC-PROPSYGNAL

Implement Yardi data ingestion (rent roll, lease data, collections, expenses) into normalized schemas for PropSygnal signals.

Acceptance criteria:
- Connector supports scheduled sync
- Data maps into KPI Observation schema
- Connector failures surface in admin UI

