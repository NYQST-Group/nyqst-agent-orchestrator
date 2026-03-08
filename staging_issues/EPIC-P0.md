# EPIC-P0 — P0 repo stabilization and CI hardening

- Type: **epic**
- Milestone: `M0-P0`
- Repo alignment: **partial**
- Labels: `milestone:M0`, `priority:P0`

## Problem

Core platform work is slowed by a small set of blocking correctness and workflow issues (async worker registration, event ordering, missing tenant FK, optional Redis, lack of PR CI).

## Proposed solution

Ship the P0 fixes as a first milestone so every subsequent wave can build on stable background jobs, reliable run streaming, tenant-aware data, and predictable CI feedback.

## Acceptance criteria

- P0 issues merged: arq worker registration fixed; run event ordering race fixed; run.tenant_id added + backfilled; Redis enabled in default dev compose; CI runs backend+frontend checks on PRs.
- Dev workflow: `docker compose up` brings up required services without profiles; `make test` (or equivalent) works from clean clone.

## Test plan

- Add/extend unit tests for RunRepository ordering and arq worker function discovery.
- CI pipeline executes lint + unit tests + minimal integration smoke for both backend and UI.
