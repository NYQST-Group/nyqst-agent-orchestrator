---
    key: STORY-GENUI-001
    title: GenUI component registry (primitives + composed patterns)
    type: story
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:high, size:L, track:frontend, type:story]
    ---

    ## Problem

    Dynamic outputs need a safe and composable set of primitives.

    ## Proposed solution

    Implement registry of components and strict descriptor schema for allowed props and bindings.

    ## Dependencies

    - EPIC-GENUI — GenUI renderer (component registry, GML, charts) for dynamic outputs

    ## Acceptance criteria

    - [ ] Registry supports at least 20 primitives used in spec
- [ ] Descriptors are validated at runtime in dev
- [ ] Components render from descriptors consistently

    ## Test plan

    - [ ] Vitest: render primitives from descriptors

    ## Notes / references

    _None_
