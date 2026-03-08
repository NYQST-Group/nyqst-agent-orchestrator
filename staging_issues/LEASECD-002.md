# LEASECD-002 — Lease extraction skill: parse DocIR blocks into structured lease terms with citations

- Type: **story**
- Milestone: `M8-LEASECD`
- Repo alignment: **missing**
- Labels: `backend`, `domain:leasecd`, `skills`
- Depends on: `LEASECD-001`, `DI-002`, `PLUG-005`

## Problem

Automated extraction is required to scale. Must be auditable and correctable.

## Proposed solution

Implement extraction workflow:
- Use DocIR blocks and pattern library to find candidate clauses.
- LLM extracts structured fields with locators.
- Store extracted fields as proposed values; user can confirm/edit.

## Acceptance criteria

- On fixture lease docs, extraction produces a populated lease record with citations to source blocks.

## Test plan

- Eval: extraction accuracy on fixtures; citations coverage.
