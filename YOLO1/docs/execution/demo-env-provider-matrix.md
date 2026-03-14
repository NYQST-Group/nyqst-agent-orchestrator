# Demo Env And Provider Matrix

Other agents should not have to reverse-engineer the env surface from `src/intelli/config.py`, four `.env` templates, shell scripts, and backlog notes. This document turns that spread into one operator-facing matrix and makes the required versus optional choices explicit. I^1 I^2

## North-Star Intent

The environment surface for the demo lane should be:

- explicit
- grouped by capability
- honest about defaults
- honest about drift
- impossible to “mostly guess” without consequence

If an env var or provider key matters to the demo, this document should say exactly how.

## Current-State Anchor

The current env surface comes from four places:

- [src/intelli/config.py](../../../src/intelli/config.py) for core application settings. I^1
- [.env.example](../../../.env.example), [.env.dev](../../../.env.dev), [.env.staging](../../../.env.staging), and [.env.prod](../../../.env.prod) for operator-facing examples. I^2
- startup and smoke scripts for deployment-time overrides. I^3
- staged backlog and issue grounding for web research provider keys that are planned but not yet fully normalized into config. I^4

The canonical meaning of the classifications below is locked in [demo-deployment-brief.md](./demo-deployment-brief.md).

## Core Application And Auth

| Setting | Current default or example | Classification | Notes |
| --- | --- | --- | --- |
| `APP_NAME` | `Intelli Document Platform` | `optional` | Cosmetic; safe to leave at default for the demo lane. |
| `DEBUG` | `.env.example=true`, config default `False` | `required for specific feature` | Needed only if the demo depends on `POST /api/v1/auth/dev-bootstrap`; acceptable for operator-controlled demos, not something to “accidentally” leave on. |
| `LOG_LEVEL` | `INFO` | `optional` | Use `INFO` unless actively debugging. |
| `SECRET_KEY` | placeholder string | `required for demo` | Secret; do not guess or keep the placeholder for any environment beyond disposable local rehearsal. |
| `JWT_EXPIRY_HOURS` | `24` | `optional` | Default is fine for the demo lane. |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | `required for specific feature` | Must match the chosen frontend origin if the UI is served on a non-default port. |
| `RATE_LIMIT_RPM` | `60` | `optional` | Leave default unless it blocks a scripted rehearsal. |

## Database And Storage

| Setting | Current default or example | Classification | Notes |
| --- | --- | --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://intelli:intelli@localhost:5433/intelli` | `required for demo` | Core dependency; smoke and health are meaningless without it. |
| `DB_POOL_SIZE` | `10` | `optional` | Leave default for single-host demo. |
| `DB_MAX_OVERFLOW` | `20` | `optional` | Leave default for single-host demo. |
| `STORAGE_BACKEND` | `.env.example=s3` | `required for demo` | The default demo lane assumes MinIO-backed S3 storage. |
| `S3_ENDPOINT_URL` | `http://localhost:9000` | `required for demo` | Required when `STORAGE_BACKEND=s3`. |
| `S3_BUCKET` | `intelli-artifacts` | `required for demo` | Must match the bucket created by `minio-init`. |
| `S3_ACCESS_KEY` | `minioadmin` | `required for demo` | Secret in non-local environments; do not improvise alternate credentials without updating compose and smoke. |
| `S3_SECRET_KEY` | `minioadmin` | `required for demo` | Secret in non-local environments. |
| `S3_REGION` | `us-east-1` | `optional` | Safe to leave at default for MinIO. |
| `LOCAL_STORAGE_PATH` | `/tmp/intelli-storage` | `required for specific feature` | Only relevant if the demo intentionally switches to `STORAGE_BACKEND=local`. |

## Models, Retrieval, And Search

| Setting | Current default or example | Classification | Notes |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | empty in templates | `required for demo` | Required for grounded ask/RAG in the current demo lane. |
| `OPENAI_BASE_URL` | unset | `required for specific feature` | Only set if routing through a non-default OpenAI-compatible gateway; do not guess. |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | `optional` | Default is fine for the demo lane. |
| `EMBEDDING_DIMENSIONS` | `1536` | `optional` | Must stay aligned with the embedding model if changed. |
| `CHAT_MODEL` | `gpt-4o-mini` | `optional` | Default is acceptable unless the meeting requires a different model. |
| `CHAT_MODEL_TEMPERATURE` | config default `0.2` | `optional` | Not exposed in `.env.example`, but can be set if needed; leave stable for demos. |
| `CHAT_MODEL_MAX_TOKENS` | config default `4096` | `optional` | Only change deliberately. |
| `CHAT_MODEL_REASONING_EFFORT` | unset | `required for specific feature` | Only for reasoning-model experiments; do not set casually. |
| `INDEX_BACKEND` | `.env.example=opensearch`, config default `pgvector` | `required for demo` | This is the main config drift. The pack recommends locking one mode per environment and retesting after any switch. |
| `OPENSEARCH_URL` | `http://localhost:9200` | `required for specific feature` | Required when `INDEX_BACKEND=opensearch`. |
| `OPENSEARCH_USERNAME` | empty | `optional` | Not needed for the current local security-disabled compose service. |
| `OPENSEARCH_PASSWORD` | empty | `optional` | Not needed for the current local security-disabled compose service. |
| `OPENSEARCH_VERIFY_CERTS` | `false` | `required for specific feature` | Must reflect the real TLS mode if OpenSearch is not local. |
| `OPENSEARCH_CHUNKS_INDEX` | `intelli-chunks-v1` | `optional` | Keep stable across rehearsals. |

## MCP, Web Research, And Provider Keys

| Setting | Current default or example | Classification | Notes |
| --- | --- | --- | --- |
| `MCP_TRANSPORT` | `streamable-http` | `optional` | Current default is acceptable. |
| `MCP_PORT` | `8001` | `optional` | Change only if the chosen host has a collision. |
| `BRAVE_SEARCH_API_KEY` | not in current config templates | `required for specific feature` | Planned in `BL-003`; if the demo promises Brave-based web research, add explicit config wiring first. |
| `JINA_API_KEY` | not in current config templates | `required for specific feature` | Planned in `BL-003`; do not smuggle this through ad hoc code paths. |
| `TAVILY_API_KEY` | not in current config templates | `required for specific feature` | North-star provider preference exists, but current repo config does not yet wire it; add explicit config before claiming Tavily-backed demo research. |

## Redis, Session Monitoring, And Observability

| Setting | Current default or example | Classification | Notes |
| --- | --- | --- | --- |
| `CHECKPOINTER_POOL_SIZE` | `5` | `optional` | Leave default unless load testing proves otherwise. |
| `REDIS_URL` | unset | `required for specific feature` | Needed only for flows that truly depend on cache or queue behavior. |
| `SESSION_MONITOR_INTERVAL_SECONDS` | `300` | `optional` | Leave default for demo use. |
| `LANGFUSE_ENABLED` | `false` | `optional` | Langfuse is useful, not required. |
| `LANGFUSE_PUBLIC_KEY` | empty | `required for specific feature` | Required only if Langfuse tracing is turned on. |
| `LANGFUSE_SECRET_KEY` | empty | `required for specific feature` | Secret; must not be guessed. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | `required for specific feature` | If using local Langfuse, change it and retest. |

## Operator Script Overrides

| Setting | Current default or example | Classification | Notes |
| --- | --- | --- | --- |
| `INTELLI_POSTGRES_PORT` | `5433` | `required for specific feature` | Override only if the host port is occupied. |
| `INTELLI_API_PORT` | `8000` | `required for specific feature` | Needed when the API runs on a non-default port. |
| `INTELLI_UI_PORT` | `3000` | `required for specific feature` | Needed when the UI runs on a non-default port. |
| `INTELLI_API_URL` | unset | `required for specific feature` | Required when the UI must point at a non-default API origin. |
| `INTELLI_REQUIRE_RAG` | `0` unless set | `required for specific feature` | Set to `1` for buyer-demo smoke so RAG failure is fatal rather than skipped. |
| `BACKEND_URL` | `http://localhost:8000` | `required for specific feature` | Used by `scripts/smoke-test.sh` when the API is not on the default port. |
| `FRONTEND_URL` | `http://localhost:3000` | `required for specific feature` | Used by `scripts/smoke-test.sh` when the UI is not on the default port. |
| `VITE_DEMO_MODE` | unset, `true` only in `dev:demo` | `required for specific feature` | Internal demo shell mode only; do not rely on it as the canonical deployed UI path. |

## Drift To Resolve Before Claiming Demo-Ready

- `.env.example` recommends `INDEX_BACKEND=opensearch` while `src/intelli/config.py` defaults to `pgvector`. The deployment pack chooses one mode per environment and requires smoke after any change.
- The repo already documents Langfuse local mode, but the local Langfuse compose profile also uses port `3000`, which conflicts with the default UI port. If local Langfuse is enabled, either the UI or Langfuse port must move and the smoke path must be rerun.
- Web research provider keys are present in issue-level design, not yet in the main config surface. Agents should not assume a provider “just works” because a key exists in some shell profile.

## Judgment Required

Do not fill in secrets or provider keys by habit. If a key is not known, the right outcome is to block the specific feature, not to invent configuration and produce a false-green deployment. Likewise, do not hide config drift such as `opensearch` versus `pgvector` behind vague language like “search is configured.” I^1 I^3

## Builder Accountability

The builder or operator responsible for env setup must verify personally:

- that the chosen demo lane has one explicit index mode
- that all secret-bearing values are real and not placeholders
- that demo auth and grounded ask are enabled intentionally, not accidentally
- that any promised web research provider is explicitly wired and smoke-tested
- that local observability choices do not silently collide with UI ports

Fake completion includes:

- claiming the env is done because `.env` exists
- leaving `SECRET_KEY` on the placeholder value and pretending it is “just a demo”
- promising web research without a real provider key and adapter
- switching to `pgvector` or `opensearch` at the last minute without rerunning smoke

## Issue Hooks

- `I^1` - [src/intelli/config.py](../../../src/intelli/config.py) is the live config contract.
- `I^2` - [.env.example](../../../.env.example), [.env.dev](../../../.env.dev), [.env.staging](../../../.env.staging), and [.env.prod](../../../.env.prod) are the current operator examples.
- `I^3` - [docs/STARTUP_SEQUENCE.md](../../../docs/STARTUP_SEQUENCE.md), [scripts/dev/run.sh](../../../scripts/dev/run.sh), [scripts/dev/validate.sh](../../../scripts/dev/validate.sh), and [scripts/smoke-test.sh](../../../scripts/smoke-test.sh) define the current override surface used by startup and smoke.
- `I^4` - `BL-003` web research tooling, preserved in [gh-issue-grounding.md](../../notes/gh-issue-grounding.md), is the source of Brave/Jina provider-key expectations; the north-star plan separately prefers Tavily as the first provider once explicitly wired.
