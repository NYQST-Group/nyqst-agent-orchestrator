# Specification: Legacy Issue Sanitization (Clean Baseline)

## Overview
Before importing any legacy issues (V1/V2/V2M) into the new GitHub repository, we must physically sanitize the markdown files in the local filesystem. This track will parse the decisions made in the V4 Drop (`DECISION_REGISTER_V4.md`) and rewrite the legacy issue files to remove contradictions, ensuring a perfectly clean baseline.

## Functional Requirements
1. **Decision Mapping**: 
   - Parse `DECISION_REGISTER_V4.md` and map the 17 core decisions to the specific legacy markdown files they impact (e.g., finding all files mentioning `Recharts` and marking them for the `Plotly` override).
2. **File Rewriting**:
   - Programmatically (or manually via agent) rewrite the affected legacy `packs/*/issues/*.md` files.
   - Inject a clear `> V4 OVERRIDE:` blockquote at the top of any heavily modified issue so future developers understand why the original text was altered.
   - Strip out obsolete acceptance criteria that explicitly violate V4 architecture (e.g., removing references to Temporal scheduling).
3. **Consolidated Output**:
   - Produce a single, unified `staging_issues/` directory containing the final, clean markdown files ready for the `meta_f2b_bootstrap` track to blindly import into GitHub.

## Non-Functional Requirements
- **Non-Destructive Origin**: The original pack directories remain untouched as historical reference; the sanitized files are placed in a dedicated staging directory.