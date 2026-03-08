---
    key: STORY-CON-001
    title: Contract governance: versioning rules + fixtures discipline
    type: story
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:S, track:testing, type:story]
    ---

    ## Problem

    Contracts drift unless there is a simple governance rule and fixtures that enforce it.

    ## Proposed solution

    Define contract versioning rules and required fixtures; add contract test runner.

    ## Dependencies

    - EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] contracts/00_index.md defines versioning policy
- [ ] fixtures/ folder exists with golden examples
- [ ] contract tests run in CI and fail on schema mismatch

    ## Test plan

    - [ ] Contract test job in CI

    ## Notes / references

    - docs/08_CONTRACTS_OVERVIEW.md
