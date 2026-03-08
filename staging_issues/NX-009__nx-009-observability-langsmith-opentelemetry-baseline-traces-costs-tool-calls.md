# [NX-009] Observability: LangSmith + OpenTelemetry baseline (traces, costs, tool calls)

**Goal**
- End-to-end trace visibility for:
  - agent runs
  - tool calls
  - retrieval
  - deliverable generation
- Costs attributed per run + per tenant.

**Implementation**
1. Add LangSmith instrumentation to LangGraph execution (traces + metadata).
2. Add OpenTelemetry SDK (FastAPI + DB + Redis) for infra-level spans.
3. Correlate:
   - trace_id ↔ run_id ↔ tenant_id
4. Surface minimal “Trace” link in UI run view.

**Acceptance criteria**
- A run produces a LangSmith trace containing:
  - model calls, tool calls, retrieval spans
- A run view shows a working trace link (in dev at least).

