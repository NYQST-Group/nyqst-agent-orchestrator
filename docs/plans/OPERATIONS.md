---
document_id: OPERATIONS
version: 1
date: 2026-03-14
status: DRAFT — specifications for v1 deployment operational concerns
gaps_resolved: GAP-025, GAP-040, GAP-042, GAP-044
---

# Operations Plan — NYQST DocuIntelli v1

This document specifies the operational requirements for NYQST DocuIntelli v1: Langfuse deployment, monitoring and alerting, staging environment, and data retention. It consolidates operational decisions that were identified as gaps (GAP-025, GAP-040, GAP-042, GAP-044) during the consistency audit phase.

---

## 1. Langfuse Self-Hosted Deployment (GAP-025)

**Decision**: DEC-045 locks Langfuse self-hosted (MIT license) for observability and billing data.

### Container Resource Requirements

| Service | CPU | RAM | Storage |
|---------|-----|-----|---------|
| Langfuse web | 0.5 vCPU | 512 MB | — |
| Langfuse worker | 0.5 vCPU | 512 MB | — |
| Langfuse PostgreSQL | 0.5 vCPU | 512 MB | 10 GB |
| Langfuse Redis | 0.25 vCPU | 256 MB | — |

These fit within Oracle Cloud Always Free tier (4 vCPU, 24 GB RAM total).

### Docker Compose Profile

Langfuse runs under the `observability` profile in `docker-compose.yml`. Start with:

```bash
docker compose --profile observability up -d
```

### Data Retention Policy

| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Traces (LLM calls) | 30 days active | Sufficient for debugging; Langfuse default |
| Run events | 90 days active | Operational debugging window |
| Billing usage records | 7 years | Regulatory audit requirement |
| Langfuse experiments | 90 days | Sprint-scoped; clean up per cycle |

### Backup Schedule

- **Daily**: `pg_dump` of Langfuse PostgreSQL to MinIO/S3 at 02:00 UTC
- **Weekly**: Restore test from most recent backup (automated, reports to ops channel)
- Retention of backups: 30 days rolling

### REST API Access for Billing

The FastAPI backend queries the Langfuse REST API for billing data export:

```
GET https://langfuse.internal/api/public/observations
  ?type=GENERATION
  &userId={tenant_id}
  &fromStartTime={period_start}
  &toStartTime={period_end}
```

Response is aggregated by `run_id` (stored as Langfuse `traceId`) to compute per-run token usage and cost. See `billing-metering-extract.md` Section 4.2 for full integration pattern.

---

## 2. Monitoring and Alerting (GAP-040)

**v1 minimal monitoring specification.**

### 2.1 Application Health

| Signal | Tool | Threshold |
|--------|------|-----------|
| API uptime | UptimeRobot (free tier) polls `/health` every 5 min | Alert if down >2 min |
| Response time | UptimeRobot | Alert if p95 >5s |
| 5xx error rate | Langfuse trace error tags | Alert if >5% over 15 min |

### 2.2 Database Monitoring

| Signal | Method | Threshold |
|--------|--------|-----------|
| Slow queries | `pg_stat_statements` — log queries >500ms | Review weekly |
| Connection pool exhaustion | Log `asyncpg` pool exhausted events | Alert immediately |
| Disk usage | Docker volume monitor | Alert at 80% capacity |

### 2.3 ARQ Worker Monitoring

| Signal | Method | Threshold |
|--------|--------|-----------|
| Job failure rate | Log failed jobs to Langfuse trace with `level=ERROR` | Alert if >3 failures/hour |
| Queue depth | `redis.llen(arq:queue:default)` logged every 60s | Alert if >50 pending jobs |
| Worker health | `/health/workers` endpoint returning worker process status | Alert if worker not seen in >5 min |

**Note**: The arq `WorkerSettings.functions` initialization bug (GAP-023) must be fixed before worker monitoring is meaningful. See GAP-023 for the fix.

### 2.4 SSE Stream Health

| Signal | Method | Threshold |
|--------|--------|-----------|
| Active connections | Prometheus counter on `streams.py` connect/disconnect | Log only in v1 |
| Disconnection rate | Log premature disconnects (client gone before `run_complete`) | Alert if >20%/hour |

### 2.5 Budget / Quota Alerting

| Trigger | Action |
|---------|--------|
| Tenant reaches 80% of monthly run quota | Send email notification to tenant admin |
| Tenant reaches 100% of quota | Block new runs; return 402 with quota exceeded message |
| Single run exceeds $2.00 hard limit (DEC-045) | LangGraph conditional edge to END; emit `budget_exceeded` RunEvent |

Email notification uses SendGrid (or equivalent SMTP provider). Template stored in `src/intelli/core/notifications.py`.

---

## 3. Staging Environment (GAP-042)

### Environment Configuration

| Config | Local Dev | Staging | Production |
|--------|-----------|---------|------------|
| `ENVIRONMENT` | `development` | `staging` | `production` |
| Stripe keys | Test mode (`sk_test_*`) | Test mode (`sk_test_*`) | Live mode (`sk_live_*`) |
| Langfuse project | `nyqst-local` | `nyqst-staging` | `nyqst-production` |
| OpenAI API key | Dev key | Staging key (rate limited) | Production key |
| PostgreSQL | Local Docker | Staging DB (reduced size) | Production DB |
| Neo4j | Local Docker | None (not needed in staging) | Aura free |
| Redis | Local Docker | Staging Redis | Production Redis |

### Staging Infrastructure

- Same `docker-compose.yml` as development with `ENVIRONMENT=staging`
- Reduced resource allocation: single PostgreSQL (no replication), no Neo4j (domain modules not active)
- Data reset capability: `make staging-reset` truncates all non-billing tables and re-seeds demo data
- Stripe test webhooks: configure Stripe CLI to forward to staging webhook endpoint

### Demo Data Reset

```bash
# Reset staging to clean demo state
make staging-reset

# What this does:
# 1. Truncates: runs, messages, artifacts, manifests, run_events
# 2. Preserves: tenants, subscriptions (Stripe test mode)
# 3. Re-seeds: demo tenant, demo user, sample conversations
```

### Access

Staging URL: `https://staging.nyqst.internal` (internal network only in v1).
No public staging URL in v1 — enterprise buyer demos use production with demo tenant.

---

## 4. Data Retention Policy (GAP-044)

### Retention Schedule

| Data | Active Retention | Cold Storage | Delete After |
|------|-----------------|--------------|--------------|
| Run events (ledger) | 90 days in PostgreSQL | 1 year in MinIO as NDJSON | 1 year + 1 day |
| SSE event stream artifacts | 90 days in MinIO | — | 90 days |
| Billing usage records | 7 years in PostgreSQL | — | Never (audit) |
| Stripe webhook logs | 90 days | — | 90 days |
| Langfuse traces | 30 days (Langfuse internal) | — | 30 days |
| User-uploaded documents | Until tenant deletes or account closed | — | On tenant deletion |
| Generated artifacts (reports, websites) | Until tenant deletes | — | On tenant deletion |

**Regulatory note**: Billing records (usage_records table, Stripe logs) are retained 7 years per UK financial services record-keeping requirements (FCA COBS 11.8.5).

### Backup Schedule

| Target | Frequency | Method | Retention |
|--------|-----------|--------|-----------|
| PostgreSQL primary | Daily at 02:00 UTC | `pg_dump` to MinIO | 30 days rolling |
| MinIO artifacts | Weekly | MinIO replication to secondary bucket | 90 days |
| Langfuse PostgreSQL | Daily at 03:00 UTC | `pg_dump` to MinIO | 30 days rolling |

### Backup Restore Testing

- Weekly automated restore test of most recent PostgreSQL backup
- Results logged to `ops/backup-restore-log.md`
- Alert if restore test fails

### Right to Deletion (GDPR)

- Tenant deletion: cascade delete all runs, messages, artifacts, usage records, and user data
- Exception: billing records retained 7 years even after tenant deletion (regulatory requirement)
- Implementation: soft-delete flag on `tenants` table; background job purges non-billing data after 30-day grace period

---

## 5. Open Items

| Item | Status | Wave |
|------|--------|------|
| Langfuse docker-compose profile implementation | Not started | W0 |
| CI pipeline (GAP-038) | Not started — tracked separately | W0 |
| UptimeRobot account setup | Not started | W1 |
| Email notification service (SendGrid) | Not started | W1 |
| Staging environment setup | Not started | W1 |
| Backup automation scripts | Not started | W2 |
| Right-to-deletion background job | Not started | W2 |

---

*Created: 2026-03-14. Resolves GAP-025 (Langfuse deployment spec), GAP-040 (monitoring spec), GAP-042 (staging environment spec), GAP-044 (data retention policy).*
