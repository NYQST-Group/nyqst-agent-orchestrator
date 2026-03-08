---
    key: STORY-ORCH-004
    title: Report preview streaming (delta + done semantics)
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:M, track:platform, type:story]
    ---

    ## Problem

    Reports must be visible while generating; delta semantics must avoid duplication bugs.

    ## Proposed solution

    Implement report preview delta buffering on client and done event replace semantics; store final report artifact.

    ## Dependencies

    - STORY-ORCH-002 — LangGraph orchestrator for Research Notebook app (fan-out, structured output)
- TASK-CON-002 — Implement run_event schema + fixtures + validators

    ## Acceptance criteria

    - [ ] Client accumulates preview deltas and replaces buffer on preview_done
- [ ] Final report artifact stored and linked to run
- [ ] Report preview can be pinned to Studio

    ## Test plan

    - [ ] Frontend unit: delta buffer correctness
- [ ] Integration: report artifact stored

    ## Notes / references

    _None_
