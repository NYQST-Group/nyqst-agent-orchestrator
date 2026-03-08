# DEBT-001 — Debt instrument data model + CRUD (facilities, tranches, rates, covenants)

- Type: **story**
- Milestone: `M9-DEBT`
- Repo alignment: **missing**
- Labels: `backend`, `domain:debt`
- Depends on: `EPIC-DEBT`

## Problem

Need canonical debt model with versioning and citations.

## Proposed solution

- DB: `debt_instruments`, `tranches`, `rate_terms`, `covenants`, `events`.
- APIs: CRUD and versioning.
- Link key fields to citations/locators.

## Acceptance criteria

- Debt instruments can be stored/updated with citations.

## Test plan

- Integration: CRUD + scoping.
