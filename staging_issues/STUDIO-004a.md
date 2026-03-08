# STUDIO-004a — Select canvas implementation (React Flow vs custom) and build base pan/zoom/drag interactions

- Type: **task**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `frontend`, `canvas`
- Depends on: `STUDIO-004`

## Problem

Canvas UX is non-trivial; choosing a stable library early avoids rework.

## Proposed solution

Evaluate React Flow (or similar) for licensing/perf; implement base board with pan/zoom, node drag, edge creation.

## Acceptance criteria

- Canvas base interactions work smoothly and meet perf target for 200 nodes.

## Test plan

- UI test: add/move node and ensure state updates.
