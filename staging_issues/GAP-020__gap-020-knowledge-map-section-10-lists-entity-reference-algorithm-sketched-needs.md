# [GAP-020] KNOWLEDGE-MAP Section 10 lists "Entity reference algorithm (sketched, needs edge cases: citations, tool outputs, deliverables)" as a needed-soon open thread. BL-016 covers the entity/citation substrate, but the exact deduplication algorithm (content-hash-based? URL-based? Both?), the algorithm for resolving inline citation identifiers to entity IDs in the GML output, and the behavior when an entity is referenced in both a deliverable and a tool output are not specified.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-020
- **Severity**: MEDIUM
- **Description**: KNOWLEDGE-MAP Section 10 lists "Entity reference algorithm (sketched, needs edge cases: citations, tool outputs, deliverables)" as a needed-soon open thread. BL-016 covers the entity/citation substrate, but the exact deduplication algorithm (content-hash-based? URL-based? Both?), the algorithm for resolving inline citation identifiers to entity IDs in the GML output, and the behavior when an entity is referenced in both a deliverable and a tool output are not specified.
- **Affected BL Items**: BL-016 (entity substrate), BL-009 (ReportRenderer — citation rendering)
- **Source Evidence**: KNOWLEDGE-MAP Section 10; orchestration-extract.md Section 1.4 (Entity schema)
- **Resolution**: Define the entity reference algorithm: (1) Primary deduplication key: SHA-256 of content; (2) Secondary: URL normalization for web sources; (3) Citation identifier: UUID assigned at entity creation, stored in entity.metadata.citation_identifier; (4) GML citation binding: `<gml-inlinecitation identifier="X"/>` resolved by looking up entity where `citation_identifier == X`; (5) Cross-type references: tool output entities and deliverable entities share the same table, differentiated by entity_type.
- **Owner Recommendation**: Backend track lead
- **Wave**: W1 — before BL-016 integration with BL-009

---

### GAP-021 — Error Handling Failure Modes Not Enumerated