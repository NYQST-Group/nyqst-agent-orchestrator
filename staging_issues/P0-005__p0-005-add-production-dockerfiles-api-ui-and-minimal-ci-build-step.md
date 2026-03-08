# [P0-005] Add production Dockerfiles (api + ui) and minimal CI build step

**Why this matters**
Without Dockerfiles, deploy and CI parity are fragile.

**Repo evidence**
- No `Dockerfile` at repo root.
- CI currently runs lint/test but not container builds.

**Goal**
- Build and run the API and UI in containers locally and in CI.

**Implementation**
1. Add `Dockerfile.api` (or `Dockerfile`) for FastAPI:
   - multi-stage, installs deps, runs `uvicorn intelli.main:app`.
2. Add `ui/Dockerfile` (or `Dockerfile.ui`) for the frontend:
   - build static assets, serve with nginx or a lightweight node server.
3. Add `docker-compose.prod.yml` (optional) or document how to run both.
4. Update GitHub Actions workflow to `docker build` both images (no push required yet).

**Acceptance criteria**
- `docker build` succeeds for both images.
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml up` serves UI + API locally.
