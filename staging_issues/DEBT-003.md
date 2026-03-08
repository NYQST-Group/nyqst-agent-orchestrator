# DEBT-003 — Deterministic debt calculation engine (amortization, interest, covenant ratios)

- Type: **story**
- Milestone: `M9-DEBT`
- Repo alignment: **missing**
- Labels: `backend`, `domain:debt`, `calc`
- Depends on: `DEBT-001`

## Problem

Debt schedules must be deterministic and testable; LLM arithmetic is unacceptable.

## Proposed solution

- Compute amortization schedules under fixed/floating rates.
- Compute covenant ratios based on financial inputs.
- Provide explain() traces per period and ratio.

## Acceptance criteria

- Engine passes golden tests; outputs stable.

## Test plan

- Unit: golden amortization fixtures; edge-case tests.
