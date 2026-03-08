# EPIC-ENTERPRISE — Enterprise baseline: SSO, RBAC, audit logs, billing/metering

- Type: **epic**
- Milestone: `M6-ENTERPRISE`
- Repo alignment: **missing**
- Labels: `milestone:M6`, `enterprise`

## Problem

To reach production in regulated financial workflows, NYQST needs enterprise auth, authorization, auditability, and usage/billing controls.

## Proposed solution

Add OIDC SSO, granular RBAC/ABAC, immutable audit logs, and a Stripe-backed billing/metering system tied to tenant_id and token/tool usage.

## Acceptance criteria

- SSO login works (OIDC) and users are mapped to workspaces/tenants.
- RBAC policies are enforced for core resources (projects, documents, runs, apps).
- Audit log captures authentication, document access, tool calls, and deliverable exports.
- Billing/metering records usage per tenant and supports quotas.

## Test plan

- Integration: RBAC denies/permits correctly; audit records written.
- Billing: usage aggregation jobs run and produce tenant summaries.
