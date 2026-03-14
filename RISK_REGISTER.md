# Risk Register

- Last generated: `2026-03-11T00:00:00Z`
- Repository: `NYQST-Group/NYQST-DocuIntelli-Build`
- Report date: `2026-03-11`

## Current Risks
- `HIGH` P0 stabilization work remains open: Open P0 items: [P0-001] Fix arq worker job registration (WorkerSettings.functions empty); [P0-002] Fix RunEvent sequence_num race (unique constraint violations under concurrency); [P0-003] Make local stack boot reliably (redis profile / env defaults / docs); [P0-004] Add tenant_id to core tables (runs, artifacts, manifests, pointers) and enforce isolation; [P0-005] Add production Dockerfiles (api + ui) and minimal CI build step (GitHub issues)
- `MEDIUM` Contract publisher is still mocked: The backstage schema publishing workflow still exits with a mock/incomplete implementation. (Workflow file)

## Reporting Policy
- Repo-first reporting is the current source of truth.
- GitHub Project mutation is deferred until a dedicated board is provisioned.
- Conductor drift is detected by validation, not resolved by automatic issue closure.
