# [NX-003] Connector platform integration (Composio + n8n) as optional tool providers

**Goal**
- Integrate at least one connector platform to accelerate SaaS integrations:
  - Composio (prebuilt app actions)
  - n8n (workflow engine + webhooks)

**Approach**
- Treat connector platforms as *tool providers* behind MCP:
  - Provide an MCP server adapter that exposes connector actions as tools.
  - Standardize auth secrets handling (tenant scoped).

**Implementation steps**
1. Add a `connectors` module:
   - connector definitions (provider, name, scopes, auth_type)
   - secret storage integration (vault / KMS later; env for dev)
2. Composio:
   - Add a provider adapter that lists actions and invokes them.
   - Map action schemas to MCP tool schemas.
3. n8n:
   - Add webhook trigger tool and a “run workflow” tool.
4. Add UI:
   - Connectors page (connect account, manage scopes)
5. Threat model:
   - prevent prompt injection / data exfil; explicit permission prompts.

**Acceptance criteria**
- User can connect a SaaS account and run a tool call against it from an agent.
- All connector calls are logged as run events and tied to tenant.

