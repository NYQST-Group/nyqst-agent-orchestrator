---
    key: EPIC-APPS
    title: Apps system (Dify-style) + context packs + runs
    type: epic
    milestone: M5 Apps + agents + context packs
    labels: [phase:5-models, priority:critical, size:XL, track:platform, type:epic]
    ---

    ## Problem

    Apps are the unit of repeatable work. Without Apps, the product becomes a pile of screens and tools.

    ## Proposed solution

    Implement app schema, builder UI, versioning/diff, runner, triggers (manual + schedule + event), and output mapping into Studio.

    ## Dependencies

    - EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)
- EPIC-FE-SHELL — Frontend shell (navigation, routes, base screens)
- EPIC-STUDIO — Studio (notebook + infinite canvas) with provenance

    ## Acceptance criteria

    - [ ] Create app from template, publish, run, and view run history
- [ ] App versions are immutable after publish; editing creates new draft
- [ ] App diff shows changes (inputs, context pack, engine, outputs)
- [ ] Run outputs can be pinned to Studio and are auditable

    ## Test plan

    - [ ] Integration: app runs create run logs + artifacts
- [ ] E2E: create app and run it
- [ ] Contract: app config fixtures validate

    ## Notes / references

    - See docs/02_USER_FLOWS_MASTER.md Flow 3
