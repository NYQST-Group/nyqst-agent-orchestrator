---
    key: STORY-MODEL-001
    title: Backend: model registry + versioning + field definitions
    type: story
    milestone: M6 Models + validation
    labels: [phase:5-models, priority:high, size:M, track:intelligence, type:story]
    ---

    ## Problem

    Model definitions are the structure for validation and dashboards.

    ## Proposed solution

    Create model tables and APIs: model, model_version, fields, field-to-evidence requirements.

    ## Dependencies

    - EPIC-MODELS — Models + validation + impact diffs
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- EPIC-CRM — CRM entities, relationships, and timelines

    ## Acceptance criteria

    - [ ] Models are versioned
- [ ] Fields can declare evidence requirements
- [ ] Model versions immutable after publish

    ## Test plan

    - [ ] Integration: create model, publish, edit to v2

    ## Notes / references

    _None_
