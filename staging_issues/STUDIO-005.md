# STUDIO-005 — Diff viewer: compare artifacts/versions and render semantic diffs

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `diff`
- Depends on: `STUDIO-004`

## Problem

Spec and DocuIntelli require diffing across versions (contracts, reports, models). Repo has artifacts but no diff UI or diff service.

## Proposed solution

Implement diff viewer:
- Backend: endpoint to compute diff between two artifact versions (text/pdf via extracted text).
- UI: Diff panel that can show side-by-side and unified diffs, with highlights.
- Integrate with canvas nodes: diff node referencing two artifacts.

## Acceptance criteria

- User can select two artifacts (or document versions) and view a diff in UI.
- Diff nodes can be added to canvas and reopened.

## Test plan

- Integration: diff endpoint returns expected hunks for text fixtures.
