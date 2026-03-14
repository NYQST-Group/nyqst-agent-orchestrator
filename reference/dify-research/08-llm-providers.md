# Requirements Document: Dify LLM Provider Connection System

**Source**: Dify v1.11.4 codebase analysis
**Date**: 2026-02-01
**Scope**: Complete specification for the model provider registration, connection, credential management, load balancing, and model selection system.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Model Provider Registration & Configuration](#2-model-provider-registration--configuration)
3. [Plugin Daemon Integration (No LiteLLM)](#3-plugin-daemon-integration)
4. [Credential Management](#4-credential-management)
5. [Model Selection: Workflows vs Chatbot](#5-model-selection)
6. [Load Balancing](#6-load-balancing)
7. [Custom/Local Model Connections](#7-customlocal-model-connections)
8. [API Endpoints](#8-api-endpoints)
9. [Pricing & Quota System](#9-pricing--quota-system)
10. [Frontend UI Components](#10-frontend-ui-components)
11. [Database Schema](#11-database-schema)
12. [Data Models & Entities](#12-data-models--entities)

---

## 1. Architecture Overview

### High-Level Call Chain

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (React/Next.js)                                        │
│  ModelProviderPage → ModelSelector → ModelParameterModal         │
│  ↓ REST API calls                                                │
├─────────────────────────────────────────────────────────────────┤
│  API Controllers (Flask-RESTful)                                 │
│  controllers/console/workspace/model_providers.py                │
│  controllers/console/workspace/models.py                         │
│  controllers/console/workspace/load_balancing_config.py          │
│  ↓                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer                                                   │
│  services/model_provider_service.py                              │
│  services/model_load_balancing_service.py                        │
│  ↓                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Provider Manager + Model Manager (Orchestration)                │
│  core/provider_manager.py  → ProviderManager                    │
│  core/model_manager.py     → ModelManager, ModelInstance,        │
│                               LBModelManager                     │
│  ↓                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Model Runtime Layer                                             │
│  core/model_runtime/model_providers/model_provider_factory.py    │
│  core/model_runtime/model_providers/__base/                      │
│  core/model_runtime/entities/                                    │
│  core/model_runtime/schema_validators/                           │
│  ↓                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Plugin Client (HTTP)                                            │
│  core/plugin/impl/model.py → PluginModelClient                  │
│  core/plugin/impl/base.py  → BasePluginClient                   │
│  ↓ HTTP POST/GET                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Plugin Daemon (External Process)                                │
│  Configured via PLUGIN_DAEMON_URL + PLUGIN_DAEMON_KEY            │
│  ↓                                                               │
├─────────────────────────────────────────────────────────────────┤
│  Model Provider Plugins (OpenAI, Anthropic, Ollama, etc.)        │
│  Each is an installable plugin with its own Python runtime       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decision: Plugin-Based, NOT LiteLLM

**Dify does NOT use LiteLLM.** There are zero references to litellm in the codebase. Instead, Dify uses a **plugin daemon architecture** where each model provider is an independently deployable plugin that communicates with the Dify core via HTTP through a plugin daemon service.

### Key Files Map

| Layer | File Path | Primary Class |
|-------|-----------|---------------|
| Controller | `api/controllers/console/workspace/model_providers.py` | `ModelProviderListApi`, `ModelProviderCredentialApi` |
| Controller | `api/controllers/console/workspace/models.py` | `DefaultModelApi`, `ModelProviderModelApi` |
| Controller | `api/controllers/console/workspace/load_balancing_config.py` | `LoadBalancingCredentialsValidateApi` |
| Service | `api/services/model_provider_service.py` | `ModelProviderService` |
| Service | `api/services/model_load_balancing_service.py` | `ModelLoadBalancingService` |
| Orchestration | `api/core/provider_manager.py` | `ProviderManager` |
| Orchestration | `api/core/model_manager.py` | `ModelManager`, `ModelInstance`, `LBModelManager` |
| Config Entity | `api/core/entities/provider_configuration.py` | `ProviderConfiguration`, `ProviderConfigurations` |
| Config Entity | `api/core/entities/provider_entities.py` | `SystemConfiguration`, `CustomConfiguration`, `QuotaConfiguration` |
| Factory | `api/core/model_runtime/model_providers/model_provider_factory.py` | `ModelProviderFactory` |
| Base Models | `api/core/model_runtime/model_providers/__base/ai_model.py` | `AIModel` |
| Base Models | `api/core/model_runtime/model_providers/__base/large_language_model.py` | `LargeLanguageModel` |
| Plugin Client | `api/core/plugin/impl/model.py` | `PluginModelClient` |
| Plugin Client | `api/core/plugin/impl/base.py` | `BasePluginClient` |
| Plugin Entities | `api/core/plugin/entities/plugin_daemon.py` | `PluginModelProviderEntity` |
| Entities | `api/core/model_runtime/entities/model_entities.py` | `ModelType`, `AIModelEntity`, `ParameterRule` |
| Entities | `api/core/model_runtime/entities/provider_entities.py` | `ProviderEntity`, `CredentialFormSchema` |
| Entities | `api/core/model_runtime/entities/llm_entities.py` | `LLMResult`, `LLMResultChunk`, `LLMUsage` |
| Validators | `api/core/model_runtime/schema_validators/` | `CommonValidator`, `ProviderCredentialSchemaValidator` |
| Encryption | `api/core/helper/encrypter.py` | `encrypt_token()`, `decrypt_token()` |
| DB Models | `api/models/provider.py` | `Provider`, `ProviderModel`, `ProviderCredential`, etc. |
| ID System | `api/models/provider_ids.py` | `ModelProviderID`, `GenericProviderID` |
| Workflow Node | `api/core/workflow/nodes/llm/entities.py` | `LLMNodeData`, `ModelConfig` |
| App Config | `api/core/app/app_config/easy_ui_based_app/model_config/manager.py` | `ModelConfigManager` |

---

## 2. Model Provider Registration & Configuration

### 2.1 Provider Identity System

**File**: `api/models/provider_ids.py`

Providers are identified by a three-part ID: `{organization}/{plugin_name}/{provider_name}`

```python
class GenericProviderID:
    organization: str       # e.g., "langgenius"
    plugin_name: str        # e.g., "openai"
    provider_name: str      # e.g., "openai"
    is_hardcoded: bool      # True if shorthand format used

    @property
    def plugin_id(self) -> str:  # "{organization}/{plugin_name}"
```

- **Shorthand**: `"openai"` → resolved to `"langgenius/openai/openai"` (hardcoded=True)
- **Full format**: `"langgenius/openai/openai"` (hardcoded=False)
- **Special aliases**: Google → `"gemini"` alias handling in `ModelProviderID`

### 2.2 Provider Discovery

**File**: `api/core/model_runtime/model_providers/model_provider_factory.py`

```python
class ModelProviderFactory:
    def __init__(self, tenant_id: str)

    def get_providers() -> Sequence[ProviderEntity]
    def get_plugin_model_providers() -> Sequence[PluginModelProviderEntity]
    def get_provider_schema(provider: str) -> ProviderEntity
    def get_model_type_instance(provider, model_type) -> AIModel
    def get_models(provider, model_type, provider_configs) -> list[SimpleProviderEntity]
```

Discovery flow:
1. `PluginModelClient.fetch_model_providers(tenant_id)` → HTTP GET to plugin daemon
2. Plugin daemon returns all installed model provider plugins for tenant
3. Results cached in `contextvars` with thread-safe locking per tenant
4. Provider names prefixed with plugin_id: `f"{plugin_id}/{provider_name}"`

### 2.3 Provider Ordering

**File**: `api/core/model_runtime/model_providers/_position.yaml`

YAML list defining display order. Top entries (44 providers listed):
```yaml
- openai
- deepseek
- anthropic
- azure_openai
- google
- vertex_ai
- nvidia
- ollama
- mistralai
- groq
- xinference
- localai
- openai_api_compatible
# ... 31 more
```

### 2.4 Configuration Methods

Providers support one or more configuration methods:

```python
class ConfigurateMethod(StrEnum):
    PREDEFINED_MODEL = "predefined-model"      # Fixed list (OpenAI, Anthropic)
    CUSTOMIZABLE_MODEL = "customizable-model"   # User-specified model name (Ollama, OpenAI-compatible)
```

### 2.5 Provider Entity Schema

**File**: `api/core/model_runtime/entities/provider_entities.py`

```python
class ProviderEntity(BaseModel):
    provider: str                                    # Provider identifier
    label: I18nObject                                # Display name (i18n)
    description: I18nObject | None                   # Description (i18n)
    icon_small: I18nObject | None                    # Small icon URL
    icon_small_dark: I18nObject | None               # Dark mode icon
    background: str | None                           # Background color
    help: ProviderHelpEntity | None                  # Help link
    supported_model_types: list[ModelType]            # LLM, embedding, etc.
    configurate_methods: list[ConfigurateMethod]      # predefined vs customizable
    models: list[AIModelEntity]                       # Available models
    provider_credential_schema: ProviderCredentialSchema | None
    model_credential_schema: ModelCredentialSchema | None
    position: int | None                              # Display position
```

---

## 3. Plugin Daemon Integration

### 3.1 Communication Protocol

**File**: `api/core/plugin/impl/base.py`

```python
class BasePluginClient:
    plugin_daemon_inner_api_baseurl: str  # from dify_config.PLUGIN_DAEMON_URL
    plugin_daemon_request_timeout: int    # from config (default 600s)
```

All communication uses HTTP REST with:
- API key authentication via `X-Api-Key` header (from `dify_config.PLUGIN_DAEMON_KEY`)
- OpenTelemetry W3C traceparent header injection for distributed tracing
- JSON request/response with streaming support via chunked transfer

### 3.2 Plugin Model Client API

**File**: `api/core/plugin/impl/model.py`

| Method | HTTP | Path | Purpose |
|--------|------|------|---------|
| `fetch_model_providers` | GET | `plugin/{tenant_id}/management/models` | List all providers |
| `get_model_schema` | POST | `plugin/{tenant_id}/dispatch/model/schema` | Get model schema |
| `validate_provider_credentials` | POST | `plugin/{tenant_id}/dispatch/model/validate_provider_credentials` | Validate creds |
| `validate_model_credentials` | POST | `plugin/{tenant_id}/dispatch/model/validate_model_credentials` | Validate model creds |
| `invoke_llm` | POST | `plugin/{tenant_id}/dispatch/llm/invoke` | Invoke LLM (streaming) |
| `get_llm_num_tokens` | POST | `plugin/{tenant_id}/dispatch/llm/num_tokens` | Count tokens |
| `invoke_text_embedding` | POST | `plugin/{tenant_id}/dispatch/text_embedding/invoke` | Generate embeddings |
| `invoke_rerank` | POST | `plugin/{tenant_id}/dispatch/rerank/invoke` | Rerank documents |
| `invoke_tts` | POST | `plugin/{tenant_id}/dispatch/tts/invoke` | Text to speech |
| `invoke_speech_to_text` | POST | `plugin/{tenant_id}/dispatch/speech2text/invoke` | Speech recognition |
| `invoke_moderation` | POST | `plugin/{tenant_id}/dispatch/moderation/invoke` | Content moderation |

### 3.3 Plugin Provider Entity

**File**: `api/core/plugin/entities/plugin_daemon.py`

```python
class PluginModelProviderEntity(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    provider: str                           # "{plugin_id}/{provider_name}"
    tenant_id: str
    plugin_unique_identifier: str
    plugin_id: str
    declaration: ProviderEntity             # Full provider schema
```

### 3.4 Model Type Hierarchy

**File**: `api/core/model_runtime/model_providers/__base/`

```
AIModel (base)
├── LargeLanguageModel       model_type = ModelType.LLM
├── TextEmbeddingModel       model_type = ModelType.TEXT_EMBEDDING
├── RerankModel              model_type = ModelType.RERANK
├── TTSModel                 model_type = ModelType.TTS
├── Speech2TextModel         model_type = ModelType.SPEECH2TEXT
└── ModerationModel          model_type = ModelType.MODERATION
```

Each model type instance delegates actual invocation to the plugin daemon via `PluginModelClient`.

---

## 4. Credential Management

### 4.1 Encryption

**File**: `api/core/helper/encrypter.py`

- **Algorithm**: RSA asymmetric encryption
- **Key scope**: Per-tenant RSA key pair (`Tenant.encrypt_public_key`)
- **Storage format**: Base64-encoded encrypted JSON in `encrypted_config` DB columns
- **Encryption**: `rsa.encrypt(token, tenant.encrypt_public_key)` → base64
- **Decryption**: `base64.b64decode(token)` → `rsa.decrypt(data, tenant_id)`
- **Batch optimization**: `batch_decrypt_token()` gets decrypt key once, decrypts list
- **Obfuscation for UI**: First 6 chars + `****` (12 asterisks) + last 2 chars

### 4.2 Credential Form Schema

**File**: `api/core/model_runtime/entities/provider_entities.py`

```python
class CredentialFormSchema(BaseModel):
    variable: str                              # Field name
    label: I18nObject                          # Display label
    type: FormType                             # TEXT_INPUT | SECRET_INPUT | SELECT | RADIO | SWITCH
    required: bool
    default: str | None
    options: list[FormOption] | None           # For SELECT/RADIO
    placeholder: I18nObject | None
    max_length: int | None
    show_on: list[FormShowOnObject]            # Conditional visibility
```

FormType values: `TEXT_INPUT`, `SECRET_INPUT`, `SELECT`, `RADIO`, `SWITCH`

### 4.3 Two-Level Credential Architecture

**Provider-Level Credentials** (shared across all models):
- DB table: `provider_credentials`
- Multiple named credentials per provider per tenant
- One active credential at a time (via `Provider.credential_id` FK)
- Switch active via `/credentials/switch` endpoint

**Model-Level Credentials** (per-model overrides):
- DB table: `provider_model_credentials`
- Multiple named credentials per model per provider per tenant
- Used for customizable models (Ollama, OpenAI-compatible)

### 4.4 Credential Validation Flow

```
1. Frontend collects credentials via dynamic form (CredentialFormSchema)
2. POST /model-providers/{provider}/credentials/validate
3. → ProviderCredentialSchemaValidator validates against schema
   - Checks required fields, max_length, type constraints
   - Evaluates show_on conditions for conditional fields
4. → PluginModelClient.validate_provider_credentials() → HTTP to daemon
5. → Plugin daemon tests actual API connectivity
6. Returns {result: "success"} or {result: "error", error: "message"}
```

### 4.5 Credential Rotation

Credential rotation is manual via the multi-credential system:
1. Add a new named credential
2. Switch active credential to the new one
3. Optionally delete old credential

There is no automatic key rotation mechanism.

### 4.6 Credential Caching

**File**: `api/core/helper/model_provider_cache.py`

`ProviderCredentialsCache` provides a caching layer with types:
- `ProviderCredentialsCacheType` enum for different cache scopes

---

## 5. Model Selection

### 5.1 Default Model Configuration

Each tenant has a default model per model type:

```python
# DB: tenant_default_models table
class TenantDefaultModel:
    tenant_id: str
    provider_name: str
    model_name: str
    model_type: str    # "llm", "text-embedding", "rerank", "speech2text", "tts"
```

API: `GET/POST /workspaces/current/default-model`

### 5.2 Chatbot Mode Model Selection

**File**: `api/core/app/app_config/easy_ui_based_app/model_config/manager.py`

```python
class ModelConfigManager:
    @classmethod
    def validate_and_set_defaults(cls, tenant_id, config) -> (dict, list[str]):
        # Validates:
        # - model.provider exists in registered providers
        # - model.name exists in provider's model list
        # - model.mode auto-detected from model properties (CHAT vs COMPLETION)
        # - model.completion_params validated (stop sequences max 4)
        # Provider format normalized: "openai" → "langgenius/openai/openai"
```

Chatbot apps store model config in the app model JSON:
```json
{
    "model": {
        "provider": "langgenius/openai/openai",
        "name": "gpt-4",
        "mode": "chat",
        "completion_params": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "stop": []
        }
    }
}
```

### 5.3 Workflow Mode Model Selection

**File**: `api/core/workflow/nodes/llm/entities.py`

```python
class ModelConfig(BaseModel):
    provider: str                      # e.g., "langgenius/openai/openai"
    name: str                          # e.g., "gpt-4"
    mode: LLMMode                      # CHAT or COMPLETION
    completion_params: dict[str, Any]  # temperature, max_tokens, etc.

class LLMNodeData(BaseNodeData):
    model: ModelConfig
    prompt_template: Sequence[LLMNodeChatModelMessage] | LLMNodeCompletionModelPromptTemplate
    memory: MemoryConfig | None
    context: ContextConfig
    vision: VisionConfig
    structured_output: Mapping | None
    structured_output_switch_on: bool
    reasoning_format: Literal["separated", "tagged"]
```

Each LLM workflow node stores its own model config independently. Model selection in workflow UI uses `ModelParameterModal` component.

### 5.4 Model Invocation Flow

```
1. ModelManager.get_model_instance(tenant_id, provider, model_type, model)
2.   → ProviderManager.get_configurations(tenant_id)
3.   → ProviderConfiguration.get_current_credentials(model_type, model)
4.   → ModelInstance created with credentials + optional LBModelManager
5. ModelInstance.invoke_llm(prompt_messages, model_parameters, ...)
6.   → If load balancing: _round_robin_invoke() with retry
7.   → LargeLanguageModel.invoke()
8.   → PluginModelClient.invoke_llm() → HTTP POST to daemon
9.   → Stream LLMResultChunk or return LLMResult
```

### 5.5 Model Types Enum

**File**: `api/core/model_runtime/entities/model_entities.py`

```python
class ModelType(StrEnum):
    LLM = "llm"
    TEXT_EMBEDDING = "text-embedding"
    RERANK = "rerank"
    SPEECH2TEXT = "speech2text"
    TTS = "tts"
    MODERATION = "moderation"
```

### 5.6 Model Features

```python
class ModelFeature(StrEnum):
    TOOL_CALL = "tool-call"
    MULTI_TOOL_CALL = "multi-tool-call"
    AGENT_THOUGHT = "agent-thought"
    STREAM_TOOL_CALL = "stream-tool-call"
    VISION = "vision"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    STRUCTURED_OUTPUT = "structured-output"
```

### 5.7 Model Parameter Rules

```python
class ParameterRule(BaseModel):
    name: str                           # Parameter name
    label: I18nObject | None
    use_template: str | None            # Reference to default template
    type: ParameterType                 # FLOAT, INT, STRING, BOOLEAN, TEXT, STRING_LIST
    default: Any | None
    min: float | None
    max: float | None
    precision: int | None
    help: I18nObject | None
    required: bool = False
    options: list[str] = []

class DefaultParameterName(StrEnum):
    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    TOP_K = "top_k"
    PRESENCE_PENALTY = "presence_penalty"
    FREQUENCY_PENALTY = "frequency_penalty"
    MAX_TOKENS = "max_tokens"
    RESPONSE_FORMAT = "response_format"
    JSON_SCHEMA = "json_schema"
    SEED = "seed"
```

---

## 6. Load Balancing

### 6.1 Configuration

**DB Table**: `load_balancing_model_configs`

```python
class LoadBalancingModelConfig:
    id: str
    tenant_id: str
    provider_name: str
    model_name: str
    model_type: str
    name: str                       # Config entry name; "__inherit__" = use provider creds
    encrypted_config: str | None    # RSA-encrypted credentials JSON
    credential_id: str | None       # FK to ProviderCredential or ProviderModelCredential
    credential_source_type: str     # "provider" | "custom_model" | None
    enabled: bool
```

**DB Table**: `provider_model_settings` (toggle per model)

```python
class ProviderModelSetting:
    # ...
    load_balancing_enabled: bool    # Master toggle for model
```

### 6.2 Round-Robin Implementation

**File**: `api/core/model_manager.py` → `LBModelManager`

```python
class LBModelManager:
    def __init__(self, tenant_id, provider, model_type, model,
                 load_balancing_configs, managed_credentials):

    def fetch_next() -> ModelLoadBalancingConfiguration | None:
        # Round-robin via Redis atomic counter
        # Skips configs in cooldown
        # Checks credential policy compliance

    def cooldown(config, expire_seconds):
        # Redis SETEX: key=lb_cooldown:{tenant}:{provider}:{model_type}:{model}:{config_id}

    def in_cooldown(config) -> bool:
        # Redis key existence check

    @staticmethod
    def get_config_in_cooldown_and_ttl(tenant_id, provider, model_type, model, config_id):
        # Returns (bool, ttl_seconds)
```

### 6.3 Cooldown Policy

When invocation fails via `_round_robin_invoke()`:

| Error Type | Cooldown Duration |
|-----------|-------------------|
| `InvokeRateLimitError` | 60 seconds |
| `InvokeAuthorizationError` | 10 seconds |
| `InvokeConnectionError` | 10 seconds |

Fallback: After cooldown, all configs retry in round-robin. If all configs exhausted, raises last error.

### 6.4 Feature Gate

Load balancing availability is controlled by `modelLoadBalancingEnabled` in the frontend `ProviderContext`, which is a plan-gated feature.

---

## 7. Custom/Local Model Connections

### 7.1 Architecture

Custom models (Ollama, LM Studio, Xinference, LocalAI, OpenAI-compatible) use `ConfigurateMethod.CUSTOMIZABLE_MODEL`:

1. User specifies model name and endpoint URL in credential form
2. Provider plugin validates connectivity
3. Model is added to tenant's model list with per-model credentials

### 7.2 Supported Custom Providers (from _position.yaml)

| Provider | Position |
|----------|----------|
| `ollama` | 14 |
| `xinference` | 19 |
| `localai` | 33 |
| `openai_api_compatible` | 35 |
| `openllm` | 32 |
| `triton_inference_server` | 20 |

### 7.3 Provider Plugin Location

In Dify v1.11.4, provider plugins are **external** — deployed via the plugin daemon system. Example from docker volumes:

```
docker/volumes/plugin_daemon/cwd/langgenius/openai-0.2.8@{hash}/
├── models/
│   ├── llm/llm.py
│   ├── text_embedding/text_embedding.py
│   ├── tts/tts.py
│   ├── speech2text/speech2text.py
│   ├── moderation/moderation.py
│   └── common_openai.py
└── .venv/
    └── lib/python3.12/site-packages/dify_plugin/
```

### 7.4 Custom Model Credential Schema

For customizable models, the `ModelCredentialSchema` includes:
```python
class ModelCredentialSchema(BaseModel):
    model: FieldModelSchema          # model name input field
    credential_form_schemas: list[CredentialFormSchema]  # API key, URL, etc.
```

Typical fields for OpenAI-compatible providers:
- `api_key` (SECRET_INPUT)
- `api_base` (TEXT_INPUT) - the custom endpoint URL
- `model_name` (TEXT_INPUT) - actual model identifier

---

## 8. API Endpoints

### 8.1 Provider Management

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/workspaces/current/model-providers` | `ModelProviderListApi.get` | List all providers (optional `model_type` filter) |
| GET | `/workspaces/{tenant_id}/model-providers/{provider}/{icon_type}/{lang}` | `ModelProviderIconApi.get` | Get provider icon |
| POST | `/workspaces/current/model-providers/{provider}/preferred-provider-type` | `PreferredProviderTypeUpdateApi.post` | Switch system/custom preference |
| GET | `/workspaces/current/model-providers/{provider}/checkout-url` | `ModelProviderPaymentCheckoutUrlApi.get` | Get payment URL (Anthropic) |

### 8.2 Provider Credentials

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/workspaces/current/model-providers/{provider}/credentials` | `.get` | Get credentials (optional `credential_id`) |
| POST | `/workspaces/current/model-providers/{provider}/credentials` | `.post` | Create credential (`{credentials, name?}`) |
| PUT | `/workspaces/current/model-providers/{provider}/credentials` | `.put` | Update credential (`{credential_id, credentials, name?}`) |
| DELETE | `/workspaces/current/model-providers/{provider}/credentials` | `.delete` | Delete credential (`{credential_id}`) |
| POST | `/workspaces/current/model-providers/{provider}/credentials/switch` | `.post` | Switch active (`{credential_id}`) |
| POST | `/workspaces/current/model-providers/{provider}/credentials/validate` | `.post` | Validate (`{credentials}`) |

### 8.3 Model Management

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/workspaces/current/model-providers/{provider}/models` | `.get` | List provider's models |
| POST | `/workspaces/current/model-providers/{provider}/models` | `.post` | Add model with LB config |
| DELETE | `/workspaces/current/model-providers/{provider}/models` | `.delete` | Remove model |
| PATCH | `/workspaces/current/model-providers/{provider}/models/enable` | `.patch` | Enable model |
| PATCH | `/workspaces/current/model-providers/{provider}/models/disable` | `.patch` | Disable model |

### 8.4 Model Credentials

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/workspaces/current/model-providers/{provider}/models/credentials` | `.get` | Get model creds (query: `model`, `model_type`, `config_from?`, `credential_id?`) |
| POST | `/workspaces/current/model-providers/{provider}/models/credentials` | `.post` | Create model credential |
| PUT | `/workspaces/current/model-providers/{provider}/models/credentials` | `.put` | Update model credential |
| DELETE | `/workspaces/current/model-providers/{provider}/models/credentials` | `.delete` | Delete model credential |
| POST | `/workspaces/current/model-providers/{provider}/models/credentials/switch` | `.post` | Switch active model credential |
| POST | `/workspaces/current/model-providers/{provider}/models/credentials/validate` | `.post` | Validate model credentials |

### 8.5 Default Model & Parameter Rules

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/workspaces/current/default-model` | `DefaultModelApi.get` | Get default model (query: `model_type`) |
| POST | `/workspaces/current/default-model` | `DefaultModelApi.post` | Set default models (`{model_settings: [...]}`) |
| GET | `/workspaces/current/model-providers/{provider}/models/parameter-rules` | `.get` | Get parameter rules (query: `model`) |
| GET | `/workspaces/current/models/model-types/{model_type}` | `.get` | Get available models by type |

### 8.6 Load Balancing

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| POST | `/workspaces/current/model-providers/{provider}/models/load-balancing-configs/credentials-validate` | `.post` | Validate LB creds |
| POST | `/workspaces/current/model-providers/{provider}/models/load-balancing-configs/{config_id}/credentials-validate` | `.post` | Validate specific LB config creds |

---

## 9. Pricing & Quota System

### 9.1 Provider Quota Types

**File**: `api/core/entities/provider_entities.py`

```python
class ProviderQuotaType(StrEnum):
    PAID = "paid"       # Hosted paid quota
    FREE = "free"       # Third-party free quota
    TRIAL = "trial"     # Hosted trial quota

class QuotaUnit(StrEnum):
    TIMES = "times"
    TOKENS = "tokens"
    CREDITS = "credits"
```

### 9.2 Quota Configuration

```python
class QuotaConfiguration(BaseModel):
    quota_type: ProviderQuotaType
    quota_unit: QuotaUnit
    quota_limit: int
    quota_used: int
    is_valid: bool
    restrict_models: list[RestrictModel]    # Models available under this quota
```

### 9.3 System Configuration (Hosted Providers)

```python
class SystemConfiguration(BaseModel):
    enabled: bool
    current_quota_type: ProviderQuotaType | None
    quota_configurations: list[QuotaConfiguration]
    credentials: dict | None    # System-managed credentials
```

### 9.4 Per-Token Pricing

**File**: `api/core/model_runtime/entities/model_entities.py`

```python
class PriceConfig(BaseModel):
    input: Decimal          # Price per unit for input
    output: Decimal         # Price per unit for output
    unit: Decimal           # Token unit size (e.g., 1000)
    currency: str           # "USD", etc.

class PriceInfo(BaseModel):
    unit_price: Decimal
    unit: Decimal
    total_amount: Decimal
    currency: str
```

Price calculation in `AIModel.get_price()`:
```python
total_amount = tokens * unit_price * unit
```

### 9.5 LLM Usage Tracking

```python
class LLMUsage(ModelUsage):
    prompt_tokens: int
    prompt_unit_price: Decimal
    prompt_price_unit: Decimal
    prompt_price: Decimal
    completion_tokens: int
    completion_unit_price: Decimal
    completion_price_unit: Decimal
    completion_price: Decimal
    total_tokens: int
    total_price: Decimal
    currency: str
    latency: float
    time_to_first_token: float | None
    time_to_generate: float | None
```

### 9.6 Payment Integration

- Payment checkout URL available for Anthropic provider:
  `GET /workspaces/current/model-providers/{provider}/checkout-url`
- Calls `BillingService.get_model_provider_payment_link()`
- Payment orders tracked in `provider_orders` table

### 9.7 Provider Orders Table

```python
class ProviderOrder:
    tenant_id: str
    provider_name: str
    account_id: str
    payment_product_id: str
    payment_id: str | None
    transaction_id: str | None
    quantity: int
    currency: str
    total_amount: int
    payment_status: str    # "wait_pay" | "paid" | "failed" | "refunded"
    paid_at: datetime | None
```

---

## 10. Frontend UI Components

### 10.1 Component Tree

**Root**: `web/app/components/header/account-setting/model-provider-page/`

```
ModelProviderPage (index.tsx)
├── SystemModelSelector (system-model-selector/)
│   └── Per-type default model dropdowns
├── ProviderAddedCard (provider-added-card/)
│   ├── CredentialPanel
│   ├── ModelListItem
│   ├── ModelLoadBalancingConfigs
│   │   ├── CooldownTimer
│   │   ├── AddCredentialInLoadBalancing
│   │   └── SwitchCredentialInLoadBalancing
│   └── AddModelButton
├── ModelAuth (model-auth/)
│   ├── ConfigProvider (config-provider.tsx)
│   ├── ConfigModel (config-model.tsx)
│   ├── Authorized (authorized/)
│   │   ├── AuthorizedItem
│   │   └── CredentialItem
│   ├── AddCredentialInLoadBalancing
│   └── SwitchCredentialInLoadBalancing
├── ModelSelector (model-selector/)
│   ├── ModelTrigger
│   ├── EmptyTrigger
│   ├── DeprecatedModelTrigger
│   ├── Popup (with search + feature filtering)
│   └── PopupItem
├── ModelParameterModal (model-parameter-modal/)
│   ├── ModelDisplay
│   ├── ParameterItem
│   ├── PresetParameter
│   └── StatusIndicators
└── InstallFromMarketplace (install-from-marketplace.tsx)
```

### 10.2 Global State

**File**: `web/context/provider-context.tsx`

```typescript
type ProviderContextState = {
    modelProviders: ModelProvider[]
    refreshModelProviders: () => void
    textGenerationModelList: Model[]
    modelLoadBalancingEnabled: boolean      // Plan-gated feature
    plan: { type: Plan; usage: UsagePlanInfo; total: UsagePlanInfo }
    enableBilling: boolean
    isAPIKeySet: boolean
    // ... additional plan/license fields
}
```

### 10.3 Key React Hooks

**File**: `web/app/components/header/account-setting/model-provider-page/hooks.ts`

| Hook | Purpose |
|------|---------|
| `useDefaultModel(type)` | Fetch/mutate default model per type |
| `useModelList(type)` | Fetch models by type |
| `useCurrentProviderAndModel(modelList, defaultModel)` | Resolve current selection |
| `useModelListAndDefaultModel(type)` | Combined convenience hook |
| `useProviderCredentialsAndLoadBalancing(provider, ...)` | Fetch creds + LB configs |
| `useRefreshModel()` | Trigger model list refresh |
| `useAnthropicBuyQuota()` | Open Anthropic payment flow |
| `useMarketplaceAllPlugins(providers, searchText)` | Browse installable plugins |

### 10.4 API Service Hooks

**File**: `web/service/use-models.ts` (React Query based)

| Hook | HTTP | Path |
|------|------|------|
| `useModelProviderModelList(provider)` | GET | `/model-providers/{provider}/models` |
| `useGetProviderCredential(...)` | GET | `/model-providers/{provider}/credentials` |
| `useAddProviderCredential(provider)` | POST | `/model-providers/{provider}/credentials` |
| `useEditProviderCredential(provider)` | PUT | `/model-providers/{provider}/credentials` |
| `useDeleteProviderCredential(provider)` | DELETE | `/model-providers/{provider}/credentials` |
| `useActiveProviderCredential(provider)` | POST | `/model-providers/{provider}/credentials/switch` |
| `useGetModelCredential(...)` | GET | `/model-providers/{provider}/models/credentials` |
| `useAddModelCredential(provider)` | POST | `/model-providers/{provider}/models/credentials` |
| `useUpdateModelLoadBalancingConfig(provider)` | POST | `/model-providers/{provider}/models` |

### 10.5 TypeScript Declarations

**File**: `web/app/components/header/account-setting/model-provider-page/declarations.ts`

Key enums:
```typescript
enum ModelTypeEnum {
    textGeneration = 'llm'
    textEmbedding = 'text-embedding'
    rerank = 'rerank'
    speech2text = 'speech2text'
    moderation = 'moderation'
    tts = 'tts'
}

enum ConfigurationMethodEnum {
    predefinedModel = 'predefined-model'
    customizableModel = 'customizable-model'
    fetchFromRemote = 'fetch-from-remote'
}

enum ModelStatusEnum { active, noConfigure, quotaExceeded, noPermission, disabled, credentialRemoved }
enum PreferredProviderTypeEnum { system = 'system', custom = 'custom' }
enum CurrentSystemQuotaTypeEnum { trial = 'trial', free = 'free', paid = 'paid' }
```

### 10.6 Fixed Providers

```typescript
const FixedModelProvider = ['langgenius/openai/openai', 'langgenius/anthropic/anthropic']
```

These two providers always sort first in the UI.

---

## 11. Database Schema

### 11.1 Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `providers` | Provider instances per tenant | `tenant_id`, `provider_name`, `provider_type`, `credential_id`, `quota_type`, `quota_limit`, `quota_used` |
| `provider_credentials` | Named credential sets (RSA encrypted) | `tenant_id`, `provider_name`, `credential_name`, `encrypted_config` |
| `provider_models` | Custom/added models per tenant | `tenant_id`, `provider_name`, `model_name`, `model_type`, `credential_id` |
| `provider_model_credentials` | Named model-level credentials | `tenant_id`, `provider_name`, `model_name`, `model_type`, `credential_name`, `encrypted_config` |
| `provider_model_settings` | Model enable/disable + LB toggle | `tenant_id`, `provider_name`, `model_name`, `model_type`, `enabled`, `load_balancing_enabled` |
| `load_balancing_model_configs` | LB config entries per model | `tenant_id`, `provider_name`, `model_name`, `model_type`, `name`, `encrypted_config`, `credential_id`, `credential_source_type`, `enabled` |
| `tenant_default_models` | Default model per tenant per type | `tenant_id`, `provider_name`, `model_name`, `model_type` |
| `tenant_preferred_model_providers` | System vs custom preference | `tenant_id`, `provider_name`, `preferred_provider_type` |
| `provider_orders` | Payment order tracking | `tenant_id`, `provider_name`, `payment_status`, `total_amount`, `currency` |

### 11.2 Key Indexes

```sql
-- providers
CREATE UNIQUE INDEX unique_provider_name_type_quota
    ON providers (tenant_id, provider_name, provider_type, quota_type);

-- provider_models
CREATE UNIQUE INDEX unique_provider_model_name
    ON provider_models (tenant_id, provider_name, model_name, model_type);

-- provider_credentials
CREATE INDEX provider_credential_tenant_provider_idx
    ON provider_credentials (tenant_id, provider_name);

-- load_balancing_model_configs
CREATE INDEX load_balancing_model_config_tenant_provider_model_idx
    ON load_balancing_model_configs (tenant_id, provider_name, model_type);
```

### 11.3 Relationships

```
Provider ──1:1──→ ProviderCredential (via credential_id FK)
ProviderModel ──1:1──→ ProviderModelCredential (via credential_id FK)
LoadBalancingModelConfig ──1:1──→ ProviderCredential or ProviderModelCredential (via credential_id + credential_source_type)
```

---

## 12. Data Models & Entities

### 12.1 Error Hierarchy

**File**: `api/core/model_runtime/errors/invoke.py`

```python
InvokeError (ValueError)
├── InvokeConnectionError       # Network/connection failures
├── InvokeServerUnavailableError  # Server down
├── InvokeRateLimitError        # Rate limited (triggers 60s LB cooldown)
├── InvokeAuthorizationError    # Bad credentials (triggers 10s LB cooldown)
└── InvokeBadRequestError       # Bad request parameters
```

### 12.2 LLM Response Types

```python
# Non-streaming
class LLMResult(BaseModel):
    id: str | None
    model: str
    prompt_messages: list[PromptMessage]
    message: AssistantPromptMessage
    usage: LLMUsage
    system_fingerprint: str | None
    reasoning_content: str | None

# Streaming
class LLMResultChunk(BaseModel):
    model: str
    prompt_messages: list[PromptMessage]
    system_fingerprint: str | None
    delta: LLMResultChunkDelta

class LLMResultChunkDelta(BaseModel):
    index: int
    message: AssistantPromptMessage
    usage: LLMUsage | None
    finish_reason: str | None
```

### 12.3 Message Types

```python
class PromptMessageRole(StrEnum):
    SYSTEM, USER, ASSISTANT, TOOL

class PromptMessageContentType(StrEnum):
    TEXT, IMAGE, AUDIO, VIDEO, DOCUMENT

# Message classes
PromptMessage (base)
├── UserPromptMessage
├── SystemPromptMessage
├── AssistantPromptMessage (with tool_calls)
└── ToolPromptMessage (with tool_call_id)

# Content classes (for multimodal)
PromptMessageContent (base)
├── TextPromptMessageContent
├── ImagePromptMessageContent (with DETAIL: LOW/HIGH)
├── AudioPromptMessageContent
├── VideoPromptMessageContent
└── DocumentPromptMessageContent
```

### 12.4 Callback System

**File**: `api/core/model_runtime/callbacks/base_callback.py`

```python
class Callback(ABC):
    raise_error: bool

    @abstractmethod
    def on_before_invoke(llm_instance, model, credentials, prompt_messages, ...)
    def on_new_chunk(llm_instance, chunk, model, ...)
    def on_after_invoke(llm_instance, result, model, ...)
    def on_invoke_error(llm_instance, ex, model, ...)
```

---

## 13. Streaming Implementation

### 13.1 Transport Layer: Chunked HTTP with SSE-style Framing

**File**: `api/core/plugin/impl/base.py` → `_stream_request()`

The Dify core does NOT use true SSE (`text/event-stream`). Instead, it uses **chunked HTTP transfer** with SSE-like framing between core and plugin daemon:

1. `httpx.stream()` opens a chunked HTTP connection to the plugin daemon
2. `response.iter_lines()` yields raw lines
3. Lines prefixed with `data:` are stripped to extract the JSON payload
4. Each line is a complete JSON object representing one `PluginDaemonBasicResponse[T]`

For LLM invocations, `T = LLMResultChunk`, so each streamed line deserializes into a chunk with a delta message.

### 13.2 Stream Processing Pipeline

```
Plugin Daemon (provider-specific SDK)
  → Chunked HTTP response (line-delimited JSON, `data:` prefixed)
  → BasePluginClient._stream_request() strips framing, yields raw JSON strings
  → _request_with_plugin_daemon_response_stream() parses each line into PluginDaemonBasicResponse[T]
    - Checks response code (0 = success, -500 = error)
    - Maps plugin daemon errors to typed exceptions (InvokeRateLimitError, etc.)
    - Yields T (e.g., LLMResultChunk)
  → PluginModelClient.invoke_llm() yields LLMResultChunk via `yield from`
  → LargeLanguageModel.invoke() wraps in _invoke_result_generator()
    - Fires on_new_chunk callbacks per chunk
    - Accumulates message content for final on_after_invoke callback
    - Re-attaches prompt_messages to each chunk (stripped by daemon for bandwidth)
  → ModelInstance._round_robin_invoke() passes through (or retries on error)
  → Application layer (workflow node / chatbot) consumes Generator[LLMResultChunk]
```

### 13.3 Non-Streaming Reconstitution

When `stream=False`, the plugin daemon still returns a stream. `LargeLanguageModel.invoke()` consumes the first chunk and reconstitutes it into an `LLMResult`:
- Concatenates string content or extends content list
- Merges incremental tool calls via `_increase_tool_call()`
- Takes usage from the chunk
- Returns a single `LLMResult` instead of a generator

### 13.4 Tool Call Streaming

**File**: `api/core/model_runtime/model_providers/__base/large_language_model.py`

Tool calls arrive incrementally across chunks. `_increase_tool_call()` merges them:
- New tool calls with a function name but no ID get a generated ID (`chatcmpl-tool-{uuid}`)
- Arguments are concatenated across chunks (streaming JSON fragments)
- Tool calls are matched by ID; new IDs create new entries; empty IDs append to the last tool call

### 13.5 Binary Streaming (TTS)

TTS responses stream hex-encoded audio bytes. Each chunk contains a hex string that is decoded via `binascii.unhexlify()` and yielded as raw bytes.

### 13.6 Frontend SSE

The frontend receives SSE from the Dify API layer (Flask), not directly from the plugin daemon. The Flask application layer converts the `Generator[LLMResultChunk]` into SSE events for the browser.

---

## 14. Request/Response Normalization

### 14.1 Unified Message Format

All providers receive and return the same normalized types regardless of their native API format:

**Input normalization** (caller → plugin daemon → provider SDK):
- `PromptMessage` hierarchy: `SystemPromptMessage`, `UserPromptMessage`, `AssistantPromptMessage`, `ToolPromptMessage`
- Multimodal content via `PromptMessageContent` subclasses (text, image, audio, video, document)
- Tool definitions via `PromptMessageTool` with JSON Schema function parameters
- All serialized via `jsonable_encoder()` before HTTP POST to daemon

**Output normalization** (provider SDK → plugin daemon → core):
- All LLM responses normalized to `LLMResultChunk` (streaming) or reconstituted `LLMResult`
- All embedding responses normalized to `EmbeddingResult`
- All rerank responses normalized to `RerankResult`
- Usage always in `LLMUsage` format with prompt/completion token counts and pricing

### 14.2 Error Normalization

**File**: `api/core/model_runtime/model_providers/__base/ai_model.py` → `_transform_invoke_error()`

Provider-specific errors are mapped to 5 unified error types via `_invoke_error_mapping`:
- `InvokeConnectionError` — network failures
- `InvokeServerUnavailableError` — provider server down
- `InvokeRateLimitError` — rate limited (triggers LB cooldown)
- `InvokeAuthorizationError` — bad credentials (triggers LB cooldown)
- `InvokeBadRequestError` — invalid parameters

The plugin daemon performs its own error normalization: when a plugin raises an error, the daemon wraps it in a `PluginDaemonError` with an `error_type` field. `BasePluginClient._handle_plugin_daemon_error()` then pattern-matches on `error_type` to re-raise the correct typed exception in the core.

### 14.3 Libraries Used

- **httpx**: HTTP client for all plugin daemon communication (both sync and streaming)
- **pydantic v2**: All entities use `BaseModel` with `model_validate()` / `model_validate_json()`
- **No LiteLLM**: Zero references in codebase. Each provider plugin uses provider-specific SDKs (openai, anthropic, etc.) directly.
- **yarl**: URL construction for plugin daemon endpoints
- **rsa**: Credential encryption/decryption
- **redis**: Load balancing counter and cooldown state
- **contextvars**: Thread-safe provider cache per tenant

### 14.4 Extension Points

1. **New model provider**: Install a plugin via the plugin daemon. Plugin implements provider-specific API calls and maps to/from Dify's normalized message types.
2. **New model type**: Add to `ModelType` enum, create base class extending `AIModel`, add dispatch endpoint in `PluginModelClient`, add plugin daemon route.
3. **Callbacks**: Implement `Callback` abstract class for custom logging, metrics, etc. Attached per-invocation.
4. **Custom credential forms**: Define `CredentialFormSchema` in plugin manifest. UI renders dynamically. `show_on` enables conditional fields.
5. **Load balancing policies**: Currently only round-robin with cooldown. Extension would require modifying `LBModelManager.fetch_next()`.

---

## Summary: Key Requirements to Recreate This System

1. **Plugin Daemon Architecture**: External process hosting model provider plugins, communicated via HTTP REST. Each plugin implements provider-specific API calls.

2. **Multi-Tenant Credential Management**: RSA-encrypted per-tenant credentials with multi-credential support (named credentials, active selection, provider-level and model-level).

3. **Two Configuration Methods**: `PREDEFINED_MODEL` (fixed model list from plugin) and `CUSTOMIZABLE_MODEL` (user-specified model names for Ollama/OpenAI-compatible).

4. **Round-Robin Load Balancing**: Redis-backed counter with cooldown policy (60s rate limit, 10s auth/connection errors). Feature-gated by plan.

5. **Provider Identity System**: Three-part ID (`org/plugin/provider`) with shorthand alias support.

6. **Dynamic Credential Forms**: Schema-driven UI forms with conditional visibility (`show_on`), type validation, and i18n labels.

7. **9 Database Tables**: providers, provider_credentials, provider_models, provider_model_credentials, provider_model_settings, load_balancing_model_configs, tenant_default_models, tenant_preferred_model_providers, provider_orders.

8. **20+ REST API Endpoints**: Full CRUD for provider/model credentials, validation, enable/disable, default model selection, load balancing configuration, and payment checkout.

9. **6 Model Type Abstractions**: LLM, TextEmbedding, Rerank, TTS, Speech2Text, Moderation — each with its own base class and plugin daemon dispatch endpoint.

10. **Quota/Billing System**: Three quota types (paid/free/trial) with per-unit tracking (times/tokens/credits), payment order management, and provider-specific checkout URLs.

11. **Streaming via Chunked HTTP**: Plugin daemon returns line-delimited JSON with `data:` prefix. Core streams `LLMResultChunk` generators through callbacks. Non-streaming reconstitutes from first chunk. Tool calls merged incrementally across chunks.

12. **Unified Error Normalization**: Two-layer error mapping — plugin daemon maps provider errors to typed `PluginInvokeError`, core re-raises as `InvokeRateLimitError` / `InvokeAuthorizationError` / etc. These drive load balancing cooldown decisions.

13. **No LiteLLM — Custom Plugin Architecture**: Each provider is an independent plugin with its own Python virtualenv, using provider-specific SDKs (openai, anthropic, etc.) directly. Normalization happens at plugin boundaries via Dify's message/response entity types.
