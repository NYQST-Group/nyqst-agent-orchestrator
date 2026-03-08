# STUDIO-004 — Analysis canvas MVP: infinite canvas with persisted nodes and links

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `frontend`, `backend`, `canvas`
- Depends on: `STUDIO-001`, `BL-011`

## Problem

AnalysisPage is currently a placeholder. Product vision requires an unlimited canvas where analysis blocks, documents, outputs, diffs, and workflows can be composed and linked.

## Proposed solution

Implement canvas MVP:
- Data model: `canvas_boards` (project_id), `canvas_nodes`, `canvas_edges` with JSON payload.
- UI: zoom/pan infinite canvas (use a proven lib like React Flow or custom minimal engine).
- Node types v1: Note, Artifact, ReportSnippet, ChartPlaceholder, Decision.
- Persistence: autosave to backend; optimistic updates.

## Repo touchpoints

- `ui/src/pages/AnalysisPage.tsx`
- `ui/src/components/canvas/* (new)`
- `src/intelli/api/v1/* (canvas router)`

## Acceptance criteria

- User can create a board within a project and add/move nodes, create links, and persist state.
- Artifacts and report snippets can be pinned to canvas nodes and opened.
- Canvas performance remains acceptable for at least 200 nodes.

## Test plan

- Unit: canvas reducer and serialization.
- E2E: create board → add nodes → refresh → state persists.
