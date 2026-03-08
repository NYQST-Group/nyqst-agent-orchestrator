# EPIC-STUDIO — Studio surfaces: Projects, Clients/CRM, Decisions, Analysis canvas, Apps/Workflows

- Type: **epic**
- Milestone: `M5-STUDIO`
- Repo alignment: **partial**
- Labels: `milestone:M5`, `surface:studio`

## Problem

Repo contains module entry pages for Projects/Clients/Decisions/Analysis, but most are placeholders. Spec and your product vision require an operational Studio: entity management + notebooks + an infinite canvas that links analysis, diffs, and agent workflows.

## Proposed solution

Implement the Studio data model and UI flows: project/client CRUD, decision register with citations, analysis canvas with node linking/diffing, plus an 'Apps' surface for configured agent/workflow presets (Dify-like).

## Acceptance criteria

- Projects and Clients pages are fully functional (list/detail/create/edit) with appropriate scoping and permissions.
- Decisions register supports citations to evidence artifacts and is searchable.
- Analysis canvas supports at least 5 node types (note, doc/artifact, chart, decision, link) with drag/drop, zoom, and persistence.
- Apps surface supports saving a configured workflow/agent template and running it against a project.

## Test plan

- Unit: canvas state reducer and persistence; decision citation binding logic.
- E2E: create project → upload docs → run research → pin outputs to canvas → create decision with citations.
