---
    key: STORY-STUDIO-002
    title: Canvas v1: pan/zoom, blocks, edges, inspector
    type: story
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:high, size:XL, track:studio, type:story]
    ---

    ## Problem

    Canvas is the spatial analysis core. Must be usable before advanced features.

    ## Proposed solution

    Implement an infinite canvas component with block library, edge linking, selection, and inspector.

    ## Dependencies

    - EPIC-STUDIO — Studio (notebook + infinite canvas) with provenance
- EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Pan/zoom works smoothly
- [ ] Blocks can be created, moved, selected
- [ ] Edges can be created between blocks (supports/derived-from/contradicts)
- [ ] Inspector shows block metadata and provenance links

    ## Test plan

    - [ ] Vitest: canvas reducers
- [ ] E2E: create blocks and link them

    ## Notes / references

    _None_
