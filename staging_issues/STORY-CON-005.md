---
    key: STORY-CON-005
    title: Generate TS types from contracts + runtime dev assertions
    type: story
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:medium, size:M, track:testing, type:story]
    ---

    ## Problem

    Type drift between backend and frontend causes late integration pain.

    ## Proposed solution

    Add a typegen pipeline (JSON schema → TS) and dev-time assertion helpers for event payloads.

    ## Dependencies

    - TASK-CON-002 — Implement run_event schema + fixtures + validators
- TASK-CON-003 — Implement app + context_pack schemas + fixtures
- TASK-CON-004 — Implement bundle/version + evidence + insight schemas + fixtures
- EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)

    ## Acceptance criteria

    - [ ] Type generation script exists and is documented
- [ ] Frontend uses generated types in reducers and renderers
- [ ] CI verifies types are up-to-date (diff check)

    ## Test plan

    - [ ] CI job fails if generated types differ from committed output

    ## Notes / references

    _None_
