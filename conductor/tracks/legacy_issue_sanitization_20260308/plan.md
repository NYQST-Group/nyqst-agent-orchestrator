# Implementation Plan: Legacy Issue Sanitization

## Rectification Note
Validated on March 11, 2026 and partially superseded by `meta_tracks_rectification_20260311`. The staging work and import readiness checks landed, but provenance was weaker than planned because the authoritative staged issues do not retain inline `V4 OVERRIDE` headers. That gap is closed via `staging_issues/SANITIZATION_MANIFEST.md` and `staging_issues/SANITIZATION_MANIFEST.json`.

## Phase 1: Mapping & Discovery (Week 1) [checkpoint: 342cd37]
- [x] Task: Map V4 Decisions to Legacy Issues b6fa16a
  - [x] Sub-task: Grep all V1/V2/V2M issues for known deprecated tech (e.g., Recharts, Temporal, Ory, PostHog)
  - [x] Sub-task: Create a mapping document (`V4_OVERRIDE_TARGETS.md`) listing exactly which markdown files need V4 overrides
- [x] Task: Conductor - User Manual Verification 'Phase 1: Mapping & Discovery' (Protocol in workflow.md) 342cd37

## Phase 2: Staging & Rewriting (Week 1) [checkpoint: ff12ead]
- [x] Task: Create Clean Staging Directory bb159e1
  - [x] Sub-task: Copy all `packs/*/issues/*.md` and `*.json` into a single, unified `staging_issues/` directory
- [x] Task: Apply V4 Overrides to Files ca8bb89
  - [~] Sub-task: Record V4 override provenance for the mapped files in the staging audit manifest
  - [x] Sub-task: Manually review and cleanse files with complex structural changes (e.g., the Migration 0005 splits)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Staging & Rewriting' (Protocol in workflow.md) ff12ead

## Phase 3: Validation & Output (Week 1) [checkpoint: 39e78c4]
- [x] Task: Validate the unified staging set 0c0e20e
  - [x] Sub-task: Run JSON schema validation on the resulting issue set to ensure the import scripts won't fail
  - [x] Sub-task: Confirm no `GAP-` tickets are left without their V4 resolution attached
- [x] Task: Update Bootstrap Track Dependency acf591c
  - [x] Sub-task: Modify the `meta_f2b_bootstrap` track to pull issues from the new `staging_issues/` directory instead of the old raw pack folders.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Validation & Output' (Protocol in workflow.md) 39e78c4
