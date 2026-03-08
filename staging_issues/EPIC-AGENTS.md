---
    key: EPIC-AGENTS
    title: Agents + skills + MCP tool system + evals
    type: epic
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:XL, track:agents, type:epic]
    ---

    ## Problem

    Agents and skills are a core differentiator. They must be safe, versioned, and testable.

    ## Proposed solution

    Implement a skill registry, MCP tool integration, agent management UI, and evaluation harness (LangSmith-style).

    ## Dependencies

    - EPIC-APPS — Apps system (Dify-style) + context packs + runs
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Skills can be registered with metadata, permissions, and versions
- [ ] MCP tools can be enabled per app/context pack
- [ ] Agent definitions are versioned and auditable
- [ ] Evaluation suite catches regressions on fixed fixtures

    ## Test plan

    - [ ] Unit: tool permission enforcement
- [ ] Integration: MCP tool invocation with sandboxed http client
- [ ] Live: provider tests manual trigger

    ## Notes / references

    - Use research docs for Superagent/Dify patterns; see research/NYQST_Platform_Proposal_Docs/06_SKILLS_AND_CONTEXT_ENGINEERING.md
