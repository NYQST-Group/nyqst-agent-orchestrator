---
    key: EPIC-CONTRACTS
    title: Contracts locked (events, apps, bundles, provenance)
    type: epic
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:critical, size:XL, track:platform, type:epic]
    ---

    ## Problem

    Parallel work will drift without stable contracts for data and events.

    ## Proposed solution

    Define and version JSON schemas for core entities and streaming events; add fixtures and contract tests.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] contracts/ JSON schemas exist for apps, context packs, bundles, run events, evidence, insights, CRM, models, workflows
- [ ] Fixtures validate against schemas in CI
- [ ] Frontend TS types align with contracts (compile + runtime dev assertions)

    ## Test plan

    - [ ] Contract tests validate fixtures against JSON Schema
- [ ] Backend unit tests validate Pydantic schemas (if used as source)
- [ ] Frontend typecheck compiles generated/handwritten types

    ## Notes / references

    - See contracts/00_index.md and docs/08_CONTRACTS_OVERVIEW.md
