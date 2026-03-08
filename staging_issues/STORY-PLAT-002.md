---
    key: STORY-PLAT-002
    title: CI: unit/integration/contract/live split + secrets discipline
    type: story
    milestone: M0 Baseline + P0 fixes
    labels: [phase:0-baseline, priority:critical, size:M, track:infra, type:story]
    ---

    ## Problem

    CI cannot run tests that require real API keys; without split, PRs become flaky or blocked.

    ## Proposed solution

    Define pytest markers, update workflows, add manual live workflow, and enforce contract tests.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI

    ## Acceptance criteria

    - [ ] pytest markers defined (unit, integration, live)
- [ ] CI runs unit on push and integration on PR (or your chosen cadence)
- [ ] Live workflow exists and is manual-trigger only
- [ ] No real secrets in repo; CI uses GitHub secrets

    ## Test plan

    - [ ] CI verifies unit+integration pass without live keys
- [ ] Manual live workflow runs provider tests

    ## Notes / references

    _None_
