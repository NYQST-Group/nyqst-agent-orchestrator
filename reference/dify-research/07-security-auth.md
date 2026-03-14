# Dify Security & Authentication System — Clean-Room Requirements Document

**Source codebase**: `~/nyqst-dify/upstream-dify/api/`
**Analysis date**: 2026-02-01
**Purpose**: Architectural requirements for independent reimplementation

---

## Table of Contents

1. [Authentication Flows](#1-authentication-flows)
2. [Authorization Model (RBAC)](#2-authorization-model-rbac)
3. [API Key Management](#3-api-key-management)
4. [Rate Limiting](#4-rate-limiting)
5. [CORS Configuration](#5-cors-configuration)
6. [Session & Token Management](#6-session--token-management)
7. [Middleware Chain](#7-middleware-chain)
8. [Multi-Tenancy & Data Isolation](#8-multi-tenancy--data-isolation)
9. [Password Hashing & Invite Flows](#9-password-hashing--invite-flows)
10. [Security Headers, CSRF & Transport Security](#10-security-headers-csrf--transport-security)
11. [Secrets & Credential Encryption at Rest](#11-secrets--credential-encryption-at-rest)
12. [Libraries Used](#12-libraries-used)
13. [Design Decisions & Trade-offs](#13-design-decisions--trade-offs)
14. [Requirements Summary](#14-requirements-summary)

---

## 1. Authentication Flows

Dify supports multiple authentication paths, gated by feature flags and the deployment edition (SELF_HOSTED vs CLOUD).

### 1.1 Email + Password Login

**Flow**:
1. Client POSTs `{email, password, remember_me, invite_token?}` to `/console/api/login`
2. Password field arrives Base64-encoded from frontend; a decorator decodes it before validation
3. Server normalizes email to lowercase (with case-fallback for legacy records)
4. Checks billing freeze status (CLOUD edition only)
5. Checks login error rate limit in Redis (max 5 failed attempts, 24h lockout window)
6. If `invite_token` is present, validates it against Redis-stored invitation data
7. Calls `AccountService.authenticate()` which loads the account by email, checks status (banned accounts rejected), verifies password via PBKDF2-HMAC comparison
8. On success: generates a `TokenPair` (access_token JWT + refresh_token + CSRF token)
9. Sets all three tokens as HTTP cookies on the response (NOT in the response body)
10. On failure: increments the per-email error counter in Redis

**Key files**:
- Controller: `controllers/console/auth/login.py` — `LoginApi.post()`
- Service: `services/account_service.py` — `AccountService.authenticate()`, `AccountService.login()`
- Password: `libs/password.py` — `compare_password()`
- Decorators: `controllers/console/wraps.py` — `setup_required`, `email_password_login_enabled`, `decrypt_password_field`

### 1.2 Email Code Login (Passwordless)

**Flow**:
1. Client POSTs email to `/console/api/email-code-login` to request a code
2. Server generates a 6-digit numeric code, stores it via `TokenManager` in Redis with a typed key (`email_code_login:token:{uuid}`)
3. Sends the code via Celery async task (email)
4. Client POSTs `{email, code, token}` to `/console/api/email-code-login/validity`
5. Server verifies the token exists in Redis, email matches, code matches
6. Revokes the one-time token
7. If no account exists and registration is allowed, creates account + tenant
8. Issues `TokenPair` as cookies

**Rate limiting**: Uses `RateLimiter` class (Redis ZSET-based sliding window), max 3 attempts per 5 minutes per email. Also has IP-based rate limiting for email sends (per-minute burst + per-hour escalating freeze).

### 1.3 OAuth (GitHub, Google)

**Flow**:
1. GET `/console/api/oauth/login/{provider}` redirects to the OAuth provider's authorization URL
2. OAuth callback at `/console/api/oauth/authorize/{provider}` exchanges code for access token
3. Fetches user info (id, name, email) from provider
4. Looks up account by `(provider, open_id)` in `account_integrates` table, falling back to email match
5. If no account and registration allowed: creates account via `RegisterService.register()`
6. Links the OAuth identity to the account via `AccountIntegrate` record
7. Issues `TokenPair` as cookies and redirects to console web URL

**Providers implemented**: GitHub (user:email scope), Google (openid email scope). Both use `httpx` for HTTP calls. Provider instances are lazily created from config (`GITHUB_CLIENT_ID/SECRET`, `GOOGLE_CLIENT_ID/SECRET`).

**Libraries**: `httpx` for OAuth HTTP calls, `libs/oauth.py` for provider abstraction.

### 1.4 WebApp Authentication

Separate from console auth. Three modes based on app access settings:
- **Public**: No auth required; anonymous `EndUser` created per session
- **Internal**: Email/password or email-code login against the same `accounts` table, but issues a different JWT with `token_source: "webapp_login_token"` and longer expiry (24x the console access token)
- **External (SSO)**: Enterprise SSO verified; delegates to `EnterpriseService.WebAppAuth`

**Key file**: `services/webapp_auth_service.py`

### 1.5 Admin API Key

A static API key (`ADMIN_API_KEY`) configurable via environment. When enabled and matched against the `Authorization: Bearer` header:
- Bypasses normal JWT verification
- Uses `X-WORKSPACE-ID` header to resolve the tenant and impersonate the owner account
- Also bypasses CSRF checks

### 1.6 Initial Setup

First-run setup is gated by `DifySetup` table. If no setup record exists:
- `setup_required` decorator blocks most endpoints
- A setup endpoint creates the first account + tenant + `DifySetup` row
- Rollback on failure deletes all created records

---

## 2. Authorization Model (RBAC)

### 2.1 Role Hierarchy

Roles are defined in `TenantAccountRole` (StrEnum):

| Role | Capabilities |
|------|-------------|
| `owner` | Full control. One per tenant. Can transfer ownership. |
| `admin` | Manage members (add), manage settings. Cannot remove members or transfer ownership. |
| `editor` | Create/edit apps, workflows, datasets |
| `normal` | View-only for apps/workflows, no dataset access |
| `dataset_operator` | Like normal but with dataset create/edit permissions |

### 2.2 Permission Check Methods

Role checks are implemented as static methods on `TenantAccountRole`:
- `is_privileged_role(role)` — owner or admin
- `is_editing_role(role)` — owner, admin, or editor
- `is_dataset_edit_role(role)` — owner, admin, editor, or dataset_operator

And as properties on the `Account` model:
- `is_admin_or_owner` — delegates to `is_privileged_role`
- `has_edit_permission` — delegates to `is_editing_role`
- `is_dataset_editor` — delegates to `is_dataset_edit_role`

### 2.3 Decorator-Based Enforcement

Authorization is enforced via view decorators:
- `login_required` — from `libs/login.py`, checks `current_user.is_authenticated` + CSRF
- `account_initialization_required` — ensures account status is not UNINITIALIZED
- `edit_permission_required` — checks `current_user.has_edit_permission`, returns 403
- `is_admin_or_owner_required` — checks `current_user.is_admin_or_owner`, returns 403

### 2.4 Member Management Permissions

`TenantService.check_member_permission()` enforces:
- **add**: owner or admin
- **remove**: owner only
- **update**: owner only
- Cannot operate on self (prevents self-removal/demotion)

### 2.5 Edition-Based Gating

Decorators restrict endpoints by deployment edition:
- `only_edition_cloud` — CLOUD only
- `only_edition_self_hosted` — SELF_HOSTED only
- `only_edition_enterprise` — Enterprise license required
- `enterprise_license_required` — checks license status (INACTIVE/EXPIRED/LOST triggers force-logout)
- `cloud_edition_billing_enabled` — requires billing feature flag

---

## 3. API Key Management

### 3.1 Token Types

`ApiToken` model stores two types of API keys:
- `type = "app"` — associated with a specific app (`app_id`), used for Service API access
- `type = "dataset"` — associated with a tenant (`tenant_id`), used for Dataset API access

### 3.2 Key Generation

`ApiToken.generate_api_key(prefix, n)` generates keys with:
- A configurable prefix (e.g., `"app-"`, `"ds-"`)
- Random alphanumeric suffix of length `n`
- Uniqueness check via database query in a loop

### 3.3 Validation Flow

`validate_and_get_api_token(scope)` in `controllers/service_api/wraps.py`:
1. Extracts `Authorization: Bearer <token>` header
2. Queries `api_tokens` table by `(token, type=scope)`
3. Atomically updates `last_used_at` (with 1-minute debounce to avoid write amplification)
4. Returns the `ApiToken` record or raises 401

### 3.4 App Token Decorator

`validate_app_token` additionally:
- Loads the associated `App` and checks status/enable_api
- Loads the `Tenant` and checks it is not archived
- Optionally resolves an end-user from query/json/form params
- If no end-user context needed, impersonates the tenant owner for downstream service calls

### 3.5 Dataset Token Decorator

`validate_dataset_token` additionally:
- Extracts `dataset_id` from URL path args
- Validates dataset exists and has `enable_api = true`
- Logs in as the tenant owner for the duration of the request

---

## 4. Rate Limiting

### 4.1 Login Rate Limiting

- **Mechanism**: Redis key `login_error_rate_limit:{email}` with integer counter
- **Threshold**: 5 failed attempts
- **Lockout**: 24 hours (configurable via `LOGIN_LOCKOUT_DURATION`)
- **Reset**: On successful login

Similar patterns exist for forgot-password (5 attempts, 24h), email-register (5 attempts, 24h), change-email (5 attempts, 24h), owner-transfer (5 attempts, 24h).

### 4.2 Email Send IP Rate Limiting

`AccountService.is_email_send_ip_limit(ip_address)`:
- Per-minute counter in Redis
- If burst exceeded: check hourly escalation counter
- If hourly limit hit: freeze the IP for 1 hour
- Two-tier escalation: first offense = 10 minute cooldown, second = 1 hour freeze

### 4.3 Email Code Login Rate Limiting

Uses `RateLimiter` class (Redis ZSET sliding window):
- 3 attempts per 5-minute window per email
- Email send rate: 1 per 60 seconds per email

### 4.4 Knowledge Base API Rate Limiting

`cloud_edition_billing_rate_limit_check("knowledge")`:
- Redis ZSET sliding window (60-second window)
- Limit is tenant-specific, loaded from feature/billing service
- Logs rate limit events to `rate_limit_logs` table

### 4.5 App Invocation Concurrency Limiting

`core/app/features/rate_limiting/rate_limit.py` — `RateLimit` class:
- Redis HASH-based active request tracking
- Per-app configurable max concurrent requests (`api_rpm`, `api_rph` on App model)
- Stale request cleanup (10-minute timeout)
- Request counting recalculation every 5 minutes
- Wraps generators to auto-release on completion

### 4.6 Annotation Import Rate Limiting

Dual-tier via decorators in `controllers/console/wraps.py`:
- Per-minute: configurable (`ANNOTATION_IMPORT_RATE_LIMIT_PER_MINUTE`, default 5)
- Per-hour: configurable (`ANNOTATION_IMPORT_RATE_LIMIT_PER_HOUR`, default 20)
- Plus concurrency limit (`ANNOTATION_IMPORT_MAX_CONCURRENT`)

### 4.7 Redis Fallback

The `@redis_fallback(default_return=...)` decorator ensures rate limiting degrades gracefully if Redis is unavailable — returns the default value instead of raising.

---

## 5. CORS Configuration

Configured in `extensions/ext_blueprints.py` using `flask-cors`.

### 5.1 Per-Blueprint CORS

| Blueprint | Origins | Credentials | Headers |
|-----------|---------|-------------|---------|
| `service_api` | `*` (default) | No | Content-Type, X-App-Code, X-App-Passport, Authorization |
| `web` (default) | `WEB_API_CORS_ALLOW_ORIGINS` | Yes | + X-CSRF-Token |
| `web` (embed endpoints) | `WEB_API_CORS_ALLOW_ORIGINS` | No | Content-Type, X-App-Code only |
| `console` | `CONSOLE_CORS_ALLOW_ORIGINS` | Yes | + Authorization, X-CSRF-Token |
| `files` | `*` (default) | No | Content-Type, X-App-Code, X-App-Passport, X-CSRF-Token |
| `inner_api` | None (no CORS) | — | — |
| `trigger` | `*` (default) | No | Content-Type, Authorization, X-App-Code |

### 5.2 Exposed Headers

All CORS-enabled blueprints expose: `X-Version`, `X-Env`, `X-Trace-Id`

### 5.3 Configuration

- `CONSOLE_CORS_ALLOW_ORIGINS` — defaults to `CONSOLE_WEB_URL`, comma-separated list
- `WEB_API_CORS_ALLOW_ORIGINS` — defaults to `*`, comma-separated list
- CORS is applied once per blueprint via `_apply_cors_once()` to prevent duplicate initialization

---

## 6. Session & Token Management

### 6.1 Access Token (JWT)

- **Algorithm**: HS256 (symmetric, single key)
- **Signing key**: `SECRET_KEY` from environment
- **Payload**: `{user_id, exp, iss: EDITION, sub: "Console API Passport"}`
- **Expiry**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 minutes)
- **Delivery**: HttpOnly, Secure, SameSite=Lax cookie named `access_token`
- **Fallback**: Also accepts `Authorization: Bearer` header (for API clients)
- **Library**: PyJWT

### 6.2 Refresh Token

- **Format**: `secrets.token_hex(64)` — 128-character hex string
- **Storage**: Redis with key `refresh_token:{token}` -> `account_id` (and reverse mapping `account_refresh_token:{account_id}` -> `token`)
- **Expiry**: Configurable via `REFRESH_TOKEN_EXPIRE_DAYS` (default 30 days)
- **Delivery**: HttpOnly, Secure, SameSite=Lax cookie named `refresh_token`
- **Rotation**: On refresh, old token is deleted and new one issued (single-use)
- **One-per-account**: Only one refresh token active per account at a time

### 6.3 CSRF Token

- **Format**: JWT (HS256) with `{exp, sub: user_id}`
- **Expiry**: Same as access token
- **Delivery**: Non-HttpOnly cookie named `csrf_token` (so JS can read it)
- **Verification**: Client must send it back via `X-CSRF-Token` header
- **Double-submit pattern**: Header value must match cookie value, and JWT must decode with matching `sub`

### 6.4 Cookie Naming

When HTTPS is used and no custom cookie domain is set, cookies use the `__Host-` prefix (e.g., `__Host-access_token`) for additional browser security enforcement.

### 6.5 Token Extraction Priority

Access token: Cookie first, then `Authorization: Bearer` header fallback.
Refresh token: Cookie only.
CSRF token: `X-CSRF-Token` header (compared against cookie).

### 6.6 Webapp Tokens

- Separate cookie name: `webapp_access_token`
- Passport tokens: Per-app cookie `passport-{app_code}` or `X-App-Passport` header
- EndUser JWTs have `{end_user_id}` in payload, no CSRF

### 6.7 One-Time Tokens (Redis-backed)

`TokenManager` handles various one-time tokens:
- Types: `reset_password`, `email_code_login`, `email_register`, `change_email`, `owner_transfer`, `account_deletion`
- Storage: Redis with key `{type}:token:{uuid4}` -> JSON data
- Expiry: Per-type configurable (e.g., `RESET_PASSWORD_TOKEN_EXPIRY_MINUTES`)
- One active token per account per type (previous is revoked on new generation)
- Contains embedded verification codes (6-digit numeric)

---

## 7. Middleware Chain

### 7.1 Flask-Login Request Loader

`extensions/ext_login.py` — `load_user_from_request()`:

The primary authentication middleware. Dispatches based on `request.blueprint`:

1. **Admin API key check** (all blueprints): If `ADMIN_API_KEY_ENABLE` and token matches, resolve workspace from `X-WORKSPACE-ID` header, return owner account
2. **`console` / `inner_api` blueprint**: Decode JWT, extract `user_id`, reject if `token_source` is set (webapp tokens not valid here), load account via `AccountService.load_user()`
3. **`web` blueprint**: Try webapp passport cookie/header first, then fall back to regular auth. Decodes JWT, extracts `end_user_id`, loads `EndUser`
4. **`mcp` blueprint**: Resolves `server_code` from URL path, looks up `AppMCPServer`, returns associated `EndUser`

### 7.2 Account Loading

`AccountService.load_user(account_id)`:
1. Loads account from DB
2. Rejects if banned
3. Resolves current tenant (from `current=True` join, or first available)
4. Updates `last_active_at` every 10 minutes (debounced)
5. Refreshes and detaches from session for cross-request safety

### 7.3 Decorator Stack (typical console endpoint)

```
@setup_required                          # Ensure initial setup complete
@login_required                          # Verify JWT + check CSRF
@account_initialization_required         # Ensure account not UNINITIALIZED
@edit_permission_required                # Check RBAC role (optional)
@cloud_edition_billing_resource_check()  # Check billing quotas (optional)
```

### 7.4 Inner API Authentication

Separate from Flask-Login. Uses `X-Inner-Api-Key` header compared against `INNER_API_KEY` config:
- `billing_inner_api_only` — for billing service callbacks
- `enterprise_inner_api_only` — for enterprise service callbacks
- `plugin_inner_api_only` — for plugin daemon, uses separate `INNER_API_KEY_FOR_PLUGIN`
- `enterprise_inner_api_user_auth` — HMAC-SHA1 signature over `"DIFY {user_id}"` using inner API key

---

## 8. Multi-Tenancy & Data Isolation

### 8.1 Data Model

- **Account**: A user identity (email/password/OAuth). Can belong to multiple tenants.
- **Tenant**: A workspace. Has a `name`, `plan`, `status`, `encrypt_public_key`, `custom_config`.
- **TenantAccountJoin**: Many-to-many join with `role` and `current` flag. Unique constraint on `(tenant_id, account_id)`.

### 8.2 Tenant Resolution

Every authenticated request resolves the current tenant:
1. During `load_user()`, the account's `current=True` join is loaded
2. If no current tenant, the first available tenant is auto-selected and marked current
3. The `Account.current_tenant` property sets `self.role` from the join record
4. All downstream service calls scope queries by `current_tenant_id`

### 8.3 Tenant Switching

`TenantService.switch_tenant(account, tenant_id)`:
1. Verify the account has a join record for the target tenant
2. Verify tenant status is NORMAL
3. Set all other joins for this account to `current=False`
4. Set target join to `current=True`

### 8.4 Data Isolation Patterns

- **Apps**: `app.tenant_id` — all app queries filter by tenant
- **Datasets**: `dataset.tenant_id` — all dataset queries filter by tenant
- **API Tokens**: `api_token.tenant_id` — scoped to tenant
- **Upload Files**: `upload_file.tenant_id`
- **Conversations, Messages**: Scoped through app -> tenant chain
- **Model Providers**: Scoped by tenant
- **Encryption Keys**: Per-tenant RSA keypair (`privkeys/{tenant_id}/private.pem`)

There is NO row-level security at the database level. Isolation is enforced entirely in application code via query filters.

### 8.5 Service API Tenant Resolution

For Service API (app/dataset tokens), the tenant is resolved from the token's `tenant_id` or the associated app's `tenant_id`. The request is then processed as the tenant owner.

---

## 9. Password Hashing & Invite Flows

### 9.1 Password Hashing

- **Algorithm**: PBKDF2-HMAC-SHA256
- **Iterations**: 10,000
- **Salt**: 16 random bytes via `secrets.token_bytes(16)`
- **Storage**: Both hash and salt stored as base64-encoded strings in the `accounts` table (`password`, `password_salt` columns)
- **Validation regex**: Must contain letters AND numbers, minimum 8 characters
- **Library**: Python stdlib `hashlib.pbkdf2_hmac`

### 9.2 Password on First Invite Login

When a user with `password=NULL` logs in with a valid `invite_token` and provides a password:
- The password is hashed and stored immediately
- This allows invited users to set their password on first login

### 9.3 Invite Flow

1. Admin calls `RegisterService.invite_new_member(tenant, email, language, role, inviter)`
2. Permission check: inviter must be owner or admin
3. If no account exists: register with PENDING status, create tenant membership
4. Generate invite token (UUID4), store in Redis with 72h expiry (configurable `INVITE_EXPIRY_HOURS`)
5. Send invite email via Celery task
6. Invite data stored in Redis: `member_invite:token:{uuid}` -> `{account_id, email, workspace_id}`
7. On acceptance: validate token, activate account, optionally set password via OAuth or login form

### 9.4 Account Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Invited but not yet logged in. Auto-activated on first login. |
| `uninitialized` | Account created but profile not completed |
| `active` | Normal operational state |
| `banned` | Blocked from all access |
| `closed` | Self-deleted (soft delete) |

---

## 10. Security Headers, CSRF & Transport Security

### 10.1 CSRF Protection

**Double-submit cookie pattern**:
1. On login, server sets `csrf_token` cookie (non-HttpOnly, so JS can read it)
2. The CSRF token is a JWT containing `{sub: user_id, exp}`
3. Client must include the same token in `X-CSRF-Token` request header
4. `check_csrf_token()` verifies:
   - Header value matches cookie value
   - JWT decodes successfully
   - `sub` matches the authenticated user's ID
   - Token is not expired

**Bypass conditions**:
- Admin API key requests bypass CSRF
- Whitelisted paths (e.g., workflow draft endpoint — sent via `navigator.sendBeacon`)
- OPTIONS requests (CORS preflight)

### 10.2 Cookie Security

- `HttpOnly`: Yes for access_token and refresh_token, No for csrf_token
- `Secure`: Yes when both CONSOLE_WEB_URL and CONSOLE_API_URL use HTTPS
- `SameSite`: Lax (default for all cookies)
- `__Host-` prefix: Applied when secure + no custom domain (prevents subdomain attacks)
- `Domain`: Stripped of leading dots, set from `COOKIE_DOMAIN` config
- `Path`: `/` for all cookies

### 10.3 Transport Security

- Cookie `Secure` flag derived from URL scheme check on console URLs
- No explicit HSTS headers in application code (expected from reverse proxy)
- No CSP headers in application code
- No additional security headers (X-Frame-Options, X-Content-Type-Options, etc.) — expected from reverse proxy/nginx

### 10.4 Field Encoding

Passwords and verification codes are Base64-encoded by the frontend before transmission. This is explicitly described as "obfuscation, not cryptographic encryption" in code comments. Real transport security relies on HTTPS.

---

## 11. Secrets & Credential Encryption at Rest

### 11.1 Per-Tenant RSA Keypair

- Each tenant gets a 2048-bit RSA keypair on creation
- Private key stored in configured storage backend (`privkeys/{tenant_id}/private.pem`)
- Public key stored in `tenants.encrypt_public_key` column
- Used for encrypting third-party provider credentials (API keys, tokens)

### 11.2 Hybrid Encryption

For encrypting credential strings:
1. Generate random 16-byte AES key
2. Encrypt data with AES-EAX mode
3. Encrypt AES key with RSA-OAEP (using tenant's public key)
4. Prepend `HYBRID:` prefix
5. Store concatenated: `enc_aes_key | nonce | tag | ciphertext`

### 11.3 Private Key Caching

- Private keys cached in Redis for 120 seconds to avoid repeated storage reads
- Cache key: SHA3-256 hash of the file path

### 11.4 Application Secret Key

Single `SECRET_KEY` used for:
- JWT signing (HS256)
- Flask session signing
- Must be at least 42 bytes, generated via `openssl rand -base64 42`

---

## 12. Libraries Used

| Library | Purpose |
|---------|---------|
| `flask-login` | Session management, `current_user` proxy, request loader hook |
| `PyJWT` (`jwt`) | JWT encode/decode for access tokens and CSRF tokens |
| `flask-cors` | CORS header management per blueprint |
| `flask-restx` | REST API framework with Swagger support |
| `pydantic` | Request payload validation |
| `SQLAlchemy` (2.0 style) | ORM, database models |
| `redis` (via `extensions/ext_redis.py`) | Token storage, rate limiting, caching |
| `hashlib` (stdlib) | PBKDF2-HMAC-SHA256 for password hashing |
| `secrets` (stdlib) | Cryptographic random for tokens, salts, codes |
| `pycryptodome` (`Crypto`) | RSA key generation, AES-EAX encryption, RSA-OAEP |
| `httpx` | OAuth provider HTTP calls |
| `celery` | Async email delivery tasks |
| `hmac` + `hashlib` (stdlib) | HMAC-SHA1 for inner API user auth |

---

## 13. Design Decisions & Trade-offs

### 13.1 JWT + Redis Hybrid

Access tokens are stateless JWTs (no server-side revocation until expiry), while refresh tokens are stateful (Redis-backed, immediately revocable). This trades some revocation latency (up to ACCESS_TOKEN_EXPIRE_MINUTES) for reduced Redis load on every request.

### 13.2 Single Secret Key for JWT

Using HS256 with a shared secret means any service with the secret can forge tokens. For a monolith this is acceptable; for a distributed system, consider RS256 with public key distribution.

### 13.3 Application-Level Tenant Isolation (No RLS)

All multi-tenancy isolation is enforced by adding `WHERE tenant_id = ?` in application queries. There is no database-level row-level security. This is simpler to implement but creates risk if any query forgets the tenant filter.

### 13.4 Cookie-Based Token Delivery

Tokens are set as cookies rather than returned in response bodies. This protects against XSS token theft (HttpOnly cookies) but requires CSRF protection and proper CORS configuration.

### 13.5 Rate Limiting in Redis

All rate limiting uses Redis, with a `@redis_fallback` decorator that degrades gracefully (allows requests through) when Redis is down. This prioritizes availability over strict rate enforcement.

### 13.6 PBKDF2 with 10,000 Iterations

The iteration count (10,000) is below modern recommendations (OWASP suggests 600,000+ for PBKDF2-SHA256 as of 2023). Consider using argon2id or bcrypt for a reimplementation, or significantly increasing the iteration count.

### 13.7 Base64 "Encryption" of Passwords in Transit

The frontend Base64-encodes passwords before sending. This provides zero security benefit — it is explicitly acknowledged as obfuscation. HTTPS provides the real transport encryption.

### 13.8 One Refresh Token Per Account

Only one refresh token is active per account at any time. This means logging in on a second device invalidates the first device's refresh token, effectively implementing single-session enforcement.

### 13.9 Admin API Key as God Mode

The admin API key bypasses all authentication, CSRF, and can impersonate any workspace owner. This is powerful for automation but represents a significant security surface if the key is compromised.

---

## 14. Requirements Summary

### REQ-AUTH-001: Email/Password Authentication
- PBKDF2-HMAC-SHA256 password hashing with random 16-byte salt
- Case-insensitive email lookup with legacy case-sensitive fallback
- Account status checks (banned, pending auto-activation)
- Failed login counter with configurable lockout duration

### REQ-AUTH-002: Email Code (Passwordless) Authentication
- 6-digit numeric OTP delivered via email
- One-time token stored in Redis with configurable TTL
- Per-email rate limiting (sliding window)
- IP-based email send rate limiting with escalating freeze

### REQ-AUTH-003: OAuth Authentication
- Pluggable provider model (GitHub, Google)
- Account linking via `account_integrates` table
- Auto-registration on first OAuth login (if enabled)
- Invite token validation via OAuth state parameter

### REQ-AUTH-004: Token Management
- Short-lived JWT access tokens (default 60 min)
- Long-lived Redis-backed refresh tokens (default 30 days)
- Refresh token rotation (old deleted on use)
- CSRF token as signed JWT in non-HttpOnly cookie
- Cookie delivery with __Host- prefix when applicable

### REQ-AUTHZ-001: Role-Based Access Control
- 5 roles: owner, admin, editor, normal, dataset_operator
- Permission checks via decorators and service methods
- Single owner per tenant constraint

### REQ-AUTHZ-002: Multi-Tenancy
- Many-to-many account-tenant relationship
- Current tenant resolution per request
- Application-level query scoping by tenant_id
- Per-tenant RSA keypair for credential encryption

### REQ-API-001: API Key Authentication
- Two key types: app (per-app) and dataset (per-tenant)
- Bearer token validation with last_used_at tracking
- Automatic owner impersonation for service context

### REQ-RATE-001: Rate Limiting
- Redis-backed with graceful degradation
- Per-email login attempt limiting
- Per-IP email send limiting with escalation
- Per-tenant knowledge API rate limiting
- Per-app concurrent request limiting
- Sliding window (ZSET) and counter patterns

### REQ-CORS-001: Cross-Origin Resource Sharing
- Per-blueprint CORS configuration
- Configurable origins for console and web API
- Credentials support for authenticated endpoints
- Distinct embedded vs authenticated web API policies

### REQ-SEC-001: CSRF Protection
- Double-submit cookie with JWT verification
- User-bound CSRF tokens
- Configurable whitelist for beacon/sendBeacon endpoints

### REQ-SEC-002: Credential Encryption at Rest
- Per-tenant RSA-2048 keypair
- Hybrid RSA+AES-EAX encryption for stored credentials
- Private key caching in Redis (120s TTL)

### REQ-INVITE-001: Member Invitation
- Redis-backed invitation tokens with configurable TTL
- Email delivery via async task queue
- Role assignment on invite
- Password-deferred (set on first login)

### REQ-SETUP-001: Initial Setup Guard
- DifySetup table gates all endpoints until first admin is created
- Atomic setup with rollback on failure
