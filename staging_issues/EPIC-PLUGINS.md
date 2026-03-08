# EPIC-PLUGINS — MCP tools, plugins, connectors, and skills registry

- Type: **epic**
- Milestone: `M5-PLUGINS`
- Repo alignment: **partial**
- Labels: `milestone:M5`, `platform:tools`

## Problem

MCP scaffold exists but knowledge tools and a tool registry / connector framework are not implemented. Product needs a consistent tool protocol and enablement model across scopes (workspace/project/app).

## Proposed solution

Implement MCP tool registry + discovery, connector credential storage, tool enablement policies, and a skills registry (packaged subgraphs) so agents and apps can be composed safely and consistently.

## Acceptance criteria

- Tools are discoverable and described in a registry; tool calls are permission-gated by scope.
- Connector credentials can be stored and used by tools without leaking secrets into run events.
- A 'skill' can be packaged, registered, enabled, and invoked inside a graph.

## Test plan

- Integration: tool discovery returns expected tool list; policy denies unauthorized calls.
- Security: secrets never appear in event payloads or client logs.
