# STUDIO-003 — Decisions register: decisions CRUD + citation binding to evidence

- Type: **story**
- Milestone: `M5-STUDIO`
- Repo alignment: **missing**
- Labels: `backend`, `frontend`, `decisions`
- Depends on: `BL-016`, `STUDIO-001`

## Problem

Decision making is the output of analysis. Repo has a placeholder Decisions page and no decision model; citations need to be first-class for compliance.

## Proposed solution

Implement Decisions:
- DB: `decisions` table (tenant_id, project_id, title, decision, rationale, status, created_by).
- DB: `decision_citations` linking decisions to entity/citation IDs (BL-016).
- UI: DecisionsPage list with filters; DecisionDetail with rationale, citations, and linked artifacts.

## Repo touchpoints

- `ui/src/pages/DecisionsPage.tsx`
- `src/intelli/db/models/* (new decisions model)`

## Acceptance criteria

- Decisions can be created, edited, and linked to a project.
- Decisions can display citations and open the referenced evidence.

## Test plan

- E2E: create decision with a citation bound to a report claim.
