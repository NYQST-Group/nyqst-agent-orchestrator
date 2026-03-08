---
    key: STORY-GENUI-003
    title: Chart rendering support (Plotly or chosen lib) + theming
    type: story
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:medium, size:M, track:frontend, type:story]
    ---

    ## Problem

    Dashboards and outputs require charts with consistent theme.

    ## Proposed solution

    Implement chart components driven by descriptors; ensure responsive layout and export.

    ## Dependencies

    - STORY-GENUI-001 — GenUI component registry (primitives + composed patterns)

    ## Acceptance criteria

    - [ ] Supports at least 5 chart types used by early dashboards
- [ ] Charts render from JSON descriptor
- [ ] Theme consistent with app

    ## Test plan

    - [ ] Component tests: chart renders from descriptor

    ## Notes / references

    _None_
