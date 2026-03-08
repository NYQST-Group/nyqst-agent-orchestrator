# [GAP-027] KNOWLEDGE-MAP Section 10 lists "Neo4j Aura free tier limits → upgrade/fallback plan" as an external dependency TBD. ADR-010 specifies Neo4j Aura free for graph domain ontologies. The free tier has storage limits (typically 200K nodes, 400K relationships, 50MB storage on the free plan). If the platform's domain ontologies for PropSygnal/RegSygnal exceed these limits, the free tier will fail without warning. No fallback plan (upgrade to paid, self-hosted Neo4j, or alternative graph DB) is documented.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-027
- **Severity**: MEDIUM
- **Description**: KNOWLEDGE-MAP Section 10 lists "Neo4j Aura free tier limits → upgrade/fallback plan" as an external dependency TBD. ADR-010 specifies Neo4j Aura free for graph domain ontologies. The free tier has storage limits (typically 200K nodes, 400K relationships, 50MB storage on the free plan). If the platform's domain ontologies for PropSygnal/RegSygnal exceed these limits, the free tier will fail without warning. No fallback plan (upgrade to paid, self-hosted Neo4j, or alternative graph DB) is documented.
- **Affected BL Items**: Domain modules (PropSygnal, RegSygnal) — not current v1 backlog but risk
- **Source Evidence**: KNOWLEDGE-MAP Section 10; KNOWLEDGE-MAP Section 3 (Infrastructure & Storage)
- **Resolution**: Assess Neo4j Aura free tier limits against the domain ontology data volume expected for v1 research module (likely well within limits). Document the fallback plan if exceeded: (1) Upgrade to Neo4j AuraDB Professional; (2) Self-hosted Neo4j Docker container. Add as a risk note in STRATEGIC-REVIEW.
- **Owner Recommendation**: DevOps / architecture lead
- **Wave**: W1 — low urgency for v1 research module; higher urgency for domain modules

---

### GAP-028 — No Migration 0005 Specification