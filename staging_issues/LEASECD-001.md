# LEASECD-001 — Lease data model + CRUD (lease, parties, dates, rent schedule, options)

- Type: **story**
- Milestone: `M8-LEASECD`
- Repo alignment: **missing**
- Labels: `backend`, `domain:leasecd`
- Depends on: `EPIC-LEASECD`

## Problem

Need a canonical lease entity model to store extracted terms and user overrides.

## Proposed solution

- DB: `leases` table (project_id, client_id, property_id optional) + child tables for rent steps, break options, indexation, covenants.
- API: CRUD endpoints + versioning of extracted vs edited values.
- Link extracted values to citations/locators.

## Acceptance criteria

- Lease terms can be stored and updated with version history and citations.

## Test plan

- Integration: lease CRUD; citation linkage.
