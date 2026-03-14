# Demo Deployment Brief

The north-star pack defines the product we are trying to sell. This document defines the honest route to a runnable demo on the infrastructure the repo actually supports today. If this brief drifts into production fantasy, it stops helping. If it hides operational shortcuts, it forces the operator back into the loop. I^1 I^2

## North-Star Intent

The deployment lane should make Intelli Studio runnable for a buyer demo without rewriting the product story:

- single host
- infrastructure managed by `docker compose`
- app processes started from the host
- clear startup order
- clear health and smoke gates
- clear fallback and stop rules

This brief is about making the north star runnable, not about changing what the north star is.

## Current-State Anchor

The repo already supports a real, if modest, demo operating shape:

- `docker-compose.yml` manages infrastructure services only: `postgres`, `minio`, `minio-init`, optional `redis`, optional `langfuse`, and `opensearch`. I^1
- [docs/STARTUP_SEQUENCE.md](../../../docs/STARTUP_SEQUENCE.md) already defines the validated local order: infra, migrations, backend health, API smoke, and UI build. I^2
- `scripts/dev/run.sh` and `scripts/dev/validate.sh` already encode that startup and validation logic. I^3
- `src/intelli/config.py` and `.env.example` define the current environment surface. I^4
- `ui/package.json` supports `build`, `dev`, and `preview`, but the repo does not yet define a containerized frontend deployment path. I^5
- Health endpoints and demo bootstrap auth already exist and are enough to support an operator-controlled demo lane. I^6

The truthful v1 deployment shape is therefore:

- compose-managed infrastructure
- host-run API process
- host-run UI process

Anything stronger than that is future work unless separately implemented.

## Operational Classifications

Use these classifications consistently across the deployment pack:

- `required for demo` means the stack is not demo-ready without it.
- `required for specific feature` means only flows that promise that feature depend on it.
- `optional` means the demo can still be buyer-credible without it.
- `accepted shortcut` means allowed in the single-host demo lane if documented and smoke-tested.
- `hard blocker` means do not continue to a buyer demo.
- `manual step` means an operator must do it deliberately; agents must not assume it happened.
- `rollback trigger` means stop and return to the last known-good demo state.
- `demo-ready` means platform smoke and buyer-path smoke both pass.

## Deployment Target

Lock the demo lane to:

- one operator-controlled host
- `docker compose` for infrastructure only
- host-run API via `uvicorn intelli.main:app`
- host-run UI from a built asset preview process

### Preferred Process Shape

- API: host-run `uvicorn intelli.main:app --port ${INTELLI_API_PORT:-8000}` without `--reload`
- UI: `npm -C ui run build` followed by `npm -C ui run preview -- --host 0.0.0.0 --port ${INTELLI_UI_PORT:-3000}`

### Accepted Shortcuts

- `DEBUG=true` with `POST /api/v1/auth/dev-bootstrap` for an operator-controlled demo environment
- `npm -C ui run dev` instead of `vite preview` for rehearsal or last-resort recovery, but only after re-running smoke checks
- Langfuse disabled
- manual project/task/bundle seed setup until onboarding automation exists

### Not Yet Truthful To Claim

- containerized API or UI deployment from this repo
- CI-backed deploy automation
- staging parity
- production-grade monitoring
- background-worker-dependent demo flows that rely on unresolved queue semantics

## Demo Service Topology

| Service or process | Classification | Rule |
| --- | --- | --- |
| `postgres` | `required for demo` | Canonical database; must pass readiness before migrations and backend startup. |
| `minio` | `required for demo` | Required under the default `STORAGE_BACKEND=s3` MinIO lane. |
| `minio-init` | `required for demo` | Required to ensure `intelli-artifacts` exists before upload smoke. |
| `opensearch` | `required for specific feature` | Required when `INDEX_BACKEND=opensearch`; not required if the demo deliberately runs in `pgvector` mode. |
| `redis` | `required for specific feature` | Only for flows that genuinely depend on cache/queue behavior; do not pretend it is always required. |
| `langfuse` | `optional` | Useful for observability, not required for the demo lane. |
| API process | `required for demo` | Run from the host; no repo-backed container path exists yet. |
| UI process | `required for demo` | Run from the host; prefer built preview over dev server. |

## Deploy Order

1. `manual step`: copy `.env.example` to `.env` and set required values for the chosen demo lane.
2. Start infrastructure:
   - `docker compose up -d postgres minio minio-init`
   - add `opensearch` if `INDEX_BACKEND=opensearch`
   - add `redis` only if a promised flow genuinely needs it
3. Run migrations:
   - `alembic upgrade head`
4. Start backend and verify readiness:
   - `curl -fsS http://localhost:${INTELLI_API_PORT:-8000}/health/ready`
   - `curl -fsS http://localhost:${INTELLI_API_PORT:-8000}/health`
5. Run API smoke:
   - `python scripts/dev/smoke_api.py`
   - for buyer demos, require RAG rather than silently skipping it
6. Build and start UI:
   - `npm -C ui install`
   - `npm -C ui run typecheck`
   - `npm -C ui run build`
   - `npm -C ui run preview -- --host 0.0.0.0 --port ${INTELLI_UI_PORT:-3000}`
7. Seed demo state:
   - follow [demo-seed-bootstrap.md](./demo-seed-bootstrap.md)
8. Run buyer-path smoke:
   - follow [demo-release-smoke-checklist.md](./demo-release-smoke-checklist.md)

Only after all eight steps pass is the deployment `demo-ready`.

## Accepted Shortcuts Vs Hard Blockers

### Accepted Shortcuts

- `DEBUG=true` plus demo bootstrap auth in a local or operator-controlled environment
- one host running both app processes
- local MinIO instead of cloud object storage
- Langfuse disabled
- manual seeded project/task creation until onboarding automation exists
- `INDEX_BACKEND=pgvector` for a smaller demo corpus if OpenSearch is the blocker and the smoke path is rerun after the switch

### Hard Blockers

- migrations fail or drift
- `/health/ready` fails on the chosen backend/index mode
- demo auth or standard auth cannot reach a usable tenant/user
- artifact upload or pointer/manifest advance fails
- grounded ask over seeded docs fails or returns uncited output
- no buyer-grade seeded document package exists for the meeting
- a promised queue/background-worker flow depends on unresolved worker behavior
- the frontend cannot load, authenticate, or route into the main shell

## Judgment Required

Do not confuse “the stack starts” with “the demo is deployable.” The demo is not ready if the only passing path uses smoke-only content, skips grounded retrieval, or relies on hand-waving around auth, uploads, or citations. Likewise, do not describe host-run processes as if the repo already contains a hardened deployment topology. I^2 I^3

## Builder Accountability

The builder or operator responsible for deployment must verify personally:

- that the chosen deployment shape matches the repo’s real current capabilities
- that the demo lane is explicit about which features are synchronous and which are not safe to promise
- that the UI and API are started in a way the next operator can reproduce
- that `demo-ready` means buyer-path smoke passed, not merely that services booted
- that accepted shortcuts are documented and retested, not silently improvised

Fake completion includes:

- calling the stack “deployed” because `docker compose up` succeeded
- relying on `hello.txt` smoke content as the buyer demo corpus
- promising background-worker flows while `GAP-023` is still unresolved
- claiming production-style hosting when the repo still depends on host-run app processes

## Issue Hooks

- `I^1` - [docker-compose.yml](../../../docker-compose.yml) is the current infrastructure truth: infra services exist, API/UI containers do not.
- `I^2` - [docs/STARTUP_SEQUENCE.md](../../../docs/STARTUP_SEQUENCE.md) is the current validated order for infra, migrations, backend health, API smoke, and UI build.
- `I^3` - [scripts/dev/run.sh](../../../scripts/dev/run.sh) and [scripts/dev/validate.sh](../../../scripts/dev/validate.sh) are the current runnable entrypoints for startup and validation.
- `I^4` - [src/intelli/config.py](../../../src/intelli/config.py) and [.env.example](../../../.env.example) define the live env/config surface.
- `I^5` - [ui/package.json](../../../ui/package.json) shows that the UI currently has `build`, `dev`, and `preview`, but no repo-defined deployment container path.
- `I^6` - [src/intelli/api/health.py](../../../src/intelli/api/health.py), [src/intelli/api/v1/health.py](../../../src/intelli/api/v1/health.py), and [src/intelli/api/v1/auth.py](../../../src/intelli/api/v1/auth.py) define the current health and demo-bootstrap auth path.
- `I^7` - `GAP-038`, `GAP-039`, `GAP-042`, and `GAP-023`, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), are the key reasons this deployment pack must be explicit about CI absence, validation gates, staging absence, and worker risk.
