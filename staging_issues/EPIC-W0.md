# EPIC-W0 — Wave 0 — Orchestrated research harness (planner + fan-out) + run events

- Type: **epic**
- Milestone: `M1-W0`
- Repo alignment: **missing**
- Labels: `milestone:M1`, `wave:0`

## Problem

Current research assistant is a single tool-using loop. The spec requires an orchestrated graph (planner → fan-out workers → fan-in synthesis) plus richer run events to drive Plan/Report UI.

## Proposed solution

Extend the LangGraph runtime to implement planner dispatch + worker subgraphs, add the plan/run event contract and UI primitives to prove end-to-end orchestration.

## Acceptance criteria

- Research runs can execute multi-step plans with concurrent worker tasks and produce a synthesized output.
- RunEvent stream includes plan lifecycle and citations lifecycle events needed by PlanViewer/ReportPanel.
- System remains backwards-compatible with existing chat streaming (Vercel AI SDK stream).

## Test plan

- Integration tests: simulated run emits expected event sequence; planner → worker → synth path executed.
- E2E: UI shows a plan timeline and a final draft report for a demo prompt.
