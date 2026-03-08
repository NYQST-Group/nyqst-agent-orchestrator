---
    key: STORY-APPS-002
    title: Frontend: App builder wizard (template → publish)
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:high, size:XL, track:frontend, type:story]
    ---

    ## Problem

    Without a builder, Apps remain developer-only artifacts.

    ## Proposed solution

    Implement a multi-step wizard: basics → type → inputs → context pack → engine → outputs → triggers → publish.

    ## Dependencies

    - STORY-FE-002 — Apps screens v1 (gallery + detail tabs) fixture-driven
- STORY-APPS-001 — Backend: apps + app_versions + app_runs data model and API

    ## Acceptance criteria

    - [ ] Wizard supports saving draft and publishing
- [ ] Templates prefill inputs/context/outputs
- [ ] Validation prevents publishing invalid configs
- [ ] Diff preview before publish (optional v1)

    ## Test plan

    - [ ] Vitest: wizard state machine
- [ ] E2E: create and publish app

    ## Notes / references

    _None_
