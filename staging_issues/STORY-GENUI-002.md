---
    key: STORY-GENUI-002
    title: GML/rehype pipeline: markdown+tags → React components
    type: story
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:medium, size:L, track:frontend, type:story]
    ---

    ## Problem

    Agent outputs often come as markdown with embedded UI tags; must render safely.

    ## Proposed solution

    Implement rehype-to-JSX pipeline mapping GML tags to components; sanitize content.

    ## Dependencies

    - STORY-GENUI-001 — GenUI component registry (primitives + composed patterns)

    ## Acceptance criteria

    - [ ] At least 10 core tags render correctly
- [ ] Unsafe HTML is rejected or sanitized
- [ ] Rendering errors fail gracefully

    ## Test plan

    - [ ] Unit: tag parsing
- [ ] Component: sample GML renders

    ## Notes / references

    _None_
