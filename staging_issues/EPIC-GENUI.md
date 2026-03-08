---
    key: EPIC-GENUI
    title: GenUI renderer (component registry, GML, charts) for dynamic outputs
    type: epic
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:high, size:XL, track:frontend, type:epic]
    ---

    ## Problem

    Deliverables and rich agent outputs require a dynamic UI layer (GenUI) rather than hard-coded components.

    ## Proposed solution

    Implement a component registry, descriptor/renderer engine, GML tag pipeline, and chart rendering so agent outputs can render safely and consistently.

    ## Dependencies

    - EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] GenUI component registry exists (primitives + composed patterns)
- [ ] Renderer supports conditional/repeat/binding patterns
- [ ] GML tags render to React components
- [ ] Chart rendering supports required types and is themed consistently

    ## Test plan

    - [ ] Unit: renderer engine
- [ ] Component tests: each primitive renders from descriptor
- [ ] E2E: streamed GenUI blocks render in app output panel

    ## Notes / references

    - Map to COMPRESSED-BUILD-SPEC.md sections on GenUI; see proposal docs 06_GENUI.md and 05_GML_AND_REHYPE.md
