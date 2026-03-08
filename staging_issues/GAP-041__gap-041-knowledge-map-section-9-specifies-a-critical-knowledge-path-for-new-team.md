# [GAP-041] KNOWLEDGE-MAP Section 9 specifies a "Critical Knowledge Path" for new team members (Day 1: read PLATFORM-FRAMING.md, etc.) but this is reading-based onboarding. There is no specification for: (1) a local development setup guide (`make dev` or equivalent); (2) database seeding scripts for local testing; (3) LangSmith Studio integration for local graph debugging; (4) Langfuse local instance for local trace observation; (5) mock data for development that doesn't require live API keys (Brave, Stripe).

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-041
- **Severity**: MEDIUM
- **Description**: KNOWLEDGE-MAP Section 9 specifies a "Critical Knowledge Path" for new team members (Day 1: read PLATFORM-FRAMING.md, etc.) but this is reading-based onboarding. There is no specification for: (1) a local development setup guide (`make dev` or equivalent); (2) database seeding scripts for local testing; (3) LangSmith Studio integration for local graph debugging; (4) Langfuse local instance for local trace observation; (5) mock data for development that doesn't require live API keys (Brave, Stripe).
- **Affected BL Items**: All BL items — affects all developer velocity
- **Source Evidence**: KNOWLEDGE-MAP Section 9 (Critical Knowledge Paths — reading-based only); CONSISTENCY-AUDIT-PLANS SC-01 (arq verification task implies no existing setup verification)
- **Resolution**: Create a `docs/plans/DEVELOPER-SETUP.md` that specifies: (1) prerequisites check script; (2) `docker-compose up` sequence and validation; (3) database initialization command; (4) test data seeding; (5) local Langfuse + LangSmith Studio startup; (6) `.env.example` with all required variables. This is a 4-hour task that pays for itself in the first week of multi-track development.
- **Owner Recommendation**: Any senior engineer; should be done during P0
- **Wave**: W0

---

### GAP-042 — No Staging Environment Specification