---
    key: TASK-PLAT-P0-TENANTRUN
    title: P0: Add tenant_id to runs and propagate
    type: task
    milestone: M0 Baseline + P0 fixes
    labels: [phase:0-baseline, priority:high, size:S, track:platform, type:task]
    ---

    ## Problem

    Billing, quotas, and audit require direct tenant linkage on runs; joining via created_by is brittle/slow.

    ## Proposed solution

    Add tenant_id FK to Run; set at run creation; add filters in run queries.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] New run records tenant_id reliably
- [ ] API endpoints filter runs by tenant/project
- [ ] Index exists for aggregation queries

    ## Test plan

    - [ ] Integration: run created via API has correct tenant_id

    ## Notes / references

    - Mirror P0-3 fix
