# STUDIO-004b — Canvas persistence API + optimistic sync

- Type: **task**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `canvas`
- Depends on: `STUDIO-004a`, `P0-003`

## Problem

Canvas nodes must persist and support multi-session reload; eventual collaboration later.

## Proposed solution

Implement backend CRUD for boards/nodes/edges; UI uses optimistic updates with debounced autosave.

## Acceptance criteria

- Refresh restores state; conflicts resolved by last-write-wins (v1).

## Test plan

- Integration: save/load board; UI e2e refresh retains state.
