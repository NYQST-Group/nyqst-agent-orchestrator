# ADR-005: Agent Runtime and Framework Choice

**Status:** Proposed
**Date:** 2026-01-26
**Deciders:** Mark Forster, Engineering Team
**PRD Reference:** [06_ARCHITECTURE.md - Agent Framework](../prd/06_ARCHITECTURE.md), [03_PLATFORM.md - Long-Running Agent Patterns](../prd/03_PLATFORM.md)

---

## Context

NYQST needs an agent runtime that can execute multi-step, multi-agent workflows with the following requirements:

1. **Stateful execution**: Agents perform complex tasks (research, analysis, document processing) that span many steps and may take minutes to hours.
2. **Streaming**: The UI must show progress in real-time (partial outputs, tool call status, reasoning steps).
3. **Durable checkpointing**: Long-running agents must survive process restarts; state must be recoverable.
4. **Human-in-the-loop**: Agents must be able to pause, request approval, and resume after human input.
5. **Tool integration**: Agents call platform tools (substrate, index, knowledge) via MCP and internal APIs.
6. **Multi-agent coordination**: Complex workflows require orchestrator/worker patterns or parallel agent execution.
7. **Auditability**: Every agent action must be recorded in the platform run ledger (not just in the framework's internal state).

The codebase currently has:
- `src/intelli/agents/graphs/__init__.py` — empty placeholder for LangGraph state graphs
- `src/intelli/mcp/` — MCP server with substrate and run tools registered
- LangGraph 0.2.0+ in `pyproject.toml` dependencies
- Run ledger and event store fully implemented

The question: which framework(s) to adopt for the agent runtime, and how they relate to the platform kernel.

---

## Decision

Adopt **LangGraph as the primary agent orchestration runtime**, with clear boundaries between LangGraph's operational state and the platform's authoritative substrate.

### Architecture

```
┌──────────────────────────────────────────────────┐
│                  Platform Kernel                  │
│  (Substrate + Run Ledger + Index + Policies)     │
│  ════════════════════════════════════════════     │
│  Authoritative record: artifacts, manifests,      │
│  pointers, run events, audit trail                │
└──────────────────────┬───────────────────────────┘
                       │ writes to
                       │
┌──────────────────────▼───────────────────────────┐
│              LangGraph Runtime                    │
│  ─────────────────────────────────────────────    │
│  • StateGraph definitions (agent workflows)       │
│  • Checkpointing (Postgres/Redis checkpointer)    │
│  • Streaming (node-level + token-level)           │
│  • Human-in-the-loop (interrupt_before/after)     │
│  • Memory/Store (per-thread operational state)    │
│  ─────────────────────────────────────────────    │
│  Operational aid: resumability, workflow state     │
│  NOT the authoritative audit record               │
└──────────────────────┬───────────────────────────┘
                       │ calls
                       │
┌──────────────────────▼───────────────────────────┐
│              Tool Layer (MCP + Internal)          │
│  ─────────────────────────────────────────────    │
│  • Substrate tools (artifacts, manifests, ptrs)   │
│  • Run tools (log_step, checkpoint, complete)     │
│  • Index tools (search, ingest)                   │
│  • Knowledge tools (kb_query)                     │
│  • External tools (browser, scraper, APIs)        │
└──────────────────────────────────────────────────┘
```

### Design Boundary (Critical)

| Concern | Owner | Not |
|---------|-------|-----|
| Workflow state & resumability | LangGraph checkpoints | Platform substrate |
| Per-thread memory & context | LangGraph Store | Platform knowledge base |
| Authoritative audit trail | Platform run ledger | LangGraph traces |
| Immutable outputs | Platform artifacts/manifests | LangGraph node outputs |
| Search & retrieval | Platform Index Service | LangGraph memory |
| Access control & governance | Platform Policy Engine | LangGraph config |

LangGraph checkpoints and stores are **operational aids** — they enable resumability and thread-level memory. The platform's substrate (artifacts, manifests, run ledger) remains the canonical record for audit, reproducibility, and trust.

### Agent Definition Model

```python
AgentDefinition(
    id="research-deep-v1",
    version="1.0.0",
    graph="research_deep",           # LangGraph StateGraph name
    capabilities=["web_search", "document_parse", "substrate_write"],
    allowed_tools=["browser_search", "docling_parse", "create_manifest", "advance_pointer"],
    retrieval_profiles=["docs.default", "docs.citation_strict"],
    model_profile="gpt-4o",          # Bound via ModelProfile (see Reference Design §2.11)
    policy_template="standard",      # Levels of care
    max_steps=100,
    timeout_seconds=3600,
    checkpoint_backend="postgres",
)
```

### Agent Lifecycle

1. **Create Run** → Platform run ledger entry created
2. **Compile Graph** → LangGraph StateGraph compiled with config (tools, model, profile)
3. **Execute** → LangGraph streams execution; each significant step emits:
   - LangGraph checkpoint (operational, for resumability)
   - Platform run event (authoritative, for audit)
4. **Interrupt** → Human-in-the-loop via LangGraph `interrupt_before`/`interrupt_after`; platform records `human.approval.recorded` event
5. **Complete/Fail** → Run status updated in platform; output artifacts published to substrate

### Streaming Contract

LangGraph's streaming output is bridged to the Vercel AI SDK UI protocol:

```
LangGraph StreamEvents
       │
       ▼
  Stream Adapter
       │
       ├──► SSE (AI SDK UI protocol) → Frontend useChat
       │
       └──► Run Ledger Events → Platform audit
```

The adapter translates LangGraph node events to:
- AI SDK messages (for chat UI rendering)
- Run ledger events (for audit and replay)

---

## Options Considered

### Option 1: LangGraph Only (Selected)

**Description:** Use LangGraph as the sole orchestration runtime for all agent workflows.

**Pros:**
- Purpose-built for stateful, multi-step agent workflows
- Native checkpointing, streaming, human-in-the-loop
- Active development by LangChain team
- Python-native (matches backend stack)
- Supports both simple chains and complex multi-agent graphs
- Already in pyproject.toml dependencies

**Cons:**
- Tight coupling to LangChain ecosystem
- Learning curve for graph-based programming model
- May need custom extensions for NYQST-specific patterns

### Option 2: Vercel AI SDK (Backend)

**Description:** Use Vercel AI SDK on the backend (via Node.js) for agent execution.

**Pros:**
- Excellent streaming and UI integration
- Multi-provider support out of the box
- Strong TypeScript ecosystem

**Cons:**
- Requires Node.js runtime (current backend is Python/FastAPI)
- Limited multi-step workflow support compared to LangGraph
- Would need a separate process or sidecar for Python tools
- Checkpointing and human-in-the-loop are less mature

### Option 3: Custom Runtime

**Description:** Build a custom agent runtime on top of FastAPI + asyncio.

**Pros:**
- Full control over execution model
- No framework dependency
- Tight integration with platform kernel

**Cons:**
- Significant engineering effort to build checkpointing, streaming, interrupts
- Reimplements solved problems
- Maintenance burden of a custom framework

### Option 4: Hybrid (LangGraph + Vercel AI SDK)

**Description:** LangGraph for backend orchestration, Vercel AI SDK for frontend streaming.

**Pros:**
- Best of both: LangGraph's workflow power + AI SDK's frontend DX
- Clear backend/frontend boundary

**Cons:**
- Two frameworks to understand and maintain
- Integration layer needed between them
- Duplication of provider/model configuration

---

## Decision Rationale

Option 1 (LangGraph) was chosen as the **primary runtime** with Vercel AI SDK used **only on the frontend** (via `useChat` and the AI SDK UI stream protocol). This gives us:

1. **Single backend runtime**: All agent logic in Python/LangGraph, no Node.js sidecar.
2. **Proven patterns**: LangGraph's checkpointing, interrupts, and streaming solve hard problems we'd otherwise build ourselves.
3. **Clear boundary**: LangGraph handles workflow orchestration; platform kernel handles trust/audit/governance. These are explicitly separate.
4. **Incremental adoption**: Start with simple single-agent graphs; evolve to multi-agent patterns as complexity demands.
5. **Frontend decoupled**: The stream adapter bridges LangGraph events to AI SDK protocol, keeping the frontend framework-agnostic on the backend.

---

## Consequences

### Positive

- Battle-tested workflow execution with checkpointing and streaming
- Human-in-the-loop patterns available out of the box
- Multi-agent coordination supported (supervisor, parallel, hierarchical patterns)
- Python-native, matching existing backend stack
- Active community and rapid development

### Negative

- Dependency on LangChain ecosystem evolution
- LangGraph's graph model has a learning curve
- Need custom adapter layer to bridge to AI SDK UI protocol
- LangGraph internal state format may change across versions

### Risks

- **Risk:** LangGraph API instability (still pre-1.0)
  - **Mitigation:** Pin versions; isolate LangGraph behind agent service layer; abstract graph definitions so they can be ported
- **Risk:** Checkpoint storage grows unbounded
  - **Mitigation:** Implement TTL-based pruning for completed runs; archive checkpoints for long-term audit needs
- **Risk:** Confusion between LangGraph state and platform state
  - **Mitigation:** Document the boundary clearly (this ADR); enforce via code review that authoritative data always writes to platform substrate, not just LangGraph stores

---

## Implementation Notes

1. **Graph definitions** go in `src/intelli/agents/graphs/` — one module per workflow type (research, analysis, indexing, document processing).
2. **Checkpointer**: Use `langgraph-checkpoint-postgres` for durable checkpointing via the existing PostgreSQL instance. Separate checkpoint tables from platform kernel tables.
3. **Tool binding**: Use LangGraph's `ToolNode` with MCP-compatible tool wrappers. Tools call platform services (substrate, index, knowledge) and external APIs.
4. **Stream adapter**: Build `LangGraphToAISDKAdapter` that converts LangGraph `StreamEvents` to Vercel AI SDK Data Stream Protocol events. This lives in the API layer (`src/intelli/api/v1/streams.py`).
5. **Run ledger integration**: Each graph node emits platform run events via a callback handler that writes to the run ledger. This ensures audit completeness regardless of LangGraph's internal state.
6. **Agent registry**: Store `AgentDefinition` objects in the database, versioned. Graph compilation uses the definition to configure tools, models, and policies.

---

## Related ADRs

- [ADR-001: Data Model Strategy](./001-data-model-strategy.md) — Agents operate on domain-first models
- [ADR-002: Code Generation Strategy](./002-code-generation-strategy.md) — Agent tool schemas flow through code generation
- ADR-004: Index Service Architecture — Agents use Index Service for retrieval
- ADR-006: Session & Workspace Architecture — Sessions bind agents to compute contexts
- ADR-008: MCP Tool Architecture — Agents call tools via MCP
- ADR-009: Human-in-the-Loop & Governance — Interrupt and approval patterns

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [langgraph-checkpoint-postgres](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-postgres)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)
- [PLATFORM_REFERENCE_DESIGN.md §2.5 — Agents, Threads, Sessions](../PLATFORM_REFERENCE_DESIGN.md)
