---
    key: EPIC-CRM
    title: CRM entities, relationships, and timelines
    type: epic
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:medium, size:L, track:intelligence, type:epic]
    ---

    ## Problem

    Users need entity-centric views to understand and act: companies, assets, relationships, timelines.

    ## Proposed solution

    Implement CRM entity store, relationship graph, entity detail screens, and link evidence/insights to entities.

    ## Dependencies

    - EPIC-INTEL — Evidence + insights + audit-first provenance

    ## Acceptance criteria

    - [ ] CRUD for CRM entities
- [ ] Relationships between entities stored and viewable
- [ ] Entity detail shows linked bundles/evidence/insights
- [ ] Saved views support CRM segmentation (later can be View Apps)

    ## Test plan

    - [ ] Integration: entity relationships queries
- [ ] E2E: link evidence to entity and view it on entity page

    ## Notes / references

    - See docs/01_MODULES_AND_SCREENS.md CRM screens
