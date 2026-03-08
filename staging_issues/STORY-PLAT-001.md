---
    key: STORY-PLAT-001
    title: Baseline dev scripts + validation harness
    type: story
    milestone: M0 Baseline + P0 fixes
    labels: [phase:0-baseline, priority:critical, size:M, track:infra, type:story]
    ---

    ## Problem

    Developers/agents need one reliable way to start the system and verify it works.

    ## Proposed solution

    Add/standardize scripts: run.sh, validate.sh, start-worker.sh; add .env.example; document Step-0 baseline checks.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] scripts/dev/run.sh starts infra + backend + frontend (or prints exact terminal commands)
- [ ] scripts/dev/validate.sh runs: deps, migrations, backend health, unit/integration tests, UI typecheck/build
- [ ] docs/05_DEV_ENVIRONMENT.md matches actual scripts
- [ ] .env.example exists and matches code requirements

    ## Test plan

    - [ ] CI: validate.sh (or equivalent) runs in integration job
- [ ] Local smoke: /health/ready returns 200

    ## Notes / references

    - Stage 0 in docs/04_BUILD_STAGES_TO_PROD.md
