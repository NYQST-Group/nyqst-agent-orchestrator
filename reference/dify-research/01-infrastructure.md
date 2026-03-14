

Now I have comprehensive data from all sources. Let me produce the full infrastructure specification document.

---

# Dify v1.11.4 — Infrastructure & Deployment Specification

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Service Inventory](#2-service-inventory)
3. [Dockerfiles & Build Pipeline](#3-dockerfiles--build-pipeline)
4. [Nginx Routing & SSL](#4-nginx-routing--ssl)
5. [Network Topology](#5-network-topology)
6. [Volume Mounts & Persistence](#6-volume-mounts--persistence)
7. [Environment Variable Inventory](#7-environment-variable-inventory)
8. [Health Checks](#8-health-checks)
9. [Init Containers & First Boot](#9-init-containers--first-boot)
10. [Database Migrations](#10-database-migrations)
11. [Scaling Patterns](#11-scaling-patterns)
12. [Kubernetes Support](#12-kubernetes-support)
13. [Backup & Restore](#13-backup--restore)
14. [Security Considerations](#14-security-considerations)
15. [Compose Profiles](#15-compose-profiles)

---

## 1. Architecture Overview

Dify is a multi-service platform composed of 5 core services behind an Nginx reverse proxy, plus pluggable metadata databases and vector stores selected via compose profiles.

```
                        ┌─────────────────────────────────────┐
                        │            Internet / Client         │
                        └──────────────┬──────────────────────┘
                                       │ :80 / :443
                                ┌──────▼──────┐
                                │    nginx     │
                                └──┬───┬───┬──┘
                   ┌───────────────┘   │   └──────────────┐
                   │                   │                   │
          /console/api            /  /explore          /e/*
          /api  /v1  /files       (frontend)         (plugins)
          /mcp  /triggers
                   │                   │                   │
            ┌──────▼──────┐    ┌───────▼──────┐   ┌───────▼────────┐
            │  api :5001   │    │  web :3000   │   │plugin_daemon   │
            │ (gunicorn/   │    │ (Next.js/    │   │    :5002       │
            │  flask)      │    │  PM2)        │   └───────┬────────┘
            └──┬───┬───┬──┘    └──────────────┘           │
               │   │   │                                   │
     ┌─────────┘   │   └──────────┐                       │
     │             │              │                        │
┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐             ┌────▼────┐
│ worker  │  │worker_beat │  │ sandbox │             │postgres │
│(celery) │  │(celery     │  │ :8194   │             │(plugin  │
│         │  │ beat)      │  │         │             │ DB)     │
└────┬────┘  └─────┬─────┘  └────┬────┘             └─────────┘
     │             │              │
     └──────┬──────┘              │
            │                     │
    ┌───────▼────────┐    ┌───────▼───────┐
    │   redis :6379  │    │  ssrf_proxy   │
    │                │    │  :3128        │
    └────────────────┘    │  (squid)      │
                          └───────────────┘
    ┌────────────────┐
    │  db_postgres   │    (or db_mysql, oceanbase, seekdb)
    │  :5432         │
    └────────────────┘
    ┌────────────────┐
    │  vector store  │    (weaviate, qdrant, pgvector, milvus, etc.)
    └────────────────┘
```

**Core services (always running):** nginx, api, worker, worker_beat, web, sandbox, ssrf_proxy, plugin_daemon, redis, init_permissions, + one metadata DB + one vector store.

---

## 2. Service Inventory

| Service | Image | Port | Purpose |
|---|---|---|---|
| **api** | `langgenius/dify-api:1.11.4` | 5001 | Flask/Gunicorn API server |
| **worker** | `langgenius/dify-api:1.11.4` | — | Celery worker (all queues) |
| **worker_beat** | `langgenius/dify-api:1.11.4` | — | Celery beat scheduler |
| **web** | `langgenius/dify-web:1.11.4` | 3000 | Next.js frontend (PM2) |
| **nginx** | `nginx:latest` | 80, 443 | Reverse proxy / TLS termination |
| **sandbox** | `langgenius/dify-sandbox:0.2.12` | 8194 | Code execution sandbox |
| **plugin_daemon** | `langgenius/dify-plugin-daemon:0.5.2-local` | 5002 | Plugin runtime |
| **ssrf_proxy** | `ubuntu/squid:latest` | 3128 | SSRF protection proxy |
| **redis** | `redis:6-alpine` | 6379 | Cache + Celery broker |
| **db_postgres** | `postgres:15-alpine` | 5432 | Metadata DB (default) |
| **db_mysql** | `mysql:8.0` | 3306 | Metadata DB (alt) |
| **init_permissions** | `busybox:latest` | — | One-shot volume permission fix |
| **certbot** | `certbot/certbot` | — | Optional SSL cert management |

### Vector Store Options (one active via profile)

| Service | Image | Profile | Default Port |
|---|---|---|---|
| weaviate | `semitechnologies/weaviate:1.27.0` | `weaviate` (default) | 8080/50051 |
| qdrant | `langgenius/qdrant:v1.8.3` | `qdrant` | 6333 |
| pgvector | `pgvector/pgvector:pg16` | `pgvector` | 5432 |
| pgvecto-rs | `tensorchord/pgvecto-rs:pg16-v0.3.0` | `pgvecto-rs` | 5432 |
| chroma | `ghcr.io/chroma-core/chroma:0.5.20` | `chroma` | 8000 |
| milvus-standalone | `milvusdb/milvus:v2.6.3` | `milvus` | 19530 |
| opensearch | `opensearchproject/opensearch:latest` | `opensearch` | 9200 |
| elasticsearch | `docker.elastic.co/.../elasticsearch:8.14.3` | `elasticsearch` | 9200 |
| oceanbase | `oceanbase/oceanbase-ce:4.3.5-lts` | `oceanbase` | 2881 |
| oracle | `container-registry.oracle.com/database/free:latest` | `oracle` | 1521 |
| couchbase | Custom build | `couchbase` | 8091 |
| myscale | `myscale/myscaledb:1.6.4` | `myscale` | 8123 |
| opengauss | `opengauss/opengauss:7.0.0-RC1` | `opengauss` | 6600 |

---

## 3. Dockerfiles & Build Pipeline

### API Dockerfile (`api/Dockerfile`)
- **3-stage build**: base → packages → production
- **Base**: `python:3.12-slim-bookworm` with `uv` 0.8.9
- **Packages stage**: Compiles C extensions (gmpy2), runs `uv sync --locked --no-dev`
- **Production**: Non-root user `dify` (UID 1001), Node.js 22 for NLTK/tiktoken, exposes port 5001
- **Entrypoint**: `/bin/bash /entrypoint.sh` — dispatches to gunicorn, celery worker, celery beat, or flask CLI based on `MODE` env var

### Web Dockerfile (`web/Dockerfile`)
- **4-stage build**: base → packages → builder → production
- **Base**: `node:24-alpine` with pnpm via corepack
- **Builder**: `NODE_OPTIONS=--max-old-space-size=4096`, runs `pnpm build:docker`
- **Production**: Non-root user `dify` (UID 1001), PM2 process manager, exposes port 3000
- **Entrypoint**: Maps env vars to `NEXT_PUBLIC_*` then `pm2 start server.js -i ${PM2_INSTANCES} --no-daemon`

### Sandbox
- Pre-built image `langgenius/dify-sandbox:0.2.12` — no Dockerfile in repo

### Plugin Daemon
- Pre-built image `langgenius/dify-plugin-daemon:0.5.2-local` — no Dockerfile in repo

`★ Insight ─────────────────────────────────────`
- The API image serves triple duty: api server, celery worker, and celery beat — differentiated solely by the `MODE` environment variable. This is a common pattern that reduces image builds but means the worker image carries unnecessary web-server dependencies.
- The web build uses a 4GB Node heap (`--max-old-space-size=4096`) indicating a substantial Next.js bundle.
`─────────────────────────────────────────────────`

---

## 4. Nginx Routing & SSL

### Upstream Routing (`docker/nginx/conf.d/default.conf.template`)

| Location | Upstream | Purpose |
|---|---|---|
| `/console/api` | `api:5001` | Console backend API |
| `/api` | `api:5001` | App API endpoints |
| `/v1` | `api:5001` | Versioned public API |
| `/files` | `api:5001` | File upload/download |
| `/mcp` | `api:5001` | Model Context Protocol |
| `/triggers` | `api:5001` | Webhook triggers |
| `/e/` | `plugin_daemon:5002` | Plugin endpoints (adds `Dify-Hook-Url` header) |
| `/explore` | `web:3000` | Explore page |
| `/` | `web:3000` | All other frontend routes |

### Proxy Settings (`proxy.conf.template`)
- HTTP/1.1 keep-alive, buffering disabled (for SSE streaming)
- Forwards: `Host`, `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Port`
- Configurable read/send timeouts (default 3600s — necessary for long LLM responses)

### SSL/TLS (`https.conf.template`)
- Enabled via `NGINX_HTTPS_ENABLED=true`
- Certificate sources (priority order): Certbot Let's Encrypt → manual `/etc/ssl/` mount
- Protocols: TLSv1.2 + TLSv1.3 (configurable)
- Session cache: 10MB shared, 10min timeout
- ACME challenge support via `NGINX_ENABLE_CERTBOT_CHALLENGE=true`

### Key Nginx Variables
| Variable | Default | Purpose |
|---|---|---|
| `NGINX_PORT` | 80 | HTTP listen port |
| `NGINX_SSL_PORT` | 443 | HTTPS listen port |
| `NGINX_SERVER_NAME` | `_` | Server name (all) |
| `NGINX_WORKER_PROCESSES` | auto | Worker count |
| `NGINX_CLIENT_MAX_BODY_SIZE` | 100M | Max upload size |
| `NGINX_KEEPALIVE_TIMEOUT` | 65s | Keep-alive |
| `NGINX_PROXY_READ_TIMEOUT` | 3600s | Proxy read timeout |
| `NGINX_PROXY_SEND_TIMEOUT` | 3600s | Proxy send timeout |

---

## 5. Network Topology

### Defined Networks

| Network | Type | Internal | Services |
|---|---|---|---|
| `default` | bridge | no | nginx, api, worker, worker_beat, web, redis, db_*, plugin_daemon, vector stores |
| `ssrf_proxy_network` | bridge | **yes** | sandbox, ssrf_proxy, api, worker, worker_beat |
| `milvus` | bridge | no | etcd, minio, milvus-standalone |
| `opensearch-net` | bridge | **yes** | opensearch, opensearch-dashboards |

### Communication Matrix

| From → To | Protocol | Network |
|---|---|---|
| nginx → api | HTTP :5001 | default |
| nginx → web | HTTP :3000 | default |
| nginx → plugin_daemon | HTTP :5002 | default |
| api → redis | TCP :6379 | default |
| api → db_postgres | TCP :5432 | default |
| api → sandbox | HTTP :8194 | ssrf_proxy_network |
| api → plugin_daemon | HTTP :5002 | default |
| api → vector_store | varies | default |
| worker → redis | TCP :6379 | default |
| worker → db_postgres | TCP :5432 | default |
| sandbox → ssrf_proxy | HTTP :3128 | ssrf_proxy_network (isolated) |
| ssrf_proxy → internet | HTTP/HTTPS | ssrf_proxy_network → external |
| plugin_daemon → api | HTTP :5001 | default (via `DIFY_INNER_API_URL`) |
| plugin_daemon → db_postgres | TCP :5432 | default (separate `dify_plugin` DB) |

`★ Insight ─────────────────────────────────────`
- The `ssrf_proxy_network` with `internal: true` is the critical security boundary. The sandbox container has NO direct internet access — all outbound traffic is forced through Squid proxy, preventing SSRF attacks from user-submitted code.
- The plugin daemon maintains a **bidirectional** relationship with the API: plugins call back to `DIFY_INNER_API_URL` (api:5001) for tool invocations.
`─────────────────────────────────────────────────`

---

## 6. Volume Mounts & Persistence

### Critical Persistent Volumes

| Host Path | Container Path | Service | Content |
|---|---|---|---|
| `./volumes/db/data` | `/var/lib/postgresql/data` | db_postgres | **All metadata** — users, apps, workflows, datasets |
| `./volumes/redis/data` | `/data` | redis | Cache, session data, Celery broker state |
| `./volumes/app/storage` | `/app/api/storage` | api, worker | Uploaded files, generated assets |
| `./volumes/plugin_daemon` | `/app/storage` | plugin_daemon | Plugin packages, working dirs |
| `./volumes/sandbox/dependencies` | `/dependencies` | sandbox | Python packages for sandbox |
| `./volumes/sandbox/conf` | `/conf` | sandbox | Sandbox configuration |
| `./volumes/weaviate` | `/var/lib/weaviate` | weaviate | Vector embeddings (default) |
| `./volumes/certbot/conf` | `/etc/letsencrypt` | nginx, certbot | SSL certificates |

### Data Criticality
- **CRITICAL (must back up):** `volumes/db/data`, `volumes/app/storage`
- **IMPORTANT:** Vector store volume (whichever is active), `volumes/plugin_daemon`
- **RECOVERABLE:** `volumes/redis/data` (cache, regenerable), `volumes/sandbox/*`

---

## 7. Environment Variable Inventory

### Tier 1: Must Configure for Production

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | `sk-9f73s...` | **CHANGE IMMEDIATELY** — `openssl rand -base64 42` |
| `POSTGRES_PASSWORD` / `DB_PASSWORD` | `difyai123456` | Database credential |
| `REDIS_PASSWORD` | `difyai123456` | Redis credential |
| `CONSOLE_API_URL` | `http://127.0.0.1:5001` | Public URL of API |
| `APP_API_URL` | `http://127.0.0.1:5001` | Public URL for app API |
| `CONSOLE_WEB_URL` | `http://127.0.0.1:3000` | Public URL of web console |
| `PLUGIN_DAEMON_KEY` / `SERVER_KEY` | hardcoded | Plugin auth key |
| `INNER_API_KEY_FOR_PLUGIN` | empty | API ↔ plugin auth |

### Tier 2: Operational Configuration

| Category | Key Variables | Defaults |
|---|---|---|
| **Database** | `DB_TYPE`, `DB_HOST`, `DB_PORT`, `DB_DATABASE` | postgresql, localhost, 5432, dify |
| **Connection Pool** | `SQLALCHEMY_POOL_SIZE`, `MAX_OVERFLOW`, `POOL_RECYCLE` | 30, 10, 3600 |
| **Redis** | `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` | localhost, 6379, 0 |
| **Redis HA** | `REDIS_USE_SENTINEL`, `REDIS_SENTINELS`, `REDIS_USE_CLUSTERS` | all false |
| **Storage** | `STORAGE_TYPE` | opendal (local filesystem) |
| **Celery** | `CELERY_BACKEND`, `CELERY_WORKER_AMOUNT`, `CELERY_AUTO_SCALE` | redis, 1, false |
| **Server** | `SERVER_WORKER_AMOUNT`, `SERVER_WORKER_CLASS`, `GUNICORN_TIMEOUT` | 1, gevent, 200 |
| **Vector DB** | `VECTOR_STORE` | — (set via profile) |
| **Migrations** | `MIGRATION_ENABLED` | true (in compose) |

### Tier 3: Feature & Limits

| Category | Key Variables | Defaults |
|---|---|---|
| **File Upload** | `UPLOAD_FILE_SIZE_LIMIT`, `UPLOAD_FILE_BATCH_LIMIT` | 15MB, 5 |
| **Workflow** | `WORKFLOW_MAX_EXECUTION_STEPS`, `WORKFLOW_MAX_EXECUTION_TIME` | 500, 1200s |
| **Code Sandbox** | `CODE_EXECUTION_ENDPOINT`, `CODE_EXECUTION_API_KEY` | sandbox:8194, dify-sandbox |
| **Web Frontend** | `PM2_INSTANCES`, `TEXT_GENERATION_TIMEOUT_MS` | 2, 60000 |
| **CORS** | `WEB_API_CORS_ALLOW_ORIGINS`, `CONSOLE_CORS_ALLOW_ORIGINS` | *, "" |
| **OAuth** | `GITHUB_CLIENT_ID/SECRET`, `GOOGLE_CLIENT_ID/SECRET` | — |
| **Mail** | `MAIL_TYPE`, `SMTP_SERVER`, `RESEND_API_KEY` | — |
| **Observability** | `ENABLE_OTEL`, `OTLP_BASE_ENDPOINT`, `SENTRY_DSN` | false, localhost:4318, — |
| **Plugins** | `PLUGIN_MAX_PACKAGE_SIZE`, `PLUGIN_MAX_EXECUTION_TIMEOUT` | 52MB, 600s |
| **Marketplace** | `MARKETPLACE_ENABLED`, `MARKETPLACE_API_URL` | true, marketplace.dify.ai |

The complete inventory exceeds **200 environment variables**. The `.env.example` file (53KB) is the canonical reference.

---

## 8. Health Checks

| Service | Method | Interval | Timeout | Retries |
|---|---|---|---|---|
| db_postgres | `pg_isready` | 1s | 3s | 30 (start 60) |
| db_mysql | `mysqladmin ping` | 1s | 3s | 30 |
| redis | `redis-cli ping` → PONG | 1s | 3s | — |
| sandbox | `curl localhost:8194/health` | — | — | — |
| weaviate | builtin | — | — | — |
| pgvector | `pg_isready` | 1s | 3s | 30 |
| milvus-standalone | `curl localhost:9091/healthz` | 30s | 20s | 3 (start 90s) |
| opensearch | cluster health API | — | — | — |
| elasticsearch | cluster health API | — | — | — |
| oceanbase | `obclient` query | 10s | 10s | 30 |
| seekdb | `mysql` ping | 5s | 5s | 60 |
| couchbase | bucket API | 10s | 10s | 10 |

**Notable:** The api, worker, worker_beat, web, nginx, plugin_daemon, and ssrf_proxy services have **no health checks** defined in compose. For production, you should add them.

---

## 9. Init Containers & First Boot

### init_permissions (busybox)
Runs once before api/worker start:
```bash
chown -R 1001:1001 /app/api/storage
# Creates .init_done flag to prevent re-runs
```
Required because the api container runs as non-root UID 1001.

### First Boot Sequence
1. `init_permissions` runs → completes
2. `db_postgres` starts → passes health check
3. `redis` starts
4. `api` starts → if `MIGRATION_ENABLED=true`, runs `flask upgrade-db` (Alembic migrations) before starting gunicorn
5. `worker`, `worker_beat` start (also run migrations if enabled)
6. `web`, `sandbox`, `ssrf_proxy`, `plugin_daemon` start
7. `nginx` starts last (depends on api + web)

`★ Insight ─────────────────────────────────────`
- Migrations are **opt-in** via `MIGRATION_ENABLED=true` and run inside the entrypoint.sh before the application server starts. This means the first API container to boot performs the migration while holding the database — there's no separate migration job or init container for this.
- A dedicated `MODE=migration` exists that runs migrations and exits — useful for CI/CD pipelines where you want migration as a separate step.
`─────────────────────────────────────────────────`

---

## 10. Database Migrations

- **Framework:** Alembic via Flask-Migrate
- **Migration count:** 157 versioned migration files
- **Model metadata source:** `models.base.TypeBase.metadata`
- **Naming convention:** `YYYY_MM_DD_HHMM-<revision>_<slug>.py`
- **Foreign keys:** Excluded from auto-generation

### Execution Methods

| Method | Command | Use Case |
|---|---|---|
| Auto on startup | `MIGRATION_ENABLED=true` in env | Default Docker deployment |
| Dedicated migration run | `MODE=migration` | CI/CD pipelines |
| Manual CLI | `flask upgrade-db` | Development |
| Job mode | `docker run -e MODE=job dify-api upgrade-db` | One-shot container |

---

## 11. Scaling Patterns

### Horizontal Scaling

| Component | How to Scale | Notes |
|---|---|---|
| **api** | Increase `SERVER_WORKER_AMOUNT` or run multiple containers behind nginx | Stateless; share storage volume or use S3 |
| **worker** | Increase `CELERY_WORKER_AMOUNT` or `CELERY_AUTO_SCALE=true` or run multiple containers | Each gets all queues by default; use `CELERY_WORKER_QUEUES` for queue-per-worker |
| **web** | Increase `PM2_INSTANCES` or run multiple containers | Stateless Next.js |
| **worker_beat** | **DO NOT scale** — must be exactly 1 | Duplicate beats = duplicate scheduled tasks |
| **sandbox** | Scale behind proxy | Each sandbox is stateless |
| **plugin_daemon** | Scale with care — shares plugin storage | Coordinate via shared storage |

### Celery Queue Architecture (Self-Hosted)
Queues: `dataset`, `priority_dataset`, `priority_pipeline`, `pipeline`, `mail`, `ops_trace`, `app_deletion`, `plugin`, `workflow_storage`, `conversation`, `workflow`, `schedule_poller`, `schedule_executor`, `triggered_workflow_dispatcher`, `trigger_refresh_executor`, `retention`

For Kubernetes, override per-pod: `CELERY_WORKER_QUEUES=dataset,pipeline` + `CELERY_WORKER_CONCURRENCY=4` + `CELERY_WORKER_POOL=gevent`

### Vertical Scaling
| Variable | Default | Tune For |
|---|---|---|
| `SQLALCHEMY_POOL_SIZE` | 30 | More concurrent DB connections |
| `SQLALCHEMY_MAX_OVERFLOW` | 10 | Burst DB connections |
| `SERVER_WORKER_CONNECTIONS` | 10 | Concurrent gevent greenlets per worker |
| `GUNICORN_TIMEOUT` | 200 | Long-running LLM requests |
| `GRAPH_ENGINE_MAX_WORKERS` | 10 | Parallel workflow execution |

### Resource Limits (from compose)
Only OpenSearch and Elasticsearch have explicit limits:
- **OpenSearch:** 2GB memory, ulimits memlock unlimited, nofile 65536
- **Elasticsearch:** 2GB memory, JVM `-Xms512m -Xmx1024m`
- **OceanBase:** `OB_MEMORY_LIMIT=6G`
- All other services: **no resource limits defined** — add them for production.

---

## 12. Kubernetes Support

**No Helm charts or K8s manifests** are included in the repository.

However, the entrypoint.sh has **built-in Kubernetes patterns**:

```bash
# Per-pod queue assignment
CELERY_WORKER_QUEUES=dataset,pipeline

# Per-pod concurrency
CELERY_WORKER_CONCURRENCY=4

# Per-pod pool type
CELERY_WORKER_POOL=gevent
```

### Community Helm Charts
The official Dify Helm chart is maintained separately at `langgenius/dify-helm`. This repo contains only Docker Compose.

### Recommended K8s Architecture
- **Deployments:** api (2+ replicas), web (2+ replicas), plugin_daemon
- **StatefulSets:** db_postgres, redis, vector_store
- **Separate worker Deployments** per queue group (e.g., `dataset-worker`, `pipeline-worker`)
- **Single-replica Deployment:** worker_beat (with leader election or `replicas: 1`)
- **Job/CronJob:** Migration (`MODE=migration`), backup scripts
- **PVCs:** database data, app storage, plugin storage

---

## 13. Backup & Restore

### No built-in backup tooling in the compose stack.

### Recommended Procedures

**PostgreSQL (critical):**
```bash
# Backup
docker exec dify-db_postgres-1 pg_dump -U postgres dify > dify_backup_$(date +%F).sql

# Restore
docker exec -i dify-db_postgres-1 psql -U postgres dify < dify_backup.sql
```

**Application Storage (critical):**
```bash
# Backup uploaded files
tar czf storage_backup_$(date +%F).tar.gz ./volumes/app/storage
```

**Vector Store** — depends on active profile:
- Weaviate: Backup API (`/v1/backups`)
- Qdrant: Snapshot API
- pgvector: `pg_dump` of the pgvector database
- Milvus: `milvus-backup` tool

**Redis** — generally recoverable, but for persistence:
```bash
docker exec dify-redis-1 redis-cli -a difyai123456 BGSAVE
cp ./volumes/redis/data/dump.rdb ./backups/
```

**Plugin Daemon:**
```bash
tar czf plugins_backup_$(date +%F).tar.gz ./volumes/plugin_daemon
```

---

## 14. Security Considerations

### Credentials That MUST Change
| Credential | Default | Location |
|---|---|---|
| `SECRET_KEY` | `sk-9f73s3ljTX...` | `.env` |
| `POSTGRES_PASSWORD` | `difyai123456` | `.env` |
| `REDIS_PASSWORD` | `difyai123456` | `.env` |
| `WEAVIATE_API_KEY` | `WVF5YThaHlk...` | `.env` |
| `PLUGIN_DAEMON SERVER_KEY` | `lYkiYYT6owG...` | `.env` |
| `OPENSEARCH_INITIAL_ADMIN_PASSWORD` | `Qazwsxedc!@#123` | `.env` |
| `CODE_EXECUTION_API_KEY` | `dify-sandbox` | `.env` |

### Network Security
- Sandbox is isolated on internal network; all egress through Squid SSRF proxy
- OpenSearch network is internal
- No services expose management ports externally by default (only `EXPOSE_*` vars)

### Container Security
- API and Web run as non-root (UID 1001)
- Sandbox runs with network restrictions + HTTP proxy enforcement

---

## 15. Compose Profiles

Activate profiles via `COMPOSE_PROFILES` in `.env`:

```bash
# Default (PostgreSQL + Weaviate)
COMPOSE_PROFILES=postgresql,weaviate

# MySQL + Qdrant
COMPOSE_PROFILES=mysql,qdrant

# PostgreSQL + Milvus (also starts etcd + minio)
COMPOSE_PROFILES=postgresql,milvus

# With SSL certificates
COMPOSE_PROFILES=postgresql,weaviate,certbot

# With document parsing
COMPOSE_PROFILES=postgresql,weaviate,unstructured
```

**Metadata DB profiles** (pick one): `postgresql` | `mysql`
**Vector store profiles** (pick one): `weaviate` | `qdrant` | `pgvector` | `pgvecto-rs` | `chroma` | `milvus` | `opensearch` | `elasticsearch` | `oceanbase` | `seekdb` | `oracle` | `couchbase` | `iris` | `opengauss` | `myscale` | `matrixone` | `vastbase`
**Optional profiles:** `certbot`, `unstructured`

---

This specification covers the complete Dify v1.11.4 Docker infrastructure across 27+ services, 200+ environment variables, 5 network segments, and 20+ persistent volume mounts. The system supports flexible database and vector store selection via compose profiles, has built-in Kubernetes worker patterns, and uses template-based Nginx configuration with optional SSL.
