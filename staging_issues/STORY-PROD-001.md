---
    key: STORY-PROD-001
    title: Containerize API + worker (Dockerfiles, entrypoints)
    type: story
    milestone: M10 Production hardening
    labels: [phase:8-prod, priority:high, size:M, track:infra, type:story]
    ---

    ## Problem

    Production deploy requires consistent runtime; local-first is insufficient.

    ## Proposed solution

    Add Dockerfiles for API and worker, and production compose/k8s manifests as chosen.

    ## Dependencies

    - EPIC-PROD — Production hardening (deploy, security, observability, perf)

    ## Acceptance criteria

    - [ ] docker build for api and worker succeeds
- [ ] Containers run against external services
- [ ] Health endpoints and readiness checks exist

    ## Test plan

    - [ ] CI: docker build job

    ## Notes / references

    _None_
