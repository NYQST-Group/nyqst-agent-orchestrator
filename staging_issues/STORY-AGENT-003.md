---
    key: STORY-AGENT-003
    title: Frontend: agent/skills management screens
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:medium, size:M, track:frontend, type:story]
    ---

    ## Problem

    Admin users need to see and configure agents/skills.

    ## Proposed solution

    Add Settings subpages for agents and skills; enable/disable per project/context pack.

    ## Dependencies

    - STORY-AGENT-001 — Backend: skill registry + permissions + versioning
- STORY-FE-001 — Implement app shell: routing + left nav + project selector

    ## Acceptance criteria

    - [ ] List skills with permissions and versions
- [ ] Enable/disable skills per project or context pack
- [ ] Show last used and recent runs

    ## Test plan

    - [ ] Vitest: management screens

    ## Notes / references

    _None_
