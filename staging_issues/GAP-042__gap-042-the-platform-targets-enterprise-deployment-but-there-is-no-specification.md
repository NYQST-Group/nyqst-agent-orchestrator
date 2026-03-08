# [GAP-042] The platform targets enterprise deployment but there is no specification for a staging environment. The only documented environments are local development (docker-compose) and production (implied). For a $200k/yr enterprise product, buyers will require sandbox testing against a non-production instance. Stripe itself requires test-mode integration before going live. Without a staging environment spec, every integration (Stripe, Langfuse, search providers) is validated in production.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-042
- **Severity**: MEDIUM
- **Description**: The platform targets enterprise deployment but there is no specification for a staging environment. The only documented environments are local development (docker-compose) and production (implied). For a $200k/yr enterprise product, buyers will require sandbox testing against a non-production instance. Stripe itself requires test-mode integration before going live. Without a staging environment spec, every integration (Stripe, Langfuse, search providers) is validated in production.
- **Affected BL Items**: BL-012 (Stripe — must be tested in test mode first), BL-013
- **Source Evidence**: billing-metering-extract.md Section 10.3 (Stripe CLI testing); KNOWLEDGE-MAP (no staging reference); PLATFORM-FRAMING.md (enterprise target)
- **Resolution**: Define a staging environment specification: (1) Same docker-compose setup as production with `ENVIRONMENT=staging` flag; (2) Separate Stripe test-mode API keys; (3) Separate Langfuse instance or project; (4) Reduced resource allocation (single Postgres, no Neo4j); (5) Data reset capability (for demo purposes). Add to `docs/plans/OPERATIONS.md`.
- **Owner Recommendation**: DevOps track
- **Wave**: W1

---

### GAP-043 — Multi-Tenant Data Isolation Not Specified for v1