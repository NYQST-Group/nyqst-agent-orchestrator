# PLUG-003b — Generic OAuth flow endpoints + connector account linking

- Type: **task**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `connectors`
- Depends on: `PLUG-003a`

## Problem

Connectors need OAuth in many cases; implement generic flow to avoid custom per-connector code.

## Proposed solution

Add endpoints: start OAuth, callback; store tokens via secrets manager; create connector_account rows.

## Acceptance criteria

- OAuth flow works for at least one connector type end-to-end.

## Test plan

- Integration: mock OAuth callback and verify account linking.
