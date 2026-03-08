# [BL-012] Billing System
**Labels:** `type:billing`, `phase:4-billing`, `priority:high`, `track:billing`, `size:L`
**Milestone:** M4: Billing & Polish
**Blocked By:** MIG-0005C (billing tables)
**Blocks:** BL-013

**Body:**
## Overview
Port and adapt the Stripe billing system from okestraai/DocuIntelli to the NYQST platform. Implements checkout sessions, webhook processing, subscription management, and per-run usage tracking. Billing unit: 1 run = 1 AI message generation; reads are free.

## Acceptance Criteria
- [ ] `POST /api/v1/billing/checkout` creates a Stripe checkout session for Pro plan ($20/month)
- [ ] `POST /api/v1/billing/webhook` processes Stripe events with signature verification (checkout.session.completed, customer.subscription.updated, customer.subscription.deleted, invoice.payment_succeeded, invoice.payment_failed)
- [ ] `GET /api/v1/billing/subscription` returns current plan, status, and period end date
- [ ] `GET /api/v1/billing/usage` returns run count for current billing period
- [ ] `POST /api/v1/billing/portal` returns Stripe customer portal URL
- [ ] Usage record created per run creation (not per retry -- check retry_attempts)
- [ ] Plan limits enforced: free=5 runs/month + 2 reports, pro=200 runs/month + $0.50/run overage

## Technical Notes
- Source: okestraai/DocuIntelli (public GitHub) -- port Stripe code, adapt from Supabase to SQLAlchemy
- New files: `src/intelli/api/v1/billing.py`, `src/intelli/services/billing/{stripe_service,subscription_service,usage_service}.py`, `src/intelli/db/models/billing.py`
- Billing tables (subscriptions, usage_records) already created in migration 0005 (Phase 0)
- Existing `Run.cost_cents` and `Run.token_usage` JSONB fields available for cost tracking
- Config vars: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_ID

### Sub-Issues

#### [BL-012a] Billing ORM Models and Schemas
**Labels:** `type:infrastructure`, `phase:4-billing`, `priority:high`, `track:billing`, `size:S`
- Create SQLAlchemy models for subscriptions and usage_records tables (already in migration 0005)
- Create Pydantic request/response schemas for billing endpoints

#### [BL-012b] Stripe Service Layer
**Labels:** `type:integration`, `phase:4-billing`, `priority:high`, `track:billing`, `size:M`
- Implement StripeService: create_checkout_session, create_portal_session, construct_webhook_event
- Implement SubscriptionService: create/update/cancel subscription from webhook events
- Implement UsageService: record_usage, get_period_usage, check_quota

#### [BL-012c] Billing API Routes
**Labels:** `type:backend`, `phase:4-billing`, `priority:high`, `track:billing`, `size:S`
- Create all 5 billing endpoints in billing.py router
- Register router in `api/v1/__init__.py`
- Webhook endpoint: no JWT auth, Stripe signature verification only

#### [BL-012d] Billing Integration Tests
**Labels:** `type:test`, `phase:4-billing`, `priority:high`, `track:billing`, `size:S`
- Mock Stripe webhook payloads, verify subscription state transitions
- Test usage recording per run
- Test quota checking logic

## References
- BACKLOG.md: BL-012
- IMPLEMENTATION-PLAN.md: Section 4.1
- Source repo: okestraai/DocuIntelli

---

### Wave 1: Depends on Wave 0 items

---