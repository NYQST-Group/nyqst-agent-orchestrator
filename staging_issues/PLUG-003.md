# PLUG-003 — Connector framework: credentials, OAuth flows, and ingestion sync jobs

- Type: **story**
- Milestone: `M5-PLUGINS`
- Repo alignment: **missing**
- Labels: `backend`, `connectors`, `security`
- Depends on: `EPIC-PLUGINS`, `BL-011`

## Problem

To support enterprise workflows (SharePoint/Drive/Slack/Email/CRM), NYQST needs connectors with secure credential storage and ingestion jobs.

## Proposed solution

Build connectors foundation:
- DB: `connectors` and `connector_accounts` (tenant_id, type, encrypted secrets ref, status).
- Secrets storage: integrate with env-based KMS or at minimum Fernet encryption with master key.
- OAuth: implement generic OAuth callback endpoints for supported connectors.
- Sync jobs: arq jobs to pull docs/messages and store as artifacts + index into RAG/context packs.

## Acceptance criteria

- At least one connector type (e.g., Google Drive or Slack) can be configured and sync a small dataset into a project notebook.
- Secrets are encrypted at rest and never emitted to clients.

## Test plan

- Security test: secrets redaction; integration test: sync job stores artifacts.
