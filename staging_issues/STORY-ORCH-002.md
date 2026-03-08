---
    key: STORY-ORCH-002
    title: LangGraph orchestrator for Research Notebook app (fan-out, structured output)
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:critical, size:XL, track:platform, type:story]
    ---

    ## Problem

    Research Notebook requires robust fan-out and aggregation of sources and structured outputs.

    ## Proposed solution

    Implement LangGraph graph with planning, subagent fan-out, tool calls, aggregation, and structured final outputs; stream intermediate events.

    ## Dependencies

    - STORY-ORCH-001 — PlanSet schemas + persistence (Plan, PlanTask linked ordering)
- STORY-AGENT-002 — MCP integration: stdio tool runner + sandboxed HTTP
- STORY-APPS-003 — App runner v1: start run, stream events, persist outputs

    ## Acceptance criteria

    - [ ] Orchestrator runs end-to-end on fixtures without external calls
- [ ] Fan-out tasks run concurrently with per-node sessions
- [ ] Structured output validated and stored as artifact
- [ ] Emits task_update/pending_sources/references_found events

    ## Test plan

    - [ ] Integration: orchestrator fixture run
- [ ] Contract: event payloads validate

    ## Notes / references

    _None_
