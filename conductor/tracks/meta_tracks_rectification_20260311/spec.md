# Specification: Tracks 1-4 Rectification & Repo-First Reporting

## Objective
Correct the historical record for Tracks 1-4 while preserving the validated work that is actually present as of March 11, 2026. The corrective scope records what truly landed, removes misleading automation claims, and establishes deterministic repo-local reporting and provenance artifacts.

## Validated Current State
1. The private GitHub repository exists and uses `main` as the default branch.
2. The issue import is materially landed, with milestones present in GitHub.
3. Branch protection is enabled on `main` with required status checks.
4. CI workflows, env templates, and Docker Compose configuration are present and structurally valid.
5. The `staging_issues/` directory remains the authoritative sanitized issue corpus.

## Deliverables
1. Annotate Tracks 1-4 with rectification notes and corrected metadata statuses.
2. Reframe `sync-conductor.sh` as a read-only validator that fails loudly on drift or mapping gaps.
3. Add a repo-first reporting MVP that emits dated Markdown and JSON health reports plus `RISK_REGISTER.md`.
4. Add sanitization provenance manifests for materially rewritten staged issues.
5. Preserve the branch-protection failure/recovery path in a repo-local incident note.

## Non-Goals
1. Do not backfill `tenant_id` into the core data model in this track.
2. Do not provision or mutate a GitHub Project V2 board in this track.
3. Do not retrofit inline `> V4 OVERRIDE:` banners into the authoritative staged issue text.
