

All analyses are complete. Let me now compile the comprehensive requirements document.

---

# Dify API Architecture Specification — Requirements Document

**Source:** Dify v1.11.4 (`/Users/markforster/nyqst-dify/upstream-dify/api/`)
**Date:** 2026-02-01

---

## 1. Flask Blueprint Structure

### 1.1 App Factory & Blueprint Registration

Entry point: `api/app_factory.py` → Extensions loaded via `api/extensions/ext_blueprints.py`

The `init_app()` function registers **7 blueprints** with CORS applied per-blueprint via a helper `_apply_cors_once()` that prevents duplicate CORS initialization.

### 1.2 Blueprint Registry

| Blueprint | URL Prefix | Purpose | Route Count |
|-----------|-----------|---------|-------------|
| **Console API** | `/console/api` | Admin/management UI | ~440 |
| **Service API** | `/v1` | Public application API | ~60 |
| **Web API** | `/api` | Embedded web app endpoints | ~37 |
| **Files API** | `/files` | File operations | ~5 |
| **Inner API** | `/inner/api` | Internal/enterprise service-to-service | ~19 |
| **MCP API** | `/mcp` | Model Context Protocol | ~1 |
| **Trigger API** | `/triggers` | Webhooks/triggers | ~3 |
| **Total** | | | **~565** |

### 1.3 Framework Stack

- **Flask** as the WSGI application
- **Flask-RESTX** (v1.3.0) — provides `Namespace`, `Resource`, `@ns.doc()`, `@ns.expect()`
- **`ExternalApi`** (`libs/external_api.py`) — custom subclass of `flask_restx.Api` adding error handlers
- Route pattern: `@namespace.route("/path")` on `Resource` subclasses

---

## 2. Console API vs Service API Split

### 2.1 Console API (`/console/api`)

**Target users:** Workspace owners, admins, editors (Dify dashboard)

**Scope:** Full system management including:
- App CRUD, configuration, deployment, export/import
- Dataset management, document indexing, segments, metadata
- RAG pipeline workflows
- Workspace/tenant, member, and role management
- Model provider configuration (LLM, embedding, rerank, TTS)
- Plugin installation and management
- Tool provider setup
- Billing, compliance, feature flags
- Auth flows (login, OAuth, registration, password reset)
- Tags, annotations, statistics, ops tracing

**Directory structure** (`api/controllers/console/`):
```
console/
├── app/           # App management (20+ files)
├── auth/          # Login, OAuth, registration (8 files)
├── billing/       # Billing & compliance
├── datasets/      # Datasets, documents, segments, RAG pipeline
├── explore/       # Marketplace, installed apps
├── workspace/     # Members, providers, plugins, models
├── tag/           # Tag management
├── admin.py       # Admin operations
├── apikey.py      # API key management
├── extension.py   # Extension config
├── feature.py     # Feature flags
├── ping.py        # Health check
├── setup.py       # Initial setup
├── spec.py        # Schema definitions
└── version.py     # Version info
```

### 2.2 Service API (`/v1`)

**Target users:** End users, third-party integrations, deployed app clients

**Scope:** App-specific operations only:
- Chat messages, completion messages (blocking + streaming)
- Conversation CRUD
- Message listing, feedback
- File upload for conversations
- Audio: TTS and speech-to-text
- Workflow execution and status
- Dataset querying (search/retrieval via API tokens)
- App metadata/parameters (read-only)

**Directory structure** (`api/controllers/service_api/`):
```
service_api/
├── app/           # Chat, completion, conversations, files, audio, workflow
├── dataset/       # Dataset query, documents, segments, metadata
├── workspace/     # Model listing
└── index.py       # Index route
```

### 2.3 Web API (`/api`)

**Target users:** Browser-based embedded applications (webapp SDK)

**Scope:** Mirrors Service API but with web-specific auth (passport/cookie) and additional endpoints:
- Pin/unpin conversations
- Saved messages
- Suggested questions, more-like-this
- Passport-based anonymous auth
- Login/logout for web apps with access control
- Remote file uploads (from URL)
- System features endpoint

---

## 3. Authentication Middleware

### 3.1 Authentication Strategies

| Strategy | Blueprint | Mechanism | Header/Cookie |
|----------|-----------|-----------|---------------|
| **Session/JWT** | Console | HS256 JWT in HttpOnly cookie | `__Host-<COOKIE_NAME>` or `Authorization: Bearer` |
| **CSRF** | Console | JWT in non-HttpOnly cookie + `X-CSRF-Token` header | Dual validation |
| **Refresh Token** | Console | Opaque token stored in Redis (7-day TTL) | HttpOnly cookie |
| **API Token** | Service API | App-scoped token from `api_tokens` table | `Authorization: Bearer <token>` |
| **Dataset Token** | Service API | Dataset-scoped token, requires `enable_api=true` | `Authorization: Bearer <token>` |
| **Passport** | Web | Anonymous JWT token | Cookie |
| **Inner API Key** | Inner API | Static shared secret | `X-Inner-Api-Key` |
| **Plugin API Key** | Inner API | Separate plugin daemon key | `X-Inner-Api-Key` |
| **HMAC User Auth** | Inner API | `user_id:HMAC-SHA1` signature | `Authorization` |
| **OAuth 2.0** | Console | GitHub, Google provider flow | Redirect-based |

### 3.2 Console Auth Flow

```
POST /console/api/login → validate credentials → issue:
  ├─ AccessToken (JWT, 15min, HttpOnly cookie)
  ├─ RefreshToken (Redis, 7 days, HttpOnly cookie)
  └─ CSRF Token (JWT, 15min, non-HttpOnly cookie)

Subsequent requests:
  Cookie auto-included → login_required extracts JWT →
  CSRF validated (header vs cookie) → current_user proxy resolved
```

### 3.3 Service API Auth Flow

```
Authorization: Bearer <api_token>
  → validate_app_token decorator
  → Query api_tokens table by token + type
  → Verify app status == "normal", tenant not archived
  → Update last_used_at (throttled: max 1/min)
  → Setup EndUser or Account context
```

### 3.4 Key Decorators

| Decorator | Location | Purpose |
|-----------|----------|---------|
| `@login_required` | `libs/login.py` | JWT session + CSRF validation |
| `@setup_required` | `console/wraps.py` | Ensures initial setup complete |
| `@account_initialization_required` | `console/wraps.py` | Account not UNINITIALIZED |
| `@edit_permission_required` | `console/wraps.py` | Role: owner/admin/editor |
| `@is_admin_or_owner_required` | `console/wraps.py` | Role: owner/admin |
| `@validate_app_token` | `service_api/wraps.py` | API token validation |
| `@validate_dataset_token` | `service_api/wraps.py` | Dataset token validation |
| `@get_app_model(mode=)` | `console/app/wraps.py` | Fetch app + mode check |
| `@enterprise_inner_api_only` | `inner_api/wraps.py` | Inner API key check |
| `@only_edition_cloud` | `console/wraps.py` | Cloud edition gate |
| `@only_edition_self_hosted` | `console/wraps.py` | Self-hosted edition gate |
| `@cloud_edition_billing_resource_check` | `console/wraps.py` | Billing quota enforcement |

### 3.5 Role-Based Access Control

Roles (enum `TenantAccountRole`):
- `OWNER` → full access
- `ADMIN` → administrative
- `EDITOR` → edit apps/content
- `NORMAL` → basic read
- `DATASET_OPERATOR` → dataset operations only

Account statuses: `PENDING`, `UNINITIALIZED`, `ACTIVE`, `BANNED`, `CLOSED`

---

## 4. Request Validation

### 4.1 Primary: Pydantic v2

The **exclusive validation framework** for request bodies. No marshmallow is used.

**Pattern:**
```python
class ChatRequestPayload(BaseModel):
    query: str
    conversation_id: str | None = Field(default=None)
    response_mode: Literal["blocking", "streaming"] | None = None
    files: list[dict[str, Any]] | None = None
    
    @field_validator("conversation_id", mode="before")
    @classmethod
    def normalize_conversation_id(cls, value):
        # Custom UUID validation
```

**Usage in controllers:**
```python
payload = ChatRequestPayload.model_validate(service_api_ns.payload or {})
args = payload.model_dump(exclude_none=True)
```

### 4.2 Secondary: Flask-RESTX reqparse

Used in limited cases (auth endpoints) for simple query/form params:
```python
parser = reqparse.RequestParser()
parser.add_argument("email", type=email, required=True, location="json")
```

### 4.3 Schema Registration for Swagger

Pydantic models registered with Flask-RESTX namespaces via:
```python
register_schema_models(service_api_ns, ChatRequestPayload, ...)
# → namespace.schema_model(name, model.model_json_schema())
```

---

## 5. Error Handling

### 5.1 Base Exception

```python
# libs/exception.py
class BaseHTTPException(HTTPException):
    error_code: str = "unknown"
    data: dict | None = None
    # Produces: {"code": error_code, "message": description, "status": http_code}
```

### 5.2 Standard Error Response Format

All errors are serialized as:
```json
{
    "code": "error_code_string",
    "message": "Human-readable description",
    "status": 400
}
```

With an additional `"params"` field for validation errors:
```json
{
    "code": "invalid_param",
    "message": "conversation_id must be a valid UUID",
    "params": "conversation_id",
    "status": 400
}
```

### 5.3 Error Handler Chain (`libs/external_api.py`)

| Exception Type | HTTP Status | Error Code |
|---------------|-------------|------------|
| `ValueError` | 400 | `invalid_param` |
| `BaseHTTPException` subclass | varies | from `error_code` attribute |
| `HTTPException` (400 with params) | 400 | `invalid_param` |
| `HTTPException` (other) | varies | snake_case of class name |
| `AppInvokeQuotaExceededError` | 429 | `too_many_requests` |
| Unhandled `Exception` | 500 | `unknown` |

Special behaviors:
- **401** → adds `WWW-Authenticate: Bearer realm="api"` header
- **Force logout** → sets cookie-clearing headers when `error_code == "unauthorized_and_force_logout"`

### 5.4 Error Class Examples

```python
# Service API errors
AppUnavailableError          (400, "app_unavailable")
NotChatAppError              (400, "not_chat_app")
ProviderQuotaExceededError   (400, "provider_quota_exceeded")
AudioTooLargeError           (413, "audio_too_large")

# Console errors
AlreadySetupError            (403, "already_setup")
UnauthorizedAndForceLogout   (401, "unauthorized_and_force_logout")
WorkspaceMembersLimitExceeded(403, "workspace_members_limit_exceeded")
```

---

## 6. Pagination

### 6.1 Primary: Cursor-Based Infinite Scroll

**Class:** `libs/infinite_scroll_pagination.py`

```python
class InfiniteScrollPagination:
    data: list       # Page of results
    limit: int       # Requested page size
    has_more: bool   # Whether more records exist
```

**Query parameters:**
- `first_id: UUID | None` — cursor (ID of first item in current view)
- `limit: int` — page size (default 20, max 100)

**Implementation:** Fetches `limit + 1` records; if extra exists, `has_more = True`.

**Response format:**
```json
{
    "data": [...],
    "limit": 20,
    "has_more": true
}
```

### 6.2 Secondary: Offset-Based

Used in limited endpoints (e.g., feedback listing):
- `page: int` (default 1, min 1)
- `limit: int` (default 20, max 101)

---

## 7. File Upload Endpoints

### 7.1 Endpoints

| Endpoint | Blueprint | Auth |
|----------|-----------|------|
| `POST /v1/files/upload` | Service API | API token |
| `POST /api/files/upload` | Web API | Passport |
| `POST /files/upload/for-plugin` | Files API | Plugin auth |
| `GET /console/api/files/upload` | Console API | Login (returns config) |

### 7.2 Handling

- Standard `request.files['file']` (werkzeug multipart)
- **Single file only** — raises `TooManyFilesError` if multiple
- Returns HTTP **201** on success

### 7.3 Validation

- Extension blacklist (`UPLOAD_FILE_EXTENSION_BLACKLIST`)
- Per-type size limits (image, video, audio, document)
- Source-specific type checking (`source="datasets"` restricts to document extensions)

### 7.4 Upload Configuration (Console GET endpoint)

```json
{
    "file_size_limit": ...,
    "batch_count_limit": ...,
    "image_file_size_limit": ...,
    "video_file_size_limit": ...,
    "audio_file_size_limit": ...,
    "workflow_file_upload_limit": ...
}
```

---

## 8. SSE/Streaming

### 8.1 Implementation

- Flask `stream_with_context` + `Response(mimetype="text/event-stream")`
- Controller helper: `libs/helper.py:compact_generate_response()`
- Stream conversion: `core/app/apps/base_app_generator.py:convert_to_event_stream()`

### 8.2 Wire Format

```
data: {"event": "message", "task_id": "...", "answer": "Hello"}\n\n
data: {"event": "message_end", "task_id": "...", "metadata": {...}}\n\n
event: ping\n\n
```

- JSON payloads: `data: {json}\n\n`
- Signal events: `event: {name}\n\n`

### 8.3 Stream Event Types (25+)

| Event | Description |
|-------|-------------|
| `ping` | Heartbeat |
| `error` | Error notification |
| `message` | Regular message chunk |
| `message_end` | Message complete |
| `message_file` | File attachment |
| `message_replace` | Message replacement |
| `tts_message` / `tts_message_end` | Text-to-speech |
| `agent_thought` / `agent_message` / `agent_log` | Agent events |
| `workflow_started` / `workflow_finished` | Workflow lifecycle |
| `node_started` / `node_finished` / `node_retry` | Node execution |
| `iteration_started` / `iteration_next` / `iteration_completed` | Iteration events |
| `loop_started` / `loop_next` / `loop_completed` | Loop events |
| `text_chunk` / `text_replace` | Token-level streaming |

### 8.4 Response Mode

Endpoints accept `response_mode: "blocking" | "streaming"`:
- **blocking** → returns single JSON response
- **streaming** → returns `text/event-stream`

---

## 9. Rate Limiting

### 9.1 Application-Level (Redis-backed concurrency)

**Location:** `core/app/features/rate_limiting/rate_limit.py`

- Tracks concurrent requests per app via Redis hash
- Key: `dify:rate_limit:{client_id}:active_requests`
- Max alive time: 10 minutes per request
- Flush interval: 5 minutes (recalculates active count)
- Exceeding limit raises `AppInvokeQuotaExceededError` → HTTP 429

**Streaming integration:** `RateLimitGenerator` wraps generators to auto-decrement on completion/error.

### 9.2 Email/Login Rate Limiting (sliding window)

**Location:** `libs/helper.py:RateLimiter`

- Redis sorted set sliding window
- Configurable `max_attempts` and `time_window`
- Used on login (max 5 failed attempts)

### 9.3 Billing Rate Limits

- `@cloud_edition_billing_rate_limit_check(resource)` — cloud edition quota enforcement
- Annotation import limits: per-minute + per-hour + concurrency

---

## 10. CORS Configuration

**Per-blueprint CORS** via `flask-cors`, applied in `ext_blueprints.py`:

| Blueprint | Origins | Credentials | Special Headers |
|-----------|---------|-------------|-----------------|
| Console API | `CONSOLE_CORS_ALLOW_ORIGINS` | Yes | Authorization, CSRF token |
| Service API | All | No | Authorization |
| Web API (default) | `WEB_API_CORS_ALLOW_ORIGINS` | Yes | Passport, App Code |
| Web API (embed chat) | `WEB_API_CORS_ALLOW_ORIGINS` | No | Content-Type, App Code only |
| Files API | All | No | CSRF token |
| Trigger API | All | No | Authorization |

**Exposed headers:** `X-Version`, `X-Env`, `X-Trace-Id`

**Methods allowed:** GET, PUT, POST, DELETE, OPTIONS, PATCH (+ HEAD for triggers)

---

## 11. API Versioning Strategy

**Single version: `/v1`** — no v2 or higher detected.

```python
bp = Blueprint("service_api", __name__, url_prefix="/v1")
api = ExternalApi(bp, version="1.0", title="Service API")
```

The Console API, Web API, Files API, Inner API, MCP API, and Trigger API are **unversioned** (rely on their unique prefixes for identification).

---

## 12. OpenAPI/Swagger Documentation

### 12.1 Status: Partial / Minimal

- **No full Swagger UI** served
- **No standalone OpenAPI JSON/YAML export endpoint**
- Flask-RESTX provides intrinsic spec generation via `@ns.doc()` and `@ns.expect()`

### 12.2 What Exists

**Schema definitions endpoint:**
```
GET /console/api/spec/schema-definitions
```
Returns JSON schema definitions from a `SchemaManager` (local registry of schemas).

**Per-endpoint documentation via decorators:**
```python
@service_api_ns.doc("create_completion")
@service_api_ns.doc(responses={200: "Success", 400: "Bad request", 401: "Unauthorized"})
@service_api_ns.expect(service_api_ns.models[ChatRequestPayload.__name__])
```

**Pydantic → JSON Schema bridge:**
```python
register_schema_models(namespace, *models)
# Converts Pydantic BaseModel.model_json_schema() → Flask-RESTX schema model
```

---

## Appendix A: Key File Reference

| File | Purpose |
|------|---------|
| `extensions/ext_blueprints.py` | Blueprint registration + CORS |
| `app_factory.py` | Flask app creation |
| `libs/external_api.py` | ExternalApi class + all error handlers |
| `libs/exception.py` | `BaseHTTPException` base class |
| `libs/login.py` | `login_required`, `current_user` proxy |
| `libs/passport.py` | JWT issue/verify (HS256) |
| `libs/token.py` | Token extraction, cookie mgmt, CSRF |
| `libs/helper.py` | `compact_generate_response`, `RateLimiter`, `uuid_value` |
| `libs/infinite_scroll_pagination.py` | Pagination class |
| `libs/oauth.py` | GitHub/Google OAuth |
| `controllers/console/wraps.py` | Permission + billing + edition decorators |
| `controllers/service_api/wraps.py` | `validate_app_token`, `validate_dataset_token` |
| `controllers/inner_api/wraps.py` | Inner API key validation |
| `controllers/console/app/wraps.py` | `get_app_model` decorator |
| `controllers/common/schema.py` | `register_schema_models` |
| `core/app/apps/base_app_generator.py` | `convert_to_event_stream` |
| `core/app/entities/task_entities.py` | `StreamEvent` enum (25+ events) |
| `core/app/features/rate_limiting/rate_limit.py` | Redis concurrency limiter |
| `core/errors/error.py` | Core LLM/provider exceptions |
| `services/account_service.py` | Token pair generation, login/logout |

---

`★ Insight ─────────────────────────────────────`
**Architecture highlights worth noting:**

1. **Console vs Service API split is a security boundary**, not just organizational. Console uses session-based auth with CSRF; Service API uses stateless API tokens. This means the same underlying services (e.g., `AppGenerateService`) are accessed through two entirely different auth models, with the Console path having far more middleware (setup checks, billing checks, role checks, edition gates).

2. **The cursor-based pagination using `first_id` is unusual** — most implementations use `after`/`before` cursors. Dify's approach queries `WHERE created_at < first_item.created_at`, which means pagination is tied to creation time ordering. This works well for append-only data (messages, conversations) but would break if records could be reordered.

3. **The streaming architecture is surprisingly simple** — no WebSocket upgrade, no dedicated SSE library. It's plain Flask `stream_with_context` with manually formatted `data: {json}\n\n` lines. The 25+ event types in `StreamEvent` reveal how complex the workflow execution model is underneath, with events for individual node execution, loop iterations, and agent reasoning steps all flowing through the same SSE channel.
`─────────────────────────────────────────────────`
