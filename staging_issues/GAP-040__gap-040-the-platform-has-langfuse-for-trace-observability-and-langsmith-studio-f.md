# [GAP-040] The platform has Langfuse for trace observability and LangSmith Studio for graph debugging. Neither of these is a production monitoring and alerting solution. There is no specification for: (1) application-level health monitoring (FastAPI health endpoint exists at `/health` but no uptime monitoring); (2) database monitoring (PostgreSQL connection pool exhaustion, replication lag); (3) arq worker monitoring (job queue depth, job failure rate); (4) SSE stream health (active connections, disconnection rate); (5) budget overrun alerting (when a tenant approaches their monthly quota).

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-040
- **Severity**: HIGH
- **Description**: The platform has Langfuse for trace observability and LangSmith Studio for graph debugging. Neither of these is a production monitoring and alerting solution. There is no specification for: (1) application-level health monitoring (FastAPI health endpoint exists at `/health` but no uptime monitoring); (2) database monitoring (PostgreSQL connection pool exhaustion, replication lag); (3) arq worker monitoring (job queue depth, job failure rate); (4) SSE stream health (active connections, disconnection rate); (5) budget overrun alerting (when a tenant approaches their monthly quota).
- **Affected BL Items**: BL-012 (billing alerts), BL-013 (quota alerts), cross-cutting
- **Source Evidence**: KNOWLEDGE-MAP Section 4 (DevOps & Observability — only lists Langfuse and LangSmith Studio); billing-metering-extract.md Section 7 (monthly invoice generation — no alerting on failure)
- **Resolution**: Define minimal v1 monitoring: (1) Uptime: use Langfuse health check endpoint + external uptime monitor (UptimeRobot free tier); (2) DB: pg_stat_statements for slow query detection; (3) arq: job failure rate logged to Langfuse trace; (4) Budget: add a webhook or email notification when tenant reaches 80% of monthly quota. Document in a new `docs/plans/OPERATIONS.md`.
- **Owner Recommendation**: DevOps track
- **Wave**: W1 — needed before staging deployment

---

### GAP-041 — No Developer Experience (DX) Tooling Spec