# STUDIO-007 — Workflow builder MVP (n8n-like): compose multi-step workflows from skills/tools

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `workflow`
- Depends on: `STUDIO-006`, `EPIC-W0`

## Problem

Some tasks are deterministic pipelines rather than chat (ingest → extract → validate → publish). A lightweight workflow builder unlocks repeatable production processes.

## Proposed solution

Implement workflow builder MVP:
- Represent workflows as DAGs of nodes (skills/tools/subgraphs).
- UI: drag/drop workflow canvas with node catalog (inspired by Dify/n8n).
- Execution: compile DAG to LangGraph and run under the same run ledger.
- Triggering: manual run now; schedules/webhooks later.

## Acceptance criteria

- User can define a workflow with at least 3 nodes and run it end-to-end.
- Workflow execution emits run events and stores artifacts like any other run.

## Test plan

- Integration: compile workflow DAG → run graph; assert node order and outputs.
