# EPIC-DEBT — Debt module (term sheets, amortization, covenant monitoring)

- Type: **epic**
- Milestone: `M9-DEBT`
- Repo alignment: **missing**
- Labels: `domain:debt`
- Depends on: `BL-016`, `DI-002`, `STUDIO-001`

## Problem

Debt MVP requires extracting terms from loan docs and producing deterministic amortization schedules, covenant checks, and alerts.

## Proposed solution

Build on platform primitives: DocIR extraction + entity/citation + deterministic calc engine + dashboards and alerts.

## Acceptance criteria

- A debt instrument can be ingested and modeled; amortization schedule and key ratios computed deterministically.
- Covenant checks and exceptions are traceable to source clauses and assumptions.

## Test plan

- Integration: fixture term sheet → model → schedule matches expected values.
