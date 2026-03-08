# EPIC-LEASECD — Lease CD module (commercial property lease cashflow and covenant analysis)

- Type: **epic**
- Milestone: `M8-LEASECD`
- Repo alignment: **missing**
- Labels: `domain:leasecd`
- Depends on: `BL-016`, `DI-002`, `STUDIO-001`

## Problem

Lease CD requires extracting structured lease terms from documents and producing deterministic cashflow/obligation schedules with auditable calculations and evidence links.

## Proposed solution

Build Lease CD on platform primitives: DocIR extraction + entity/citation, deterministic calc engine, and Studio surfaces for lease entities and scenarios.

## Acceptance criteria

- A lease document can be ingested, key terms extracted with citations, and a cashflow schedule generated deterministically.
- Outputs are exportable to report/slides/document and traceable to source clauses.

## Test plan

- Integration: fixture lease → extracted terms → schedule matches expected values.
