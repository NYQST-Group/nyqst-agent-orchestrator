---
    key: STORY-BILL-004
    title: Stripe integration + webhook handler (test mode)
    type: story
    milestone: M9 Billing + quota
    labels: [phase:8-prod, priority:low, size:L, track:billing, type:story]
    ---

    ## Problem

    If using Stripe, subscription state must sync via webhooks securely.

    ## Proposed solution

    Implement Stripe service and webhook endpoint reading raw body and verifying signature.

    ## Dependencies

    - STORY-BILL-001 — Billing tables migration (subscriptions, usage_records)

    ## Acceptance criteria

    - [ ] Checkout creates customer/subscription (test mode)
- [ ] Webhooks update subscription status correctly
- [ ] Signature verification uses raw bytes

    ## Test plan

    - [ ] Live: manual webhook test
- [ ] Integration: webhook handler unit tests with signed fixture

    ## Notes / references

    _None_
