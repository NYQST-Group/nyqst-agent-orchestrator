# [P0-003] Make local stack boot reliably (redis profile / env defaults / docs)

**Why this matters**
Developers should be able to run the platform with one command. Right now redis can be skipped depending on compose profile usage, and `.env` defaults are unclear.

**Repo evidence**
- `docker-compose.yml` marks redis under a `full` profile (not started by default).
- Settings allow `redis_url=None`, so jobs silently downgrade to sync mode.

**Goal**
- `docker compose up` starts the full dev stack (api + db + redis + minio + opensearch) with predictable defaults.
- Docs explicitly state what is optional vs required.

**Implementation**
1. Remove the `profiles: [full]` gate from redis (or add a documented default profile).
2. Ensure `.env.example` includes `REDIS_URL=redis://redis:6379`.
3. Add a `make dev` (or `justfile`) that starts compose and runs migrations.
4. Update `README.md` with a “first run” section.

**Acceptance criteria**
- Fresh clone → `docker compose up` + `make migrate` works without manual env edits.
- Background jobs run when worker started.

