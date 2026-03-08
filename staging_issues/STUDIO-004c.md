# STUDIO-004c — Implement v1 node types (Note, Artifact, ReportSnippet, ChartPlaceholder, Decision)

- Type: **task**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `frontend`, `canvas`
- Depends on: `STUDIO-004b`, `STUDIO-003`

## Problem

Canvas needs meaningful node types that connect to existing platform primitives.

## Proposed solution

Implement node components and serialization for each type; add node creation palette; integrate with artifact and decision APIs.

## Acceptance criteria

- All v1 node types can be created and persisted; clicking opens relevant viewer.

## Test plan

- UI test: create each node type; persist; reopen.
