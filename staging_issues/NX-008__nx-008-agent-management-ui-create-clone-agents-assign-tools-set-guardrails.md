# [NX-008] Agent management UI (create/clone agents, assign tools, set guardrails)

**Goal**
Make agents configurable assets:
- manage system prompts, model choice, tool set, context policy, and max spend
- clone agents
- assign to projects/apps

**Implementation**
Backend:
- `agents` table (tenant_id, name, config JSON, status)
- API: CRUD + “test” endpoint
Frontend:
- Agents page:
  - list, create, edit
  - tool assignment with permissions
  - guardrails (max cost, max tokens, restricted connectors)

**Acceptance criteria**
- An agent can be created and used in a run without code changes.
- Guardrails are enforced server-side.

