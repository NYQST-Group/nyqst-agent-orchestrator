# PLUG-004 — Plugin/Tools manager UI: list tools, configure connectors, enable per project/app

- Type: **story**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `frontend`, `tools`, `settings`
- Depends on: `PLUG-001`, `PLUG-003`

## Problem

Without a UI, tool/connector management is invisible and cannot be delegated to users/admins.

## Proposed solution

Add Settings → Tools & Connectors UI:
- Tools list with schemas and toggle switches per scope.
- Connector setup forms and status indicators.
- Logs/last sync timestamps.

## Repo touchpoints

- `ui/src/pages/SettingsPage.tsx (new)`
- `ui/src/components/tools/* (new)`

## Acceptance criteria

- Admin can enable/disable tools for a project and configure at least one connector.
- UI reflects current enablement state and sync health.

## Test plan

- E2E: toggle tool enablement; connector setup persists.
