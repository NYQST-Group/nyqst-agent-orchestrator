---
    key: TASK-PLAT-P0-ARQ
    title: P0: Fix arq worker registration + Redis always-on
    type: task
    milestone: M0 Baseline + P0 fixes
    labels: [phase:0-baseline, priority:critical, size:S, track:platform, type:task]
    ---

    ## Problem

    Worker starts but processes zero jobs due to function registry snapshot; Redis not started by default can cause silent sync fallback.

    ## Proposed solution

    Make WorkerSettings.functions dynamic; ensure Redis is started in docker-compose; require REDIS_URL; add start-worker script.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] Worker sees registered jobs at startup
- [ ] Redis starts by default in docker compose
- [ ] Enqueued job executes via worker (not sync fallback)
- [ ] Regression test/prototype exists for enqueue -> execute round trip

    ## Test plan

    - [ ] Integration: enqueue job and assert worker processes within timeout

    ## Notes / references

    - Mirror the P0-1 fix described in your plan
