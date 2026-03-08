# DEBT-004 — Debt dashboards + alerts (exceptions, covenant breaches) with provenance

- Type: **story**
- Milestone: `M9-DEBT`
- Repo alignment: **missing**
- Labels: `frontend`, `domain:debt`
- Depends on: `DEBT-003`, `STUDIO-004`

## Problem

Value comes from monitoring and surfacing exceptions with evidence.

## Proposed solution

- UI dashboards for schedules and covenant status.
- Alert rules (thresholds) stored per project.
- Evidence links to source clauses and calculation assumptions.

## Acceptance criteria

- Dashboard shows covenant status and exceptions; alerts can be configured.

## Test plan

- E2E: configure alert → simulate breach → alert appears.
