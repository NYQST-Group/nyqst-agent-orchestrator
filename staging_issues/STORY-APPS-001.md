---
    key: STORY-APPS-001
    title: Backend: apps + app_versions + app_runs data model and API
    type: story
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:critical, size:L, track:platform, type:story]
    ---

    ## Problem

    Apps require versioned definitions and auditable runs.

    ## Proposed solution

    Create tables for apps and app_versions; implement CRUD; ensure runs reference specific app_version.

    ## Dependencies

    - EPIC-APPS — Apps system (Dify-style) + context packs + runs
- TASK-CON-003 — Implement app + context_pack schemas + fixtures
- EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] Published app versions immutable
- [ ] App edit creates new draft version
- [ ] Runs reference app_version and store inputs/context pack
- [ ] Tenant/project scoping enforced

    ## Test plan

    - [ ] Integration: create app, publish, edit to v2, verify immutability

    ## Notes / references

    _None_
