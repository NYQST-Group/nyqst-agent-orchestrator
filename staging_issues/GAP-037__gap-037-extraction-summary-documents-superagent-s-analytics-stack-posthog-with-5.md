# [GAP-037] EXTRACTION-SUMMARY documents Superagent's analytics stack: PostHog with 5 modules (recorder, surveys, web vitals, dead-click detection, exception tracking), GA4 with 5 properties, Facebook/Twitter/LinkedIn pixels. NYQST v1 uses Langfuse for observability (DEC-037) and explicitly excludes PostHog (DEC-064). This is the correct strategic choice for a B2B enterprise platform, but the gap in behavioral analytics (session recording, funnel analysis, product analytics) is not quantified or planned for.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-037
- **Severity**: LOW
- **Description**: EXTRACTION-SUMMARY documents Superagent's analytics stack: PostHog with 5 modules (recorder, surveys, web vitals, dead-click detection, exception tracking), GA4 with 5 properties, Facebook/Twitter/LinkedIn pixels. NYQST v1 uses Langfuse for observability (DEC-037) and explicitly excludes PostHog (DEC-064). This is the correct strategic choice for a B2B enterprise platform, but the gap in behavioral analytics (session recording, funnel analysis, product analytics) is not quantified or planned for.
- **Affected BL Items**: Enterprise Shell Layer 3 (analytics and notifications)
- **Source Evidence**: EXTRACTION-SUMMARY Section (Analytics Stack); DEC-064; PLATFORM-FRAMING.md
- **Resolution**: Accept the gap for v1. Document in STRATEGIC-REVIEW that product analytics (session recording, funnels) is a Layer 3 Enterprise Shell concern and will be addressed when the enterprise billing tier requires product-led growth tooling. This is an acceptable deferred risk for a $200k/yr sales-led enterprise motion.
- **Owner Recommendation**: Product lead
- **Wave**: W3 — post-v1

---

## Category 5: Operational Gaps

### GAP-038 — No CI/CD Pipeline for the Platform