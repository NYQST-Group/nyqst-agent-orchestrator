---
    key: EPIC-PROD
    title: Production hardening (deploy, security, observability, perf)
    type: epic
    milestone: M10 Production hardening
    labels: [phase:8-prod, priority:critical, size:XL, track:infra, type:epic]
    ---

    ## Problem

    Without hardening, the system cannot be deployed safely or operated reliably.

    ## Proposed solution

    Containerize, add observability, rate limits, backup/restore, security scanning, and deploy runbooks.

    ## Dependencies

    - EPIC-DOCUMENTS — Document management (bundles, versions, ingest, diff)
- EPIC-STUDIO — Studio (notebook + infinite canvas) with provenance
- EPIC-APPS — Apps system (Dify-style) + context packs + runs
- EPIC-MODELS — Models + validation + impact diffs
- EPIC-WORKFLOWS — Workflow builder + triggers + schedules (n8n-like)

    ## Acceptance criteria

    - [ ] Staging deploy is automated and repeatable
- [ ] Health checks, rollbacks, and migrations are safe
- [ ] Observability covers API, pipelines, and runs
- [ ] Security baseline controls are implemented
- [ ] Performance smoke tests meet minimum SLOs

    ## Test plan

    - [ ] Load smoke test in staging
- [ ] Security scan gates in CI
- [ ] Disaster recovery drill (backup/restore) documented

    ## Notes / references

    _None_
