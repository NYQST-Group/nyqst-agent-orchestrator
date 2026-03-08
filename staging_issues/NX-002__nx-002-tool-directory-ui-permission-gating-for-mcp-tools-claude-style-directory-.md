# [NX-002] Tool directory UI + permission gating for MCP tools (Claude-style directory pattern)

**Problem**
MCP server exists, but there is no first-class “tool directory” surface for:
- discovery (what tools exist)
- permissions (what this tenant/project can use)
- observability (what tools were called)

**Goal**
- A UI and API that behaves like a tool marketplace/directory:
  - list available tools (built-in + external MCP servers)
  - enable/disable per tenant/project
  - show required scopes (read/write)
  - audit log of tool invocations

**Implementation**
Backend:
- Extend MCP tool registry to expose structured tool metadata (name, description, args schema, scopes).
- Add `tool_grants` table keyed by tenant_id/project_id/tool_name.
- Enforce tool grants in the tool-calling layer (deny by default).

Frontend:
- Add “Tools” page:
  - directory list
  - enable/disable toggle
  - tool detail drawer (args, scopes, example)
- Add “Run → Tool calls” panel for auditability (pull from run events).

**Acceptance criteria**
- Disabling a tool prevents calls (and surfaces a clear error).
- Tool list is accurate and generated from the runtime registry.

