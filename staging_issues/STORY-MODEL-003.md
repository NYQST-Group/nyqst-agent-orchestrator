---
    key: STORY-MODEL-003
    title: Validation engine v1: rule evaluation + run logs
    type: story
    milestone: M6 Models + validation
    labels: [phase:5-models, priority:high, size:L, track:intelligence, type:story]
    ---

    ## Problem

    Validation ensures intelligence is trustworthy and produces actionable exceptions.

    ## Proposed solution

    Implement rule engine (deterministic) and validation runs that emit events and store results linked to evidence.

    ## Dependencies

    - STORY-MODEL-001 — Backend: model registry + versioning + field definitions
- EPIC-INTEL — Evidence + insights + audit-first provenance
- TASK-CON-002 — Implement run_event schema + fixtures + validators

    ## Acceptance criteria

    - [ ] Rules can be defined and evaluated
- [ ] Validation run produces pass/fail per rule
- [ ] Results link to evidence or gaps
- [ ] Run log shows validation steps

    ## Test plan

    - [ ] Unit: rule evaluation
- [ ] Integration: validation run persistence

    ## Notes / references

    _None_
