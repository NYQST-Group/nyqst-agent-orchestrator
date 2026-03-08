# STUDIO-006 — Apps surface (Dify-like): save configured agent workflows and run them

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `apps`
- Depends on: `EPIC-PLUGINS`, `BL-014`, `STUDIO-001`

## Problem

To scale beyond ad-hoc chat, users need reusable 'apps' that package graphs + context + toolsets into repeatable workflows.

## Proposed solution

Implement Apps MVP:
- DB: `apps` table (tenant_id, name, description, graph_template, config JSON, enabled_tools, default_context_packs).
- UI: Apps list/detail/create. Create wizard: pick template (research, lease CD, debt), select tools, select context packs.
- Run: allow launching an app run against a project; results stored as runs/deliverables.

## Acceptance criteria

- User can create an app configuration and run it against a project.
- App run uses configured tool set and context packs.

## Test plan

- E2E: create app → run → see deliverable output.
