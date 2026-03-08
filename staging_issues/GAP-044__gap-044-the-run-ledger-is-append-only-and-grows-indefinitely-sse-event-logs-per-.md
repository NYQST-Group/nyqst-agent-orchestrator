# [GAP-044] The run ledger is append-only and grows indefinitely. SSE event logs per run include the full NDJSON event stream (stored as `event_stream_artifact_id` per the Message schema). Langfuse traces accumulate. There is no documented data retention policy (how long are runs kept, how long are events kept, when are artifacts purged), no backup schedule for the PostgreSQL primary, and no disaster recovery plan.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-044
- **Severity**: LOW
- **Description**: The run ledger is append-only and grows indefinitely. SSE event logs per run include the full NDJSON event stream (stored as `event_stream_artifact_id` per the Message schema). Langfuse traces accumulate. There is no documented data retention policy (how long are runs kept, how long are events kept, when are artifacts purged), no backup schedule for the PostgreSQL primary, and no disaster recovery plan.
- **Affected BL Items**: BL-012 (billing records must be retained for audit), cross-cutting
- **Source Evidence**: billing-metering-extract.md (UsageRecord table — billing audit requires long retention); streaming-events-extract.md (event_stream_artifact_id — event logs stored); no retention policy in any document
- **Resolution**: Define a minimal v1 data retention policy: (1) Run ledger events: 90 days active, 1 year cold storage; (2) Billing records: 7 years (regulatory requirement); (3) Langfuse traces: 30 days (consistent with DEC-045 Langfuse plan); (4) Daily PostgreSQL backups via `pg_dump` to S3/MinIO; (5) Weekly backup restore tests. Add to `docs/plans/OPERATIONS.md`.
- **Owner Recommendation**: DevOps track
- **Wave**: W2 — before production deployment

---

### GAP-045 — Slice Structure Plan (CLAUDE.md Team Briefs) Not Created