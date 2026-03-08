# PROP-001 — Asset data model + CRUD (properties, portfolios, KPIs)

- Type: **story**
- Milestone: `M11-PROPSYGNAL`
- Repo alignment: **missing**
- Labels: `backend`, `domain:propsygnal`
- Depends on: `EPIC-PROPSYGNAL`

## Problem

Need canonical property/portfolio models to anchor signals and analysis.

## Proposed solution

- DB: `assets`, `portfolios`, `asset_kpis`.
- APIs + UI under Projects or separate PropSygnal section.

## Acceptance criteria

- Assets can be created and linked to projects/clients.

## Test plan

- Integration: CRUD + scoping.
