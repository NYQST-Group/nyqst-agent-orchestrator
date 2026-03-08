# LEASECD-004 — Lease CD UI: term review, scenario builder, export to deliverables

- Type: **story**
- Milestone: `M8-LEASECD`
- Repo alignment: **missing**
- Labels: `frontend`, `domain:leasecd`
- Depends on: `LEASECD-003`, `BL-018`, `BL-019`

## Problem

Users need a UI to review extracted terms, correct them, run scenarios, and export outputs to report/slides/document.

## Proposed solution

Implement Lease CD pages:
- Lease list/detail under Projects.
- Term review table with citations and edit controls.
- Scenario builder for assumptions (inflation, break exercise).
- Export: generate deliverables using shared DataBrief + calc outputs.

## Acceptance criteria

- User can review/edit lease terms, run scenarios, and export a deliverable with charts.

## Test plan

- E2E: lease extraction → review → scenario → export slides.
