---
    key: TASK-CON-004
    title: Implement bundle/version + evidence + insight schemas + fixtures
    type: task
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:M, track:documents, type:task]
    ---

    ## Problem

    Document/versioning + provenance are the foundation for diff, evidence, and stale propagation.

    ## Proposed solution

    Finalize bundle.schema.json, evidence.schema.json, insight.schema.json and add fixtures (v1/v2 + deltas).

    ## Dependencies

    - STORY-CON-001 — Contract governance: versioning rules + fixtures discipline

    ## Acceptance criteria

    - [ ] Bundle fixture includes two versions and ingest run ids
- [ ] Evidence fixture includes source spans and confidence
- [ ] Insight fixture includes evidence links and stale flag example

    ## Test plan

    - [ ] Contract tests validate fixtures

    ## Notes / references

    _None_
