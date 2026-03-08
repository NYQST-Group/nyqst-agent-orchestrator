---
    key: STORY-ORCH-003
    title: Clarification flow (clarification_needed event → UI prompt → resume)
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:M, track:platform, type:story]
    ---

    ## Problem

    Some runs require user input mid-run; without this, agent quality degrades or fails.

    ## Proposed solution

    Implement clarification events, UI prompt, user response API, and run resumption.

    ## Dependencies

    - STORY-ORCH-002 — LangGraph orchestrator for Research Notebook app (fan-out, structured output)
- STORY-FE-003 — Runs screens v1 (list + run detail timeline) fixture-driven

    ## Acceptance criteria

    - [ ] Run can emit clarification_needed and pause
- [ ] UI shows prompt and collects answer
- [ ] Run resumes and completes
- [ ] Audit logs include clarification message and response

    ## Test plan

    - [ ] E2E: clarification round-trip on fixture graph

    ## Notes / references

    _None_
