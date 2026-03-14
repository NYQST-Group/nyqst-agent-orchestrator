# Dify Database Schema — Clean-Room ERD Requirements

> Comprehensive entity-relationship analysis of Dify's SQLAlchemy models.
> Sufficient for independent schema design. Source: upstream Dify codebase.

---

## 1. Overview

**Database:** PostgreSQL (via SQLAlchemy + Alembic, ~155 migrations)
**ID Strategy:** UUID v4 (most tables), UUID v7 (newer tables like providers, pipelines)
**Base Classes:**
- `Base` — plain SQLAlchemy declarative base (uses `__init__` with positional kwargs)
- `TypeBase` — dataclass-style base with `MappedAsDataclass` (uses `init=False` on auto-generated fields)
- `DefaultFieldsMixin` — adds `id` (UUID PK) and `created_at` (server timestamp)

**Common Column Patterns:**
- `id`: StringUUID, PK, client-generated UUID
- `tenant_id`: StringUUID, NOT NULL — multi-tenancy FK (see Section 3)
- `created_at`: DateTime, server_default=CURRENT_TIMESTAMP
- `updated_at`: DateTime, server_default=CURRENT_TIMESTAMP, onupdate=CURRENT_TIMESTAMP
- `created_by` / `updated_by`: StringUUID — polymorphic FK to Account or EndUser
- `created_by_role`: String — discriminator: 'account' | 'end_user'

**Custom Column Types:**
- `StringUUID`: UUID stored as string
- `LongText`: Text (unbounded)
- `BinaryData`: LargeBinary
- `AdjustedJSON`: JSON with index support (JSONB on PostgreSQL)
- `EnumText`: String-backed enum storage

---

## 2. Domain: Authentication & Tenancy

### accounts
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | String(255) | |
| email | String(255) | Indexed |
| password | String(255) | Nullable, salted |
| password_salt | String(255) | Nullable |
| avatar | String(255) | |
| interface_language | String(255) | |
| interface_theme | String(255) | |
| timezone | String(255) | |
| last_login_at | DateTime | |
| last_login_ip | String(255) | |
| last_active_at | DateTime | NOT NULL |
| status | String(16) | 'pending','uninitialized','active','banned','closed' |
| initialized_at | DateTime | |
| created_at, updated_at | DateTime | Standard |

**Business:** User account. Not tenant-scoped — accounts exist globally and join tenants via `tenant_account_joins`.

### tenants
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | String(255) | Workspace name |
| encrypt_public_key | LongText | RSA public key for credential encryption |
| plan | String(255) | 'basic' default |
| status | String(255) | 'normal','archive' |
| custom_config | LongText | JSON — tenant-level feature flags |
| created_at, updated_at | DateTime | |

**Business:** Workspace / organization. All business entities are scoped to a tenant.

### tenant_account_joins
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID FK→tenants | Indexed |
| account_id | UUID FK→accounts | Indexed |
| current | Boolean | Which workspace the account is "in" |
| role | String(16) | 'owner','admin','editor','normal','dataset_operator' |
| invited_by | UUID | Nullable |
| created_at, updated_at | DateTime | |

**Constraints:** UNIQUE(tenant_id, account_id)
**Cardinality:** Many-to-many join table (Account ↔ Tenant). One account can belong to many tenants; one tenant has many accounts.

### account_integrates
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| account_id | UUID | |
| provider | String(16) | OAuth provider name |
| open_id | String(255) | Provider's user ID |
| encrypted_token | String(255) | |
| created_at, updated_at | DateTime | |

**Constraints:** UNIQUE(account_id, provider), UNIQUE(provider, open_id)
**Business:** SSO/OAuth integration per account.

### invitation_codes
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| batch | String(255) | Indexed |
| code | String(32) | Indexed with status |
| status | String(16) | 'unused' default |
| used_at | DateTime | |
| used_by_tenant_id, used_by_account_id | UUID | |
| created_at | DateTime | |

### account_plugin_permissions (TenantPluginPermission)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | UNIQUE |
| install_permission | String(16) | 'everyone','admins','noone' |
| debug_permission | String(16) | 'everyone','admins','noone' |

**Cardinality:** One-to-one with Tenant.

---

## 3. Multi-Tenancy Pattern

**Enforcement:** Application-level. Nearly every business table has a `tenant_id` column. There are no database-level row-level security policies. Queries filter by `tenant_id` in the WHERE clause. No foreign key constraints reference `tenants.id` in the schema definitions (all are implicit application-level references).

**Cross-tenant entities:** `accounts` (global), `invitation_codes` (global), `recommended_apps` (marketplace), `dify_setups` (system singleton), `celery_taskmeta` (task queue).

---

## 4. Domain: Apps & Configuration

### apps
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | Indexed |
| name | String(255) | |
| description | LongText | |
| mode | String(255) | 'completion','workflow','chat','advanced-chat','agent-chat','channel','rag-pipeline' |
| icon_type | String(255) | 'image','emoji','link' |
| icon | String(255) | |
| icon_background | String(255) | |
| app_model_config_id | UUID | FK→app_model_configs (current config) |
| workflow_id | UUID | FK→workflows (published workflow) |
| status | String(255) | 'normal' default |
| enable_site | Boolean | WebApp enabled |
| enable_api | Boolean | API access enabled |
| api_rpm, api_rph | Integer | Rate limits |
| is_demo, is_public, is_universal | Boolean | |
| tracing | LongText | JSON tracing config |
| max_active_requests | Integer | Nullable |
| use_icon_as_answer_icon | Boolean | |
| created_by, updated_by | UUID | |
| created_at, updated_at | DateTime | |

**Relationships:**
- App → Tenant (many-to-one via tenant_id)
- App → AppModelConfig (many-to-one, optional — for simple mode apps)
- App → Workflow (many-to-one, optional — for workflow/advanced-chat mode apps)
- App → Site (one-to-one)
- App → Tag (many-to-many via tag_bindings)
- App → Conversation (one-to-many)
- App → InstalledApp (one-to-many)
- App → Dataset (many-to-many via app_dataset_joins)

### app_model_configs
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | Indexed |
| provider | String(255) | LLM provider |
| model_id | String(255) | Model name |
| configs | JSON | |
| opening_statement | LongText | |
| suggested_questions | LongText | JSON array |
| suggested_questions_after_answer | LongText | JSON {enabled:bool} |
| speech_to_text | LongText | JSON {enabled:bool} |
| text_to_speech | LongText | JSON {enabled:bool} |
| more_like_this | LongText | JSON {enabled:bool} |
| model | LongText | JSON — model params (temperature etc.) |
| user_input_form | LongText | JSON array of form fields |
| dataset_query_variable | String(255) | |
| pre_prompt | LongText | System prompt |
| agent_mode | LongText | JSON {enabled,strategy,tools[],prompt} |
| sensitive_word_avoidance | LongText | JSON |
| retriever_resource | LongText | JSON {enabled:bool} |
| prompt_type | String(255) | 'simple','advanced' |
| chat_prompt_config | LongText | JSON |
| completion_prompt_config | LongText | JSON |
| dataset_configs | LongText | JSON {retrieval_model:'single'|'multiple'} |
| file_upload | LongText | JSON |
| external_data_tools | LongText | JSON array |
| created_by, updated_by | UUID | |
| created_at, updated_at | DateTime | |

**Business:** Snapshot of app configuration. App points to "current" config; conversations snapshot the config at creation time.

### sites
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | Indexed |
| title | String(255) | |
| icon_type, icon, icon_background | String(255) | |
| description | LongText | |
| default_language | String(255) | |
| chat_color_theme | String(255) | |
| copyright, privacy_policy | String(255) | |
| show_workflow_steps | Boolean | |
| custom_disclaimer | LongText | Max 512 chars (app-enforced) |
| customize_domain | String(255) | |
| customize_token_strategy | String(255) | |
| prompt_public | Boolean | |
| status | String(255) | 'normal' |
| code | String(255) | Indexed with status — short URL code |
| created_by, updated_by | UUID | |
| created_at, updated_at | DateTime | |

**Cardinality:** One-to-one with App.

### api_tokens
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | Nullable — app-scoped tokens |
| tenant_id | UUID | Nullable — dataset-scoped tokens |
| type | String(16) | 'app','dataset' |
| token | String(255) | Indexed with type |
| last_used_at | DateTime | |
| created_at | DateTime | |

### app_mcp_servers
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | |
| app_id | UUID | UNIQUE(tenant_id, app_id) |
| name | String(255) | |
| description | String(255) | |
| server_code | String(255) | UNIQUE — random alphanumeric |
| status | String(255) | 'normal' |
| parameters | LongText | JSON |
| created_at, updated_at | DateTime | |

### installed_apps
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | |
| app_id | UUID | UNIQUE(tenant_id, app_id) |
| app_owner_tenant_id | UUID | Cross-tenant reference |
| position | Integer | |
| is_pinned | Boolean | |
| last_used_at | DateTime | |
| created_at | DateTime | |

### recommended_apps
Marketplace listing. Global (no tenant_id). References app_id.

### tags / tag_bindings
Polymorphic tagging system. `tags.type` = 'app' | 'knowledge'. `tag_bindings.target_id` = app.id or dataset.id.
**Cardinality:** Many-to-many (Tag ↔ App, Tag ↔ Dataset via TagBinding).

### trace_app_config
Per-app tracing/observability config (LangSmith, LangFuse, etc.). One-to-one with App.

---

## 5. Domain: Conversations & Messages

### conversations
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | Indexed with from_source, from_end_user_id |
| app_model_config_id | UUID | Snapshot reference |
| model_provider | String(255) | |
| override_model_configs | LongText | JSON — debug overrides |
| model_id | String(255) | |
| mode | String(255) | AppMode value |
| name | String(255) | Auto-generated or user-set |
| summary | LongText | |
| inputs | JSON | Conversation-level inputs |
| introduction | LongText | |
| system_instruction | LongText | |
| system_instruction_tokens | Integer | |
| status | String(255) | 'normal' |
| invoke_from | String(255) | 'service-api','web-app','explore','debugger' |
| from_source | String(255) | 'console','api','web_app' |
| from_end_user_id | UUID | Nullable |
| from_account_id | UUID | Nullable |
| read_at | DateTime | |
| read_account_id | UUID | |
| dialogue_count | Integer | |
| is_deleted | Boolean | **Soft delete** |
| created_at, updated_at | DateTime | |

**Relationships:**
- Conversation → App (many-to-one)
- Conversation → Message (one-to-many, backref via SQLAlchemy relationship)
- Conversation → MessageAnnotation (one-to-many, backref)

**Soft Delete:** `is_deleted` boolean flag. Queries must filter `is_deleted=false`.

### messages
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | Indexed with created_at |
| model_provider | String(255) | |
| model_id | String(255) | |
| override_model_configs | LongText | |
| conversation_id | UUID | FK→conversations, Indexed |
| inputs | JSON | Per-message inputs |
| query | LongText | User question |
| message | JSON | Prompt messages sent to LLM |
| message_tokens | Integer | |
| message_unit_price | Numeric(10,4) | |
| message_price_unit | Numeric(10,7) | |
| answer | LongText | LLM response |
| answer_tokens | Integer | |
| answer_unit_price | Numeric(10,4) | |
| answer_price_unit | Numeric(10,7) | |
| parent_message_id | UUID | Tree structure for branching |
| provider_response_latency | Float | |
| total_price | Numeric(10,7) | |
| currency | String(255) | |
| status | String(255) | 'normal','error' |
| error | LongText | |
| message_metadata | LongText | JSON — retriever_resources, etc. |
| invoke_from | String(255) | |
| from_source | String(255) | |
| from_end_user_id | UUID | |
| from_account_id | UUID | |
| agent_based | Boolean | |
| workflow_run_id | UUID | Links to WorkflowRun for advanced-chat |
| app_mode | String(255) | Denormalized for query perf |
| created_at, updated_at | DateTime | |

**Indexes:** 8 indexes covering app+time, conversation, end_user, account, workflow_run, created_at, app_mode.

### message_feedbacks
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | |
| conversation_id | UUID | |
| message_id | UUID | Indexed with from_source |
| rating | String(255) | 'like','dislike' |
| from_source | String(255) | 'user','admin' |
| content | LongText | Optional text feedback |
| from_end_user_id, from_account_id | UUID | |
| created_at, updated_at | DateTime | |

### message_files
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| message_id | UUID | Indexed |
| type | String(255) | File type category |
| transfer_method | String(255) | 'local_file','remote_url','tool_file' |
| created_by_role | String(255) | |
| created_by | UUID | |
| belongs_to | String(255) | 'user','assistant' |
| url | LongText | For remote URLs |
| upload_file_id | UUID | FK→upload_files |
| created_at | DateTime | |

### message_annotations
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | |
| conversation_id | UUID | FK→conversations |
| message_id | UUID | |
| question | LongText | |
| content | LongText | Annotated answer |
| hit_count | Integer | |
| account_id | UUID | Who annotated |
| created_at, updated_at | DateTime | |

### message_agent_thoughts
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| message_id | UUID | Indexed |
| position | Integer | Order in chain |
| message_chain_id | UUID | |
| thought | LongText | Chain-of-thought text |
| tool | LongText | Semicolon-separated tool names |
| tool_labels_str | LongText | JSON |
| tool_meta_str | LongText | JSON |
| tool_input | LongText | JSON |
| observation | LongText | Tool output |
| message | LongText | |
| answer | LongText | |
| tokens, message_token, answer_token | Integer | |
| total_price, currency | Numeric, String | |
| latency | Float | |
| message_files | LongText | JSON |
| created_by_role, created_by | String, UUID | |
| created_at | DateTime | |

**Business:** ReAct agent thought chain. Ordered by position within a message.

### message_chains
Links messages in a chain (type + input/output).

### dataset_retriever_resources
Per-message RAG retrieval results. Indexed by message_id.

### end_users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | |
| app_id | UUID | |
| type | String(255) | 'service_api','web_app' |
| external_user_id | String(255) | |
| name | String(255) | |
| is_anonymous | Boolean | |
| session_id | String(255) | Indexed with type |
| created_at, updated_at | DateTime | |

**Business:** Anonymous or identified API/web users. Referenced polymorphically by `from_end_user_id` + `created_by_role='end_user'`.

### saved_messages / pinned_conversations
Web app user preferences. Scoped by app_id + created_by.

---

## 6. Domain: Datasets (Knowledge Base / RAG)

### datasets
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | Indexed |
| name | String(255) | |
| description | LongText | |
| provider | String(255) | 'vendor','external' |
| permission | String(255) | 'only_me','all_team_members','partial_members' |
| data_source_type | String(255) | |
| indexing_technique | String(255) | 'high_quality','economy',null |
| index_struct | LongText | JSON |
| embedding_model | String(255) | |
| embedding_model_provider | String(255) | |
| keyword_number | Integer | Default 10 |
| collection_binding_id | UUID | FK→dataset_collection_bindings |
| retrieval_model | AdjustedJSON | JSON — search_method, reranking_enable, top_k, etc. |
| built_in_field_enabled | Boolean | |
| icon_info | AdjustedJSON | |
| runtime_mode | String(255) | 'general' |
| pipeline_id | UUID | FK→pipelines |
| chunk_structure | String(255) | |
| enable_api | Boolean | |
| is_multimodal | Boolean | |
| created_by, updated_by | UUID | |
| created_at, updated_at | DateTime | |

**Relationships:**
- Dataset → Document (one-to-many)
- Dataset → App (many-to-many via app_dataset_joins)
- Dataset → Tag (many-to-many via tag_bindings)
- Dataset → DatasetKeywordTable (one-to-one)
- Dataset → Pipeline (many-to-one, optional)

### documents
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | Indexed |
| dataset_id | UUID | Indexed |
| position | Integer | Order in dataset |
| data_source_type | String(255) | 'upload_file','notion_import','website_crawl' |
| data_source_info | LongText | JSON — upload_file_id, notion details, etc. |
| dataset_process_rule_id | UUID | |
| batch | String(255) | Import batch identifier |
| name | String(255) | |
| created_from | String(255) | 'web','api' |
| created_by | UUID | |
| created_api_request_id | UUID | |
| file_id | LongText | |
| word_count | Integer | |
| tokens | Integer | |
| indexing_latency | Float | |
| indexing_status | String(255) | 'waiting','parsing','cleaning','splitting','indexing','completed','error' |
| enabled | Boolean | |
| archived | Boolean | **Soft archive** |
| archived_reason, archived_by, archived_at | String, UUID, DateTime | |
| disabled_at, disabled_by | DateTime, UUID | |
| is_paused | Boolean | Pause during indexing |
| paused_by, paused_at | UUID, DateTime | |
| error | LongText | |
| doc_type | String(40) | |
| doc_metadata | AdjustedJSON | Custom metadata key-value |
| doc_form | String(255) | 'text_model','qa_model','hierarchical_model' |
| doc_language | String(255) | |
| processing timestamps | DateTime | parsing/cleaning/splitting/completed_at, stopped_at |
| created_at, updated_at | DateTime | |

**Soft Delete:** Uses `archived` boolean + `enabled` boolean (two separate flags). No hard deletes.

### document_segments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | Indexed |
| dataset_id | UUID | Indexed |
| document_id | UUID | Indexed |
| position | Integer | |
| content | LongText | Chunk text |
| answer | LongText | For QA-mode chunks |
| word_count, tokens | Integer | |
| keywords | JSON | Extracted keywords array |
| index_node_id | String(255) | Vector store node ID |
| index_node_hash | String(255) | Content hash |
| hit_count | Integer | |
| enabled | Boolean | |
| status | String(255) | 'waiting','indexing','completed','error' |
| disabled_at, disabled_by | DateTime, UUID | |
| error | LongText | |
| created_by, updated_by | UUID | |
| created_at, updated_at, indexing_at, completed_at, stopped_at | DateTime | |

**Indexes:** 6 indexes — dataset, document, tenant+dataset, tenant+document, node+dataset, tenant.

### child_chunks
Sub-chunks of segments for hierarchical chunking. Same structure as segments but with `segment_id` FK.

### app_dataset_joins
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| app_id | UUID | |
| dataset_id | UUID | Indexed together |
| created_at | DateTime | |

**Cardinality:** Many-to-many (App ↔ Dataset).

### dataset_process_rules
Per-dataset processing configuration. mode='automatic'|'custom'|'hierarchical', rules=JSON.

### dataset_keyword_tables
One-to-one with Dataset. Stores keyword→segment_id mapping for BM25 search. Can be stored in DB or file storage.

### embeddings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| model_name | String(255) | |
| provider_name | String(255) | |
| hash | String(64) | UNIQUE(model_name, hash, provider_name) |
| embedding | BinaryData | Pickled float array |
| created_at | DateTime | |

**Business:** Deduplication cache for embedding vectors.

### dataset_collection_bindings
Maps embedding model to vector collection name. Referenced by datasets and annotation settings.

### dataset_permissions
Per-account access control for datasets with 'partial_members' permission.

### dataset_queries
Query log for datasets. Tracks who queried what.

### dataset_metadata / dataset_metadata_bindings
Custom metadata fields defined per dataset, bound to documents.

### segment_attachment_bindings
Links document segments to uploaded attachment files (multimodal segments).

### external_knowledge_apis / external_knowledge_bindings
External knowledge base API integration.

### dataset_auto_disable_logs / rate_limit_logs
Operational logging tables.

---

## 7. Domain: Workflows

### workflows
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | |
| app_id | UUID | |
| type | String(255) | 'workflow','chat','rag-pipeline' |
| version | String(255) | 'draft' or timestamp string |
| marked_name | String(255) | User-assigned version label |
| marked_comment | String(255) | |
| graph | LongText | JSON — {nodes:[], edges:[]} |
| features | LongText | JSON — file_upload, speech, etc. |
| environment_variables | LongText | JSON — encrypted secrets |
| conversation_variables | LongText | JSON — persistent chat vars |
| rag_pipeline_variables | LongText | JSON |
| created_by, updated_by | UUID | |
| created_at, updated_at | DateTime | |

**Index:** (tenant_id, app_id, version)
**Business:** Each app has one 'draft' version and zero or more published versions (timestamp-based).

### workflow_runs
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id | UUID | |
| app_id | UUID | |
| workflow_id | UUID | |
| type | String(255) | WorkflowType |
| triggered_from | String(255) | 'debugging','app-run' |
| version | String(255) | |
| graph | LongText | Snapshot of workflow graph |
| inputs | LongText | JSON |
| status | String(255) | 'running','succeeded','failed','stopped','partial-succeeded' |
| outputs | LongText | JSON |
| error | LongText | |
| elapsed_time | Float | |
| total_tokens | BigInteger | |
| total_steps | Integer | |
| created_by_role | String(255) | 'account','end_user' |
| created_by | UUID | |
| created_at | DateTime | |
| finished_at | DateTime | |
| exceptions_count | Integer | |

**Relationships:**
- WorkflowRun → WorkflowPause (one-to-one, optional)
- WorkflowRun → WorkflowNodeExecution (one-to-many)

### workflow_node_executions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| tenant_id, app_id, workflow_id | UUID | |
| triggered_from | String(255) | 'single-step','workflow-run','rag-pipeline-run' |
| workflow_run_id | UUID | Nullable for single-step |
| index | Integer | Execution order |
| predecessor_node_id | String(255) | |
| node_execution_id | String(255) | |
| node_id | String(255) | |
| node_type | String(255) | 'start','llm','tool','code','if-else','iteration', etc. |
| title | String(255) | |
| inputs, process_data, outputs | LongText | JSON — may be offloaded |
| status | String(255) | 'running','succeeded','failed' |
| error | LongText | |
| elapsed_time | Float | |
| execution_metadata | LongText | JSON — {total_tokens, total_price, currency, tool_info} |
| created_by_role, created_by | String, UUID | |
| created_at, finished_at | DateTime | |

**Offloading:** Large inputs/outputs are offloaded to file storage via `workflow_node_execution_offload` table.

### workflow_node_execution_offload
Links node executions to UploadFile records for offloaded large payloads. Type: 'inputs'|'outputs'|'process_data'.

### workflow_app_logs
Execution log for published apps (excludes debugging). References workflow_run_id.

### workflow_conversation_variables
Persistent conversation-scoped variables. PK: (id, conversation_id).

### workflow_draft_variables / workflow_draft_variable_files
Debug-time variable inspection. Supports offloading large values to file storage.

### workflow_pauses / workflow_pause_reasons
Pause state for human-in-the-loop workflows. Stores serialized `GraphEngine` state via `state_object_key`. Pause reasons: 'human_input_required', 'scheduling'.

---

## 8. Domain: Providers & Models

### providers
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK (v7) | |
| tenant_id | UUID | |
| provider_name | String(255) | e.g., 'openai','anthropic' |
| provider_type | String(40) | 'custom','system' |
| is_valid | Boolean | |
| credential_id | UUID | FK→provider_credentials |
| quota_type | String(40) | 'paid','free','trial' |
| quota_limit, quota_used | BigInteger | |
| last_used | DateTime | |
| created_at, updated_at | DateTime | |

**Constraint:** UNIQUE(tenant_id, provider_name, provider_type, quota_type)

### provider_credentials
Named credential instances per provider per tenant. Stores encrypted_config (LongText JSON).

### provider_models
Per-model configuration. UNIQUE(tenant_id, provider_name, model_name, model_type).

### provider_model_credentials
Named credential instances per model per tenant.

### tenant_default_models
Default model selection per tenant per model_type.

### tenant_preferred_model_providers
Preferred provider type (custom vs system) per tenant.

### provider_model_settings
Model enable/disable and load balancing toggle.

### load_balancing_model_configs
Load balancing configuration per model.

### provider_orders
Payment/purchase records for hosted model quotas.

---

## 9. Domain: Tools

### tool_builtin_providers (BuiltinToolProvider)
Stores credentials for built-in tool providers per tenant. Supports multiple named credential instances.
UNIQUE(tenant_id, provider, name).

### tool_api_providers (ApiToolProvider)
Custom OpenAPI-based tool providers. Stores schema, tools (JSON), credentials (JSON).
UNIQUE(name, tenant_id).

### tool_workflow_providers (WorkflowToolProvider)
Published workflows exposed as tools. References app_id.
UNIQUE(name, tenant_id), UNIQUE(tenant_id, app_id).

### tool_mcp_providers (MCPToolProvider)
MCP (Model Context Protocol) tool providers.
UNIQUE(tenant_id, server_url_hash), UNIQUE(tenant_id, name), UNIQUE(tenant_id, server_identifier).

### tool_label_bindings
Labels for tools. UNIQUE(tool_id, label_name).

### tool_oauth_system_clients / tool_oauth_tenant_clients
OAuth credentials for tool providers at system and tenant level.

---

## 10. Domain: Triggers

### trigger_subscriptions
Plugin trigger subscription instances. Stores credentials, parameters, properties (JSON). Indexed by endpoint_id.

### workflow_webhook_triggers
Maps webhook endpoints to workflow nodes. UNIQUE(app_id, node_id), UNIQUE(webhook_id).

### workflow_plugin_triggers
Maps plugin trigger events to workflow nodes.

### app_triggers
Per-app trigger registry with enable/disable status. Types: 'webhook','schedule','plugin'.

### workflow_schedule_plans
Cron-based scheduling. Stores cron_expression, timezone, next_run_at.

### workflow_trigger_logs
Execution log for triggered workflows. Tracks status, retry_count, celery_task_id.

### trigger_oauth_system_clients / trigger_oauth_tenant_clients
OAuth for trigger providers (parallel to tool OAuth tables).

---

## 11. Domain: Data Sources

### data_source_oauth_bindings
OAuth tokens for data sources (Notion, etc.). Per tenant.

### data_source_api_key_auth_bindings
API key credentials for data sources. Per tenant.

### datasource_providers
Plugin-based data source credentials.

### datasource_oauth_params / datasource_oauth_tenant_params
System-level and tenant-level OAuth configuration for datasource plugins.

---

## 12. Domain: Files & Storage

### upload_files
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | Client-generated |
| tenant_id | UUID | Indexed |
| storage_type | String(255) | Storage backend |
| key | String(255) | Object storage key |
| name | String(255) | Original filename |
| size | Integer | Bytes |
| extension | String(255) | |
| mime_type | String(255) | |
| created_by_role | String(255) | 'account','end_user' |
| created_by | UUID | |
| used | Boolean | Indicates if consumed |
| used_by | UUID | |
| used_at | DateTime | |
| hash | String(255) | Content hash |
| source_url | LongText | |
| created_at | DateTime | |

**Business:** Central file registry. Referenced by message_files, workflow offload, document data_source_info, segment attachments.

---

## 13. Domain: System & Operations

### dify_setups
Single-row table tracking installed version. PK: version string.

### celery_taskmeta / celery_tasksetmeta
Celery task result storage (standard Celery schema).

### api_requests
API request logging per tenant per token.

### api_based_extensions
Custom webhook-based extensions per tenant.

### operation_logs
Audit trail: tenant_id + account_id + action + content (JSON) + IP.

### whitelists
Feature flag whitelist per tenant.

### tenant_credit_pools
Credit quota tracking. pool_type='trial'. Tracks quota_limit, quota_used.

### oauth_provider_apps (OAuthProviderApp)
Dify Cloud only. Global OAuth app registrations for SSO.

---

## 14. Soft Delete Patterns

1. **Conversations:** `is_deleted` boolean. The only true soft-delete pattern.
2. **Documents:** `archived` boolean + `enabled` boolean — two independent flags. Archived docs are hidden; disabled docs exist but are excluded from search.
3. **Document Segments:** `enabled` boolean only.
4. **No global soft-delete mixin.** Each table handles deletion differently.

---

## 15. JSON Column Schema Summary

| Table.Column | Schema |
|-------------|--------|
| app_model_configs.model | {provider, name, mode, completion_params:{temperature,...}} |
| app_model_configs.agent_mode | {enabled, strategy:'function_call'|'react', tools:[], prompt} |
| app_model_configs.dataset_configs | {retrieval_model:'single'|'multiple', ...} |
| app_model_configs.file_upload | {image:{enabled, number_limits, detail, transfer_methods}} |
| conversations.inputs | {var_name: value_or_file_object, ...} |
| messages.message | [{role:'system'|'user'|'assistant', content:...}] |
| messages.message_metadata | {retriever_resources:[...], annotation_reply:{...}} |
| workflows.graph | {nodes:[{id, data:{type, ...}, position}], edges:[{source, target}]} |
| workflows.features | {file_upload:{enabled, number_limits, ...}, speech_to_text:{...}} |
| workflows.environment_variables | {var_name: {id, name, value_type, value}} |
| datasets.retrieval_model | {search_method, reranking_enable, reranking_model, top_k, score_threshold_enabled} |
| documents.data_source_info | {upload_file_id:...} or {notion_page_id:...} or {url:...} |
| documents.doc_metadata | {field_name: value, ...} |
| trigger_subscriptions.parameters | Provider-specific subscription params |

---

## 16. Redis Usage Patterns

Redis is used extensively but **not for primary data storage**. Key patterns:

1. **Document indexing locks:** `document_{id}_is_paused`, `document_{id}_is_retried` (TTL 600s), `document_{id}_indexing` (TTL 600s), `segment_{id}_indexing` (TTL 600s), `segment_{id}_delete_indexing` (TTL 600s)
2. **Provider last-used cache:** `provider_cache_key(tenant_id, provider_name)` — prevents excessive DB updates
3. **RSA key cache:** `tenant_privkey:{hash}` (TTL 120s) — cached private keys
4. **Session storage:** Flask session backend
5. **Rate limiting:** Application-level rate limiting state
6. **Celery broker:** Task queue message broker

---

## 17. Database Constraints & Indexes

**No stored procedures or database-level triggers** found in the codebase. All business logic is application-level.

**Notable unique constraints:**
- `tenant_account_joins`: UNIQUE(tenant_id, account_id)
- `providers`: UNIQUE(tenant_id, provider_name, provider_type, quota_type)
- `provider_models`: UNIQUE(tenant_id, provider_name, model_name, model_type)
- `app_mcp_servers`: UNIQUE(tenant_id, app_id), UNIQUE(server_code)
- `installed_apps`: UNIQUE(tenant_id, app_id)
- `tool_api_providers`: UNIQUE(name, tenant_id)
- `embeddings`: UNIQUE(model_name, hash, provider_name)

**No foreign key constraints at database level** — all referential integrity is maintained in application code. The only FK declarations in SQLAlchemy are:
- `messages.conversation_id → conversations.id`
- `message_annotations.conversation_id → conversations.id`

**Performance-critical indexes:** Message table has 8 composite indexes. Document segments have 6 indexes. Workflow node executions have 4 composite indexes.

---

## 18. Entity Count Summary

| Domain | Tables |
|--------|--------|
| Auth & Tenancy | 7 (accounts, tenants, tenant_account_joins, account_integrates, invitation_codes, tenant_plugin_permissions, tenant_plugin_auto_upgrade_strategies) |
| Apps & Config | 10 (apps, app_model_configs, sites, api_tokens, app_mcp_servers, installed_apps, recommended_apps, tags, tag_bindings, trace_app_config) |
| Conversations & Messages | 12 (conversations, messages, message_feedbacks, message_files, message_annotations, message_agent_thoughts, message_chains, dataset_retriever_resources, end_users, saved_messages, pinned_conversations, app_annotation_*) |
| Datasets | 16 (datasets, documents, document_segments, child_chunks, dataset_process_rules, dataset_keyword_tables, app_dataset_joins, dataset_queries, embeddings, dataset_collection_bindings, dataset_permissions, dataset_metadata, dataset_metadata_bindings, external_knowledge_*, segment_attachment_bindings, pipelines, pipeline_*) |
| Workflows | 10 (workflows, workflow_runs, workflow_node_executions, workflow_node_execution_offload, workflow_app_logs, workflow_conversation_variables, workflow_draft_variables, workflow_draft_variable_files, workflow_pauses, workflow_pause_reasons) |
| Providers | 8 (providers, provider_credentials, provider_models, provider_model_credentials, tenant_default_models, tenant_preferred_model_providers, provider_model_settings, load_balancing_model_configs, provider_orders) |
| Tools | 7 (tool_builtin_providers, tool_api_providers, tool_workflow_providers, tool_mcp_providers, tool_label_bindings, tool_oauth_system_clients, tool_oauth_tenant_clients) |
| Triggers | 8 (trigger_subscriptions, workflow_webhook_triggers, workflow_plugin_triggers, app_triggers, workflow_schedule_plans, workflow_trigger_logs, trigger_oauth_*) |
| Data Sources | 4 (data_source_oauth_bindings, data_source_api_key_auth_bindings, datasource_providers, datasource_oauth_*) |
| Files | 1 (upload_files) |
| System | 8 (dify_setups, celery_*, api_requests, api_based_extensions, operation_logs, whitelists, tenant_credit_pools, oauth_provider_apps) |
| **Total** | **~80+ tables** |
