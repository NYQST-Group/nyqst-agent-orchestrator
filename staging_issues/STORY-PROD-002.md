---
    key: STORY-PROD-002
    title: Observability baseline: structured logs + metrics + traces
    type: story
    milestone: M10 Production hardening
    labels: [phase:8-prod, priority:high, size:L, track:infra, type:story]
    ---

    ## Problem

    Without observability, debugging pipelines and runs becomes impossible.

    ## Proposed solution

    Add OpenTelemetry (or equivalent), structured logging, correlation IDs, and dashboards for key metrics.

    ## Dependencies

    - EPIC-PROD — Production hardening (deploy, security, observability, perf)

    ## Acceptance criteria

    - [ ] Every request has correlation id
- [ ] Runs have trace/span linkage
- [ ] Key metrics exported: ingest duration, run duration, SSE latency, error rates

    ## Test plan

    - [ ] Integration: metrics endpoint returns data
- [ ] Manual: trace appears in collector

    ## Notes / references

    _None_
