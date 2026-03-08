---
    key: STORY-ORCH-001
    title: PlanSet schemas + persistence (Plan, PlanTask linked ordering)
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:M, track:platform, type:story]
    ---

    ## Problem

    Planning is a first-class object and must be persisted for audit and UI replay.

    ## Proposed solution

    Implement Pydantic schemas and DB persistence for PlanSet/Plan/PlanTask; include ordering strategy (linked list or explicit ordering).

    ## Dependencies

    - EPIC-ORCH — Orchestration & planning (PlanSet, LangGraph, subagents)
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] PlanSet stored and linked to run_id
- [ ] Tasks have stable IDs and ordering
- [ ] Updates can be appended as events and reconciled into latest plan state

    ## Test plan

    - [ ] Integration: save and load PlanSet

    ## Notes / references

    _None_
