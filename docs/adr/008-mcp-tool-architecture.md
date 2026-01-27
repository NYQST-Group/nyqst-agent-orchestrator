# ADR-008: MCP Tool Architecture

**Status:** Proposed
**Date:** 2026-01-26
**Deciders:** Mark Forster, Engineering Team
**PRD Reference:** [06_ARCHITECTURE.md - MCP Architecture](../prd/06_ARCHITECTURE.md), [03_PLATFORM.md - Tool Design Standards](../prd/03_PLATFORM.md)

---

## Context

NYQST agents interact with the platform through tools. The Model Context Protocol (MCP) provides a standard for exposing tools to LLMs and agent frameworks. The platform needs a tool architecture that addresses:

1. **Standard protocol**: MCP is the emerging standard for tool interoperability. Agents (LangGraph, Claude, Copilot) can call MCP tools without custom integration.
2. **Tool namespacing**: As the platform grows, dozens of tools across substrate, indexing, knowledge, connectors, and domain services must be organized without name collisions.
3. **Tool discovery**: Agents should discover available tools based on their context (session, permissions, module) rather than receiving all tools in every context.
4. **Input/output contracts**: Tool schemas (JSON Schema) must be precise, versioned, and validated at runtime.
5. **Audit and governance**: Every tool call must be logged to the run ledger. Some tools require human approval before execution.
6. **Context window efficiency**: Research shows that MCP-based dynamic tool discovery reduces context window usage from ~77K to ~8.7K tokens (see Research Synthesis).

Today's codebase has:
- `src/intelli/mcp/server.py` — MCP server (`intelli-platform`) registered with substrate, run, and knowledge tool modules
- `src/intelli/mcp/tools/substrate_tools.py` — 10 implemented substrate tools (list_pointers, resolve_pointer, checkout_manifest, etc.)
- `src/intelli/mcp/tools/run_tools.py` — Run lifecycle tools (defined, partially wired)
- `src/intelli/mcp/tools/knowledge_tools.py` — Knowledge tools (stub)
- MCP 1.2.0+ in dependencies
- Tools use `AsyncSessionLocal` for database access and return `TextContent` JSON

The current implementation works but lacks namespacing, discovery, session scoping, and governance hooks.

---

## Decision

Adopt **MCP as the primary tool protocol** for agent-platform interaction, with a namespaced, session-scoped, governance-aware tool architecture.

### Tool Namespace Convention

All platform tools follow a hierarchical namespace:

```
{domain}.{resource}.{action}
```

| Domain | Examples |
|--------|----------|
| `substrate` | `substrate.pointer.list`, `substrate.pointer.advance`, `substrate.manifest.checkout`, `substrate.artifact.upload` |
| `run` | `run.create`, `run.start`, `run.complete`, `run.log_step`, `run.checkpoint` |
| `index` | `index.ingest`, `index.search`, `index.explain` |
| `knowledge` | `knowledge.kb_query`, `knowledge.kb_create` |
| `document` | `document.parse`, `document.extract_tables`, `document.classify` |
| `connector` | `connector.slack.post_message`, `connector.hubspot.update_deal` |
| `claim` | `claim.create`, `claim.link_evidence`, `claim.decide` |
| `schema` | `schema.register`, `schema.validate`, `schema.list` |

This replaces the current flat naming (e.g., `list_pointers` → `substrate.pointer.list`).

### Tool Discovery (Context-Scoped)

Agents receive tools based on their session context, not a global list:

```python
def discover_tools(session: Session, agent_definition: AgentDefinition) -> list[Tool]:
    """Return tools available to this agent in this session context."""
    tools = []

    # 1. Agent's allowed capabilities determine base tool set
    for capability in agent_definition.capabilities:
        tools.extend(CAPABILITY_TOOL_MAP[capability])

    # 2. Session mounts filter resource-specific tools
    #    (e.g., only connectors for mounted providers)
    tools = filter_by_session_mounts(tools, session)

    # 3. Policy removes tools not allowed at this level of care
    tools = filter_by_policy(tools, session.policy_template)

    return tools
```

This keeps the agent's context window focused on relevant tools.

### Tool Execution Pipeline

Every tool call passes through a standard pipeline:

```
Agent calls tool
       │
       ▼
┌──────────────┐
│ 1. Validate   │  ← JSON Schema validation of inputs
│    Inputs      │
└──────┬───────┘
       │
┌──────▼───────┐
│ 2. Check      │  ← Policy Engine: is this tool allowed?
│    Policy      │     Does this call require approval?
└──────┬───────┘
       │
  ┌────▼────┐
  │Approval │  ← If policy requires human confirmation
  │Required?│     (interrupt agent, wait for approval)
  └────┬────┘
       │
┌──────▼───────┐
│ 3. Execute    │  ← Call the actual service layer
│    Tool       │
└──────┬───────┘
       │
┌──────▼───────┐
│ 4. Log to     │  ← Record in run ledger:
│    Run Ledger  │     tool name, input hash, output refs,
│               │     duration, token usage
└──────┬───────┘
       │
┌──────▼───────┐
│ 5. Return     │  ← MCP TextContent response
│    Result      │
└──────────────┘
```

### Tool Response Contract

All tools return structured responses following a consistent envelope:

```json
{
  "status": "success",
  "data": { ... },
  "refs": [
    {"type": "artifact", "sha256": "abc123..."},
    {"type": "pointer", "id": "uuid..."}
  ],
  "warnings": [],
  "tool_call_id": "uuid..."
}
```

The `refs` field enables the UI to render clickable references to platform objects (artifacts, pointers, runs) within tool call results.

### MCP Server Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    MCP Server                             │
│                 ("intelli-platform")                      │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │ Substrate   │  │ Run        │  │ Index              │ │
│  │ Tools       │  │ Tools      │  │ Tools              │ │
│  ├────────────┤  ├────────────┤  ├────────────────────┤ │
│  │ Knowledge   │  │ Document   │  │ Connector          │ │
│  │ Tools       │  │ Tools      │  │ Tools              │ │
│  ├────────────┤  ├────────────┤  ├────────────────────┤ │
│  │ Claim       │  │ Schema     │  │ (Future domains)   │ │
│  │ Tools       │  │ Tools      │  │                    │ │
│  └────────────┘  └────────────┘  └────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Tool Execution Pipeline                  │   │
│  │  Validate → Policy Check → Execute → Log → Return │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Transport: stdio (local) | SSE (remote) | HTTP          │
└──────────────────────────────────────────────────────────┘
```

### External MCP Servers (Future)

The platform will also consume external MCP servers as tool providers:

- **Browser tools** (web search, page fetch) via external MCP server
- **Domain-specific tools** from MCP marketplace
- **Customer-provided tools** via custom MCP servers

External tools are registered in the platform's tool registry and subject to the same policy and audit pipeline.

---

## Options Considered

### Option 1: MCP as Primary Protocol (Selected)

**Description:** Use MCP as the standard protocol for all agent-tool interaction. Internal tools are MCP tools; external tools are consumed via MCP clients.

**Pros:**
- Emerging industry standard (Anthropic-backed, growing ecosystem)
- Framework-agnostic (works with LangGraph, Claude, Copilot, custom agents)
- Standard discovery, schema, and transport mechanisms
- Dynamic tool loading reduces context window usage
- Aligns with Reference Design's tool architecture

**Cons:**
- MCP is still maturing (pre-1.0 in some aspects)
- Overhead for simple internal function calls
- Must bridge MCP to LangGraph's tool calling mechanism

### Option 2: LangChain/LangGraph Tools Only

**Description:** Define tools as LangChain `BaseTool` subclasses, callable within LangGraph.

**Pros:**
- Direct integration with LangGraph
- No protocol overhead
- Mature ecosystem

**Cons:**
- Tied to LangChain ecosystem
- No standard discovery for non-LangChain agents
- Must build custom protocol for external tool providers
- Doesn't support Claude/Copilot directly

### Option 3: Custom REST API Tools

**Description:** Expose tools as REST API endpoints, called by agents via HTTP.

**Pros:**
- Simple, well-understood pattern
- Language-agnostic

**Cons:**
- No standard schema/discovery mechanism
- Must build custom tool registry
- No streaming support for long-running tools
- Reinvents what MCP provides

---

## Decision Rationale

Option 1 (MCP as Primary Protocol) was chosen because:

1. **Standard over custom**: MCP provides schema, discovery, and transport that we'd otherwise build ourselves. The protocol overhead is minimal.
2. **Already implemented**: The codebase has a working MCP server with 10+ tools. This ADR extends and formalizes the existing pattern.
3. **Multi-agent future**: As NYQST integrates with Claude, Copilot, and other agents, MCP provides a single interop standard.
4. **Context efficiency**: Dynamic tool discovery keeps agent context windows focused on relevant tools.
5. **Audit by design**: The execution pipeline naturally logs every tool call through MCP's structured invoke/response pattern.

LangGraph tools are a **thin wrapper** over MCP tools — LangGraph's `ToolNode` calls MCP tools via the execution pipeline. This gives us both LangGraph integration and MCP interoperability.

---

## Consequences

### Positive

- Single tool protocol for all agent types (internal + external)
- Namespacing prevents collisions as tool count grows
- Session-scoped discovery reduces context window usage
- Policy enforcement on every tool call
- Complete audit trail in run ledger
- External MCP servers can extend platform capabilities

### Negative

- MCP adds protocol overhead for purely internal calls
- Namespace migration needed for existing flat-named tools
- Must bridge MCP to LangGraph tool system
- MCP versioning may require adapter updates

### Risks

- **Risk:** MCP protocol breaks backward compatibility
  - **Mitigation:** Pin MCP library version; abstract tool definitions so they can be ported. Platform's tool execution pipeline is the stable layer.
- **Risk:** Too many tools overwhelm agent context
  - **Mitigation:** Session-scoped discovery limits tool set. Agent definitions declare required capabilities. Profile-based tool grouping.
- **Risk:** Tool execution pipeline adds latency
  - **Mitigation:** Pipeline steps are lightweight (validation + policy check + logging). Execution is the only heavy step, and it's the actual service call.

---

## Implementation Notes

1. **Namespace migration**: Rename existing tools from flat names to namespaced names (e.g., `list_pointers` → `substrate.pointer.list`). Support old names temporarily via aliases for backward compatibility during transition.
2. **Tool registry**: Add `ToolDefinition` model to database. Each tool has name, namespace, schema, version, required capabilities, and policy annotations. Discovery queries this registry filtered by session context.
3. **Execution pipeline**: Implement as middleware in the MCP server's `call_tool` handler. Steps: validate → policy check → execute → log. The policy check hooks into the Policy Engine (when built) or passes through in the foundation phase.
4. **LangGraph bridge**: Create `MCPToolNode` that wraps MCP tool calls for use in LangGraph graphs. The node handles MCP invoke/response and maps to LangGraph's expected tool output format.
5. **Response envelope**: Standardize all tool responses to include `status`, `data`, `refs`, and `warnings`. Update existing tools to conform.
6. **Run ledger integration**: Each tool call emits a `tool.call.started` event (with input hash) and `tool.call.completed` event (with output refs and duration) to the run ledger.

---

## Related ADRs

- [ADR-002: Code Generation Strategy](./002-code-generation-strategy.md) — Tool schemas as MCP contracts flow through code generation
- ADR-004: Index Service Architecture — Index tools exposed via MCP
- ADR-005: Agent Runtime & Framework — LangGraph agents call MCP tools
- ADR-006: Session & Workspace Architecture — Tools scoped by session context
- ADR-009: Human-in-the-Loop & Governance — Tool calls may require approval

---

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [PLATFORM_REFERENCE_DESIGN.md Appendix A — MCP Tool Surface](../PLATFORM_REFERENCE_DESIGN.md)
- [RESEARCH_SYNTHESIS.md — Dynamic Tool Discovery](../RESEARCH_SYNTHESIS.md)
