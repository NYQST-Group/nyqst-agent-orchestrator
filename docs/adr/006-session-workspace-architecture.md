# ADR-006: Session and Workspace Architecture

**Status:** Proposed
**Date:** 2026-01-26
**Deciders:** Mark Forster, Engineering Team
**PRD Reference:** [06_ARCHITECTURE.md - Session/VM Architecture](../prd/06_ARCHITECTURE.md)

---

## Context

NYQST sessions bind a user + project/objective + compute context together. The platform needs a session architecture that supports:

1. **Stateful agent interaction**: Users converse with agents across multiple exchanges, with context preserved.
2. **Ephemeral compute, persistent outputs**: Sessions are disposable; results are published to the substrate (artifacts, manifests, pointers).
3. **Resource mounting**: Sessions have access to specific data assets (bundles, corpora, knowledge bases) based on project/objective context.
4. **Multi-module navigation**: A user may switch between Research, Analysis, and Document modules within a single work context.
5. **Return-to-topic**: Users must be able to resume previous work, seeing what was done, what artifacts were produced, and what the agent's state was.
6. **Concurrent sessions**: A user may have multiple active sessions (different projects/objectives).

The Reference Design (§2.5) specifies sessions as binding user + project/objective + compute realm, with mounts to substrate and ephemeral filesystem. Today, the codebase has:
- `session_id` field on `Run` model (UUID, nullable) — runs can be grouped by session
- Authentication via JWT (user identity established)
- No explicit `Session` database model or API endpoint
- Frontend has route-based "pages" (Research, Analysis, etc.) but no session persistence

The question: how should sessions be modeled, persisted, and used to scope agent work?

---

## Decision

Adopt a **lightweight session model** that binds user context to agent interactions without introducing VM/container orchestration in the foundation phase.

### Session Model

```python
Session(
    id: UUID,
    tenant_id: UUID,
    user_id: UUID,
    project_id: UUID | None,         # Scoping to a project (optional)
    objective: str | None,            # What the user is trying to accomplish
    module: str,                      # "research" | "analysis" | "document" | "modelling" | "knowledge" | "insight"
    status: SessionStatus,            # "active" | "paused" | "closed"

    # Context mounts
    mounted_pointers: list[UUID],     # Pointers (bundles/corpora) available to this session
    mounted_kbs: list[UUID],          # Knowledge bases available
    pinned_artifacts: list[str],      # Artifact SHA-256s pinned for reference

    # Agent state
    agent_definition_id: str | None,  # Which agent is bound (from agent registry)
    langgraph_thread_id: str | None,  # LangGraph thread for resumability

    # Workspace state (UI layout, not authoritative)
    workspace: dict | None,           # Saved layout, pinned resources, active panes

    # Lifecycle
    created_at: datetime,
    last_active_at: datetime,
    closed_at: datetime | None,
)
```

### Session Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Create   │───►│  Active   │───►│  Paused   │───►│  Closed   │
│           │    │           │◄───│           │    │           │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │
                     │ produces
                     ▼
              ┌──────────────┐
              │ Run Ledger    │  ← Authoritative record
              │ Artifacts     │
              │ Manifests     │
              │ Pointer moves │
              └──────────────┘
```

1. **Create**: User opens a module context (e.g., "Research for Project X"). Session created with mounted resources inherited from project defaults.
2. **Active**: User and agent interact. Each interaction creates a `Run` linked to the session. Outputs published to substrate.
3. **Paused**: User navigates away. Session state preserved (LangGraph thread + workspace layout). Can be resumed.
4. **Closed**: User explicitly ends the session or it expires (configurable TTL). Session metadata preserved for audit; LangGraph checkpoints eligible for pruning.

### Context Inheritance

Sessions inherit their initial context from the project/objective hierarchy:

```
Tenant (policies, quotas)
  └── Project (default pointers, KBs, model profile)
        └── Objective (task-specific mounts, constraints)
              └── Session (inherited + user-pinned resources)
```

Users can pin additional resources or remove inherited ones during a session.

### Session Scoping for Agents

When an agent executes within a session:
- **Mounted resources** define what the agent can access (pointers, KBs, artifacts)
- **Policy template** (from project or session) defines the level of care
- **Model profile** (from project or agent definition) defines which LLM to use
- **Tool permissions** (from agent definition + policy) define allowed operations

This prevents agents from accessing resources outside their session scope.

### Workspace State (UI-Only)

Workspace state (panel layout, active tabs, scroll positions) is stored on the session but is explicitly **not authoritative**. It exists solely for "return to topic" UX. The authoritative record is always the substrate (artifacts, manifests, run ledger).

---

## Options Considered

### Option 1: Lightweight Database Session (Selected)

**Description:** Model sessions as a database row with context mounts and agent state references. No VM/container orchestration.

**Pros:**
- Simple to implement (SQL model + API endpoints)
- Fast creation (no VM cold start)
- Fits current scale (single-server deployment)
- Session context is queryable (SQL joins to runs, artifacts)
- LangGraph handles agent state; session just holds references

**Cons:**
- No filesystem isolation between sessions
- No per-session compute resource limits
- Agent tools share the same process

### Option 2: Container-per-Session (VM Model)

**Description:** Each session gets an isolated container with an ephemeral filesystem, mounted resources, and dedicated agent process.

**Pros:**
- Strong isolation between sessions
- Per-session resource limits (CPU, memory)
- Ephemeral filesystem for scratch work
- Closer to the Reference Design's "session VM" concept

**Cons:**
- Significant infrastructure complexity (container orchestration)
- Cold start latency (seconds to minutes)
- Higher resource cost per session
- Premature for current scale and demo phase

### Option 3: Stateless Sessions (Frontend-Only)

**Description:** Sessions exist only in the browser (URL state + local storage). No server-side session model.

**Pros:**
- No backend changes needed
- Simple implementation

**Cons:**
- No "return to topic" across devices
- No server-side scoping for agent access control
- Run-to-session linkage lost
- Cannot enforce resource mounting policies

---

## Decision Rationale

Option 1 (Lightweight Database Session) was chosen because:

1. **Foundation phase appropriate**: Container orchestration is infrastructure that should be deferred until scale demands it. The Reference Design explicitly lists Temporal and container orchestration as "defer until trigger" items.
2. **Agent state handled by LangGraph**: LangGraph checkpointing already provides durable agent state. Sessions just need to reference the LangGraph thread, not replicate state management.
3. **Context scoping is critical now**: Even without VM isolation, sessions provide the scoping model (mounted resources, policy, model profile) that agents need to operate safely.
4. **Upgrade path clear**: When VM isolation is needed, the session model can be extended with `container_id`, `vm_status`, and orchestration metadata. The scoping/context model stays the same.
5. **Queryable**: Session-to-run-to-artifact relationships are queryable via SQL, enabling "show me everything from this session" views.

---

## Consequences

### Positive

- Sessions provide scoped context for agent operations
- "Return to topic" works across devices and browser sessions
- Run ledger entries linked to sessions enable audit trails
- Project-level defaults inherited automatically
- No cold start — session creation is a database insert

### Negative

- No filesystem isolation between concurrent sessions
- No per-session compute resource limits
- Workspace state is best-effort (not critical)
- Must manually manage session TTL and cleanup

### Risks

- **Risk:** Sessions accumulate and consume database space
  - **Mitigation:** Auto-close sessions after configurable inactivity period (default: 24h). Archive closed session metadata; prune LangGraph checkpoints for closed sessions.
- **Risk:** Agent accesses resources outside session scope
  - **Mitigation:** Tool layer checks session mounts before granting access. Policy Engine enforces at service boundary.
- **Risk:** Lightweight sessions insufficient for compute-intensive workloads
  - **Mitigation:** Monitor resource usage. When isolation is needed, add container orchestration as an optional session backend. The session model supports this extension without breaking the API.

---

## Implementation Notes

1. **Database model**: Add `Session` table to the substrate schema. Include foreign keys to `User`, `Tenant`, and optional `Project`.
2. **API endpoints**: `POST /api/v1/sessions` (create), `GET /api/v1/sessions/{id}` (get), `PATCH /api/v1/sessions/{id}` (update mounts/workspace), `POST /api/v1/sessions/{id}/close` (close).
3. **Run linking**: When creating a run within a session, set `run.session_id`. This is already supported in the `Run` model.
4. **LangGraph thread**: On first agent interaction, create a LangGraph thread and store the `thread_id` on the session. Subsequent interactions use the same thread for continuity.
5. **Frontend integration**: `SessionStore` (Zustand) mirrors the server session. On page load, fetch or create a session for the current module/project context. Workspace layout saves debounced to the session.
6. **Context injection**: When an agent starts, the session's mounted resources are injected into the LangGraph state as initial context. The agent's tools are scoped to these mounts.

---

## Related ADRs

- [ADR-001: Data Model Strategy](./001-data-model-strategy.md) — Sessions scope access to domain-first models
- ADR-005: Agent Runtime & Framework — LangGraph provides agent state within sessions
- ADR-008: MCP Tool Architecture — Tools are scoped by session context
- ADR-009: Human-in-the-Loop & Governance — Approval workflows operate within session context

---

## References

- [PLATFORM_REFERENCE_DESIGN.md §2.5 — Agents, Threads, Sessions](../PLATFORM_REFERENCE_DESIGN.md)
- [PLATFORM_REFERENCE_DESIGN.md §3 — Sessions and Module Boundaries](../PLATFORM_REFERENCE_DESIGN.md)
- [PLATFORM_FOUNDATION.md — F4: Orchestration Layer](../planning/PLATFORM_FOUNDATION.md)
