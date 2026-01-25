# Agent‑First Trusted Analysis Platform — Reference Design (Working Draft)

Date: 2026-01-24  
Status: Working draft for iteration (intended to preserve all key decisions discussed so far)

## 0) Intent (product outcome)

Build a commercial analysis platform where:
- Agents and users can ingest documents/data, run research + analysis workflows, and emit structured artifacts (tables/graphs/claims/citations).
- Stakeholders can **trust** outputs because work is visible, auditable, reproducible, and confidence‑qualified (“levels of care”).
- Everything is **searchable** and benefits from a shared **Index Service** (hybrid search + retrieval), without exposing proprietary indexing strategies.
- The system integrates with common business tools and can run SaaS or single‑tenant/local cloud.

The core design tension is “strong kernel / weak periphery”:
- Keep the backbone rigid around containers/sessions, provenance, runs, promotion, policy, and indexing contracts.
- Keep domain content (ontologies, models, schemas, skills) extensible and promotable.

## 1) Core principles

1. **Single source of truth**: immutable artifacts + manifests + run ledger. No module‑specific “truth”.
2. **Ephemeral compute, persistent outputs**: sessions/VMs/workbenches are disposable; outputs are published into substrate.
3. **Schema‑on‑read first, promote later**: accept discovered structures; promote stable structures with governance.
4. **Everything is inspectable**: agentic work is not “chat logs”; it is structured events + artifacts.
5. **Pointers not mutations**: reversion is moving pointers to older manifests (Git‑like), not rewriting history.
6. **Policy‑driven levels of care**: required provenance/tool permissions/gates vary by policy templates.
7. **Index is substrate**: no module owns indexing; modules select profiles, not strategies.

## 2) Kernel (backbone objects)

### 2.1 Tenancy / identity / access

- **Tenant**: org boundary (residency/billing/policies).
- **Principal**: user/service/agent identity.
- **AccessPolicy**: RBAC/ABAC rules scoped to project/corpus/kb/tool/connector; changes are audited.

### 2.2 Work context (commercial delivery)

Unit of delivery is what the user defines as the **Objective** (can be anything).

- **Project**: client engagement / internal initiative container.
- **Objective / Task**: coordination primitives linking runs, artifacts, claims, and decisions.
- **Workspace (UI)**: saved layout + pinned resources (not authoritative storage).

### 2.3 Artifact substrate (“filesystem semantics”)

**Artifact (immutable)**  
Any emitted file/object (pdf/json/parquet/md/html/png). Content‑addressed, deduplicated.

**Manifest (immutable)**  
An immutable tree of refs to artifacts (and optionally nested manifests) + metadata. A manifest is the unit of versioning.

**Pointer (mutable)**  
A HEAD reference to a manifest (bundle/corpus/etc.). Pointer moves are the only “mutation”.

Interpretation:
- **Bundle** = named pointer (working snapshot; publish/revert is moving pointer)
- **Corpus** = governed pointer (promotion + evaluation + approvals)
- **Snapshot** = point‑in‑time freeze

### 2.4 Runs + run ledger (reproducibility)

**Run** is an execution instance (agentic/deterministic/hybrid).  
**Run ledger** is an append‑only event stream for audit + replay:
- plans, tool calls, retrieval
- artifact/manifests produced
- pointer moves
- human approvals/comments

### 2.5 Agents, threads, and sessions

- **AgentDefinition (versioned)**: capabilities, allowed tools, retrieval profiles, policy template, prompt assets.
- **Thread**: chat‑like interaction + pinned context + attachments; used for collaboration but not treated as “truth”.
- **Session**: binds user + project/objective + compute realm; has mounts to substrate and ephemeral FS.

### 2.6 Knowledge bases (governed retrieval)

- **KnowledgeBase**: governed retrieval object built from one or more corpus/bundle versions.
- **RetrievalProfile**: profile configs like `legal-citations`, `fast-skim`, `strict-evidence`.

### 2.7 Evidence / claims / decisions (trust primitives)

- **EvidenceSpan**: anchored to DocIR/PDF offsets; supports citations and explainability.
- **Claim**: requirement/control/mapping/risk/interpretation/fact.
- **ClaimSupportLink**: claim ↔ evidence relationship.
- **Decision**: approvals, overrides, sign‑offs; attached to claims, promotions, gates.

### 2.8 Schema registry + promotion

- **SchemaRegistry**: JSON Schema / Zod / Protobuf, versioned with render hints.
- **Promotion pipeline**: discovered structure → schema proposal → reviewed schema → promoted typed dataset/model.

### 2.9 DataAssets (mounting + permissions)

Unify “things a session can use” as versioned, permissioned DataAssets:
- **Dataset** (files/tables)
- **Database** (relational)
- **Graph** (provenance/ontology)
- **Index snapshot** (KB)
- **ModelSpec** (schema/model)
- **SkillPack** (reusable prompts/toolchains/evals)

Rules:
- Projects/Objectives declare default DataAssets.
- Sessions inherit mounts from the objective/project plus explicit user pins.
- Agents are limited to mounted assets and their team/policy permissions.

### 2.10 Ontologies (industry knowledge)

Ontologies live in graph and relational stores for ontology elements, but are treated as governed assets:
- Ontology releases are versioned (artifact/manifest) and mounted as DataAssets.
- Retrieval uses Index Service profiles; deep traversal uses graph queries (or edge tables early).

## 3) Sessions and module boundaries

### 3.1 Research session (deep research VM/container)

Goal: run commodity tooling (browser automation/scrapers) plus agents that convert outputs into structured artifacts.

Boundary:
- Session has an ephemeral filesystem (SessionFS).
- SessionFS is not authoritative outside the session.
- To share outputs, you **Publish** into the artifact substrate:
  - upload artifacts (content‑addressed)
  - create a manifest (bundle snapshot)
  - move bundle pointer
  - emit run ledger events

### 3.2 Analysis session

Goal: take pinned inputs (bundles/corpora), run iterative extract/normalize/analyze loops, generate structured outputs + claims + citations.

Key properties:
- Analysis is pinned to specific manifest versions.
- Runs emit outputs linked to inputs (tight provenance).
- Diffs can trigger degradation hooks (re-index/re-evaluate/notify downstream).

### 3.3 Modelling workbench (Theia-like, optional)

Goal: structured modelling workflows (IR definition, validations, provenance, decision logging), optionally agent-assisted.

Approach:
- Theia is a UI host; data persists via artifact substrate.
- Virtual FS exposes project/bundle/corpus as read-only/check-out views.
- Saves create new artifacts + update pointers/manifests, never mutate history.

## 4) Index Service (substrate capability)

### 4.1 What “index” means (broad, not just embeddings)

Index Service is the shared “knowledge plane” that makes everything fast and discoverable:
- Primitive search: keyword/BM25
- Semantic search: dense embeddings
- Hybrid retrieval + reranking
- Faceting/filtering over metadata
- Trace search over runs/events/provenance
- (Later) graph/ontology retrieval and constrained reasoning

### 4.2 Contract (stable surface; swappable backend)

Modules and agents call the Index Service through a stable contract:

**Ingest**  
`ingest(target, profile)` where target is `manifest_sha256` or `pointer_id`.

**Search/Retrieve**  
`search(query, scope, profile)` returns references (doc ids + offsets + metadata), not “the truth”.

**Explain**  
`explain(result)` returns why a result matched (scores/features), for trust.

Backends can change (pgvector → OpenSearch/Qdrant/Vespa/etc.) without rewriting product logic, as long as the contract stays stable.

### 4.3 Profiles (IP boundary)

Users do not see chunking/reranking knobs. Modules choose **profiles** such as:
- `docs.default`
- `docs.citation_strict`
- `runs.trace_search`
- `projects.cross_project_reuse`

Profiles bind internal strategies (chunking/hybrid/rerankers) and policy constraints (e.g., strict evidence requirements).

### 4.4 Always‑on triggers (no “Index” button)

Indexing is automatic:
- Artifact upload → manifest created → pointer advanced → ingest scheduled
- Connector sync → new manifests → ingest scheduled
- Periodic jobs are used for health/compaction, not as the primary mechanism

### 4.5 Cursor-style pattern (privacy mode, later)

Cursor’s pattern is: incremental sync + server-side embeddings + client-side span reads at retrieval time.

The platform should support both:
- **Server‑authoritative (default demo)**: all docs are artifacts in object storage; retrieval loads spans server-side.
- **Privacy mode (optional later)**: vectors + metadata can be stored server-side, but plaintext is fetched “just in time” from a local connector that owns the bytes (path obfuscation + offset references).

### 4.6 Incremental indexing (Merkle + chunk-hash cache)

To make “always‑on indexing” cheap enough to be a default:
- Use **content hashes** as the primary change signal (artifact SHA-256 is already the substrate primitive).
- Maintain a **Merkle tree** (or equivalent hash DAG) over the checked-out inputs (e.g., pointer HEAD manifest tree) so the Index Service can detect deltas without reprocessing everything.
- Key embedding/cache artifacts by **chunk hash** so re-indexing after re-clones or pointer churn reuses prior compute.
- Treat the visible index as a **materialized view**: rebuildable from substrate + profiles, never the source of truth.

## 5) Run ledger: canonical logging for agentic work

### 5.1 Why this matters

- “Show me exactly what ran” requires step-level event logging.
- “Revert” requires pointer moves tied to events.
- “Audit” requires immutable inputs/outputs + tool versions + evidence.

### 5.2 Event categories (append-only stream)

Conversation and planning:
- `thread.message.created`
- `agent.plan.proposed` / `agent.plan.updated`
- `agent.action.proposed`
- `human.comment.added`
- `human.approval.recorded`

Tooling and retrieval:
- `tool.call.started` / `tool.call.completed` (args hash, tool version, output refs)
- `retrieval.query` / `retrieval.result` (kb/profile, top-k refs, scores)

Artifacts and manifests:
- `artifact.emitted`
- `manifest.created`
- `pointer.moved` (publish/promote/revert)

Diffs and gates:
- `diff.detected`
- `evaluation.started` / `evaluation.completed`
- `degradation.hook.triggered`

Session lifecycle:
- `session.started` / `session.closed`
- `run.checkpoint.created`
- `run.completed` / `run.failed`

### 5.3 “Thinking outputs” policy

Store “thinking” as:
- structured plan artifacts (steps, dependencies, expected outputs)
- intermediate reasoning artifacts only when policy allows

Avoid relying on raw internal reasoning logs for product behavior.

## 6) Document processing (tool swap boundary)

### 6.1 Canonical DocIR

Define a canonical intermediate representation (DocIR):
- pages
- blocks (headings, paragraphs, tables, figures)
- spans/offsets
- table model
- layout geometry (optional)
- provenance back to source bytes

Downstream modules depend on DocIR, not vendor formats.

### 6.2 Adapters

- Docling → DocIR
- Unstructured → DocIR
- LlamaParse → DocIR

## 7) Business-system integration (connectors)

### 7.1 Integration strategy options

Option A — minimal internal coordination layer (thin):
- Provide Projects/Objectives/Tasks, approvals, notifications, and audit inside the platform.
- Integrate outward to Slack/Monday/HubSpot etc. rather than replacing them.

Option B — embed a lightweight CRM/PM module (medium):
- Add Accounts/Contacts/Engagements, pipelines, and richer coordination.
- Higher build/maintenance burden; stronger “single pane” story.

### 7.2 Connector framework (table stakes)

Connector:
- provider (slack, hubspot, monday, jira, confluence, sharepoint…)
- auth (OIDC/OAuth), secret references
- scopes, rate-limit policy
- webhook subscriptions

ConnectorRun:
- sync job instances producing artifacts/manifests

Patterns:
- idempotent sync (event IDs, cursor-based paging)
- webhook + backfill (webhooks are not enough)
- permissions mapping (membership and access constraints)
- “linking UX”: tie an external task to a project objective/run/artifact

### 7.3 Canonical “work coordination” mapping

Minimal canonical object set external systems map into:
- Account/Client
- Engagement/Project
- Task/Ticket
- Message/Thread
- Document/Attachment
- Approval

## 8) Module UX (NotebookLM‑like entry)

### 8.1 Product shell

After login, users land on **Overview** and navigate modules from a sidebar:
- Research Intelligence
- Doc Intelligence
- Analysis Intelligence
- Decision Intelligence
- Client Intelligence
- Project Intelligence

Dev/diagnostic surfaces exist but are not the default entry point.

### 8.2 What each module is for (human explanation)

- **Doc Intelligence**: build trusted notebooks of sources; ask questions; produce cited outputs.
- **Research Intelligence**: gather sources from the outside world and publish bundles with provenance.
- **Analysis Intelligence**: repeatable workflows that emit structured outputs and claims.
- **Decision Intelligence**: confidence + recommendations + approvals + audit (levels of care).
- **Client Intelligence**: client context and deliverables linked back to evidence.
- **Project Intelligence**: objectives/tasks/deliverables and history of what changed.

## 9) Governance + promotion (later phases)

Corpus promotion requires:
- evaluation suites (tests)
- approval workflow (human gate)
- change record (decision + rationale)
- diffs + degradation hooks when inputs change

### 9.1 Models and database bridge (agent-to-DB)

Model artifacts:
- **ModelSpec** (artifact): entities/tables, fields, types, constraints, relationships, lineage to evidence.
- **DDL/ORM outputs** (artifacts): SQL migrations, ORM models.
- **ModelManifest** (manifest): pinned model + dependencies (schemas, corpora, runs).

DB query MCP tool (read-only by default):
- uses ModelSpec to generate/validate SQL
- enforces guardrails (row limits, timeouts, safe allowlist)
- logs queries/results to run ledger
- stores results as artifacts (parquet + preview)

### 9.2 Canonical business schema (CDM-like) + Mapping Specs

Practical approach:
- Seed a minimal canonical schema for coordination/CRM primitives.
- Onboard external providers via versioned **Mapping Specs** (transform + identity linking), not ad-hoc code paths.
- Promote mappings only after evaluation + human approval for governed environments.

## 10) Exchange / export (optional but useful)

**Exchange Package (XPKG)** supports:
- moving work between isolated environments/tenants
- offline review and regulated evidence packs
- client deliveries

Minimal contents:
- `package.json` (metadata)
- `manifests/`
- `artifacts/` (optional embed vs reference-only)
- `runs/` (run ledger extract)
- `schemas/`
- `provenance/` (optional materialized edges)
- `signatures/` (hashes + signing chain)

## 11) Insight system (learning loop without destabilizing)

Treat Insight as a consumer that reads:
- run ledger events
- artifacts/manifests
- evaluations and diffs

…and writes back governed outputs:
- Skill Packs (tools + prompts + retrieval profiles + evals + policy templates)
- ontology/graph updates for specific KBs
- process mining reports (defects, inefficiencies)

This keeps Insight powerful while preventing it from becoming a second orchestration system.

## 12) Bootstrap stack recommendation (min services, max shipping speed)

Core stateful services:
- Postgres (kernel metadata + run ledger + JSONB) + pgvector as fallback
- object storage (S3/MinIO) for artifacts
- OpenSearch (hybrid search; “real service” index backend)
- Redis optional for queues/caches (can start without if workloads are small)

What to defer (until a clear trigger):
- durable workflow engine (Temporal) until long-running/resumable runs matter
- dedicated search cluster tuning beyond OpenSearch defaults until scale forces it
- dedicated vector DB (Qdrant/Milvus) until vector throughput/ANN needs exceed current backend
- graph DB (e.g., Apache AGE/Neo4j) until ontology/provenance traversal becomes a first-class query surface
- Theia/IDE-grade modelling workbench until modelling UX truly needs it
- heavy connector/wiring platforms (NiFi) until integration volume forces it

Upgrade triggers (decision rules):
- add Temporal when runs need durable resume/retry across hours/days
- add dedicated vector DB when pgvector/OpenSearch limits are hit at scale
- add graph DB when provenance/ontology traversal is a first-class query surface

### 12.0 Demo-first posture (swap later)

For early demos, delete engineering work by using managed tools *behind platform contracts*:
- managed Postgres + object storage + auth (e.g., Supabase) as a temporary “infra delete” lever
- parsing: Docling first; add fallbacks for edge cases when needed
- connectors: Make/Zapier for demo wiring until native connectors are core value
- observability: Langfuse optional to accelerate iteration

Swap-out roadmap is trigger-based: replace components only when real constraints appear (cost, residency, throughput, enterprise isolation).

## 12.1 Practical delivery plan (iterative, integration-aware)

This is a suggested sequencing, not a date-bound plan:

- **Phase 0 — substrate + run trace**
  - artifacts + manifests + pointers
  - run ledger (event stream) + explorer UI
  - publish bundle manifests from sessions
- **Phase 1 — research + doc intelligence**
  - research session + publish
  - DocIR + document viewer + evidence spans
  - always-on indexing via Index Service profiles
- **Phase 2 — analysis + governance**
  - workflow-style analysis runs producing claims + evaluations
  - bundle→corpus promotion + gates + diffs + degradation hooks
  - KB indexing tied to corpus version + downstream dependency view
- **Phase 3 — integrations + admin hardening**
  - connector framework (Slack + one PM/CRM)
  - tenancy/admin/quotas/retention/export

## 13) Current repo reality (what exists today)

Today’s demo stack expresses the kernel shape:
- Artifacts (content-addressed) + manifests + pointers
- Run ledger events + streaming
- Doc conversion via Docling for text extraction
- Always‑on indexing triggered on pointer advance (no UI index button)
- Index backend selectable:
  - `INDEX_BACKEND=opensearch` uses OpenSearch for hybrid chunk retrieval
  - pgvector remains as a fallback path

Additional repo-observed capabilities (already implemented):
- **Real-time delivery**: SSE endpoints stream updates using Postgres LISTEN/NOTIFY channels (`run_events`, `pointer_changes`, `activity`).
- **Auth + tenancy primitives**: Tenants/Users/API keys + JWT auth exist; “demo login” is `POST /api/v1/auth/dev-bootstrap` (requires `DEBUG=true`).
- **Storage backends**: S3-compatible object storage is the default (MinIO in dev); a local filesystem backend exists for simple setups.
- **UI**: the demo UI that `scripts/dev/run.sh` starts is the Vite app in `ui/` (module sidebar + `/overview` landing). A second root-level UI/package exists (component/storybook-style) but is not part of the validated dev startup flow.
- **MCP server**: an MCP server exists. Substrate tools are implemented; run tool definitions exist but need wiring/transaction commit for “real” agent usage; knowledge tools are currently a stub (Phase 2).
- **Optional Redis layer**: Redis-based caching/rate limiting and ARQ job queue exist with graceful fallbacks when Redis is not configured.
- **Schemas folder**: JSON schemas exist for `document`, `event`, and `claim` as early registry material; there are also early CRE configs (e.g., lease events) showing how domain schemas enter the system.

HTTP surface that exists today (v1):
- `/api/v1/auth` (login, dev-bootstrap, api keys)
- `/api/v1/artifacts` (upload + read + pre-signed URL)
- `/api/v1/manifests` (create/read/diff/history)
- `/api/v1/pointers` (create/read/advance/history)
- `/api/v1/runs` (create/start/complete/events)
- `/api/v1/rag` (index/ask)
- `/api/v1/streams` (SSE)
- `/health/*` (liveness/readiness)

See also:
- `docs/INDEX_CONTRACT.md`

## Appendix A — Minimal MCP tool surface (agents)

Current substrate tools (implemented):
- `list_pointers` / `resolve_pointer`
- `checkout_manifest` / `get_manifest_history` / `diff_manifests`
- `create_pointer` / `advance_pointer`
- `create_manifest`
- `get_artifact_info` / `get_artifact_url`

Run tools (defined, not yet fully wired for MCP usage):
- `create_run` / `start_run` / `complete_run` / `fail_run`
- `get_run` / `list_runs`
- `log_step` / `log_tool_call` / `checkpoint`
- `get_latest_checkpoint` / `get_run_events`

Knowledge and indexing (stub today; Phase 2):
- `kb_query`
- (planned) `kb_create` / `kb_index_build` (index snapshot manifests + governed retrieval profiles)

Claims and provenance (planned; Phase 2+):
- `create_claim` / `link_evidence` / `decide`

## Appendix B — Minimal HTTP API surface (GUI)

Current v1 (implemented):
- `/api/v1/auth`
- `/api/v1/artifacts`
- `/api/v1/manifests`
- `/api/v1/pointers`
- `/api/v1/runs`
- `/api/v1/rag`
- `/api/v1/streams`
- `/health/*`

Target (later phases):
- `/api/v1/sessions` (create, mount, publish)
- `/api/v1/index` or `/api/v1/kb` (ingest, query, eval)
- `/api/v1/models` (propose, diff, promote)
- `/api/v1/connectors` (providers, auth, sync, webhooks)
- `/api/v1/admin` (users, roles, policies, quotas)

## Appendix C — UI surface map (workbench)

Addressable resources (URI-like):
- `project://`, `bundle://`, `corpus://`, `run://`, `artifact://`, `claim://`, `kb://`

Core panes:
- Chat/Thread
- Planner (plan artifact + comments)
- Run Explorer (timeline + DAG + tool calls)
- Artifact Browser (search/facet by type/schema/project/run)
- Viewers: Document (DocIR + highlights), Table, Graph, Diff
- Context Pinboard (pinned corpora/bundles/artifacts/claims)
- Evaluations (gates/metrics)
- Provenance (“why/how”: evidence links)
