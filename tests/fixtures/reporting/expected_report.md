# Project Health Report - 2026-03-11

- Repository: `NYQST-Group/NYQST-DocuIntelli-Build`
- Total issues: `4`
- Open issues: `3`
- Milestones: `2`
- Branch protection enabled: `True`
- Required status checks: `Backend Tests, Lint`
- Reporting project board present: `False`
- Mock contract publisher present: `True`

## Latest Workflow Statuses
- `Backend Tests`: `success`
- `External Schema Publisher`: `failure`
- `Lint`: `success`

## Conductor Validation
- /tmp/repo/conductor/tracks/example_track/plan.md:3: task is complete but mapped issue #12 is OPEN

## Open P0 Issues
- [P0-004] Add tenant_id to core run tables

## Active Risks
- `HIGH` Conductor plan / issue drift detected: 1 validation issue(s) need correction. (sync-conductor validation)
- `HIGH` Workflow not green: External Schema Publisher: The latest recorded conclusion is 'failure'. (GitHub Actions)
- `HIGH` P0 stabilization work remains open: Open P0 items: [P0-004] Add tenant_id to core run tables (GitHub issues)
- `MEDIUM` Contract publisher is still mocked: The backstage schema publishing workflow still exits with a mock/incomplete implementation. (Workflow file)

## Notes
- Reporting remains repo-first; GitHub Project automation is intentionally deferred.
- GitHub issue closure remains governed by PR merge semantics, not local plan checkbox mutation.
