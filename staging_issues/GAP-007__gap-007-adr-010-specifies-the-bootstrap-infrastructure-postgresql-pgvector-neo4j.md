# [GAP-007] ADR-010 specifies the bootstrap infrastructure: PostgreSQL + pgvector + Neo4j + Redis. The DECISION-REGISTER has no infrastructure decision. DEC-037 mentions Langfuse self-hosted but not the database or cache infrastructure. A team member tasked with environment setup has no single locked decision to point to for infrastructure.

_Source: reference/gaps/COMPREHENSIVE-GAP-ANALYSIS.md_

## Details

- **ID**: GAP-007
- **Severity**: MEDIUM
- **Description**: ADR-010 specifies the bootstrap infrastructure: PostgreSQL + pgvector + Neo4j + Redis. The DECISION-REGISTER has no infrastructure decision. DEC-037 mentions Langfuse self-hosted but not the database or cache infrastructure. A team member tasked with environment setup has no single locked decision to point to for infrastructure.
- **Affected BL Items**: All BL items (infrastructure is cross-cutting)
- **Source Evidence**: hypothesis-consistency.md H2 gap 3
- **Resolution**: Add a decision "Bootstrap Infrastructure: PostgreSQL 16+ + pgvector 0.8+ (RDBMS and vector search dev), Neo4j Aura free (domain ontologies), Redis 7+ (cache, arq queue, profiles: full), MinIO (S3-compatible object storage, dev). Sourced from ADR-010." This is a documentation task; the infrastructure is already in docker-compose.yml.
- **Owner Recommendation**: DevOps / infrastructure track
- **Wave**: W0

---

### GAP-008 — Stale Claims Not Corrected in Source Documents