# Dify App Configuration & Publishing System — Requirements Document

**Source:** Dify v1.11.4 (`/Users/markforster/nyqst-dify/upstream-dify/`)
**Date:** 2026-02-01
**Scope:** Complete analysis of app types, configuration, publishing, APIs, embedding, templates, conversations, analytics, and import/export.

---

## Table of Contents

1. [App Types & Data Models](#1-app-types--data-models)
2. [App Creation Flow](#2-app-creation-flow)
3. [App Configuration Panel](#3-app-configuration-panel)
4. [Publishing Flow (Draft vs Published)](#4-publishing-flow-draft-vs-published)
5. [App API (Service API)](#5-app-api-service-api)
6. [Embed / iframe Widget](#6-embed--iframe-widget)
7. [App Templates / Marketplace](#7-app-templates--marketplace)
8. [Conversation Management](#8-conversation-management)
9. [App-Level Analytics](#9-app-level-analytics)
10. [App Import / Export (DSL)](#10-app-import--export-dsl)

---

## 1. App Types & Data Models

### 1.1 AppMode Enum

**File:** `api/models/model.py:49-69`

```python
class AppMode(StrEnum):
    COMPLETION    = "completion"       # Single-turn text completion
    WORKFLOW      = "workflow"         # Workflow automation engine
    CHAT          = "chat"             # Multi-turn conversational (simple prompt-based)
    ADVANCED_CHAT = "advanced-chat"    # Chat powered by workflow engine
    AGENT_CHAT    = "agent-chat"       # Chat with tool calling (function_call / react)
    CHANNEL       = "channel"          # Universal channel (internal)
    RAG_PIPELINE  = "rag-pipeline"     # Retrieval-augmented generation pipeline
```

### 1.2 App Type Comparison Matrix

| Property | COMPLETION | CHAT | AGENT_CHAT | ADVANCED_CHAT | WORKFLOW |
|----------|-----------|------|------------|---------------|----------|
| Config store | AppModelConfig | AppModelConfig | AppModelConfig | Workflow (draft) | Workflow (draft) |
| Has conversations | No (single-turn) | Yes | Yes | Yes | No (runs) |
| Memory/history | No | TokenBufferMemory | TokenBufferMemory | Workflow variables | No |
| Tool calling | No | No | Yes (function_call/react) | Yes (via tool nodes) | Yes (via tool nodes) |
| Runner class | CompletionAppRunner | ChatAppRunner | AgentChatAppRunner | AdvancedChatAppRunner | WorkflowAppRunner |
| Generator class | CompletionAppGenerator | ChatAppGenerator | AgentChatAppGenerator | AdvancedChatAppGenerator | WorkflowAppGenerator |
| Base class | AppRunner | AppRunner | AppRunner | WorkflowBasedAppRunner | WorkflowBasedAppRunner |
| Draft/Publish | No (direct config) | No (direct config) | No (direct config) | Yes (workflow versions) | Yes (workflow versions) |
| DSL export section | `model_config` | `model_config` | `model_config` | `workflow` | `workflow` |

### 1.3 App Runner Hierarchy

```
api/core/app/apps/
├── base_app_runner.py              # AppRunner base
├── base_app_generator.py           # BaseAppGenerator base
├── message_based_app_generator.py  # Shared by chat/completion/agent
├── workflow_app_runner.py          # WorkflowBasedAppRunner base
├── chat/
│   ├── app_config_manager.py       # ChatAppConfig
│   ├── app_generator.py            # ChatAppGenerator
│   └── app_runner.py               # ChatAppRunner
├── completion/
│   ├── app_config_manager.py       # CompletionAppConfig
│   ├── app_generator.py            # CompletionAppGenerator
│   └── app_runner.py               # CompletionAppRunner
├── agent_chat/
│   ├── app_config_manager.py       # AgentChatAppConfig
│   ├── app_generator.py            # AgentChatAppGenerator
│   └── app_runner.py               # AgentChatAppRunner (function_call, react, CoT)
├── advanced_chat/
│   ├── app_config_manager.py       # AdvancedChatAppConfig
│   ├── app_generator.py            # AdvancedChatAppGenerator
│   ├── app_runner.py               # AdvancedChatAppRunner (extends WorkflowBasedAppRunner)
│   └── generate_task_pipeline.py
├── workflow/
│   ├── app_config_manager.py       # WorkflowAppConfig
│   ├── app_generator.py            # WorkflowAppGenerator
│   ├── app_runner.py               # WorkflowAppRunner (extends WorkflowBasedAppRunner)
│   ├── app_queue_manager.py
│   └── generate_task_pipeline.py
└── pipeline/                       # RAG pipeline support
```

### 1.4 Core Data Models

#### 1.4.1 App Model

**Table:** `apps` | **File:** `api/models/model.py:78-108`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | App unique identifier |
| tenant_id | StringUUID (indexed) | Workspace ID |
| name | String(255) | App display name |
| description | LongText | App description |
| mode | String(255) | AppMode value |
| icon_type | String(255) NULL | "image", "emoji", "link" |
| icon | String(255) | Icon value (emoji char or image path) |
| icon_background | String(255) NULL | Background color hex |
| app_model_config_id | StringUUID NULL | FK → AppModelConfig (active config for non-workflow apps) |
| workflow_id | StringUUID NULL | FK → Workflow (published workflow for workflow-based apps) |
| status | String(255) | "normal" (default) |
| enable_site | Boolean | Enable web share/embed |
| enable_api | Boolean | Enable service API |
| api_rpm | Integer | API rate limit per minute (default: 0 = unlimited) |
| api_rph | Integer | API rate limit per hour (default: 0 = unlimited) |
| is_demo | Boolean | Demo flag |
| is_public | Boolean | Public visibility |
| is_universal | Boolean | Universal app (hidden from normal lists) |
| tracing | LongText NULL | Tracing configuration JSON |
| max_active_requests | Integer NULL | Max concurrent requests |
| use_icon_as_answer_icon | Boolean | Use app icon in responses |
| created_by | StringUUID NULL | Creator Account ID |
| created_at | DateTime | Creation timestamp |
| updated_by | StringUUID NULL | Last updater Account ID |
| updated_at | DateTime | Last update timestamp |

**Key Properties:**
- `site` → lazy loads Site record
- `app_model_config` → lazy loads AppModelConfig by `app_model_config_id`
- `workflow` → lazy loads Workflow by `workflow_id` (published workflow)
- `is_agent` → checks if CHAT app has agent_mode enabled (auto-upgrades mode)
- `deleted_tools` → checks for tool providers that no longer exist
- `tags` → loads associated Tag records via TagBinding

#### 1.4.2 AppModelConfig Model

**Table:** `app_model_configs` | **File:** `api/models/model.py:318-494`

Used by: CHAT, COMPLETION, AGENT_CHAT modes. Stores the **active** configuration directly (no draft/publish cycle).

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Config unique ID |
| app_id | StringUUID (indexed) | Parent App ID |
| provider | String(255) NULL | LLM provider name |
| model_id | String(255) NULL | LLM model ID |
| configs | JSON NULL | Generic configuration |
| opening_statement | LongText | Initial greeting message |
| suggested_questions | LongText | JSON array of suggested prompts |
| suggested_questions_after_answer | LongText | JSON: `{enabled: bool}` |
| speech_to_text | LongText | JSON: `{enabled: bool}` |
| text_to_speech | LongText | JSON: `{enabled: bool, ...}` |
| more_like_this | LongText | JSON: `{enabled: bool}` |
| model | LongText | JSON: `{provider, name, mode, completion_params}` |
| user_input_form | LongText | JSON array: dynamic form field definitions |
| dataset_query_variable | String(255) | Variable name for dataset queries |
| pre_prompt | LongText | System prompt / instruction template |
| agent_mode | LongText | JSON: `{enabled, strategy, tools[], prompt}` |
| sensitive_word_avoidance | LongText | JSON: content filter config |
| retriever_resource | LongText | JSON: `{enabled: bool}` RAG settings |
| prompt_type | String(255) | "simple" or "advanced" (default: "simple") |
| chat_prompt_config | LongText | JSON: chat-specific prompt template |
| completion_prompt_config | LongText | JSON: completion-specific prompt template |
| dataset_configs | LongText | JSON: `{retrieval_model: "single"|"multiple"}` |
| external_data_tools | LongText | JSON array: external tool definitions |
| file_upload | LongText | JSON: file upload configuration |

#### 1.4.3 Workflow Model

**Table:** `workflows` | **File:** `api/models/workflow.py:102-168`

Used by: WORKFLOW, ADVANCED_CHAT modes. Supports draft/publish versioning.

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Workflow unique ID |
| tenant_id | StringUUID | Workspace ID |
| app_id | StringUUID | Parent App ID |
| type | String(255) | "workflow", "chat", or "rag-pipeline" |
| version | String(255) | **"draft"** for draft, timestamp-based for published |
| marked_name | String(255) | Version label (max 20 chars) |
| marked_comment | String(255) | Version comment (max 100 chars) |
| graph | LongText | Full workflow canvas JSON (nodes[], edges[]) |
| features | LongText | Feature configuration JSON |
| environment_variables | LongText | JSON: encrypted environment variables |
| conversation_variables | LongText | JSON: conversation-persistent variables |
| rag_pipeline_variables | LongText | JSON: RAG pipeline variables |
| created_by | StringUUID | Creator Account ID |
| created_at | DateTime | Creation timestamp |
| updated_by | StringUUID NULL | Last updater |
| updated_at | DateTime | Last update |

**Critical constant:** `VERSION_DRAFT = "draft"` — Only ONE draft per app.

**Index:** `workflow_version_idx` on `(tenant_id, app_id, version)` — ensures efficient draft/published lookups.

#### 1.4.4 Conversation Model

**Table:** `conversations` | **File:** `api/models/model.py:637-957`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Conversation ID |
| app_id | StringUUID | Parent App |
| app_model_config_id | StringUUID NULL | Config snapshot at conversation creation |
| model_provider | String(255) NULL | Provider used |
| override_model_configs | LongText NULL | Per-conversation model overrides (debug mode) |
| model_id | String(255) NULL | Model used |
| mode | String(255) | App mode at creation |
| name | String(255) | Title (user-editable or auto-generated) |
| summary | LongText NULL | Auto-generated summary |
| inputs | JSON | Input variable values |
| introduction | LongText NULL | Custom introduction |
| system_instruction | LongText NULL | System prompt |
| system_instruction_tokens | Integer | Token count |
| status | String(255) | Conversation status |
| invoke_from | String(255) NULL | InvokeFrom enum value |
| from_source | String(255) | "api" or "console" |
| from_end_user_id | StringUUID NULL | End user (API conversations) |
| from_account_id | StringUUID NULL | Account (console conversations) |
| read_at | DateTime NULL | Read timestamp |
| dialogue_count | Integer | Message turn count (default: 0) |
| is_deleted | Boolean | Soft delete flag (default: false) |
| created_at | DateTime | Creation |
| updated_at | DateTime | Last update |

**Index:** `conversation_app_from_user_idx` on `(app_id, from_source, from_end_user_id)`

#### 1.4.5 Message Model

**Table:** `messages` | **File:** `api/models/model.py:960-1333`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Message ID |
| app_id | StringUUID | Parent App |
| model_provider | String(255) NULL | Provider used |
| model_id | String(255) NULL | Model used |
| conversation_id | StringUUID (FK) | Parent Conversation |
| inputs | JSON | Input variables for this message |
| query | LongText | User input |
| message | JSON | Formatted message structure |
| message_tokens | Integer | Input tokens (default: 0) |
| message_unit_price | Numeric(10,4) | Price per token (input) |
| answer | LongText | LLM response |
| answer_tokens | Integer | Output tokens (default: 0) |
| answer_unit_price | Numeric(10,4) | Price per token (output) |
| parent_message_id | StringUUID NULL | For message chains |
| provider_response_latency | Float | Response time seconds (default: 0) |
| total_price | Numeric(10,7) NULL | Total cost |
| currency | String(255) | Currency code |
| status | String(255) | "normal", "error" |
| error | LongText NULL | Error message |
| message_metadata | LongText NULL | JSON metadata (retriever_resources, etc.) |
| agent_based | Boolean | From agent execution (default: false) |
| workflow_run_id | StringUUID NULL | Associated WorkflowRun |
| app_mode | String(255) NULL | App mode at time of message |

**Indexes:** 7 indexes covering app, conversation, user, workflow_run, created_at, app_mode.

#### 1.4.6 Site Model

**Table:** `sites` | **File:** `api/models/model.py:1637-1694`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Site ID |
| app_id | StringUUID (indexed) | Parent App |
| title | String(255) | Display title |
| icon_type, icon, icon_background | String | Icon configuration |
| description | LongText | Site description |
| default_language | String(255) | UI language |
| chat_color_theme | String(255) | Theme color hex |
| chat_color_theme_inverted | Boolean | Invert theme |
| copyright | String(255) | Copyright notice |
| privacy_policy | String(255) | Privacy URL |
| custom_disclaimer | LongText | Max 512 chars |
| show_workflow_steps | Boolean | Show execution steps (default: true) |
| use_icon_as_answer_icon | Boolean | Use app icon in responses |
| customize_domain | String(255) | Custom domain |
| customize_token_strategy | String(255) | "must", "allow", "not_allow" |
| prompt_public | Boolean | Make prompt visible |
| status | String(255) | "normal" |
| code | String(255) | **16-char share token** (unique, used in embed URLs) |

#### 1.4.7 ApiToken Model

**Table:** `api_tokens` | **File:** `api/models/model.py:1696-1719`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Token ID |
| app_id | StringUUID NULL | Associated App |
| tenant_id | StringUUID NULL | Associated Tenant |
| type | String(16) | Token type ("app" for service API) |
| token | String(255) | The API token string (unique, prefix: "app-") |
| last_used_at | DateTime NULL | Last usage |
| created_at | DateTime | Creation |

#### 1.4.8 WorkflowRun Model

**Table:** `workflow_runs` | **File:** `api/models/workflow.py`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Run ID |
| tenant_id, app_id, workflow_id | StringUUID | Context |
| type | String(255) | WorkflowType |
| triggered_from | String(255) | "debugging" or "app-run" |
| version | String(255) | Workflow version snapshot |
| graph | LongText NULL | Graph snapshot |
| inputs | LongText NULL | Input values JSON |
| status | String(255) | running, succeeded, failed, stopped, partial-succeeded |
| outputs | LongText | Output JSON |
| error | LongText NULL | Error message |
| elapsed_time | Float | Seconds (default: 0) |
| total_tokens | BigInteger | Total tokens (default: 0) |
| total_steps | Integer NULL | Steps count |
| exceptions_count | Integer NULL | Exception count |
| created_by_role | String(255) | "account" or "end_user" |
| created_by | StringUUID | User who triggered |
| created_at, finished_at | DateTime | Timing |

### 1.5 Entity Relationship Diagram

```
┌────────────┐    1:1     ┌─────────────────┐
│    App      │──────────→│ AppModelConfig   │  (for chat/completion/agent)
│            │            └─────────────────┘
│ mode       │
│ workflow_id─│──────┐ 1:1 (published)
│ app_model_  │      │
│ config_id   │      ▼
│ enable_site │    ┌──────────┐   1:N (versions)
│ enable_api  │    │ Workflow  │──────────────────→ WorkflowRun
└─────┬───┬──┘    │ version:  │                     │
      │   │       │ "draft"   │                     └→ WorkflowNodeExecution
      │   │       │ or dated  │
      │   │       └──────────┘
      │   │
      │   └──────→ ┌──────┐  1:1
      │            │ Site  │  (share token, theme, branding)
      │            └──────┘
      │
      └──────────→ ┌──────────────┐  1:N
                   │ Conversation  │
                   │ is_deleted    │
                   └──────┬───────┘
                          │  1:N
                          ▼
                   ┌──────────┐
                   │ Message   │──→ MessageFeedback (1:N)
                   │ tokens    │──→ MessageFile (1:N)
                   │ cost      │──→ MessageAnnotation (1:N)
                   │ answer    │──→ MessageAgentThought (1:N)
                   └──────────┘

┌──────────┐  N:1 App
│ ApiToken  │  (type="app", token="app-xxx")
└──────────┘

┌──────────┐  N:1 App
│ EndUser   │  (session-based, per-app)
└──────────┘

┌───────────────┐  N:1 App
│ InstalledApp   │  (cross-workspace installs)
└───────────────┘

┌─────────────────┐
│ RecommendedApp   │  (template marketplace)
│ category, lang   │
└─────────────────┘
```

---

## 2. App Creation Flow

**Files:**
- `api/controllers/console/app/app.py` — `AppListApi.post()`
- `api/services/app_service.py:80-173` — `AppService.create_app()`
- `constants/model_template.py` — `default_app_templates`
- `events/app_event.py` — `app_was_created` signal

### 2.1 Endpoint

```
POST /console/api/apps
```

**Request:**
```json
{
  "name": "My App",                    // required, min 1 char
  "mode": "chat",                      // required: chat|agent-chat|advanced-chat|workflow|completion
  "description": "Description",        // optional, max 400 chars
  "icon_type": "emoji",                // optional: emoji|image|link
  "icon": "🤖",                        // optional
  "icon_background": "#FFEAD5"         // optional
}
```

**Permissions:** `login_required`, `edit_permission_required`, `cloud_edition_billing_resource_check`

### 2.2 Creation Sequence

```
1. Validate mode → AppMode enum
2. Load default template from default_app_templates[mode]
3. Resolve default LLM model:
   a. Try ModelManager.get_default_model_instance(tenant_id, ModelType.LLM)
   b. If provider matches template → use template defaults
   c. If different provider → fetch model schema, build new config
   d. If no provider → get_default_provider_model_name fallback
4. Create App record:
   - Set name, description, mode, icon, tenant_id
   - enable_site = True (from template)
   - enable_api = True (from template)
5. If mode has model_config template:
   - Create AppModelConfig with defaults
   - Link via app.app_model_config_id
6. db.session.commit()
7. Fire app_was_created event → creates Site record (via event handler)
8. If webapp_auth feature enabled → set access_mode to "private"
9. If billing enabled → clean billing cache
10. Return App
```

### 2.3 What the Event Handler Creates

The `app_was_created` event triggers creation of:
- **Site** record with auto-generated 16-char `code` (share token)
- Default site settings (title = app.name, language, etc.)

### 2.4 App Templates

**File:** `constants/model_template.py`

Each mode has a default template dict containing:
- `app`: base App field defaults (`enable_site: True`, `enable_api: True`)
- `model_config`: default AppModelConfig fields (prompt, model settings, features)

For workflow/advanced-chat modes, no `model_config` template is provided — the user creates the workflow via the canvas editor.

---

## 3. App Configuration Panel

### 3.1 Non-Workflow Apps (CHAT, COMPLETION, AGENT_CHAT)

**Endpoint:** `POST /console/api/apps/{app_id}/model-config`

**File:** `api/controllers/console/app/model_config.py`

**Request Body — Full Configuration:**
```json
{
  "model": {
    "provider": "openai",
    "name": "gpt-4",
    "mode": "chat",
    "completion_params": { "temperature": 0.7, "max_tokens": 4096 }
  },
  "pre_prompt": "You are a helpful assistant. {{variable1}}",
  "prompt_type": "simple",
  "opening_statement": "Hello! How can I help?",
  "suggested_questions": ["What can you do?", "Tell me about..."],
  "suggested_questions_after_answer": { "enabled": true },
  "speech_to_text": { "enabled": false },
  "text_to_speech": { "enabled": false, "voice": "", "language": "" },
  "more_like_this": { "enabled": false },
  "sensitive_word_avoidance": { "enabled": false, "type": "", "configs": [] },
  "retriever_resource": { "enabled": true },
  "user_input_form": [
    { "text-input": { "label": "Topic", "variable": "variable1", "required": true, "default": "" } },
    { "paragraph": { "label": "Context", "variable": "context", "required": false } },
    { "select": { "label": "Style", "variable": "style", "options": ["formal","casual"], "required": true } }
  ],
  "dataset_configs": { "retrieval_model": "multiple" },
  "dataset_query_variable": "",
  "file_upload": {
    "image": { "enabled": true, "number_limits": 3, "detail": "high", "transfer_methods": ["local_file","remote_url"] }
  },
  "agent_mode": {
    "enabled": true,
    "strategy": "function_call",
    "tools": [
      { "provider_type": "builtin", "provider_id": "google", "tool_name": "google_search", "tool_parameters": {} }
    ]
  },
  "chat_prompt_config": {},
  "completion_prompt_config": {},
  "external_data_tools": []
}
```

**Process:**
1. Validate via `AppModelConfigService.validate_configuration()`
2. Create NEW AppModelConfig record (immutable — each save creates new row)
3. For agent-chat: encrypt tool parameters
4. Update `app.app_model_config_id` to new config ID
5. Fire `app_model_config_was_updated` event

### 3.2 Workflow-Based Apps (WORKFLOW, ADVANCED_CHAT)

**Endpoint:** `POST /console/api/apps/{app_id}/workflows/draft/sync`

**File:** `api/controllers/console/app/workflow.py`

**Request Body:**
```json
{
  "graph": {
    "nodes": [
      { "id": "start", "data": { "type": "start", "title": "Start", "variables": [] } },
      { "id": "llm-1", "data": { "type": "llm", "title": "LLM", "model": {...}, "prompt_template": [...] } },
      { "id": "end", "data": { "type": "end", "title": "End", "outputs": [] } }
    ],
    "edges": [
      { "id": "e1", "source": "start", "target": "llm-1" },
      { "id": "e2", "source": "llm-1", "target": "end" }
    ]
  },
  "features": {
    "opening_statement": "Hello!",
    "suggested_questions": [],
    "text_to_speech": { "enabled": false },
    "file_upload": { "image": { "enabled": false } }
  },
  "hash": "abc123...",
  "environment_variables": [],
  "conversation_variables": []
}
```

**Process:**
1. Hash-based conflict detection (optimistic concurrency)
2. Updates the single draft Workflow record (version="draft")
3. Features stored as JSON in Workflow.features
4. Fires `app_model_config_was_updated` event

### 3.3 Frontend Configuration Panel

**Directory:** `web/app/components/app/configuration/`

The configuration panel is a React component tree providing UI for all the config fields above. It renders different sections based on app mode:

- **Prompt Template**: System prompt editor with variable interpolation (`{{variable}}`)
- **Variables**: Dynamic form builder for user_input_form
- **Model Selection**: Provider + model picker with completion_params
- **Tools** (agent only): Tool browser and configuration
- **Datasets**: Knowledge base attachment and retrieval settings
- **Features**: Toggle switches for speech-to-text, text-to-speech, etc.

---

## 4. Publishing Flow (Draft vs Published)

### 4.1 State Machine

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
                    ▼                                         │
┌──────────┐  sync_draft  ┌──────────┐  publish  ┌──────────┐│
│  Created  │────────────→│  Draft   │──────────→│ Published ││
│  (empty)  │             │ (editing)│           │ (v1, v2..)││
└──────────┘             └────┬─────┘           └──────────┘│
                              │                       │       │
                              │    ◄── reset to ──────┘       │
                              │        published              │
                              │                               │
                              └───── sync again ──────────────┘
```

### 4.2 For Non-Workflow Apps (CHAT, COMPLETION, AGENT_CHAT)

**No draft/publish cycle.** Each config update creates a new `AppModelConfig` record and atomically updates `app.app_model_config_id`. The previous config records remain in the database but are orphaned.

### 4.3 For Workflow Apps (WORKFLOW, ADVANCED_CHAT)

**File:** `api/services/workflow_service.py:92-317`

#### Draft Operations

- **Get draft:** `GET /console/api/apps/{app_id}/workflows/draft`
  - Queries Workflow where `version == "draft"` and `app_id == app.id`
  - Exactly ONE draft per app

- **Sync draft:** `POST /console/api/apps/{app_id}/workflows/draft/sync`
  - Updates the draft Workflow record in-place
  - Hash-based optimistic concurrency control
  - Returns updated draft

#### Publish Operation

**Endpoint:** `POST /console/api/apps/{app_id}/workflows/publish`

**File:** `api/services/workflow_service.py:252-317`

**Process:**
```
1. Load draft workflow (version="draft")
2. Validate credentials (if plugin_manager enabled)
3. Validate graph structure
4. Billing check (SANDBOX plan: max 2 trigger nodes)
5. Create NEW Workflow record:
   - version = timestamp-based string (e.g., "2024-01-15T10:30:00")
   - Copy: graph, features, environment_variables, conversation_variables
   - Set: marked_name, marked_comment
6. Add to session
7. Fire app_published_workflow_was_updated event
   → This updates app.workflow_id to new published workflow
8. Draft remains unchanged for continued editing
```

**Key insight:** `app.workflow_id` always points to the latest **published** workflow. `version="draft"` is the working copy. Multiple published versions coexist in the database.

#### Published Workflow Versions

- **List versions:** `GET /console/api/apps/{app_id}/workflows/published`
  - Returns paginated list of all published workflow versions
  - Each with `marked_name`, `marked_comment`, `created_at`, `created_by`
  - Supports `named_only` filter

- **Get specific version:** `GET /console/api/apps/{app_id}/workflows/published/{workflow_id}`

### 4.4 Workflow Version Naming

```python
@staticmethod
def version_from_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")
```

Versions are human-readable timestamps. Users can additionally assign `marked_name` (max 20 chars) and `marked_comment` (max 100 chars) during publish.

---

## 5. App API (Service API)

**Directory:** `api/controllers/service_api/`

### 5.1 Authentication

**File:** `api/controllers/service_api/wraps.py`

```
Authorization: Bearer app-<random_string>
```

**Validation flow:**
1. Extract token from `Authorization` header
2. Query `ApiToken` where `token == value` and `type == "app"`
3. Update `last_used_at` if stale (>1 minute)
4. Load associated App
5. Verify `app.enable_api == True` and `app.status == "normal"`
6. Verify tenant status != ARCHIVE
7. Optionally resolve EndUser from query/JSON/form `user` parameter

### 5.2 Endpoints

#### Chat Messages

```
POST /v1/chat-messages
```
**Modes:** CHAT, AGENT_CHAT, ADVANCED_CHAT

**Request:**
```json
{
  "query": "Hello, what can you do?",
  "inputs": { "variable1": "value" },
  "conversation_id": "uuid-or-empty",
  "response_mode": "blocking|streaming",
  "files": [{ "type": "image", "transfer_method": "local_file", "upload_file_id": "uuid" }],
  "user": "end_user_id"
}
```

**Response (blocking):**
```json
{
  "event": "message",
  "message_id": "uuid",
  "conversation_id": "uuid",
  "answer": "Response text",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Response (streaming):** SSE events

```
POST /v1/chat-messages/{task_id}/stop
```

#### Completion

```
POST /v1/completion-messages
```
**Modes:** COMPLETION only

```
POST /v1/completion-messages/{task_id}/stop
```

#### Workflows

```
POST /v1/workflows/run                          # Execute default published workflow
POST /v1/workflows/{workflow_id}/run             # Execute specific workflow version
GET  /v1/workflows/run/{workflow_run_id}         # Get run details
POST /v1/workflows/tasks/{task_id}/stop          # Stop running workflow
GET  /v1/workflows/logs                          # Paginated execution logs
```

#### Conversations

```
GET    /v1/conversations                         # List (cursor-based, sort_by, pinned filter)
DELETE /v1/conversations/{id}                     # Delete (soft)
POST   /v1/conversations/{id}/name               # Rename
GET    /v1/conversations/{id}/variables           # Get conversation variables
PUT    /v1/conversations/{id}/variables/{var_id}  # Update variable
```

#### Messages

```
GET  /v1/messages                                # List messages in conversation
POST /v1/messages/{id}/feedbacks                  # Submit feedback (like/dislike)
GET  /v1/messages/{id}/suggested                  # Get suggested follow-up questions
```

#### Files

```
POST /v1/files/upload                            # Upload file (multipart, single file)
```

#### App Info

```
GET /v1/parameters                               # Get app parameters (input form, features)
GET /v1/meta                                     # Get tool icons and metadata
GET /v1/info                                     # Get app basic info
```

#### Annotations

```
GET    /v1/apps/annotations                      # List
POST   /v1/apps/annotations                      # Create
PUT    /v1/apps/annotations/{id}                  # Update
DELETE /v1/apps/annotations/{id}                  # Delete
POST   /v1/apps/annotation-reply/{enable|disable} # Toggle annotation reply
GET    /v1/apps/annotation-reply/{action}/status/{job_id} # Job status
```

### 5.3 Error Codes

| Error | HTTP | Description |
|-------|------|-------------|
| AppUnavailableError | 403 | App doesn't exist or API disabled |
| NotChatAppError | 403 | Endpoint requires chat app |
| NotWorkflowAppError | 403 | Endpoint requires workflow app |
| ConversationNotExistsError | 404 | Conversation not found |
| ProviderQuotaExceededError | 400 | LLM quota exceeded |
| InvokeRateLimitError | 429 | Rate limit hit |

---

## 6. Embed / iframe Widget

### 6.1 Architecture

**Files:**
- `web/app/components/app/overview/embedded/index.tsx` — Embed code generator UI
- `web/public/embed.js` — Browser-side chatbot injection script
- `web/app/components/base/chat/embedded-chatbot/index.tsx` — Embedded chatbot component
- `web/app/(shareLayout)/chatbot/[token]/` — Share route

### 6.2 Three Embedding Methods

#### iframe

```html
<iframe
  src="{APP_WEB_URL}/chatbot/{site.code}"
  style="width: 100%; height: 100%; min-height: 700px"
  frameborder="0"
  allow="microphone">
</iframe>
```

#### Script Tag (Bubble Widget)

```html
<script>
  window.difyChatbotConfig = {
    token: '{site.code}',
    baseUrl: '{APP_WEB_URL}',
    inputs: { key: "VALUE" },
    systemVariables: { user_id: 'UUID', conversation_id: 'UUID' },
    userVariables: { avatar_url: 'url', name: 'User Name' }
  }
</script>
<script src="{APP_WEB_URL}/embed.min.js" id="{site.code}" defer></script>
```

The script creates a floating bubble button (bottom-right) that opens a chat iframe on click.

**Styling:**
- Default: 24rem × 43.75rem (384×700px)
- Expanded: 48% width × 88% height
- Z-index: 2147483640
- Configurable primary color via CSS variable
- Mobile-responsive

#### Chrome Plugin

Direct URL: `{APP_WEB_URL}/chatbot/{site.code}`

### 6.3 Share URL Structure

```
/chatbot/{token}    → Embedded chatbot (for iframe/bubble)
/chat/{token}       → Full-page chat interface
/completion/{token} → Completion interface
/workflow/{token}   → Workflow interface
```

The `token` is `site.code` (16-char random string). No API token needed — authentication is via the share token.

### 6.4 Site Configuration API

```
POST /console/api/apps/{app_id}/site          # Update site settings
POST /console/api/apps/{app_id}/site/access-token-reset  # Regenerate share token
```

---

## 7. App Templates / Marketplace

### 7.1 Architecture

**Files:**
- `api/services/recommended_app_service.py` — Template service
- `api/controllers/console/explore/recommended_app.py` — Console API
- `api/models/model.py:543-571` — RecommendedApp model

### 7.2 RecommendedApp Model

**Table:** `recommended_apps`

| Column | Type | Description |
|--------|------|-------------|
| id | StringUUID (PK) | Template ID |
| app_id | StringUUID | Source App ID |
| description | JSON | Multi-language descriptions |
| copyright | String(255) | Copyright |
| privacy_policy | String(255) | Privacy URL |
| custom_disclaimer | LongText | Disclaimer |
| category | String(255) | Category name |
| position | Integer | Sort order |
| is_listed | Boolean | Visible in marketplace |
| install_count | Integer | Install counter |
| language | String(255) | Language code (default: "en-US") |

### 7.3 Template Retrieval Modes

Configurable via `HOSTED_FETCH_APP_TEMPLATES_MODE`:
1. **Built-in**: Local YAML files with predefined templates
2. **Hosted**: Remote API/marketplace
3. **Custom**: User-defined templates

### 7.4 Endpoints

```
GET  /console/api/explore/apps                    # List templates (by language)
GET  /console/api/explore/apps/{app_id}           # Get template detail
```

### 7.5 Installing a Template

Templates are installed by exporting the source app's DSL and importing it into the user's workspace. This reuses the DSL import/export system (Section 10).

---

## 8. Conversation Management

### 8.1 Service Layer

**File:** `api/services/conversation_service.py`

### 8.2 Key Operations

| Operation | Method | Details |
|-----------|--------|---------|
| List | `pagination_by_last_id()` | Keyset pagination, sort by created_at or updated_at |
| Delete | `delete()` | Soft delete (`is_deleted = True`) |
| Rename | `rename()` | Manual name or auto-generate via LLM |
| Get Variables | `get_conversational_variable()` | Paginated variable list |
| Update Variable | `update_conversation_variable()` | Type-validated update |

### 8.3 Pagination Algorithm

Uses **keyset pagination** (not offset-based):

```python
1. If last_id provided:
   a. Load reference conversation
   b. Build filter: created_at < ref.created_at (for -created_at sort)
2. Query with limit + 1 to detect has_more
3. Return InfiniteScrollPagination(data, limit, has_more)
```

### 8.4 Conversation Scoping

| Caller | from_source | User Filter |
|--------|-------------|-------------|
| Service API (EndUser) | "api" | from_end_user_id = user.id |
| Console (Account) | "console" | from_account_id = user.id |
| Web App (EndUser) | "api" | from_end_user_id = user.id |

All queries also filter by `is_deleted == False` and `app_id == app.id`.

### 8.5 Conversation Variables

**Table:** `conversation_variables`

Purpose: Store persistent state across turns in advanced-chat workflows.

| Column | Type |
|--------|------|
| id | UUID |
| conversation_id | UUID |
| variable_name | String (validated: alphanumeric, `-`, `_`, `.`) |
| value | JSON |
| variable_type | String |

**Security:** Variable names validated against SQL injection patterns (`'`, `"`, `;`, `--`, `/*`).

---

## 9. App-Level Analytics

### 9.1 Endpoints

**File:** `api/controllers/console/app/statistic.py`

All endpoints accept `start` and `end` query params (format: `YYYY-MM-DD HH:MM`), convert from user timezone to UTC, and exclude debugger invocations.

| Endpoint | Metric | App Modes |
|----------|--------|-----------|
| `GET /apps/{id}/statistics/daily-messages` | Messages per day | All |
| `GET /apps/{id}/statistics/daily-conversations` | Unique conversations per day | All |
| `GET /apps/{id}/statistics/daily-end-users` | Unique end users per day | All |
| `GET /apps/{id}/statistics/token-costs` | Token count + cost per day | All |
| `GET /apps/{id}/statistics/average-session-interactions` | Avg messages per conversation per day | CHAT, AGENT_CHAT, ADVANCED_CHAT |
| `GET /apps/{id}/statistics/user-satisfaction-rate` | Like rate (likes/messages × 1000) | All |
| `GET /apps/{id}/statistics/average-response-time` | Provider latency in ms per day | COMPLETION only |
| `GET /apps/{id}/statistics/tokens-per-second` | TPS (answer_tokens / latency) | All |

### 9.2 Response Format

```json
{
  "data": [
    { "date": "2024-01-15", "<metric_name>": <value> }
  ]
}
```

---

## 10. App Import / Export (DSL)

### 10.1 DSL Format

**File:** `api/services/app_dsl_service.py`

**Current version:** `0.5.0` | **Format:** YAML | **Max size:** 10MB

#### For Workflow/Advanced-Chat Apps:
```yaml
version: "0.5.0"
kind: "app"
app:
  name: "My Workflow"
  mode: "workflow"           # or "advanced-chat"
  icon: "🤖"
  icon_background: "#FFEAD5"
  description: "A workflow app"
  use_icon_as_answer_icon: false

workflow:
  graph:
    nodes:
      - id: "start"
        data: { type: "start", title: "Start", variables: [] }
      - id: "llm-1"
        data: { type: "llm", title: "LLM", model: {...}, prompt_template: [...] }
      - id: "end"
        data: { type: "end", title: "End", outputs: [] }
    edges:
      - { id: "e1", source: "start", target: "llm-1" }
      - { id: "e2", source: "llm-1", target: "end" }
  features:
    opening_statement: ""
    suggested_questions: []
  environment_variables: []
  conversation_variables: []

dependencies:
  - { package_name: "langgenius/openai", version: "1.0.0" }
```

#### For Chat/Completion/Agent Apps:
```yaml
version: "0.5.0"
kind: "app"
app:
  name: "My Chatbot"
  mode: "chat"
  icon: "🤖"
  icon_background: "#FFEAD5"
  description: "A chat app"

model_config:
  model: { provider: "openai", name: "gpt-4", mode: "chat", completion_params: {} }
  pre_prompt: "You are helpful."
  opening_statement: "Hello!"
  suggested_questions: ["Question 1"]
  agent_mode: { enabled: false, strategy: null, tools: [] }
  # ... all AppModelConfig fields

dependencies:
  - { package_name: "langgenius/openai", version: "1.0.0" }
```

### 10.2 Import Flow

**Endpoint:** `POST /console/api/apps/import`

```python
import_mode: "yaml-content" | "yaml-url"
yaml_content: str              # direct YAML
yaml_url: str                  # URL (GitHub auto-converted to raw)
name, description, icon: str   # optional overrides
app_id: str                    # optional: overwrite existing app (workflow/advanced-chat only)
```

**Import State Machine:**

```
                    ┌──────────┐
         Parse YAML │          │
    ┌──────────────→│ VALIDATE │
    │               │          │
    │               └────┬─────┘
    │                    │
    │         ┌──────────┼──────────┐
    │         ▼          ▼          ▼
    │   ┌──────────┐ ┌────────┐ ┌───────────────────┐
    │   │ COMPLETED │ │ WARN   │ │ PENDING            │
    │   │          │ │ (minor │ │ (major version gap) │
    │   └──────────┘ │ version│ │ → stored in Redis   │
    │                │ gap)   │ │ → 10 min expiry     │
    │                └────────┘ └──────────┬──────────┘
    │                                      │
    │                              confirm_import()
    │                                      │
    │                                      ▼
    │                               ┌──────────┐
    │                               │ COMPLETED │
    │                               └──────────┘
    │
    │    On any error:
    │         ┌──────────┐
    └────────→│  FAILED  │
              └──────────┘
```

**Version Compatibility:**
```
imported > current           → PENDING (user confirmation required)
imported.major < current.major → PENDING (breaking changes)
imported.minor < current.minor → COMPLETED_WITH_WARNINGS
otherwise                     → COMPLETED
```

### 10.3 Export Flow

**Endpoint:** `GET /console/api/apps/{app_id}/export`

**Query params:**
- `include_secret`: bool (default: false) — include credentials
- `workflow_id`: string — export specific published version (default: draft)

**Process:**
1. Build export dict with app metadata
2. For workflow apps: serialize draft workflow graph, features, variables; encrypt dataset IDs; strip webhook URLs and schedule configs
3. For model config apps: serialize AppModelConfig
4. Extract dependencies from nodes (tools, models, datasets)
5. Return YAML string

### 10.4 App Copy

**Endpoint:** `POST /console/api/apps/{app_id}/copy`

Internally uses: `export_dsl(include_secret=True)` → `import_app(yaml_content=...)`. This ensures a complete deep copy including all configuration.

---

## Appendix A: Key File Index

| Area | File |
|------|------|
| App model | `api/models/model.py:78` |
| AppMode enum | `api/models/model.py:49` |
| AppModelConfig model | `api/models/model.py:318` |
| Workflow model | `api/models/workflow.py:102` |
| WorkflowRun model | `api/models/workflow.py` |
| Conversation model | `api/models/model.py:637` |
| Message model | `api/models/model.py:960` |
| Site model | `api/models/model.py:1637` |
| ApiToken model | `api/models/model.py:1696` |
| EndUser model | `api/models/model.py:1561` |
| RecommendedApp model | `api/models/model.py:543` |
| App controller | `api/controllers/console/app/app.py` |
| Workflow controller | `api/controllers/console/app/workflow.py` |
| Model config controller | `api/controllers/console/app/model_config.py` |
| Statistics controller | `api/controllers/console/app/statistic.py` |
| Site controller | `api/controllers/console/app/site.py` |
| Service API controllers | `api/controllers/service_api/` |
| Web/share controllers | `api/controllers/web/` |
| App service | `api/services/app_service.py` |
| Workflow service | `api/services/workflow_service.py` |
| Conversation service | `api/services/conversation_service.py` |
| DSL service | `api/services/app_dsl_service.py` |
| Recommended app service | `api/services/recommended_app_service.py` |
| Embed script | `web/public/embed.js` |
| Embed UI component | `web/app/components/app/overview/embedded/index.tsx` |
| Embedded chatbot | `web/app/components/base/chat/embedded-chatbot/index.tsx` |
| Share routes | `web/app/(shareLayout)/` |
| App runners | `api/core/app/apps/{mode}/app_runner.py` |
| App generators | `api/core/app/apps/{mode}/app_generator.py` |
| Config managers | `api/core/app/apps/{mode}/app_config_manager.py` |
| Default templates | `constants/model_template.py` |

## Appendix B: Queue Events (Execution Pipeline)

### Message-Based Apps (CHAT, COMPLETION, AGENT_CHAT)

| Event | Description |
|-------|-------------|
| QueueTextChunkEvent | Streaming text chunk |
| QueueLLMChunkEvent | Token-level streaming |
| QueueAnnotationReplyEvent | Annotation hit |
| QueueAgentMessageEvent | Agent thought step |

### Workflow-Based Apps (WORKFLOW, ADVANCED_CHAT)

| Event | Description |
|-------|-------------|
| QueueWorkflowStartedEvent | Workflow execution started |
| QueueNodeStartedEvent | Node execution started |
| QueueNodeSucceededEvent | Node completed |
| QueueNodeFailedEvent | Node failed |
| QueueLoopStartEvent | Loop iteration started |
| QueueLoopNextEvent | Loop next iteration |
| QueueLoopCompletedEvent | Loop finished |
| QueueIterationStartEvent | Iteration started |
| QueueIterationCompletedEvent | Iteration finished |
| QueueWorkflowSucceededEvent | Workflow completed |
| QueueWorkflowFailedEvent | Workflow failed |
