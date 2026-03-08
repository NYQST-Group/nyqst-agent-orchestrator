# EPIC-OBS — Observability, evals, and production readiness

- Type: **epic**
- Milestone: `M6-OBS`
- Repo alignment: **partial**
- Labels: `milestone:M6`, `quality`

## Problem

Complex agentic systems fail silently without tracing, metrics, and continuous evals. Repo has an evals folder but needs wiring into CI and runtime instrumentation (LangSmith/Langfuse/OTel).

## Proposed solution

Standardize logging/metrics/tracing, wire evals into CI/CD, and add reliability guardrails (timeouts, retries, circuit breakers) so production incidents are diagnosable and regressions are caught early.

## Acceptance criteria

- Tracing provider configurable; runs include trace IDs; key tool/LLM calls are trace-linked.
- Evals run in CI on a small golden set; failures block merges.
- Operational dashboards exist for latency, error rates, cost/usage, and queue depth.

## Test plan

- Smoke test: tracing enabled emits spans; eval harness can run headlessly.
- Load test: run streaming stays stable under N concurrent runs (define N).
