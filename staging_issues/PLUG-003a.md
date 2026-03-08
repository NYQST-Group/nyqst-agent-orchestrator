# PLUG-003a — Secrets storage abstraction (encryption at rest + redaction)

- Type: **task**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `security`
- Depends on: `PLUG-003`, `ENT-002`

## Problem

Connector credentials must be stored securely and never leak into logs/events.

## Proposed solution

Implement secrets manager abstraction: encrypt/decrypt with master key, redact in logs, and restrict access by RBAC.

## Acceptance criteria

- Secrets are encrypted in DB and redacted in logs and API responses.

## Test plan

- Security unit test: ensure redaction; integration: encryption roundtrip.
