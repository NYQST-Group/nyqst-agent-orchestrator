---
    key: TASK-STUDIO-003
    title: Canvas persistence v1: save/load layout per project
    type: task
    milestone: M3 Studio (notebook + canvas)
    labels: [phase:3-studio, priority:medium, size:M, track:studio, type:task]
    ---

    ## Problem

    Users need their canvas layouts saved; otherwise the canvas is a demo toy.

    ## Proposed solution

    Persist canvas state (blocks/edges/positions) to backend per project and reload on open.

    ## Dependencies

    - STORY-STUDIO-002 — Canvas v1: pan/zoom, blocks, edges, inspector

    ## Acceptance criteria

    - [ ] Canvas layout persists across refresh
- [ ] Save is debounced and resilient
- [ ] Versioning approach defined (simple v1: latest only)

    ## Test plan

    - [ ] Integration: save/load endpoints
- [ ] E2E: layout persists across reload

    ## Notes / references

    _None_
