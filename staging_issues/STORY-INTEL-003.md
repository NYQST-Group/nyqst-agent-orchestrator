---
    key: STORY-INTEL-003
    title: Review queue: low confidence and conflicts view + actions
    type: story
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:medium, size:M, track:frontend, type:story]
    ---

    ## Problem

    Users need an operational way to review and approve extracted intelligence.

    ## Proposed solution

    Implement a review queue screen (can later be saved as a View App) showing evidence needing attention.

    ## Dependencies

    - STORY-INTEL-001 — Backend: evidence model + API + provenance enforcement
- STORY-INTEL-002 — Backend: insights lifecycle + linkage to evidence/CRM/models
- EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)

    ## Acceptance criteria

    - [ ] Queue shows low confidence evidence and conflicts
- [ ] Actions: approve, edit (creates new version), mark conflict, link to insight
- [ ] Queue filters and sorting

    ## Test plan

    - [ ] Vitest: review queue UI
- [ ] E2E: approve evidence (when API wired)

    ## Notes / references

    _None_
