# Start Here (Agent Build Brief)

This repo is a working demo of an **agent-first, enterprise-trustworthy analysis platform**.

## Canonical docs (treat these as “source of truth”)

- `docs/PLATFORM_REFERENCE_DESIGN.md` — product + architecture reference design
- `docs/INDEX_CONTRACT.md` — indexing contract (“profiles not knobs”, always-on, auditability)
- `docs/STARTUP_SEQUENCE.md` — validated startup / troubleshooting

## Repo layout (what to modify)

- **Backend (FastAPI)**: `src/intelli/`
- **Product UI (Vite app)**: `ui/` (this is what `scripts/dev/run.sh` starts)
- **Infra + dev scripts**: `docker-compose.yml`, `scripts/dev/*`
- **Schemas**: `schemas/` (early registry material)

## Historical / background material

The prior large analysis set was moved to `docs/analysis/`. It can be useful context, but it is **not canonical** compared to the reference design and index contract.

## “Gotchas” that can confuse new agents

- There is a second, older/experimental frontend codepath at repo root (`package.json`, `src/*.tsx`). The validated dev flow uses `ui/`. Prefer `ui/` unless you are explicitly working on the root package.

