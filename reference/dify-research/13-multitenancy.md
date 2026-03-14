# Dify Multi-Tenancy and Workspace System Analysis

> Deep analysis for clean-room reimplementation.
> Source: Dify upstream codebase (Python/Flask backend).
> Date: 2026-02-01

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Data Model](#2-core-data-model)
3. [Workspace (Tenant) Lifecycle](#3-workspace-tenant-lifecycle)
4. [Account-to-Workspace Relationships](#4-account-to-workspace-relationships)
5. [Data Isolation Patterns](#5-data-isolation-patterns)
6. [Workspace Settings and Configuration](#6-workspace-settings-and-configuration)
7. [Plan and Quota System](#7-plan-and-quota-system)
8. [Feature Gating by Plan](#8-feature-gating-by-plan)
9. [Billing Integration](#9-billing-integration)
10. [Member Management](#10-member-management)
11. [Cross-Tenant Data Sharing](#11-cross-tenant-data-sharing)
12. [SSO and Enterprise Features](#12-sso-and-enterprise-features)
13. [Credit Pool System](#13-credit-pool-system)
14. [Free Plan Tenant Cleanup](#14-free-plan-tenant-cleanup)
15. [Reimplementation Recommendations](#15-reimplementation-recommendations)

---

## 1. Overview

Dify uses a **workspace-based multi-tenancy model** where "tenant" and "workspace" are
synonymous throughout the codebase. Every piece of user-generated data (apps, datasets,
conversations, workflows, provider configs) is scoped to a tenant via a `tenant_id` foreign
key. Users (accounts) can belong to multiple workspaces simultaneously, with one designated
as "current" at any time.

**Key architectural characteristics:**

- Single shared database (PostgreSQL) with application-level tenant isolation
- No row-level security (RLS) at the database layer; all filtering is in SQLAlchemy queries
- Redis used for session state, rate limiting, invitation tokens, and plan caching
- External billing API (separate microservice) for cloud edition; self-hosted skips billing
- Enterprise features gated behind a separate enterprise API service
- Three deployment editions: `SELF_HOSTED`, `CLOUD`, `ENTERPRISE`

---

## 2. Core Data Model

### 2.1 Tenant (Workspace)

The `tenants` table is the root entity for multi-tenancy.

**Fields:**
| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID (PK) | Workspace identifier |
| `name` | VARCHAR(255) | Display name (e.g., "Mark's Workspace") |
| `encrypt_public_key` | TEXT | RSA public key generated per-tenant for encrypting secrets |
| `plan` | VARCHAR(255) | Plan tier string, defaults to `'basic'` |
| `status` | VARCHAR(255) | `'normal'` or `'archive'` |
| `custom_config` | TEXT (JSON) | Workspace-level settings (branding, logo) |
| `created_at` | DATETIME | Creation timestamp |
| `updated_at` | DATETIME | Last modification |

**Design notes:**
- The `plan` column on the tenant table is a local cache/default. The authoritative plan
  comes from the external billing API in cloud edition.
- `encrypt_public_key` is generated via RSA key pair generation at tenant creation time.
  The private key is stored separately (likely in a secrets manager or config).
- `custom_config` is a JSON blob stored as text, accessed via a `custom_config_dict`
  property that handles JSON serialization/deserialization.
- Tenant status is a simple two-state enum: `normal` (active) or `archive` (soft-deleted).

### 2.2 Account (User)

The `accounts` table stores user identity, independent of any workspace.

**Fields:**
| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID (PK) | Account identifier |
| `name` | VARCHAR(255) | Display name |
| `email` | VARCHAR(255) | Login email (indexed) |
| `password` | VARCHAR(255) | Base64-encoded salted hash |
| `password_salt` | VARCHAR(255) | Base64-encoded salt |
| `status` | VARCHAR(16) | `pending`, `uninitialized`, `active`, `banned`, `closed` |
| `interface_language` | VARCHAR(255) | UI language preference |
| `last_login_at` | DATETIME | Last login timestamp |
| `last_active_at` | DATETIME | Activity tracking (updated every 10 minutes) |
| `initialized_at` | DATETIME | When account completed setup |

**Runtime-only fields (not persisted):**
- `role`: The user's role in the *current* workspace, set at load time
- `_current_tenant`: The active workspace object, set at load time

### 2.3 TenantAccountJoin (Membership)

The `tenant_account_joins` table is the many-to-many join between accounts and tenants.

**Fields:**
| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID (PK) | Join record ID |
| `tenant_id` | UUID (FK) | Workspace reference |
| `account_id` | UUID (FK) | Account reference |
| `current` | BOOLEAN | Whether this is the user's active workspace |
| `role` | VARCHAR(16) | Role within this workspace |
| `invited_by` | UUID | Who invited this member |
| `created_at` | DATETIME | When membership was created |

**Constraints:**
- Unique constraint on `(tenant_id, account_id)` -- a user can only be in a workspace once
- Indexed on both `tenant_id` and `account_id` independently
- The `current` field acts as a "selected workspace" flag; when switching workspaces, all
  other joins for the account have `current` set to `false`

### 2.4 AccountIntegrate (OAuth Bindings)

The `account_integrates` table links OAuth/SSO providers to accounts.

**Fields:**
| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID (PK) | Record ID |
| `account_id` | UUID (FK) | Account reference |
| `provider` | VARCHAR(16) | OAuth provider name |
| `open_id` | VARCHAR(255) | Provider-specific user ID |
| `encrypted_token` | VARCHAR(255) | OAuth token (currently empty placeholder) |

**Constraints:**
- Unique on `(account_id, provider)` -- one binding per provider per account
- Unique on `(provider, open_id)` -- each provider ID maps to one account

---

## 3. Workspace (Tenant) Lifecycle

### 3.1 Creation

Workspace creation follows this sequence:

1. **Permission check**: System feature flag `is_allow_create_workspace` must be true
   (unless this is initial setup or admin dashboard creation)
2. **License check** (enterprise): Verify workspace count has not exceeded license limit
3. **Create tenant record**: Insert into `tenants` table with the given name
4. **Create plugin upgrade strategy**: Each tenant gets a default plugin auto-upgrade
   configuration (fix-only, exclude mode)
5. **Generate RSA keypair**: Creates an encryption key pair, stores public key on tenant
6. **Create credit pool**: Initializes a trial credit pool with system-default quota
7. **Create owner membership**: Insert `TenantAccountJoin` with role `owner`
8. **Fire event**: `tenant_was_created` signal is sent for downstream handlers

**Auto-creation pattern**: When a new account registers and workspace creation is allowed,
a workspace named `"{name}'s Workspace"` is automatically created with that account as owner.

### 3.2 Switching

When a user switches workspaces:

1. Verify the user has a `TenantAccountJoin` for the target tenant
2. Verify the target tenant has status `normal` (not archived)
3. Set `current = false` on all other joins for this account
4. Set `current = true` on the target join
5. Update the in-memory `_current_tenant` on the account object

### 3.3 Archival

Tenants can be archived (status set to `archive`). When a user's current tenant is archived,
the system automatically switches them to the first available non-archived tenant. If no
tenants remain, the user gets an `Unauthorized` error.

---

## 4. Account-to-Workspace Relationships

### 4.1 Role System

Five roles exist, forming a hierarchy:

| Role | Permissions |
|------|------------|
| `owner` | Full control, transfer ownership, billing management. Exactly one per workspace. |
| `admin` | Add/manage members, manage all apps and datasets, model configuration |
| `editor` | Create and edit apps and datasets, but cannot manage members |
| `normal` | Read-only access to apps, can use but not modify |
| `dataset_operator` | Special role: can manage datasets/knowledge bases but not apps |

**Permission check helpers** on `TenantAccountRole`:
- `is_privileged_role(role)`: owner or admin
- `is_editing_role(role)`: owner, admin, or editor
- `is_dataset_edit_role(role)`: owner, admin, editor, or dataset_operator
- `is_non_owner_role(role)`: any role except owner (used for invitation validation)

**Action-based permission matrix:**
| Action | Required Role |
|--------|--------------|
| Add member | owner, admin |
| Remove member | owner only |
| Update member role | owner only |
| Transfer ownership | owner only (with email verification) |

### 4.2 Current Workspace Resolution

On every request, the user's current workspace is resolved via `AccountService.load_user()`:

1. Look up `TenantAccountJoin` where `account_id` matches and `current = true`
2. If found, set the tenant on the account
3. If not found, fall back to the first join (ordered by ID) and mark it as current
4. If no joins exist at all, return `None` (user has no workspace)

This ensures a user always has an active workspace as long as they belong to at least one.

### 4.3 Role Resolution on Account

The account's `role` property is a runtime-only field. It is set whenever the current
tenant is assigned:

```
account.set_tenant_id(tenant_id)
  -> queries TenantAccountJoin for (tenant_id, account_id)
  -> sets account.role = TenantAccountRole(join.role)
  -> sets account._current_tenant = tenant
```

This means the role is always relative to the *current* workspace. Convenience properties
like `is_admin_or_owner`, `has_edit_permission`, `is_dataset_editor` delegate to the
`TenantAccountRole` static methods.

---

## 5. Data Isolation Patterns

### 5.1 Application-Level Filtering

Dify does **not** use database-level row-level security. All tenant isolation is enforced
in Python application code via SQLAlchemy query filters.

**Universal pattern**: Every query for tenant-scoped data includes a `tenant_id` filter.

Example from `AppService`:
```
filters = [App.tenant_id == tenant_id, App.is_universal == False]
```

**Entities with `tenant_id` columns** (non-exhaustive):
- `apps` -- Applications
- `datasets` -- Knowledge bases
- `conversations` -- Chat conversations
- `messages` -- Individual messages
- `workflow_runs` -- Workflow execution records
- `workflow_node_executions` -- Individual node executions
- `workflow_app_logs` -- Workflow application logs
- `upload_files` -- User-uploaded files
- `api_tokens` -- API keys
- `provider_configs` -- Model provider configurations
- `tool_providers` -- Tool configurations
- `dataset_permissions` -- Fine-grained dataset access
- `tenant_credit_pools` -- Credit/quota pools
- `account_plugin_permissions` -- Plugin installation permissions

### 5.2 No Automatic Scoping

There is no middleware or base query class that automatically adds `tenant_id` filters.
Each service method is responsible for including the filter. This is a significant
risk surface for tenant data leakage in a reimplementation.

**Recommendation for reimplementation**: Implement automatic tenant scoping at the
repository/query layer. Options include:
- SQLAlchemy event listeners that inject `tenant_id` filters
- A base repository class that requires `tenant_id` for all queries
- Database-level RLS policies as a defense-in-depth measure

### 5.3 API Key Scoping

API tokens (`api_tokens` table) are scoped to both a tenant and an app. The service API
uses the token to resolve the tenant context, ensuring that API callers can only access
resources within the workspace that issued the token.

### 5.4 File Storage Isolation

Uploaded files are stored with paths that include the tenant ID:
```
files/workspaces/{tenant_id}/webapp-logo
free_plan_tenant_expired_logs/{tenant_id}/messages/...
```

This provides namespace isolation in object storage (S3, local filesystem, etc.).

---

## 6. Workspace Settings and Configuration

### 6.1 Custom Configuration

The `Tenant.custom_config` field stores a JSON blob with workspace-level settings:

```json
{
  "remove_webapp_brand": true,
  "replace_webapp_logo": "file-id-here"
}
```

These settings control:
- **Brand removal**: Whether to hide the default branding from web apps
- **Custom logo**: A reference to an uploaded logo file

Custom config is gated behind the `workspace_custom` billing check -- only paid plans
can customize branding.

### 6.2 Plugin Permissions

Each tenant has associated plugin permission settings in `account_plugin_permissions`:

| Setting | Values | Default |
|---------|--------|---------|
| `install_permission` | everyone, admins, noone | everyone |
| `debug_permission` | everyone, admins, noone | noone |

### 6.3 Plugin Auto-Upgrade Strategy

Each tenant has a `tenant_plugin_auto_upgrade_strategies` record:

| Setting | Values | Default |
|---------|--------|---------|
| `strategy_setting` | disabled, fix_only, latest | fix_only |
| `upgrade_mode` | all, partial, exclude | exclude |
| `exclude_plugins` | JSON list of plugin IDs | [] |
| `include_plugins` | JSON list of plugin IDs | [] |
| `upgrade_time_of_day` | integer (hour) | 0 |

### 6.4 Encryption

Each workspace has its own RSA keypair (`encrypt_public_key` on the tenant). This is
used for encrypting sensitive configuration values (API keys, provider credentials) at
rest. The key is generated during tenant creation via `generate_key_pair(tenant.id)`.

---

## 7. Plan and Quota System

### 7.1 Plan Tiers

Dify cloud edition defines three plan tiers in the `CloudPlan` enum:

| Plan | Description |
|------|------------|
| `sandbox` | Free tier with limited features |
| `professional` | Individual paid plan |
| `team` | Collaborative paid plan |

The tenant table has a `plan` column defaulting to `'basic'`, but the authoritative plan
in cloud edition comes from the external billing API.

### 7.2 Resource Quotas

The `FeatureModel` defines per-tenant quotas that vary by plan:

| Resource | Description | Sandbox Default |
|----------|-------------|-----------------|
| `members` | Max workspace members | 1 |
| `apps` | Max applications | 10 |
| `vector_space` | Knowledge base storage (MB) | 5 |
| `documents_upload_quota` | Max documents | 50 |
| `annotation_quota_limit` | Max annotations | 10 |
| `knowledge_rate_limit` | Requests per minute to knowledge API | 10 |
| `trigger_event` | Event triggers per billing period | 3000 |
| `api_rate_limit` | API calls per billing period | 5000 |

These quotas are populated from the billing API for cloud edition. Self-hosted installations
use the hardcoded defaults (effectively unlimited for most resources).

### 7.3 Credit Pool System

Each tenant has a credit pool (`tenant_credit_pools` table) for metered usage:

| Field | Type | Purpose |
|-------|------|---------|
| `tenant_id` | UUID | Workspace reference |
| `quota_limit` | INTEGER | Total credits allocated |
| `quota_used` | INTEGER | Credits consumed |
| `pool_type` | VARCHAR | `'trial'` or `'paid'` |

The `remaining_credits` property is computed as `quota_limit - quota_used`. Credit
deduction uses an atomic SQL UPDATE to prevent race conditions:

```sql
UPDATE tenant_credit_pools
SET quota_used = quota_used + :credits
WHERE tenant_id = :tenant_id AND pool_type = :pool_type
```

### 7.4 Quota Reset

Some quotas (trigger events, API rate limits) have a `reset_date` field indicating when
the counter resets. The `next_credit_reset_date` on `FeatureModel` tracks the next billing
period reset.

---

## 8. Feature Gating by Plan

### 8.1 Feature Resolution Flow

`FeatureService.get_features(tenant_id)` builds the complete feature set:

1. **Start with defaults**: Hardcoded `FeatureModel` with minimal quotas
2. **Apply environment config**: Override flags from `dify_config` (e.g.,
   `MODEL_LB_ENABLED`, `DATASET_OPERATOR_ENABLED`)
3. **Apply billing API** (cloud only): If `BILLING_ENABLED`, fetch quotas, limits,
   and subscription info from the billing microservice
4. **Apply enterprise info** (enterprise only): If `ENTERPRISE_ENABLED`, fetch workspace
   member limits and enable additional features

### 8.2 Billing Resource Check Decorators

Controller endpoints use decorators to enforce plan limits:

**`@cloud_edition_billing_resource_check(resource)`**

Checks current usage against plan limits before allowing the action. Resources checked:
- `"members"` -- workspace member count
- `"apps"` -- application count
- `"vector_space"` -- knowledge base storage
- `"documents"` -- document upload count
- `"workspace_custom"` -- branding customization
- `"annotation"` -- annotation count

Returns HTTP 403 if the limit is reached.

**`@cloud_edition_billing_knowledge_limit_check(resource)`**

Specifically blocks sandbox-tier users from certain knowledge base operations (e.g.,
adding segments).

**`@cloud_edition_billing_rate_limit_check(resource)`**

Uses Redis sorted sets for sliding-window rate limiting on knowledge API requests.
Tracks request timestamps in a 60-second window and compares against the plan's limit.

### 8.3 Plan-Gated Features

| Feature | Sandbox | Professional | Team |
|---------|---------|-------------|------|
| Custom branding | No | Yes | Yes |
| Copyright removal | No | Yes | Yes |
| Model load balancing | Config-dependent | Config-dependent | Config-dependent |
| Dataset operator role | Config-dependent | Config-dependent | Config-dependent |
| Knowledge segment add | No | Yes | Yes |
| Workspace transfer | No | Yes | Yes |
| Docs processing mode | Standard only | Standard + high quality | Standard + high quality |

### 8.4 Enterprise-Only Features

When `ENTERPRISE_ENABLED`:
- WebApp copyright removal is always enabled
- Knowledge pipeline publishing is enabled
- Workspace member limits come from the enterprise license
- SSO enforcement for signin
- Custom branding (application title, login logo, workspace logo, favicon)
- WebApp authentication (SSO, email code login, email password login)
- Plugin installation scope control

---

## 9. Billing Integration

### 9.1 Architecture

Billing is implemented as an **external microservice** accessed via HTTP. The `BillingService`
class is a thin HTTP client that forwards requests to `BILLING_API_URL`, authenticated
with `BILLING_API_SECRET_KEY`.

This design completely decouples billing logic from the main application, allowing:
- Self-hosted editions to run with `BILLING_ENABLED=false` (no billing code executes)
- Cloud edition to use a proprietary billing backend
- Clean separation of subscription management from application logic

### 9.2 Billing API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/subscription/info` | GET | Get full subscription details + resource limits |
| `/subscription/payment-link` | GET | Get Stripe checkout link for plan upgrade |
| `/subscription/plan/batch` | POST | Bulk fetch plans for multiple tenants |
| `/subscription/knowledge-rate-limit` | GET | Get knowledge API rate limit for plan |
| `/subscription/cleanup/whitelist` | GET | Get tenants exempt from free plan cleanup |
| `/tenant-feature-usage/info` | GET | Get trigger event and API rate limit usage |
| `/tenant-feature-usage/usage` | POST | Record feature usage (with refund support) |
| `/tenant-feature-usage/refund` | POST | Refund a previous usage charge |
| `/invoices` | GET | Get customer portal link for invoices |
| `/model-provider/payment-link` | GET | Get payment link for model provider credits |
| `/account/` | DELETE | Delete billing account |
| `/account/in-freeze` | GET | Check if email is in 30-day deletion freeze |
| `/education/verify` | GET | Verify education discount eligibility |
| `/education/` | POST | Activate education discount |
| `/compliance/download` | POST | Get compliance document download link |
| `/partners/{key}/tenants` | PUT | Sync partner tenant bindings |

### 9.3 Caching Strategy

Plan data is cached in Redis with a 10-minute TTL:
- Key pattern: `tenant_plan:{tenant_id}`
- Bulk fetch API supports up to 200 tenant IDs per request
- `get_plan_bulk_with_cache()` checks Redis first, falls back to API for cache misses
- Cache is invalidated when members are added/removed (`clean_billing_info_cache`)

### 9.4 Usage Tracking

Feature usage (trigger events, API calls) is tracked via the billing API:
- `update_tenant_feature_plan_usage(tenant_id, feature_key, delta)` records usage
- Returns a `history_id` that can be used for refunds
- `refund_tenant_feature_plan_usage(history_id)` reverses a charge

---

## 10. Member Management

### 10.1 Invitation Flow

1. **Inviter** must have `owner` or `admin` role (checked via `check_member_permission`)
2. **Check workspace member limit**: Enterprise license workspace member count, or
   billing API member limit for cloud edition
3. **Email normalization**: All emails are lowercased before processing
4. **New user path**:
   a. Create account with status `PENDING`
   b. Create `TenantAccountJoin` with the specified role
   c. Switch the new user's current workspace to the inviting tenant
5. **Existing user path**:
   a. If user already in tenant and status is `PENDING`, allow re-sending invitation
   b. If user already in tenant and status is `ACTIVE`, raise `AccountAlreadyInTenantError`
   c. If user not in tenant, create the join record
6. **Generate invitation token**: UUID stored in Redis with configurable expiry
   (`INVITE_EXPIRY_HOURS`)
7. **Send invitation email**: Async Celery task with activation URL

### 10.2 Invitation Token Storage

Tokens are stored in Redis with two key patterns:
- `member_invite:token:{token}` -- maps to JSON `{account_id, email, workspace_id}`
- `member_invite_token:{workspace_id}, {email_hash}:{token}` -- alternative lookup path

### 10.3 Member Removal

- Only the `owner` can remove members
- Cannot remove yourself (`CannotOperateSelfError`)
- Deletes the `TenantAccountJoin` record
- Invalidates billing cache if billing is enabled

### 10.4 Role Changes

- Only the `owner` can change roles
- Cannot change your own role
- If new role is `owner`, the current owner is automatically demoted to `admin`
- This ensures exactly one owner per workspace at all times

### 10.5 Ownership Transfer

A multi-step verification process:
1. Owner requests transfer, triggering an email verification code
2. Owner enters code to get a confirmation token
3. Owner confirms transfer with the token and target member ID
4. System: demotes old owner to admin, promotes target to owner
5. Notification emails sent to both old and new owners

Rate limited to 1 attempt per 60 seconds, with a 5-error lockout.

---

## 11. Cross-Tenant Data Sharing

### 11.1 No Direct Cross-Tenant Sharing

Dify does **not** support sharing apps, datasets, or configurations between workspaces.
Each workspace is a fully isolated data silo.

### 11.2 Intra-Workspace Dataset Permissions

Within a single workspace, datasets have a three-tier permission model:

| Permission | Behavior |
|-----------|----------|
| `only_me` | Only the creator can access |
| `all_team_members` | All workspace members can access |
| `partial_members` | Specific members granted access via `dataset_permissions` table |

The `dataset_permissions` table stores per-user grants:

| Field | Type | Purpose |
|-------|------|---------|
| `dataset_id` | UUID | Dataset reference |
| `account_id` | UUID | User granted access |
| `tenant_id` | UUID | Workspace context |
| `has_permission` | BOOLEAN | Permission flag |

Permission checks cascade through the role hierarchy: owners and admins bypass dataset
permission checks entirely. Editors and dataset_operators must pass the permission check.
Normal users can only access `all_team_members` datasets.

### 11.3 Recommended Apps (Global Catalog)

The `recommended_apps` table provides a global app catalog that is **not tenant-scoped**.
These are curated applications visible across all workspaces as templates/inspirations.
They reference an `app_id` but are managed by platform administrators.

### 11.4 Universal Apps

Apps can be marked as `is_universal = True`, which makes them available outside the
normal tenant scope. This appears to be used for platform-level shared applications.
Standard app queries explicitly filter `is_universal == False` to exclude them from
regular workspace listings.

---

## 12. SSO and Enterprise Features

### 12.1 Enterprise API Architecture

Enterprise features are accessed via a separate API service (`EnterpriseRequest`),
similar to the billing API pattern. The `EnterpriseService` class is an HTTP client
that communicates with the enterprise backend.

### 12.2 SSO Enforcement

Enterprise edition supports enforced SSO for:
- **Console signin**: `sso_enforced_for_signin` + `sso_enforced_for_signin_protocol`
- **WebApp access**: Per-app access mode control (`public`, `private`, `private_all`,
  `sso_verified`)

When SSO is enforced, email/password login can be disabled entirely.

### 12.3 WebApp Authentication

Enterprise edition provides granular webapp auth:
- `allow_sso`: Enable SSO for webapp access
- `allow_email_code_login`: Enable passwordless email code login
- `allow_email_password_login`: Enable traditional email/password
- Per-app access mode: Controls who can access each published webapp

### 12.4 License Management

Enterprise licenses track:
- `status`: none, inactive, active, expiring, expired, lost
- `expired_at`: License expiration date
- `workspaces`: Workspace count limit (enabled, size, limit)

The license workspace limit gates workspace creation. When the limit is reached,
`WorkspacesLimitExceededError` is raised.

### 12.5 Branding

Enterprise supports custom branding:
- Application title
- Login page logo
- Workspace logo
- Favicon

These are configured at the enterprise level and applied globally.

### 12.6 Plugin Installation Control

Enterprise can restrict plugin installation:
- `plugin_installation_scope`: none, official_only, official_and_specific_partners, all
- `restrict_to_marketplace_only`: Force all installs through the marketplace

---

## 13. Credit Pool System

### 13.1 Pool Types

Each tenant can have multiple credit pools distinguished by `pool_type`:
- `trial`: Default pool created at workspace creation, funded with `HOSTED_POOL_CREDITS`
- `paid`: Purchased credits for paid plans

### 13.2 Credit Check and Deduction

The `CreditPoolService` provides atomic credit operations:

1. **Check availability**: `check_credits_available(tenant_id, credits_required)` --
   read-only check without deduction
2. **Check and deduct**: `check_and_deduct_credits(tenant_id, credits_required)` --
   atomic deduction using SQL UPDATE, returns actual credits deducted (may be less than
   requested if pool is partially depleted)

The deduction uses a separate SQLAlchemy `Session` for transaction isolation.

### 13.3 Display in Workspace Info

The workspace info endpoint shows credit information:
- Prefers `paid` pool if it exists
- Falls back to `trial` pool
- Exposes `trial_credits` (total) and `trial_credits_used` (consumed)

---

## 14. Free Plan Tenant Cleanup

### 14.1 Purpose

The `ClearFreePlanTenantExpiredLogs` service is a batch job that purges old data from
sandbox (free) tier tenants. This enforces data retention limits on the free tier.

### 14.2 Cleanup Scope

The cleanup targets, in order:
1. **Messages**: Individual conversation messages older than `days` threshold
2. **Message-related tables**: Feedback, files, annotations, chains, agent thoughts,
   saved messages, annotation hit histories
3. **Conversations**: Conversations older than the threshold
4. **Workflow node executions**: Individual workflow step records
5. **Workflow runs**: Complete workflow execution records
6. **Workflow app logs**: Application-level workflow logs

### 14.3 Data Preservation

Before deletion, all records are serialized to JSON and saved to object storage:
```
free_plan_tenant_expired_logs/{tenant_id}/{table_name}/{date}-{timestamp}.json
```

This provides a recovery path if data is needed after cleanup.

### 14.4 Execution Model

- Processes tenants in parallel using a `ThreadPoolExecutor` with 10 workers
- Iterates through tenants by creation date, dynamically adjusting batch intervals
  to target ~100 tenants per batch
- Only processes tenants where billing reports `sandbox` plan (or billing is disabled)
- Supports a whitelist from the billing API for exempt tenants

---

## 15. Reimplementation Recommendations

### 15.1 Improve Data Isolation

Dify's reliance on application-level `tenant_id` filtering is fragile. For a
reimplementation:

1. **Add database-level RLS** as defense-in-depth. Set `tenant_id` in the session
   context and have PostgreSQL enforce row filtering automatically.
2. **Create a base repository class** that requires `tenant_id` for all queries,
   making it impossible to accidentally issue unscoped queries.
3. **Audit query generation** to ensure every data-access path includes tenant scoping.

### 15.2 Simplify the Role Model

Dify's five-role system with special-case `dataset_operator` creates complexity. Consider:

- Start with three roles: owner, admin, member
- Add granular permissions via a capability-based system rather than role-based if
  fine-grained control is needed later
- Use a permissions table rather than hardcoded role checks scattered throughout services

### 15.3 Internalize Billing

Dify's external billing API is appropriate for their SaaS model but adds operational
complexity. For a smaller deployment:

- Start with a local quota/limits table per tenant
- Implement plan enforcement in application middleware
- Add Stripe integration when needed, but keep the quota state local

### 15.4 Simplify Workspace Switching

The `current` flag on `TenantAccountJoin` is clever but creates write-heavy operations
on every workspace switch. Consider:

- Store the current workspace in the JWT token or session instead
- Eliminate the `current` column and database writes on switch
- Use Redis or cookie-based workspace selection

### 15.5 Improve Invitation Security

Dify stores invitation tokens in Redis with a simple UUID. Consider:

- Signed invitation tokens (JWT) with embedded expiry and workspace context
- Single-use tokens that are invalidated on first use
- Rate limiting invitation generation per workspace

### 15.6 Add Tenant Lifecycle Events

Dify fires `tenant_was_created` but lacks comprehensive lifecycle events. Add events for:

- Tenant archived/restored
- Member added/removed
- Role changed
- Plan changed
- Settings updated

These enable audit logging, analytics, and integration hooks.

### 15.7 Consider Multi-Database Tenancy

For true isolation at scale, consider per-tenant databases or schemas rather than
shared-table tenancy. This provides:

- Stronger isolation guarantees
- Per-tenant backup/restore
- Independent scaling
- Cleaner data lifecycle management

The trade-off is operational complexity, but tools like Citus or schema-per-tenant
patterns on PostgreSQL can mitigate this.

---

## Appendix: Key Source Files

| File | Purpose |
|------|---------|
| `api/models/account.py` | Tenant, Account, TenantAccountJoin, role enums |
| `api/models/model.py` | App model with tenant_id, RecommendedApp |
| `api/models/dataset.py` | Dataset with tenant_id, DatasetPermission |
| `api/services/account_service.py` | TenantService, AccountService, RegisterService |
| `api/services/feature_service.py` | FeatureModel, plan feature resolution |
| `api/services/billing_service.py` | External billing API client |
| `api/services/workspace_service.py` | Workspace info assembly |
| `api/services/credit_pool_service.py` | Credit pool management |
| `api/services/enterprise/enterprise_service.py` | Enterprise API client |
| `api/controllers/console/workspace/workspace.py` | Workspace REST endpoints |
| `api/controllers/console/workspace/members.py` | Member management endpoints |
| `api/controllers/console/wraps.py` | Billing check decorators |
| `api/enums/cloud_plan.py` | CloudPlan enum (sandbox, professional, team) |
| `api/services/clear_free_plan_tenant_expired_logs.py` | Free tier data cleanup |
