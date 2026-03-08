# EPIC-W3 — Wave 3 — Polish, integration, and safety rails

- Type: **epic**
- Milestone: `M4-W3`
- Repo alignment: **missing**
- Labels: `milestone:M4`, `wave:3`

## Problem

After core capability exists, the product needs UX polish (generation overlay, clarification loops), stronger safety rails (never-confidently-wrong), and integrated provenance across surfaces.

## Proposed solution

Ship the remaining spec polish items: overlay, clarification flow, shared data brief, plus auditability and guardrails across UI and runtime.

## Acceptance criteria

- Generation overlay shows run progress, plan state, citations, and artifacts being produced.
- Clarification flow interrupts low-confidence or ambiguous prompts with structured questions.
- Shared data brief is available and reused across deliverables.

## Test plan

- E2E: ambiguous prompt triggers clarification; resolved prompt continues run.
- Unit/Integration: shared data brief stored and referenced by deliverable pipelines.
