

Now let me compile the complete requirements document from all the findings.

---

# DIFY CELERY TASK QUEUE & BACKGROUND JOBS — REQUIREMENTS DOCUMENT

**Codebase:** Dify v1.11.4 (`/Users/markforster/nyqst-dify/upstream-dify/`)
**Analysis Date:** 2026-02-01

---

## 1. CELERY CONFIGURATION

### 1.1 Broker & Backend

| Setting | Value | Source |
|---------|-------|--------|
| **Broker** | Redis (default `redis://:difyai123456@redis:6379/1`) | `api/configs/middleware/__init__.py:236` |
| **Backend** | Redis (configurable: `redis`, `database`, `rabbitmq`) | `CeleryConfig.CELERY_BACKEND` |
| **Result Backend** | Computed: Redis → same as broker URL; database → `db+{SQLALCHEMY_DATABASE_URI}` | `CeleryConfig.CELERY_RESULT_BACKEND` (computed field) |
| **Results Stored?** | **No** — `task_ignore_result=True` | `api/extensions/ext_celery.py:80` |
| **Serializer** | Default (JSON) — not explicitly overridden | — |
| **Timezone** | `pytz.timezone(LOG_TZ or "UTC")` | `ext_celery.py:79` |
| **Connection Retry** | `broker_connection_retry_on_startup=True` | `ext_celery.py:75` |

### 1.2 Redis Sentinel Support

| Setting | Default |
|---------|---------|
| `CELERY_USE_SENTINEL` | `False` |
| `CELERY_SENTINEL_MASTER_NAME` | `None` |
| `CELERY_SENTINEL_PASSWORD` | `None` |
| `CELERY_SENTINEL_SOCKET_TIMEOUT` | `0.1s` |

### 1.3 SSL/TLS

Enabled when `CELERY_BROKER_URL` starts with `rediss://`. Configurable cert requirements: `CERT_NONE`, `CERT_OPTIONAL`, `CERT_REQUIRED`. Custom CA/cert/key paths supported via `REDIS_SSL_CA_CERTS`, `REDIS_SSL_CERTFILE`, `REDIS_SSL_KEYFILE`.

### 1.4 Worker Concurrency

| Setting | Default | Notes |
|---------|---------|-------|
| **Worker Pool** | `gevent` | Via `CELERY_WORKER_CLASS` |
| **Concurrency** | `1` greenlet | `CELERY_WORKER_AMOUNT` |
| **Auto-scale** | `false` | `CELERY_AUTO_SCALE` → `--autoscale=MAX,MIN` |
| **Max Tasks Per Child** | `50` | Worker restarts after 50 tasks |
| **Prefetch Multiplier** | `1` | One task at a time per greenlet |

### 1.5 Custom Task Base Class

All tasks inherit `FlaskTask` (`ext_celery.py:48-52`) which wraps every task invocation in `app.app_context()` and initializes `core.logging.context.init_request_context()`.

---

## 2. WORKER TYPES

### 2.1 Docker Compose Services (`docker/docker-compose.yaml`)

| Service | MODE env | Command | Purpose |
|---------|----------|---------|---------|
| `worker` | `worker` | `celery worker -P gevent -Q <all queues> --max-tasks-per-child 50` | General-purpose worker consuming ALL queues |
| `worker_beat` | `beat` | `celery beat --loglevel INFO` | Periodic task scheduler only |

### 2.2 Queue Assignment

**Single generic worker** consumes all queues. Kubernetes deployments can specialize workers via `CELERY_WORKER_QUEUES` env override per pod.

### 2.3 Default Queue List (Community Edition)

```
dataset, priority_dataset, priority_pipeline, pipeline, mail, ops_trace,
app_deletion, plugin, workflow_storage, conversation, workflow,
schedule_poller, schedule_executor, triggered_workflow_dispatcher,
trigger_refresh_executor, retention
```

**Cloud Edition** replaces `workflow` with three tier-based queues: `workflow_professional`, `workflow_team`, `workflow_sandbox`.

---

## 3. ALL REGISTERED TASKS (62 tasks, 19 queues)

### 3.1 Document Indexing Tasks — Queue: `dataset`

| Task | File | Parameters | Retry | Notes |
|------|------|------------|-------|-------|
| `document_indexing_task` | `tasks/document_indexing_task.py:21` | `dataset_id, document_ids` | None | **DEPRECATED** |
| `normal_document_indexing_task` | `tasks/document_indexing_task.py:149` | `tenant_id, dataset_id, document_ids` | None | Standard priority; uses tenant isolation queue |
| `document_indexing_update_task` | `tasks/document_indexing_update_task.py:17` | `dataset_id, document_id` | None | Delete old + re-index |
| `document_indexing_sync_task` | `tasks/document_indexing_sync_task.py:19` | `dataset_id, document_id` | None | Notion sync |
| `add_document_to_index_task` | `tasks/add_document_to_index_task.py:20` | `dataset_document_id` | None | Re-enable completed document |
| `remove_document_from_index_task` | `tasks/remove_document_from_index_task.py:17` | `document_id` | None | Disable from vector index |
| `duplicate_document_indexing_task` | `tasks/duplicate_document_indexing_task.py:21` | `dataset_id, document_ids` | None | **DEPRECATED** |
| `normal_duplicate_document_indexing_task` | `tasks/duplicate_document_indexing_task.py:149` | `tenant_id, dataset_id, document_ids` | None | Tenant-isolated |
| `recover_document_indexing_task` | `tasks/recover_document_indexing_task.py` | `dataset_id, document_ids` | None | Recover from error |
| `retry_document_indexing_task` | `tasks/retry_document_indexing_task.py` | `dataset_id, document_ids, user_id` | None | Clean + restart from "parsing" |
| `sync_website_document_indexing_task` | `tasks/sync_website_document_indexing_task.py` | `dataset_id, document_id` | None | Website crawl sync |
| `clean_document_task` | `tasks/clean_document_task.py:18` | `document_id, dataset_id, doc_form, file_id` | None | Delete document + vector + segments |
| `clean_dataset_task` | `tasks/clean_dataset_task.py:32` | `dataset_id, tenant_id, indexing_technique, ...` | None | Full dataset cleanup with rollback |
| `batch_clean_document_task` | `tasks/batch_clean_document_task.py` | `document_ids, dataset_id` | None | Batch delete |
| `clean_notion_document_task` | `tasks/clean_notion_document_task.py` | `document_ids, dataset_id` | None | Notion-specific cleanup |
| `deal_dataset_index_update_task` | `tasks/deal_dataset_index_update_task.py` | `dataset_id, action` | None | Index config changes |
| `deal_dataset_vector_index_task` | `tasks/deal_dataset_vector_index_task.py` | `dataset_id, action` | None | Vector index changes |
| `delete_account_task` | `tasks/delete_account_task.py:14` | `account_id` | None | Account deletion |

### 3.2 Priority Document Indexing — Queue: `priority_dataset`

| Task | File | Notes |
|------|------|-------|
| `priority_document_indexing_task` | `tasks/document_indexing_task.py:163` | Paid plan documents |
| `priority_duplicate_document_indexing_task` | `tasks/duplicate_document_indexing_task.py:163` | Paid plan duplicates |

### 3.3 Segment Operations — Queue: `dataset`

| Task | File | Parameters |
|------|------|------------|
| `enable_segment_to_index_task` | `tasks/enable_segment_to_index_task.py` | `segment_id` |
| `enable_segments_to_index_task` | `tasks/enable_segments_to_index_task.py` | `segment_ids, dataset_id, document_id` |
| `disable_segment_from_index_task` | `tasks/disable_segment_from_index_task.py` | `segment_id` |
| `disable_segments_from_index_task` | `tasks/disable_segments_from_index_task.py` | `segment_ids, dataset_id, document_id` |
| `delete_segment_from_index_task` | `tasks/delete_segment_from_index_task.py` | `index_node_ids, dataset_id, document_id` |
| `create_segment_to_index_task` | `tasks/create_segment_to_index_task.py` | `segment_id` |
| `batch_create_segment_to_index_task` | `tasks/batch_create_segment_to_index_task.py` | `job_id, upload_file_id, dataset_id, document_id, tenant_id, user_id` |

### 3.4 Annotation Tasks — Queue: `dataset`

| Task | File |
|------|------|
| `add_annotation_to_index_task` | `tasks/annotation/add_annotation_to_index_task.py:16` |
| `update_annotation_to_index_task` | `tasks/annotation/update_annotation_to_index_task.py` |
| `delete_annotation_index_task` | `tasks/annotation/delete_annotation_index_task.py` |
| `batch_import_annotations_task` | `tasks/annotation/batch_import_annotations_task.py:19` |
| `enable_annotation_reply_task` | `tasks/annotation/enable_annotation_reply_task.py` |
| `disable_annotation_reply_task` | `tasks/annotation/disable_annotation_reply_task.py` |

### 3.5 Workflow Execution — Tier-Based Queues

| Task | Queue | Notes |
|------|-------|-------|
| `execute_workflow_professional` | `workflow_professional` (Cloud) / `workflow` (Community) | Highest priority |
| `execute_workflow_team` | `workflow_team` / `workflow` | Standard |
| `execute_workflow_sandbox` | `workflow_sandbox` / `workflow` | Lowest priority |

Uses **CFS (Completely Fair Scheduler)** plan entity for Cloud edition time-slicing. Community edition uses `Nop` strategy.

### 3.6 Workflow Storage — Queue: `workflow_storage`

| Task | Retry | Notes |
|------|-------|-------|
| `save_workflow_execution_task` | **bind=True, max_retries=3, default_retry_delay=60s, exponential backoff** | `countdown=60 * (2^retries)` |
| `save_workflow_node_execution_task` | **bind=True, max_retries=3, default_retry_delay=60s, exponential backoff** | Same pattern |

### 3.7 Workflow Draft Variables — Queue: `workflow_draft_var`

| Task | Retry |
|------|-------|
| `save_workflow_execution_task` (draft vars) | **bind=True, max_retries=3, default_retry_delay=60s** |

### 3.8 Workflow Scheduling

| Task | Queue | Notes |
|------|-------|-------|
| `poll_workflow_schedules` | `schedule_poller` | Uses `group()` for parallel dispatch |
| `run_schedule_trigger` | `schedule_executor` | Per-schedule execution, quota-checked |

### 3.9 RAG Pipeline — Queues: `pipeline`, `priority_pipeline`

| Task | Queue | Notes |
|------|-------|-------|
| `rag_pipeline_run_task` | `pipeline` | ThreadPoolExecutor(max_workers=10), tenant isolation |
| `priority_rag_pipeline_run_task` | `priority_pipeline` | Same structure, higher priority |

### 3.10 Mail Tasks — Queue: `mail`

| Task | File |
|------|------|
| `send_email_register_mail_task` | `tasks/mail_register_task.py:14` |
| `send_email_register_mail_task_when_account_exist` | `tasks/mail_register_task.py:50` |
| `send_reset_password_mail_task` | `tasks/mail_reset_password_task.py:14` |
| `send_reset_password_mail_task_when_account_not_exist` | `tasks/mail_reset_password_task.py:50` |
| `send_invite_member_mail_task` | `tasks/mail_invite_member_task.py:14` |
| `send_deletion_success_task` | `tasks/mail_account_deletion_task.py:13` |
| `send_account_deletion_verification_code` | `tasks/mail_account_deletion_task.py:48` |
| `send_owner_transfer_confirm_task` | `tasks/mail_owner_transfer_task.py:13` |
| `send_old_owner_transfer_notify_email_task` | `tasks/mail_owner_transfer_task.py:54` |
| `send_new_owner_transfer_notify_email_task` | `tasks/mail_owner_transfer_task.py:95` |

### 3.11 Trigger Tasks

| Task | Queue |
|------|-------|
| `dispatch_triggered_workflows_async` | `triggered_workflow_dispatcher` |
| `trigger_subscription_refresh` | `trigger_refresh_executor` |
| `trigger_provider_refresh` | `trigger_refresh_publisher` |

### 3.12 Other Tasks

| Task | Queue | Retry |
|------|-------|-------|
| `remove_app_and_related_data_task` | `app_deletion` | **bind=True, max_retries=3** (60s countdown on SQLAlchemyError) |
| `delete_conversation_related_data` | `conversation` | None (rollback on exception) |
| `process_trace_tasks` | `ops_trace` | None |
| `process_tenant_plugin_autoupgrade_check_task` | `plugin` | Internal retry: 3 per plugin per tenant |

---

## 4. DOCUMENT PROCESSING PIPELINE (End-to-End)

### 4.1 Flow

```
User Upload → POST /datasets/<id>/documents
  → DatasetDocumentListApi.post() [controllers/console/datasets/datasets_document.py:336]
  → DocumentService.save_document_with_dataset_id() [services/dataset_service.py:1516]
    → Creates Document records (status="waiting")
    → DocumentIndexingTaskProxy(tenant_id, dataset_id, doc_ids).delay()
      → Routes by billing plan:
         Sandbox → normal_document_indexing_task (queue="dataset")
         Paid    → priority_document_indexing_task (queue="priority_dataset")
         Self-hosted → priority_document_indexing_task (direct)
  → _document_indexing() [tasks/document_indexing_task.py:38]
    → Status: waiting → parsing
    → IndexingRunner.run() [core/indexing_runner.py:64]
      → _extract()   → Status: parsing → splitting
      → _transform()  → Text splitting by chunk size/overlap/separator
      → _load_segments() → Status: splitting → indexing (segments saved to DB)
      → _load()        → Status: indexing → completed
        → ThreadPoolExecutor(max_workers=10)
        → Documents grouped by hash % 10 (deadlock prevention)
        → Per chunk: embed → store in vector DB → segment status → completed
```

### 4.2 Status Lifecycle

```
waiting → parsing → splitting → indexing → completed
  └── any stage → error (on exception, message stored in Document.error)
  └── error → parsing (via retry_document_indexing_task: cleans old data first)
  └── completed + disabled → re-enabled via add_document_to_index_task
```

### 4.3 Pause Mechanism

Redis key `document_{document_id}_is_paused` checked in `_process_chunk()`. Raises `DocumentIsPausedError` to halt mid-indexing.

---

## 5. EMBEDDING GENERATION PIPELINE

### 5.1 Flow

```
IndexingRunner._load() [core/indexing_runner.py:550]
  → Vector.create() [core/rag/datasource/vdb/vector_factory.py:193]
    → Batch size: 1000 documents per batch
    → CacheEmbedding.embed_documents() [core/rag/embedding/cached_embedding.py:28]
      → Cache lookup: Embedding table by (model_name, hash, provider_name)
      → Uncached texts → model_instance.invoke_text_embedding()
      → L2 normalize: vector / np.linalg.norm(vector)
      → Cache store: pickle to Embedding table
    → vector_processor.create(texts, embeddings)
      → Insert into configured vector DB (Qdrant/Milvus/PGVector/Chroma/etc.)
```

### 5.2 Embedding Cache

- **Table:** `Embedding` (model `api/models/dataset.py`)
- **Key:** `(model_name, hash, provider_name)` where hash = SHA256 of text content
- **Storage:** `pickle.dumps(embedding, protocol=HIGHEST_PROTOCOL)`
- **Invalidation:** Via `clean_embedding_cache_task` scheduled task

### 5.3 Concurrency

- 10 parallel threads per document indexing task (hash-based grouping prevents DB deadlocks)
- Embedding model batch size is model-specific (typically 10-100 texts per API call)

---

## 6. WORKFLOW EXECUTION VIA CELERY

### 6.1 Async Workflow Dispatch

Workflows are dispatched to tier-based queues (`tasks/async_workflow_tasks.py`):

- **Professional** → `workflow_professional` queue
- **Team** → `workflow_team` queue
- **Sandbox** → `workflow_sandbox` queue
- **Community** → all use single `workflow` queue

Each uses a **CFS Plan Scheduler** entity. Cloud edition applies `TimeSlice` strategy for fair scheduling. Community uses `Nop` (no scheduling overhead).

### 6.2 Workflow Persistence

Two dedicated tasks with retry logic save execution state asynchronously to `workflow_storage` queue:
- `save_workflow_execution_task` — Workflow-level run record
- `save_workflow_node_execution_task` — Per-node execution record

Both: `bind=True, max_retries=3, exponential backoff (60s × 2^retries)`

---

## 7. SCHEDULED/PERIODIC TASKS (Celery Beat)

All controlled by feature flags. `day` = `CELERY_BEAT_SCHEDULER_TIME` (default: 1).

| Beat Task | Celery Task Path | Schedule | Flag | Default |
|-----------|-----------------|----------|------|---------|
| `clean_embedding_cache_task` | `schedule.clean_embedding_cache_task.clean_embedding_cache_task` | **2:00 AM every N days** | `ENABLE_CLEAN_EMBEDDING_CACHE_TASK` | `False` |
| `clean_unused_datasets_task` | `schedule.clean_unused_datasets_task.clean_unused_datasets_task` | **3:00 AM every N days** | `ENABLE_CLEAN_UNUSED_DATASETS_TASK` | `False` |
| `create_tidb_serverless_task` | `schedule.create_tidb_serverless_task.create_tidb_serverless_task` | **Every hour** | `ENABLE_CREATE_TIDB_SERVERLESS_TASK` | `False` |
| `update_tidb_serverless_status_task` | `schedule.update_tidb_serverless_status_task...` | **Every 10 min** | `ENABLE_UPDATE_TIDB_SERVERLESS_STATUS_TASK` | `False` |
| `clean_messages` | `schedule.clean_messages.clean_messages` | **4:00 AM every N days** | `ENABLE_CLEAN_MESSAGES` | `False` |
| `mail_clean_document_notify_task` | `schedule.mail_clean_document_notify_task...` | **Monday 10:00 AM** | `ENABLE_MAIL_CLEAN_DOCUMENT_NOTIFY_TASK` | `False` |
| `datasets-queue-monitor` | `schedule.queue_monitor_task.queue_monitor_task` | **Every 30 min** (configurable) | `ENABLE_DATASETS_QUEUE_MONITOR` | `False` |
| `check_upgradable_plugin_task` | `schedule.check_upgradable_plugin_task...` | **Every 15 min** | `ENABLE_CHECK_UPGRADABLE_PLUGIN_TASK` | `True` |
| `clean_workflow_runlogs_precise` | `schedule.clean_workflow_runlogs_precise...` | **2:00 AM daily** | `WORKFLOW_LOG_CLEANUP_ENABLED` | `False` |
| `clean_workflow_runs_task` | `schedule.clean_workflow_runs_task...` | **Midnight daily** | `ENABLE_WORKFLOW_RUN_CLEANUP_TASK` | `False` |
| `workflow_schedule_task` | `schedule.workflow_schedule_task.poll_workflow_schedules` | **Every 1 min** (configurable) | `ENABLE_WORKFLOW_SCHEDULE_POLLER_TASK` | `True` |
| `trigger_provider_refresh` | `schedule.trigger_provider_refresh_task.trigger_provider_refresh` | **Every 1 min** (configurable) | `ENABLE_TRIGGER_PROVIDER_REFRESH_TASK` | `True` |

**Enabled by default in production:** `check_upgradable_plugin_task`, `workflow_schedule_task`, `trigger_provider_refresh`.

---

## 8. ERROR HANDLING & RETRY POLICIES

### 8.1 Tasks WITH Retry Configuration

| Task | max_retries | Delay Strategy | Trigger |
|------|------------|----------------|---------|
| `save_workflow_execution_task` | 3 | Exponential: `60 × 2^retries` (60s, 120s, 240s) | Any exception |
| `save_workflow_node_execution_task` | 3 | Exponential: `60 × 2^retries` | Any exception |
| `remove_app_and_related_data_task` | 3 | Fixed 60s | SQLAlchemyError or Exception |
| `save_workflow_execution_task` (draft vars) | 3 | Fixed 60s | Any exception |

### 8.2 Tasks WITHOUT Retry

**All other 58 tasks have no Celery-level retry.** Error handling patterns:
- **Document indexing:** Sets `Document.indexing_status = "error"` and stores error message. Manual retry via `retry_document_indexing_task`.
- **Dataset cleanup:** DB rollback on exception.
- **Conversation deletion:** DB rollback on exception.
- **Mail tasks:** Fail silently (log only).

### 8.3 Application-Level Retry

- **Plugin auto-upgrade:** Internal constant `RETRY_TIMES_OF_ONE_PLUGIN_IN_ONE_TENANT = 3`
- **Trigger subscription refresh:** Redis-based in-flight lock prevents concurrent refresh

---

## 9. TASK MONITORING

### 9.1 Queue Monitor Task

- **Task:** `queue_monitor_task` (`schedule/queue_monitor_task.py`)
- **Schedule:** Every 30 minutes (configurable via `QUEUE_MONITOR_INTERVAL`)
- **Mechanism:** Checks Redis queue length against `QUEUE_MONITOR_THRESHOLD`
- **Alert:** Sends email to `QUEUE_MONITOR_ALERT_EMAILS` when threshold exceeded
- **Flag:** `ENABLE_DATASETS_QUEUE_MONITOR` (default: `False`)

### 9.2 Flower

**Not configured.** No Flower web monitoring is included in the default deployment. The only monitoring is the queue length alert task above.

### 9.3 OpenTelemetry

Dependency `opentelemetry-instrumentation-celery==0.48b0` is present, enabling distributed tracing integration if configured.

---

## 10. RATE LIMITING

### 10.1 Celery-Level Rate Limiting

**No tasks use Celery's `rate_limit` parameter.** Zero tasks have `rate_limit=` in their decorator.

### 10.2 Application-Level Rate Limiting

| Mechanism | Location | Description |
|-----------|----------|-------------|
| **Tenant Isolation Queue** | `services/document_indexing_proxy/` | Serializes indexing tasks per-tenant to prevent resource hogging |
| **Quota Checks** | `run_schedule_trigger`, `dispatch_triggered_workflows_async` | `QuotaType.TRIGGER.consume()` enforces per-tenant trigger quotas |
| **Redis In-Flight Lock** | `trigger_subscription_refresh_tasks.py` | Prevents concurrent refresh of same subscription |
| **Batch Size Limits** | `WORKFLOW_SCHEDULE_POLLER_BATCH_SIZE=100`, `TRIGGER_PROVIDER_REFRESH_BATCH_SIZE=200` | Caps per-tick processing |
| **Max Dispatch Per Tick** | `WORKFLOW_SCHEDULE_MAX_DISPATCH_PER_TICK=0` (unlimited) | Configurable cap on schedule dispatches |

### 10.3 Tenant Isolation Queue

The `DocumentIndexingTaskProxy` routes tasks through a tenant-isolated queue pattern: each tenant's indexing tasks are serialized so only one runs at a time per tenant. When a task completes, it pulls the next waiting task for that tenant and dispatches it via `.delay()`.

---

## 11. QUEUE ROUTING SUMMARY

| Queue | Tasks | Purpose |
|-------|-------|---------|
| `dataset` | 30+ tasks | Document indexing, segments, annotations, cleanup |
| `priority_dataset` | 2 tasks | Paid-plan document indexing |
| `pipeline` | 1 task | RAG pipeline execution |
| `priority_pipeline` | 1 task | Priority RAG pipeline |
| `workflow` | 3 tasks (community) | Workflow execution |
| `workflow_professional` | 1 task (cloud) | Pro-tier workflows |
| `workflow_team` | 1 task (cloud) | Team-tier workflows |
| `workflow_sandbox` | 1 task (cloud) | Free-tier workflows |
| `workflow_storage` | 2 tasks | Workflow execution persistence |
| `workflow_draft_var` | 1 task | Draft variable cleanup |
| `mail` | 10+ tasks | All email notifications |
| `ops_trace` | 1 task | Observability trace processing |
| `app_deletion` | 1 task | Full app + related data deletion |
| `conversation` | 1 task | Conversation data deletion |
| `plugin` | 2 tasks | Plugin upgrade checks |
| `schedule_poller` | 1 task | Workflow schedule polling |
| `schedule_executor` | 1 task | Scheduled workflow execution |
| `triggered_workflow_dispatcher` | 1 task | Plugin trigger dispatch |
| `trigger_refresh_executor` | 1 task | Trigger subscription refresh |
| `trigger_refresh_publisher` | 1 task | Trigger provider refresh scan |
| `retention` | 1 task | Workflow run cleanup (SaaS) |

---

## 12. KEY ARCHITECTURAL OBSERVATIONS

`★ Insight ─────────────────────────────────────`

1. **Single-worker-all-queues design.** Dify runs one generic worker consuming all 19+ queues. This simplifies deployment but means a flood of `dataset` tasks can starve `mail` or `workflow` queues. Kubernetes deployments should use `CELERY_WORKER_QUEUES` to create specialized worker pods.

2. **Most tasks have NO retry policy.** Only 4 of 62 tasks use Celery retries. Document indexing failures are stored as status="error" for manual retry. This is a deliberate design — document indexing is idempotent (retry cleans old data first) so Celery-level retry adds complexity without benefit.

3. **Tenant isolation is application-level, not Celery-level.** Rather than using Celery queue-per-tenant, Dify serializes tenant tasks through a Redis-backed queue proxy. This prevents any single tenant from monopolizing worker capacity.

4. **Embedding caching is aggressive.** The `CacheEmbedding` class checks a database table before every embedding API call, keyed by `(model, provider, text_hash)`. This means re-indexing the same content is nearly free, but the `Embedding` table can grow very large — hence the `clean_embedding_cache_task` periodic cleanup.

5. **Gevent + ThreadPoolExecutor hybrid.** The worker runs gevent greenlets, but `IndexingRunner._load()` spawns a `ThreadPoolExecutor(max_workers=10)` for parallel embedding generation. This works because gevent patches I/O, and the thread pool handles CPU-bound numpy normalization without blocking the greenlet.

`─────────────────────────────────────────────────`
