---
    key: STORY-DASH-001
    title: Backend: dashboards model + API (tiles, queries, provenance)
    type: story
    milestone: M7 Dashboards + provenance
    labels: [phase:6-dashboards, priority:medium, size:M, track:platform, type:story]
    ---

    ## Problem

    Dashboards need persistence and a data contract for tiles and drilldowns.

    ## Proposed solution

    Implement dashboards tables and APIs; tiles reference model fields and provenance rules.

    ## Dependencies

    - EPIC-DASH — Dashboards with provenance drilldowns
- EPIC-MODELS — Models + validation + impact diffs

    ## Acceptance criteria

    - [ ] Dashboard CRUD endpoints exist
- [ ] Tiles reference model fields and can load data
- [ ] Provenance links included in responses

    ## Test plan

    - [ ] Integration: create dashboard, add tile, query tile data

    ## Notes / references

    _None_
