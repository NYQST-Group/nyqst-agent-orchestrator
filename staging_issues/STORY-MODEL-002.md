---
    key: STORY-MODEL-002
    title: Frontend: model editor (schema + fields + requirements)
    type: story
    milestone: M6 Models + validation
    labels: [phase:5-models, priority:medium, size:XL, track:frontend, type:story]
    ---

    ## Problem

    Users must be able to define and evolve domain models without code changes.

    ## Proposed solution

    Implement model editor UI with schema builder, field definitions, and evidence requirements.

    ## Dependencies

    - STORY-MODEL-001 — Backend: model registry + versioning + field definitions
- STORY-FE-001 — Implement app shell: routing + left nav + project selector

    ## Acceptance criteria

    - [ ] Create/edit model draft
- [ ] Publish model version
- [ ] Configure evidence requirements per field

    ## Test plan

    - [ ] Vitest: model editor state
- [ ] E2E: create model and publish

    ## Notes / references

    _None_
