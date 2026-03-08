# STUDIO-001 — Projects: backend model + API + UI list/detail (replace placeholder ProjectsPage)

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `projects`
- Depends on: `EPIC-STUDIO`, `P0-003`

## Problem

UI has a Projects page placeholder but no project data model or CRUD APIs. Project scoping is required for context inheritance, document organisation, and downstream CRM/intelligence workflows.

## Proposed solution

Implement Projects end-to-end:
- DB: `projects` table (tenant_id, name, description, status, tags, created_by, timestamps).
- API: CRUD endpoints under `/api/v1/projects`.
- UI: ProjectsPage shows list with search/filter; ProjectDetail shows notebooks, runs, deliverables, context packs.
- Integrate with existing Conversation scopes: allow conversations to be attached to a project_id.

## Repo touchpoints

- `ui/src/pages/ProjectsPage.tsx`
- `src/intelli/api/v1/* (new projects router)`
- `src/intelli/db/models/* (new projects model)`

## Acceptance criteria

- User can create/edit/archive projects; list view shows projects scoped to tenant.
- Research conversations can be created within a project and appear in project detail.
- Project can own notebooks and context packs (even if minimal initially).

## Test plan

- Integration: project CRUD with tenant scoping.
- E2E: create project → navigate → run research in project scope.
