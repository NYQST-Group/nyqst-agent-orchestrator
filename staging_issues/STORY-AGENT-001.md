---
    key: STORY-AGENT-001
    title: Backend: skill registry + permissions + versioning
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:M, track:agents, type:story]
    ---

    ## Problem

    Skills/tools must be controlled and auditable. Agents should not have arbitrary power.

    ## Proposed solution

    Implement skills table with metadata (name, description, permissions, provider), versions, and enablement per context pack.

    ## Dependencies

    - EPIC-AGENTS — Agents + skills + MCP tool system + evals
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Skills are versioned
- [ ] Skills have declared permissions (web, storage, write models, etc.)
- [ ] Apps/context packs can enable/disable skills
- [ ] Audit records skill usage in runs

    ## Test plan

    - [ ] Integration: create skill, enable in context pack, enforce permissions

    ## Notes / references

    _None_
