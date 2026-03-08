---
    key: EPIC-MODELS
    title: Models + validation + impact diffs
    type: epic
    milestone: M6 Models + validation
    labels: [phase:5-models, priority:high, size:XL, track:intelligence, type:epic]
    ---

    ## Problem

    To drive dashboards and automation, intelligence must be modeled and validated, with explainable deltas.

    ## Proposed solution

    Implement model registry, rule engine, validation runs, and impact diffs that link to evidence.

    ## Dependencies

    - EPIC-INTEL — Evidence + insights + audit-first provenance
- EPIC-CRM — CRM entities, relationships, and timelines

    ## Acceptance criteria

    - [ ] Model definitions are versioned and editable
- [ ] Validation runs produce pass/fail results with evidence coverage gaps
- [ ] Document updates produce explainable model deltas
- [ ] Model diffs show schema and field changes

    ## Test plan

    - [ ] Unit: rule evaluation correctness
- [ ] Integration: validation run persistence
- [ ] E2E: doc update triggers model delta

    ## Notes / references

    - See docs/02_USER_FLOWS_MASTER.md Flow 5
