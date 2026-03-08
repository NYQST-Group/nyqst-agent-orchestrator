# PLUG-005 — Skills registry: package reusable subgraphs with metadata, permissions, and tests

- Type: **story**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `skills`
- Depends on: `PLUG-002`, `EPIC-OBS`

## Problem

Scaling workflows requires reusable building blocks ('skills') with clear contracts. Repo has graphs and tools but no registry, versioning, or permission model for reusable skills.

## Proposed solution

Implement Skills:
- Define a Skill manifest format: id, name, description, inputs/outputs schema, required tools, permissions, eval tests.
- Provide a registry (code-based first) and optionally DB-backed publishing later.
- Provide a CLI to scaffold a skill and its tests.

## Acceptance criteria

- At least 3 skills are registered (e.g., WebResearch, DocSummarize, TableExtract) and invokable.
- Each skill has a contract test and at least one eval fixture.

## Test plan

- Unit/integration: skill invocation; eval harness for skill fixtures.
