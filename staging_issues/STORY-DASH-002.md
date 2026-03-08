---
    key: STORY-DASH-002
    title: Frontend: dashboard builder and runtime + provenance panel
    type: story
    milestone: M7 Dashboards + provenance
    labels: [phase:6-dashboards, priority:medium, size:XL, track:frontend, type:story]
    ---

    ## Problem

    A dashboard must be editable, understandable, and trusted.

    ## Proposed solution

    Implement dashboard builder (add/edit tiles) and runtime view with provenance drilldown.

    ## Dependencies

    - STORY-DASH-001 — Backend: dashboards model + API (tiles, queries, provenance)
- STORY-FE-001 — Implement app shell: routing + left nav + project selector

    ## Acceptance criteria

    - [ ] Add/remove/reorder tiles
- [ ] Tile drilldown shows model field + evidence
- [ ] Exceptions view supports navigation to Studio blocks

    ## Test plan

    - [ ] Vitest: dashboard screens
- [ ] E2E: create and drilldown

    ## Notes / references

    _None_
