---
    key: TASK-FE-004
    title: Integrate mockups route (dev-only) and keep in sync with contracts
    type: task
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:medium, size:S, track:frontend, type:task]
    ---

    ## Problem

    The mockup is a high-signal reference. It should be visible in-dev and remain coherent with the evolving system.

    ## Proposed solution

    Add /mockups route rendering NyqstPortalMockupV2.tsx and a checklist to update it when screens change.

    ## Dependencies

    - STORY-FE-001 — Implement app shell: routing + left nav + project selector

    ## Acceptance criteria

    - [ ] /mockups route exists in dev build
- [ ] Mockup compiles with repo shadcn paths
- [ ] README explains how to use it

    ## Test plan

    - [ ] Typecheck passes

    ## Notes / references

    _None_
