---
    key: EPIC-PLATFORM
    title: Platform baseline, core primitives, and CI
    type: epic
    milestone: M0 Baseline + P0 fixes
    labels: [phase:0-baseline, priority:critical, size:XL, track:platform, type:epic]
    ---

    ## Problem

    The repo must be a stable baseline so parallel agents can work without breaking each other.

    ## Proposed solution

    Establish repeatable local setup, fix P0 bugs (worker, event ordering, tenancy linkage), and implement professional CI gating.

    ## Dependencies

    _None_

    ## Acceptance criteria

    - [ ] One-command local startup documented and reproducible
- [ ] P0 fixes merged and regression tested
- [ ] CI runs unit + integration + contract checks deterministically
- [ ] Run events are ordered correctly under concurrency
- [ ] Worker processes jobs reliably (no silent fallbacks)

    ## Test plan

    - [ ] Integration tests for worker round trip
- [ ] Concurrency test for RunEvent sequencing
- [ ] CI pipeline green on PRs

    ## Notes / references

    - See docs/04_BUILD_STAGES_TO_PROD.md Stage 0
