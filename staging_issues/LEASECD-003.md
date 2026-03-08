# LEASECD-003 — Deterministic lease calculation engine (cashflows, indexation, scenarios)

- Type: **story**
- Milestone: `M8-LEASECD`
- Repo alignment: **missing**
- Labels: `backend`, `domain:leasecd`, `calc`
- Depends on: `LEASECD-001`

## Problem

Lease cashflow outputs must be deterministic, testable, and explainable. LLM-only calculations are unacceptable.

## Proposed solution

Build a deterministic calc engine:
- Inputs: structured lease terms (dates, rent steps, indexation rules).
- Outputs: cashflow schedule, NPV, key dates, scenario comparisons.
- Provide explain() outputs for each computed line item.

## Acceptance criteria

- Engine produces expected schedules for known examples and passes unit tests.
- UI can show explain traces per line item and link back to terms and citations.

## Test plan

- Unit: calc engine with golden fixtures; property-based tests for edge cases.
