## Description
<!-- Describe your changes in detail -->

## Issue Tracking
Resolves #<issue_number>

## AO Execution
- AO Session:
- Task Brief / Spec:
- Worker Lane: `orchestrator` / `worker` / `manual`

## Verification
- [ ] `python -m pytest -m unit -q`
- [ ] `python -m pytest -m integration -q` or justified skip
- [ ] `npm -C ui run typecheck`
- [ ] `npm -C ui run test`
- [ ] `ruff check src/ tests/`
- [ ] `ruff format --check src/ tests/`

## Quality Gates
- [ ] My code follows the project's code style guidelines
- [ ] I have written unit tests for these changes
- [ ] All tests pass locally and in CI
- [ ] I have checked for security vulnerabilities

## Learning / Handoff
- [ ] I captured reusable learning, follow-up debt, or explicit non-learning in the issue / PR narrative

## Core Contract Review (For Schema Changes Only)
If this PR modifies any Pydantic models, JSON schemas, or TypeScript interfaces in the `src/intelli/schemas/` or `ui/src/types/` directories:
- [ ] I have verified backwards compatibility.
- [ ] I have regenerated the TypeScript schemas (if applicable).
- [ ] This change aligns with the V4 EPIC-CONTRACTS definition.
