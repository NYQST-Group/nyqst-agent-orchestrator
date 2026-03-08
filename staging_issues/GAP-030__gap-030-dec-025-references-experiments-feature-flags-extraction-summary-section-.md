# [GAP-030] DEC-025 references experiments/feature flags. EXTRACTION-SUMMARY Section 6 (Feature Flags) confirms Superagent has `/api/feature-flags` and client-side evaluation endpoints. DEC-047 defers the clarification UI feature to v1.5 (presumably behind a feature flag). However, there is no decision specifying how v1 will implement feature flags: PostHog is excluded (DEC-064 uses Langfuse), and the DEC-025 entry is vague. The `streaming-events-extract.md` also makes no reference to a v1 feature flag mechanism.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-030
- **Severity**: MEDIUM
- **Description**: DEC-025 references experiments/feature flags. EXTRACTION-SUMMARY Section 6 (Feature Flags) confirms Superagent has `/api/feature-flags` and client-side evaluation endpoints. DEC-047 defers the clarification UI feature to v1.5 (presumably behind a feature flag). However, there is no decision specifying how v1 will implement feature flags: PostHog is excluded (DEC-064 uses Langfuse), and the DEC-025 entry is vague. The `streaming-events-extract.md` also makes no reference to a v1 feature flag mechanism.
- **Affected BL Items**: DEC-047 (clarification UI deferred implies a feature flag), future domain modules
- **Source Evidence**: EXTRACTION-SUMMARY Section 6; DEC-064 (no PostHog); DEC-025; DEC-047
- **Resolution**: Decide v1 feature flag mechanism. Options: (a) Tenant-level configuration in the database (simplest — `tenant.features JSONB`); (b) Langfuse experiment tracking (reuses existing observability); (c) Simple environment variable flags. Recommend option (a) for v1: add `features JSONB` column to tenants table in MIG-0005A.
- **Owner Recommendation**: Architecture lead — small decision with disproportionate downstream impact
- **Wave**: W0

---

### GAP-031 — Slides Generation Viewer Not Fully Specified