# Platform Ground Truth — nyqst-intelli-230126 (Real Dev Copy)

**Surveyed:** 2026-02-18
**Source path:** `/Users/markforster/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126`
**Previous plan based on:** Kiro-Jan26Demo copy (now known to be wrong)

---

## 1. Executive Summary

Key differences from the Kiro copy assumptions:

- **LangGraph is NOT empty** — a fully implemented `ResearchAssistantGraph` exists in `src/intelli/agents/graphs/research_assistant.py`, using `StateGraph` with agent/tools/capture_sources nodes and a real tool-use loop.
- **FOUR migrations exist, not three** — migration `0004` adds `sessions`, `conversations`, `messages`, `message_feedback`, and `tags` tables (added 2026-02-01).
- **`APPROVAL_REQUESTED/GRANTED/DENIED` ARE present** in `RunEventType` — this assumption was CONFIRMED correct, not a gap.
- **No Anthropic SDK anywhere** — only `langchain-openai` is used; the LLM layer is fully OpenAI-compatible (supports custom base_url for routing). No `anthropic` or `langchain-anthropic` package.
- **Artifact model has NO `entity_type` or arbitrary `metadata` JSONB** — it is a pure content-addressed storage record (sha256 PK, media_type, size_bytes, storage_uri). Manifests carry a `tree` JSONB. Pointers carry a `metadata` JSONB column (aliased as `meta`).
- **Streaming is via PostgreSQL LISTEN/NOTIFY** (not polling) — `GET /api/v1/streams/runs/{run_id}` and `GET /api/v1/streams/activity` use raw `asyncpg` persistent connections.
- **Full auth system is in place** — JWT bearer + API key, tenant/user model, rate limiting, scopes.

---

## 2. Package Structure

```
nyqst-intelli-230126/
├── pyproject.toml
├── docker-compose.yml          # postgres(pgvector), minio, minio-init, redis
├── .env.example
├── alembic.ini
├── migrations/
│   └── versions/
│       ├── 20260123_0001_initial_substrate.py
│       ├── 20260123_0002_auth_tables.py
│       ├── 20260124_0003_rag_chunks.py
│       └── 20260201_0004_conversations_sessions_tags.py  ← NEW vs. Kiro
├── src/intelli/
│   ├── main.py
│   ├── config.py
│   ├── agents/
│   │   ├── adapters/
│   │   ├── graphs/
│   │   │   └── research_assistant.py   ← REAL GRAPH IMPLEMENTATION
│   │   ├── observability.py
│   │   └── tools/
│   │       └── research_tools.py
│   ├── api/
│   │   ├── health.py
│   │   ├── dependencies.py
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   ├── context.py
│   │   │   ├── correlation.py
│   │   │   └── error_handler.py
│   │   └── v1/
│   │       ├── __init__.py             ← registers all 11 routers
│   │       ├── agent.py
│   │       ├── artifacts.py
│   │       ├── auth.py
│   │       ├── conversations.py
│   │       ├── health.py
│   │       ├── manifests.py
│   │       ├── pointers.py
│   │       ├── rag.py
│   │       ├── runs.py
│   │       ├── sessions.py
│   │       ├── streams.py              ← SSE via PG LISTEN/NOTIFY
│   │       └── tags.py
│   ├── core/
│   │   ├── cache.py, clock.py, context.py, exceptions.py
│   │   ├── jobs.py, logging.py, pubsub.py
│   │   ├── security.py, session_monitor.py
│   ├── db/
│   │   ├── base.py, engine.py, checkpointer.py
│   │   └── models/
│   │       ├── auth.py          (Tenant, User, APIKey)
│   │       ├── conversations.py (Conversation, Message, MessageFeedback)
│   │       ├── rag.py           (RagChunk)
│   │       ├── runs.py          (Run, RunEvent, RunStatus, RunEventType)
│   │       ├── substrate.py     (Artifact, Manifest, Pointer, PointerHistory)
│   │       └── tags.py          (Tag, tagging join tables)
│   ├── mcp/
│   │   ├── server.py
│   │   └── tools/
│   │       ├── knowledge_tools.py
│   │       ├── run_tools.py
│   │       └── substrate_tools.py
│   ├── repositories/
│   │   ├── artifacts.py, base.py, conversations.py, manifests.py
│   │   ├── messages.py, pointers.py, runs.py, sessions.py, tags.py
│   ├── schemas/
│   │   ├── agent.py, conversations.py, rag.py, runs.py
│   │   ├── sessions.py, substrate.py, tags.py
│   ├── services/
│   │   ├── audit_service.py
│   │   ├── conversation_service.py
│   │   ├── session_service.py
│   │   ├── docir/, governance/
│   │   ├── indexing/
│   │   │   ├── auto_index.py, init.py
│   │   │   ├── opensearch_chunks.py, opensearch_client.py
│   │   ├── knowledge/
│   │   │   └── rag_service.py
│   │   ├── runs/
│   │   │   ├── ledger_service.py
│   │   │   └── run_service.py
│   │   └── substrate/
│   │       ├── artifact_service.py
│   │       └── manifest_service.py
│   └── storage/
│       ├── base.py, factory.py
│       ├── local_storage.py, s3_storage.py
└── ui/
    └── src/
        ├── api/           (auth.ts, client.ts, conversations.ts, sessions.ts, tags.ts, tour-feedback.ts)
        ├── components/
        │   ├── artifacts/     (ArtifactViewer.tsx)
        │   ├── auth/          (AuthGuard.tsx, LoginPage.tsx)
        │   ├── chat/          (ChatPanel.tsx, CitationAwareText.tsx, CitationLink.tsx,
        │   │                   SourcesPanel.tsx, SourcesSidebar.tsx, branch-indicator.tsx,
        │   │                   message-feedback.tsx, message-metadata.tsx, tool-uis.tsx)
        │   ├── manifests/     (ManifestViewer.tsx)
        │   ├── pointers/      (PointerViewer.tsx)
        │   ├── rag/           (NotebookPanel.tsx)
        │   ├── runs/          (RunTimeline.tsx, RunViewer.tsx)
        │   ├── ui/            (shadcn primitives: button, badge, dialog, tabs, toast, etc.)
        │   └── workbench/     (Workbench.tsx, WorkbenchHeader.tsx, DetailsPanel.tsx,
        │                       ExplorerPanel.tsx, MainPanel.tsx, TimelinePanel.tsx)
        ├── contexts/      (SourcesContext.tsx)
        ├── hooks/         (use-session-lifecycle.ts, use-sse.ts, use-thread-sources.ts, use-toast.ts)
        ├── pages/         (AnalysisPage, ClientsPage, DecisionsPage, NotebookPage,
        │                   OverviewPage, ProjectsPage, ResearchPage, ModulePlaceholder)
        ├── providers/     (assistant-runtime.tsx)
        ├── stores/        (auth-store.ts, conversation-store.ts, run-store.ts,
        │                   tour-store.ts, workbench-store.ts)
        └── types/         (api.ts)
```

---

## 3. LangGraph Status

**Status: IMPLEMENTED — one real graph exists.**

File: `/Users/markforster/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/src/intelli/agents/graphs/research_assistant.py`

### Graph Architecture

```
agent ──(tools_condition)──► tools ──► capture_sources ──► agent  (loop)
  │
  └──(END condition)──► END
```

### Key Implementation Details

```python
# State
@dataclass
class ResearchState:
    messages: Annotated[list[BaseMessage], add_messages]
    context_pointer_id: str | None = None
    manifest_sha256: str | None = None
    sources: list[dict] = field(default_factory=list)
    error: str | None = None
    run_id: UUID | None = None

# Graph construction (line 172)
graph = StateGraph(ResearchState)
graph.add_node("agent", self._agent_node)
graph.add_node("tools", ToolNode(self.tools))
graph.add_node("capture_sources", self._capture_sources_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
```

### LLM

- Uses `ChatOpenAI` (langchain-openai), NOT Anthropic.
- Supports OpenAI-compatible `base_url` override for model routing.
- Supports reasoning model effort param (o1/o3/o4-mini).
- Default model from config: `gpt-4o-mini`.

### Tools

- `build_research_tools(session)` from `src/intelli/agents/tools/research_tools.py`
- Tools: `search_documents`, `list_notebooks`, `get_document_info`, `compare_manifests`

### Fan-out (Send) Pattern

**No `Send(` pattern found** — parallel fan-out is not implemented. The graph is a single linear agent+tool loop.

### Checkpointer

`src/intelli/db/checkpointer.py` uses `AsyncPostgresSaver` from `langgraph-checkpoint-postgres`.

---

## 4. Database Models

### Tables Summary (from 4 migrations)

| Table | Migration | Notes |
|---|---|---|
| artifacts | 0001 | Content-addressed blobs |
| manifests | 0001 | Immutable tree snapshots |
| pointers | 0001 | Mutable HEAD references |
| pointer_history | 0001 | Audit trail for pointer moves |
| runs | 0001 | Execution instances |
| run_events | 0001 | Append-only ledger |
| tenants | 0002 | Auth: multi-tenant |
| users | 0002 | Auth: user accounts |
| api_keys | 0002 | Auth: programmatic access |
| rag_chunks | 0003 | Vector search chunks |
| sessions | 0004 | Scoped work context |
| conversations | 0004 | Chat conversation threads |
| messages | 0004 | Individual chat messages |
| message_feedback | 0004 | Thumbs up/down on messages |
| tags | 0004 | Taxonomy labels |
| (tag join tables) | 0004 | Many-to-many tagging |

**Total: ~16 tables**

### Artifact Model (Key Fields)

```python
class Artifact(Base, TimestampMixin):
    __tablename__ = "artifacts"
    sha256: str         # PK — SHA-256 of content (64 hex chars)
    media_type: str     # MIME type
    size_bytes: int     # BigInteger
    filename: str|None  # Original filename
    storage_uri: str    # e.g. "s3://bucket/key"
    storage_class: str  # STANDARD, GLACIER, etc.
    created_by: UUID|None
    reference_count: int
    # NO entity_type column
    # NO metadata JSONB column
```

### Manifest Model (Key Fields)

```python
class Manifest(Base, TimestampMixin):
    __tablename__ = "manifests"
    sha256: str          # PK — SHA-256 of canonical JSON
    tree: dict           # JSONB — the actual tree entries
    parent_sha256: str|None
    entry_count: int
    total_size_bytes: int
    created_by: UUID|None
    message: str|None    # Commit message
```

### Pointer Model (Key Fields)

```python
class Pointer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "pointers"
    id: UUID
    namespace: str       # default "default"
    name: str
    manifest_sha256: str|None   # FK → manifests
    pointer_type: str    # "bundle" | "corpus" | "snapshot"
    description: str|None
    meta: dict           # JSONB (DB column name: "metadata")
    created_by: UUID|None
```

### RunEventType Enum (Complete)

```python
class RunEventType(StrEnum):
    # Lifecycle
    RUN_STARTED, RUN_PAUSED, RUN_RESUMED, RUN_COMPLETED, RUN_FAILED, RUN_CANCELLED
    # Steps
    STEP_STARTED, STEP_COMPLETED
    # Tool calls
    TOOL_CALL_STARTED, TOOL_CALL_COMPLETED
    # LLM
    LLM_REQUEST, LLM_RESPONSE
    # Retrieval
    RETRIEVAL_QUERY, RETRIEVAL_RESULT
    # Artifacts
    ARTIFACT_EMITTED, MANIFEST_CREATED, POINTER_MOVED
    # State
    CHECKPOINT, STATE_UPDATE
    # Human interaction
    USER_INPUT, APPROVAL_REQUESTED, APPROVAL_GRANTED, APPROVAL_DENIED, COMMENT_ADDED
    # Errors
    ERROR, WARNING
```

### Run Model (Key Fields)

```python
class Run(Base, TimestampMixin):
    id: UUID
    run_type: str         # "document_parse" | "research" | "analysis" | etc.
    name: str|None
    status: str           # RunStatus enum
    started_at, completed_at: datetime|None
    input_manifest_sha256: str|None   # FK → manifests
    output_manifest_sha256: str|None  # FK → manifests
    config: dict          # JSONB
    result: dict|None     # JSONB
    error: dict|None      # JSONB
    token_usage: dict     # JSONB — cost tracking
    cost_cents: int
    created_by: UUID|None
    project_id: UUID|None
    session_id: UUID|None
    parent_run_id: UUID|None  # Self-referential FK for nested runs
```

---

## 5. API Routes

All routes are registered under `/api/v1` prefix.

### Health
- `GET /health/live`
- `GET /health/ready`
- `GET /health`

### Auth (`/api/v1/auth`)
- `POST /auth/login`
- `POST /auth/dev-bootstrap`
- `GET /auth/me`
- `GET /auth/keys`
- `POST /auth/keys`
- `DELETE /auth/keys/{key_id}`

### Agent (`/api/v1/agent`)
- `POST /agent/chat` — streaming chat endpoint (StreamingResponse)

### Artifacts (`/api/v1/artifacts`)
- `POST /artifacts` — upload (multipart)
- `GET /artifacts/{sha256}`
- `GET /artifacts/{sha256}/content` — StreamingResponse download
- `GET /artifacts/{sha256}/url` — presigned URL
- `GET /artifacts`
- `DELETE /artifacts/{sha256}`

### Manifests (`/api/v1/manifests`)
- `POST /manifests`
- `GET /manifests/{sha256}`
- `GET /manifests/{sha256}/entries`
- `GET /manifests/{sha256}/history`
- `GET /manifests/{old_sha256}/diff/{new_sha256}`
- `GET /manifests`

### Pointers (`/api/v1/pointers`)
- `POST /pointers`
- `GET /pointers/{namespace}/{name}`
- `GET /pointers/{namespace}/{name}/resolve`
- `PUT /pointers/{pointer_id}/advance`
- `PUT /pointers/{pointer_id}/reset`
- `GET /pointers/{pointer_id}/history`
- `DELETE /pointers/{pointer_id}`
- `GET /pointers`

### Runs (`/api/v1/runs`)
- `POST /runs`
- `GET /runs/{run_id}`
- `POST /runs/{run_id}/start`
- `POST /runs/{run_id}/pause`
- `POST /runs/{run_id}/resume`
- `POST /runs/{run_id}/complete`
- `POST /runs/{run_id}/fail`
- `POST /runs/{run_id}/cancel`
- `GET /runs`
- `POST /runs/{run_id}/events`
- `GET /runs/{run_id}/events`
- `GET /runs/{run_id}/checkpoint`

### Streams (`/api/v1/streams`) — SSE via PG LISTEN/NOTIFY
- `GET /streams/runs/{run_id}` — real-time run events (SSE)
- `GET /streams/activity` — global activity feed (SSE)

### Conversations (`/api/v1/conversations`)
- `POST /conversations`
- `GET /conversations`
- `GET /conversations/{conversation_id}`
- `PATCH /conversations/{conversation_id}`
- `DELETE /conversations/{conversation_id}`
- `GET /conversations/{conversation_id}/messages`
- `POST /conversations/{conversation_id}/messages` (at least 2 variants)
- `GET /conversations/{conversation_id}/...` (feedback endpoint)

### Sessions (`/api/v1/sessions`)
- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `PATCH /sessions/{session_id}`
- `GET /sessions/{session_id}/cost`

### RAG (`/api/v1/rag`)
- `POST /rag/index`
- `POST /rag/ask`

### Tags (`/api/v1/tags`)
- `POST /tags`
- `DELETE /tags/{tag_id}`
- `GET /tags`
- `GET /tags/search`

---

## 6. Frontend Structure

### Stores (Zustand)
- `auth-store.ts` — JWT/user state, persisted
- `conversation-store.ts` — conversation list, persisted
- `workbench-store.ts` — panel layout state, persisted
- `run-store.ts` — run events/status
- `tour-store.ts` — onboarding tour state

### Pages
- `OverviewPage`, `ResearchPage`, `NotebookPage`
- `AnalysisPage`, `DecisionsPage`, `ClientsPage`, `ProjectsPage`
- `ModulePlaceholder` (stub for deferred features)

### Key Components
- `Workbench.tsx` + panels (Explorer, Main, Details, Timeline)
- `ChatPanel.tsx` — uses `@assistant-ui/react-ui` Thread/Composer
- `CitationAwareText.tsx`, `CitationLink.tsx`, `SourcesPanel.tsx`, `SourcesSidebar.tsx`
- `RunTimeline.tsx`, `RunViewer.tsx`
- `ArtifactViewer.tsx`, `ManifestViewer.tsx`, `PointerViewer.tsx`
- `NotebookPanel.tsx`
- `LoginPage.tsx`, `AuthGuard.tsx`
- `tool-uis.tsx` — `makeAssistantToolUI` tool call visualizations
- `message-feedback.tsx` — thumbs up/down
- `branch-indicator.tsx` — conversation branching

### Key Libraries (UI)
- `@assistant-ui/react` ^0.12.3
- `@assistant-ui/react-ai-sdk` ^1.3.3
- `@assistant-ui/react-ui` ^0.2.1
- `@ai-sdk/react` ^3.0.59 (Vercel AI SDK React)
- `ai` ^6.0.57 (Vercel AI SDK core)
- `zustand` ^4.5.4
- `@tanstack/react-query` ^5.51.0
- `react-router-dom` ^6.24.1
- `react-resizable-panels` ^2.0.22
- `react-markdown` + `remark-gfm`

### Providers
- `assistant-runtime.tsx` — `useChatRuntime` from `@assistant-ui/react-ai-sdk`, wraps `AssistantRuntimeProvider`; maps internal message IDs to backend UUIDs; implements feedback adapter

### Hooks
- `use-sse.ts` — SSE connection hook
- `use-session-lifecycle.ts` — session mount/unmount
- `use-thread-sources.ts` — citation sources from `@assistant-ui/react` thread context

---

## 7. Existing Capabilities (What Works Today)

Based on code completeness:

| Capability | Status |
|---|---|
| Auth (JWT + API keys, multi-tenant) | Fully implemented |
| Artifact upload/download (S3/MinIO) | Fully implemented |
| Manifest creation/history/diff | Fully implemented |
| Pointer advance/reset/history | Fully implemented |
| RAG: indexing + asking | Fully implemented |
| Run lifecycle CRUD + events | Fully implemented |
| SSE streaming (PG LISTEN/NOTIFY) | Fully implemented |
| Research assistant LangGraph agent | Fully implemented (research loop) |
| Conversations/messages | Fully implemented |
| Sessions (scoped context) | Fully implemented |
| Tags | Fully implemented |
| MCP server (substrate + knowledge + run tools) | Implemented |
| Langfuse observability hook | Config wired, optional |
| OpenSearch indexing backend | Implemented |
| pgvector indexing backend | Implemented |

**Not yet in codebase (implementation gaps for Superagent parity):**
- Multi-step parallel workstreams (no `Send(` fan-out)
- Stripe/billing integration (no stripe dependency)
- Document upload → auto RAG pipeline via UI
- Progress/activity panel showing numbered subtasks
- Approval workflow UI (API events exist, UI does not)

---

## 8. Auth System

File: `/Users/markforster/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/src/intelli/api/middleware/auth.py`

**Dual-mode auth:**
1. `X-API-Key` header → hashed lookup in `api_keys` table
2. `Authorization: Bearer <JWT>` → `decode_access_token` + tenant/user DB lookup

**JWT:**
- `pyjwt>=2.9.0` — standard JWT, no third-party auth provider
- `SECRET_KEY` env var for signing
- `JWT_EXPIRY_HOURS` (default 24h)
- Payload contains `sub` (user_id), `tid` (tenant_id)

**Scopes:** `read`, `write`, `admin` (checked via `require_scope()` dependency)

**Rate limiting:** `RATE_LIMIT_RPM=60` (via `rate_limiter` in security.py)

**Models:** `Tenant`, `User`, `APIKey` in `src/intelli/db/models/auth.py`

**Dev bootstrap:** `POST /auth/dev-bootstrap` — creates dev tenant/user for local development

---

## 9. Infrastructure

### Docker Compose Services
```
postgres    pgvector/pgvector:pg16  — port 5433 (configurable via INTELLI_POSTGRES_PORT)
minio       minio/minio:latest      — ports 9000 (API), 9001 (console)
minio-init  minio/mc                — creates "intelli-artifacts" bucket
redis       redis:7-alpine          — port 6379 (for arq jobs / cache)
```

No OpenSearch in docker-compose (must be run separately or configured via env).

### No Dockerfile
No `Dockerfile` found in the repo root — dev workflow uses `uv` + docker-compose for infra.

### Config System
Pydantic-settings via `src/intelli/config.py`. All settings from env or `.env` file.

Key env vars:
```
DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY=
CHAT_MODEL=gpt-4o-mini
INDEX_BACKEND=opensearch | pgvector
OPENSEARCH_URL=http://localhost:9200
S3_ENDPOINT_URL=http://localhost:9000
SECRET_KEY=<random hex>
JWT_EXPIRY_HOURS=24
LANGFUSE_ENABLED=false
MCP_TRANSPORT=streamable-http
MCP_PORT=8001
```

### Background Jobs
`arq>=0.26.0` + `redis` wired but background job definitions in `src/intelli/core/jobs.py`.

---

## 10. Assumption Validation Table

| Previous Assumption (Kiro copy) | Status | Notes |
|---|---|---|
| "LangGraph is installed but completely empty" | **DIFFERENT** | A complete `ResearchAssistantGraph` exists with StateGraph, 3 nodes, tool loop, and AsyncPostgresSaver checkpointer |
| "No Anthropic SDK — only langchain-openai" | **CONFIRMED** | No anthropic or langchain-anthropic in pyproject.toml. Only `langchain-openai` is used. Config model defaults to `gpt-4o-mini`. |
| "Artifact model has no JSONB metadata or entity_type" | **CONFIRMED (partially different)** | Artifact has NO metadata JSONB and NO entity_type. However, Pointer DOES have a `meta` JSONB column, and Manifest has a `tree` JSONB. The missing field is specific to Artifact only — confirmed as accurate. |
| "Three migrations already exist (initial_substrate, auth_tables, rag_chunks)" | **DIFFERENT** | Four migrations exist. Migration `0004` (2026-02-01) added sessions, conversations, messages, message_feedback, tags. This is a significant addition. |
| "RunEventType already has APPROVAL_REQUESTED/GRANTED/DENIED" | **CONFIRMED** | All three human-interaction event types are present in both `db/models/runs.py` and `schemas/runs.py`. |

---

## 11. Impact on Implementation Plan

### What Changes Are Needed

**1. LangGraph is NOT a greenfield — extend the existing graph.**
The previous plan likely assumed we'd build the research graph from scratch. We must instead extend `ResearchAssistantGraph` to support:
- Parallel workstreams via `Send(` fan-out
- Multiple output deliverables
- Plan-first node before tool loop
Do NOT replace `research_assistant.py` — extend it.

**2. Migration 0004 tables are available for free.**
`sessions`, `conversations`, `messages`, `message_feedback`, `tags` are already migrated. Any plan to "add conversation support" should instead consume these existing tables. The next migration will be `0005`.

**3. Billing/Stripe is a clean addition.**
No stripe in pyproject.toml. The `cost_cents` and `token_usage` JSONB fields in Run are placeholders. Stripe integration starts from zero — no conflicts.

**4. `entity_type` on Artifact is still missing — plan to add it still stands.**
The Artifact model is purely a blob record. Adding `entity_type` (document, report, spreadsheet, etc.) will require a migration.

**5. The OpenAI-only constraint is real.**
All LLM calls go through `ChatOpenAI`. If the plan assumes Anthropic Claude for subagents, that needs either:
- Adding `langchain-anthropic` to pyproject.toml, OR
- Using an OpenAI-compatible proxy pointed at Claude's API via `openai_base_url`

**6. Approval workflow has backend events but no UI.**
`APPROVAL_REQUESTED/GRANTED/DENIED` events are already in the RunEventType enum and ledger schema. The UI side (ApprovalPanel, notification badges) is what needs building.

**7. SSE infrastructure is production-ready.**
The `streams` router uses PG LISTEN/NOTIFY — this is the correct pattern for the activity panel showing parallel subagent progress. Extend `streams.py`, don't replace it.

**8. Fan-out (parallel workstreams) is the primary missing LangGraph feature.**
`Send(` is absent. The Superagent-parity parallel workstream feature requires adding a supervisor/coordinator pattern on top of the existing research graph.

**9. No Dockerfile — containerization plan needs adjustment.**
The dev setup assumes uv + docker-compose for infra. If deployment requires a container image, a `Dockerfile` needs to be added.

**10. OpenSearch is the recommended index backend.**
The docker-compose does NOT include OpenSearch. The `.env.example` sets `INDEX_BACKEND=opensearch` but requires an external service. For local dev the plan should include an OpenSearch container or default to `pgvector`.
