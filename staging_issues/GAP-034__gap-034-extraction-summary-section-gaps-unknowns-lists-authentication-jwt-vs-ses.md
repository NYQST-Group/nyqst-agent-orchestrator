# [GAP-034] EXTRACTION-SUMMARY Section (Gaps/Unknowns) lists "Authentication: JWT vs session cookies unclear from bundle." The Superagent bundle shows `/api/session/redeem-token` and `credentials: include` on SSE requests, suggesting cookie-based sessions. NYQST uses JWT + API keys (confirmed in PLATFORM-GROUND-TRUTH). If Superagent's session-redeem pattern is something NYQST needs to replicate for enterprise SSO or shared workspace access, the design gap is unclear.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-034
- **Severity**: MEDIUM
- **Description**: EXTRACTION-SUMMARY Section (Gaps/Unknowns) lists "Authentication: JWT vs session cookies unclear from bundle." The Superagent bundle shows `/api/session/redeem-token` and `credentials: include` on SSE requests, suggesting cookie-based sessions. NYQST uses JWT + API keys (confirmed in PLATFORM-GROUND-TRUTH). If Superagent's session-redeem pattern is something NYQST needs to replicate for enterprise SSO or shared workspace access, the design gap is unclear.
- **Affected BL Items**: Enterprise Shell layer (Layer 3 — post-v1)
- **Source Evidence**: EXTRACTION-SUMMARY Section (Gaps/Unknowns); streaming-events-extract.md (Frontend Event Consumption, credentials: include)
- **Resolution**: Assess whether Superagent's token-redeem pattern has a v1 analog in NYQST. If enterprise SSO is deferred (it is — per PLATFORM-FRAMING.md Layer 3), this gap is post-v1. Document as a known unknown in the Enterprise Shell layer specifications.
- **Owner Recommendation**: Product lead — scope clarification
- **Wave**: W3 — post-v1 enterprise shell

---

### GAP-035 — Superagent SSO Details Not Recovered