---
    key: STORY-INTEL-002
    title: Backend: insights lifecycle + linkage to evidence/CRM/models
    type: story
    milestone: M4 Evidence + insights + CRM
    labels: [phase:4-intelligence, priority:high, size:M, track:intelligence, type:story]
    ---

    ## Problem

    Insights are how humans make decisions; they must be linked to evidence and have lifecycle states.

    ## Proposed solution

    Implement insights model/API with status transitions, evidence links, and optional CRM/model links.

    ## Dependencies

    - STORY-INTEL-001 — Backend: evidence model + API + provenance enforcement
- EPIC-CRM — CRM entities, relationships, and timelines
- EPIC-MODELS — Models + validation + impact diffs

    ## Acceptance criteria

    - [ ] Insights require at least one evidence link
- [ ] Status transitions recorded (audit)
- [ ] Insights can link to CRM entities and model fields
- [ ] Insights can be marked stale

    ## Test plan

    - [ ] Integration: create insight with evidence, change status

    ## Notes / references

    _None_
