# DEBT-002 — Debt extraction skill: parse DocIR into structured debt terms with citations

- Type: **story**
- Milestone: `M9-DEBT`
- Repo alignment: **missing**
- Labels: `backend`, `domain:debt`, `skills`
- Depends on: `DEBT-001`, `DI-002`, `PLUG-005`

## Problem

Automated extraction required for scale; must be auditable and editable.

## Proposed solution

- Use DocIR blocks and patterns to locate key clauses.
- LLM extracts structured fields with locators.
- Store proposed values and allow user edits.

## Acceptance criteria

- On fixtures, extraction yields a populated debt model with citations.

## Test plan

- Eval: extraction fixtures and citation coverage.
