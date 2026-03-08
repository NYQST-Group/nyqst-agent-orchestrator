---
    key: STORY-FE-002
    title: Apps screens v1 (gallery + detail tabs) fixture-driven
    type: story
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:M, track:frontend, type:story]
    ---

    ## Problem

    Apps are the primary UX. We need screens early even before backend integration.

    ## Proposed solution

    Implement Apps gallery and App detail (Run/Configure/Runs/Outputs/Permissions) using contract fixtures.

    ## Dependencies

    - STORY-FE-001 — Implement app shell: routing + left nav + project selector
- TASK-CON-003 — Implement app + context_pack schemas + fixtures

    ## Acceptance criteria

    - [ ] Apps gallery renders cards with type/status/triggers/last run
- [ ] App detail Run tab shows inputs + context toggles + run button
- [ ] Runs tab shows run history list
- [ ] Outputs tab shows artifacts list
- [ ] All views work with fixtures and will later swap to API

    ## Test plan

    - [ ] Vitest component tests for Apps screens

    ## Notes / references

    _None_
