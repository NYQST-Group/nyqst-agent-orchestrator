---
    key: EPIC-BILLING
    title: Billing, subscriptions, usage and quota
    type: epic
    milestone: M9 Billing + quota
    labels: [phase:8-prod, priority:low, size:L, track:billing, type:epic]
    ---

    ## Problem

    Production monetization and abuse prevention requires usage tracking and quotas.

    ## Proposed solution

    Implement subscriptions + usage records + quota enforcement and (optional) Stripe integration.

    ## Dependencies

    - EPIC-PLATFORM — Platform baseline, core primitives, and CI
- EPIC-CONTRACTS — Contracts locked (events, apps, bundles, provenance)

    ## Acceptance criteria

    - [ ] Usage recorded per run and linked to tenant/project
- [ ] Quota middleware blocks over-limit usage
- [ ] Billing UI shows plan and usage
- [ ] Stripe integration works in test mode (if enabled)

    ## Test plan

    - [ ] Integration: usage record creation on run completion
- [ ] Integration: quota blocks new runs
- [ ] Live: Stripe webhook validation (manual)

    ## Notes / references

    _None_
