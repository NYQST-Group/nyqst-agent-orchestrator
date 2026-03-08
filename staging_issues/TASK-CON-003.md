---
    key: TASK-CON-003
    title: Implement app + context_pack schemas + fixtures
    type: task
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:S, track:platform, type:task]
    ---

    ## Problem

    Apps are central; without a stable schema, app builder and runner cannot be developed in parallel.

    ## Proposed solution

    Finalize app.schema.json and context_pack.schema.json and add template fixtures.

    ## Dependencies

    - STORY-CON-001 — Contract governance: versioning rules + fixtures discipline

    ## Acceptance criteria

    - [ ] Schema validates apps of all four types (VIEW/AGENT/ANALYSIS/WORKFLOW)
- [ ] At least 4 template fixtures: Research Notebook, Lease Review, Weekly Refresh, Bundle Review Queue
- [ ] Fixtures include triggers and output mappings

    ## Test plan

    - [ ] Contract tests validate fixtures

    ## Notes / references

    _None_
