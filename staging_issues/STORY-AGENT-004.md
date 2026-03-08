---
    key: STORY-AGENT-004
    title: Evals harness: fixed fixtures + regression tests for core apps
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:medium, size:L, track:testing, type:story]
    ---

    ## Problem

    Without evals, agent quality regresses and bugs are found late.

    ## Proposed solution

    Implement evaluation harness that runs core app templates on fixed fixtures and checks structured outputs and required events.

    ## Dependencies

    - STORY-APPS-003 — App runner v1: start run, stream events, persist outputs
- STORY-AGENT-002 — MCP integration: stdio tool runner + sandboxed HTTP

    ## Acceptance criteria

    - [ ] Evals run in CI (mocked) and in manual live pipeline (real providers)
- [ ] Evals report deltas and failures clearly
- [ ] Cost caps enforced for live evals

    ## Test plan

    - [ ] CI: evals mocked
- [ ] Manual live: evals real

    ## Notes / references

    _None_
