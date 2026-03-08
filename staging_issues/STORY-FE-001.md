---
    key: STORY-FE-001
    title: Implement app shell: routing + left nav + project selector
    type: story
    milestone: M1 Contracts locked + UI shell
    labels: [phase:1-contracts, priority:high, size:M, track:frontend, type:story]
    ---

    ## Problem

    Without a shell, teams build isolated pages that don't integrate.

    ## Proposed solution

    Implement layout with persistent nav, top bar project selector, and route placeholders.

    ## Dependencies

    - EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)

    ## Acceptance criteria

    - [ ] Routes exist for all primary modules
- [ ] Left nav highlights active route
- [ ] Project selector changes project context (at least in state)
- [ ] All pages have loading/empty/error skeletons

    ## Test plan

    - [ ] Vitest: nav + routing
- [ ] Playwright smoke: route navigation

    ## Notes / references

    _None_
