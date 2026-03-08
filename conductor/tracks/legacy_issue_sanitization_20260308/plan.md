# Implementation Plan: Legacy Issue Sanitization

## Phase 1: Mapping & Discovery (Week 1) [checkpoint: 342cd37]
- [x] Task: Map V4 Decisions to Legacy Issues b6fa16a
  - [x] Sub-task: Grep all V1/V2/V2M issues for known deprecated tech (e.g., Recharts, Temporal, Ory, PostHog)
  - [x] Sub-task: Create a mapping document (`V4_OVERRIDE_TARGETS.md`) listing exactly which markdown files need V4 overrides
- [x] Task: Conductor - User Manual Verification 'Phase 1: Mapping & Discovery' (Protocol in workflow.md) 342cd37

## Phase 2: Staging & Rewriting (Week 1)
- [x] Task: Create Clean Staging Directory bb159e1
  - [x] Sub-task: Copy all `packs/*/issues/*.md` and `*.json` into a single, unified `staging_issues/` directory
- [x] Task: Apply V4 Overrides to Files ca8bb89
  - [x] Sub-task: Write a script to prepend `> V4 OVERRIDE: [DEC-V4-XXX]` blocks to the mapped files in the staging directory
  - [x] Sub-task: Manually review and cleanse files with complex structural changes (e.g., the Migration 0005 splits)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Staging & Rewriting' (Protocol in workflow.md)

## Phase 3: Validation & Output (Week 1)
- [ ] Task: Validate the unified staging set
  - [ ] Sub-task: Run JSON schema validation on the resulting issue set to ensure the import scripts won't fail
  - [ ] Sub-task: Confirm no `GAP-` tickets are left without their V4 resolution attached
- [ ] Task: Update Bootstrap Track Dependency
  - [ ] Sub-task: Modify the `meta_f2b_bootstrap` track to pull issues from the new `staging_issues/` directory instead of the old raw pack folders.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Validation & Output' (Protocol in workflow.md)