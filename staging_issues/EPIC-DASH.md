---
    key: EPIC-DASH
    title: Dashboards with provenance drilldowns
    type: epic
    milestone: M7 Dashboards + provenance
    labels: [phase:6-dashboards, priority:medium, size:XL, track:frontend, type:epic]
    ---

    ## Problem

    Dashboards must be trustworthy: every KPI must link to evidence and explain deltas.

    ## Proposed solution

    Implement dashboard builder and runtime with provenance panels and exception drilldowns.

    ## Dependencies

    - EPIC-MODELS — Models + validation + impact diffs
- EPIC-INTEL — Evidence + insights + audit-first provenance

    ## Acceptance criteria

    - [ ] Dashboard tiles can be configured and saved
- [ ] Every tile has provenance link to evidence/model fields
- [ ] Exceptions list supports drilldown into sources and runs
- [ ] Refresh updates are explainable with deltas

    ## Test plan

    - [ ] E2E: create dashboard, add tile, drilldown provenance
- [ ] Integration: dashboard persistence and queries

    ## Notes / references

    _None_
