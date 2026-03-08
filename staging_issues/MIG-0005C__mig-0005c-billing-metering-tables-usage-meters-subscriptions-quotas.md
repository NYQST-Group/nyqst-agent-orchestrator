# [MIG-0005C] Billing + metering tables (usage meters, subscriptions, quotas)

**Purpose**
Support usage-based billing, quotas, and per-run cost attribution.

**Target schema (suggested)**
- `billing_accounts` (tenant_id, stripe_customer_id, status, plan)
- `usage_meters` (tenant_id, period_start, period_end, tokens_in/out, cost_cents)
- `quotas` (tenant_id, token_limit, spend_limit, reset_period)
- optional `billing_events` (append-only ledger, if not using RunEvent)

**Acceptance criteria**
- Migration applies cleanly.
- Minimal service layer can:
  - record token usage deltas per run and aggregate to tenant meter
  - enforce quota checks pre-run
