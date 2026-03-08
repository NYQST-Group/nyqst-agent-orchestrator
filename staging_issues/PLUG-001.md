# PLUG-001 — MCP tool registry + discovery service (list, describe, enable by scope)

- Type: **story**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `mcp`, `tools`
- Depends on: `EPIC-PLUGINS`, `P0-003`

## Problem

MCP tools exist but there is no registry/discovery surface, nor an enablement model per workspace/project/app. This blocks safe composition of tools and Dify-like app configuration.

## Proposed solution

Implement Tool Registry:
- DB: `tools` table (name, domain, schema, version, provider, enabled_default).
- Runtime discovery: scan local MCP server tools and register/refresh.
- Enablement: `tool_enablements` table linking tool → scope (tenant/workspace/project/app).
- API: list tools, describe schema, update enablements.

## Repo touchpoints

- `src/intelli/mcp/*`
- `src/intelli/db/models/* (new tools)`

## Acceptance criteria

- Tool list API returns all available tools with schemas.
- Tool enablement can be toggled per project/app and enforced at runtime.

## Test plan

- Integration: disabling a tool prevents it being callable by the agent (policy check).
