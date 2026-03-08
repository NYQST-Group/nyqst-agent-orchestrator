---
    key: EPIC-ORCH
    title: Orchestration & planning (PlanSet, LangGraph, subagents)
    type: epic
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:critical, size:XL, track:platform, type:epic]
    ---

    ## Problem

    The platform needs a production-grade orchestration layer (PlanSet → tasks → tool execution) with streaming updates.

    ## Proposed solution

    Implement PlanSet schemas, LangGraph orchestration patterns (fan-out, per-node sessions), and event emission aligning to the production event chain.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- EPIC-AGENTS — Agents + skills + MCP tool system + evals

    ## Acceptance criteria

    - [ ] PlanSet/Plan/PlanTask schemas exist and are persisted for runs where applicable
- [ ] LangGraph orchestration can fan-out tasks and stream task updates
- [ ] Run events cover planning/tool/report/clarification categories per spec
- [ ] Frontend can render plan viewer from streamed events

    ## Test plan

    - [ ] Integration: orchestrator run on fixtures yields deterministic event stream
- [ ] Contract: event payloads validate
- [ ] E2E: plan viewer updates in real time

    ## Notes / references

    - Map to COMPRESSED-BUILD-SPEC.md Domain A/B; see proposal docs 04_ORCHESTRATION.md
