---
    key: STORY-PROD-004
    title: Backup/restore + retention policy runbook
    type: story
    milestone: M10 Production hardening
    labels: [phase:8-prod, priority:medium, size:M, track:infra, type:story]
    ---

    ## Problem

    Production requires recovery. Without backups, data loss is fatal.

    ## Proposed solution

    Define backup strategy for Postgres and object storage; write runbook; test restore to staging.

    ## Dependencies

    - EPIC-PROD — Production hardening (deploy, security, observability, perf)

    ## Acceptance criteria

    - [ ] Automated backups configured (staging)
- [ ] Restore procedure documented and tested
- [ ] Retention policy defined for runs/events/artifacts

    ## Test plan

    - [ ] Manual: restore drill in staging

    ## Notes / references

    _None_
