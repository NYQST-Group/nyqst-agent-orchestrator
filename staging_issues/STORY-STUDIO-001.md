---
    key: STORY-STUDIO-001
    title: Notebook v1: pages, blocks, and citations
    type: story
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:high, size:L, track:studio, type:story]
    ---

    ## Problem

    Notebook is the narrative surface; it must support sources and evidence embeds.

    ## Proposed solution

    Implement notebook pages and basic block types with citation/evidence embedding.

    ## Dependencies

    - EPIC-STUDIO — Studio (notebook + infinite canvas) with provenance
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- EPIC-INTEL — Evidence + insights + audit-first provenance

    ## Acceptance criteria

    - [ ] Create/edit notebook pages
- [ ] Block types: text, evidence embed, app output embed
- [ ] Citations panel shows linked evidence and sources
- [ ] Notebook blocks link to provenance inspector

    ## Test plan

    - [ ] Vitest: notebook store and block rendering
- [ ] E2E: create page and add evidence block

    ## Notes / references

    _None_
