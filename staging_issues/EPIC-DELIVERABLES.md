---
    key: EPIC-DELIVERABLES
    title: Deliverables pipeline (reports/websites) + co-generation + diff
    type: epic
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:XL, track:platform, type:epic]
    ---

    ## Problem

    Production systems need deliverables (reports, websites, dashboards) generated with provenance and versioning.

    ## Proposed solution

    Implement deliverable selection, generation pipelines, artifact storage, preview streaming, co-generation jobs, and diff/revision flows.

    ## Dependencies

    - EPIC-ORCH — Orchestration & planning (PlanSet, LangGraph, subagents)
- EPIC-GENUI — GenUI renderer (component registry, GML, charts) for dynamic outputs
- EPIC-APPS — Apps system (Dify-style) + context packs + runs

    ## Acceptance criteria

    - [ ] User can select deliverable type and trigger generation
- [ ] Report preview streams and final artifact stored
- [ ] Website co-generation supported with async pending entities flag
- [ ] Deliverable versions diffable and pin-able to Studio

    ## Test plan

    - [ ] Integration: deliverable generation run emits preview events and stores artifact
- [ ] E2E: generate report deliverable and view it
- [ ] Regression: co-generation pending entities logic

    ## Notes / references

    - Map to COMPRESSED-BUILD-SPEC.md Deliverables domains; see proposal docs 07_DELIVERABLES.md
