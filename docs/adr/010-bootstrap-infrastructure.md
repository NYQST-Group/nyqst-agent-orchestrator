# ADR-010: Bootstrap Infrastructure — PostgreSQL + pgvector + Neo4j

**Status:** Proposed
**Date:** 2026-02-04
**Deciders:** Mark Forster
**PRD Reference:** [03_PLATFORM.md - Infrastructure](../prd/03_PLATFORM.md)
**Supersedes:** Draft Oracle Cloud ADR in NYQST-MCP repo

---

## Context

NYQST requires production-grade infrastructure to support:

1. **Platform MCP** — Conversations, sessions, artifacts, manifests, run ledger, RAG
2. **Domain Model MCP** — ISDA CDM, CRE ontologies, regulatory taxonomies (graph queries)
3. **Project Registry MCP** — GitHub-fed project inventory
4. **Connector MCPs** — External system integrations (Slack, etc.)

### Constraints

- **£0/month budget** during pre-funding bootstrap
- **Solo/small team** — minimal operational overhead
- **Must be real cloud infrastructure** — not localhost
- **Architecture must scale** without re-platforming when funded

### Key Insight from Dify Research

Analysis of Dify v1.11.4 (production RAG platform with 80 database tables, 565 API routes) revealed:

> **Dify runs production with PostgreSQL + pgvector + Redis only.**

Dify does NOT use:
- Neo4j or any graph database
- OpenSearch or Elasticsearch (uses pgvector for hybrid search)
- Qdrant or Milvus (pgvector is sufficient)

This validates a simpler approach than the original Oracle converged database proposal.

### Why Graph is Still Needed

Unlike Dify, NYQST has domain-specific requirements:
- **ISDA CDM entity navigation** — regulatory domain model with complex relationships
- **CRE ontologies** — commercial real estate entity graphs
- **domain.navigate, domain.trace tools** — graph traversal for knowledge queries

Graph capability is required but can be **isolated to Domain Model MCP** as a separate service.

---

## Decision

Adopt a **purpose-fit services** approach with service-specific storage:

| MCP Server | Storage | Managed Option | Self-Hosted Option |
|------------|---------|----------------|-------------------|
| **Platform MCP** | PostgreSQL + pgvector | Supabase / Neon | Docker Compose |
| **Domain Model MCP** | Neo4j | Neo4j Aura (free tier) | Docker Compose |
| **Project Registry MCP** | PostgreSQL (shared) | Same as Platform | Same as Platform |
| **Connector MCP** | Stateless | — | — |
| **Cache/Queue** | Redis | Upstash | Docker Compose |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Platform MCP                                                    │
│  ├── PostgreSQL + pgvector (Supabase/Neon)                      │
│  │   ├── conversations, sessions, messages                      │
│  │   ├── artifacts, manifests, pointers                         │
│  │   ├── runs, run_events (ledger)                              │
│  │   └── rag_chunks (embeddings)                                │
│  └── Redis (Upstash)                                            │
│      └── cache, Celery queues                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Domain Model MCP  (separate service, separate DB)              │
│  └── Neo4j Aura (free tier: 50K nodes, 175K relationships)      │
│      ├── ISDA CDM entities and relationships                    │
│      ├── CRE ontologies                                         │
│      └── Regulatory taxonomies                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Project Registry MCP                                            │
│  └── PostgreSQL (shared with Platform)                          │
│      └── projects, repos, sync state                            │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Pattern

```
Agent calls domain.query_ontology
       │
       ▼
┌─────────────────┐      MCP call      ┌─────────────────┐
│  Platform MCP   │ ─────────────────► │ Domain Model MCP │
│  (orchestrates) │                    │ (Neo4j Aura)     │
└─────────────────┘                    └─────────────────┘
```

---

## Options Considered

### Option 1: Oracle Cloud Always Free (Original Proposal)

**Description:** Single converged database (Oracle Autonomous DB) providing relational + vector + graph + JSON capabilities on Oracle's permanently free tier.

**Pros:**
- Single database for all workloads (operational simplicity)
- 4 ARM OCPUs, 24 GB RAM free forever
- 20 GB storage included
- SQL/PGQ for property graphs

**Cons:**
- Significant learning curve (Oracle-specific: ORDS, SQL/PGQ, AI Vector Search)
- ARM-specific Docker images required
- Capacity shortages in popular regions
- Idle VM reclamation risk (CPU must be >20% at p95)
- Lock-in to Oracle ecosystem
- Dify research shows converged DB is overkill — PostgreSQL + pgvector handles the workload

### Option 2: PostgreSQL + pgvector + Neo4j (Selected)

**Description:** Purpose-fit services with managed free tiers — PostgreSQL for relational/vector, Neo4j for graph.

**Pros:**
- Proven at scale (Dify validates PostgreSQL + pgvector approach)
- Generous free tiers (Supabase 500MB, Neo4j Aura 50K nodes)
- Standard tooling, no learning curve
- Each MCP server owns its storage (clean boundaries)
- Easy local development (Docker Compose)
- Portable to any cloud when funded

**Cons:**
- Two databases to manage instead of one
- Neo4j Aura free tier has limits (50K nodes)
- Need to coordinate schema migrations across services

### Option 3: PostgreSQL + Apache AGE (Deferred)

**Description:** Add graph capability via PostgreSQL extension (Apache AGE) instead of separate Neo4j.

**Pros:**
- Single database technology
- Cypher query support
- No additional managed service

**Cons:**
- AGE is less mature than Neo4j
- Mixing graph and relational in one DB may complicate scaling
- Less tooling/ecosystem support

**Status:** Viable future option if Neo4j Aura limits are hit.

---

## Decision Rationale

1. **Dify validates PostgreSQL + pgvector** — A production system with similar scope runs successfully without Oracle, Neo4j, or dedicated vector DBs for RAG workloads.

2. **Graph is genuinely needed but isolatable** — ISDA CDM and ontology navigation require graph queries, but this capability belongs in Domain Model MCP only. Separation allows independent scaling and technology choice.

3. **Free tier availability** — Supabase (500MB PostgreSQL), Neon (512MB), and Neo4j Aura (50K nodes) provide sufficient capacity for bootstrap without cost.

4. **Operational simplicity** — Managed services reduce ops burden for a solo/small team compared to self-hosting Oracle on ARM VMs.

5. **No lock-in** — Standard PostgreSQL and Neo4j are portable to any cloud.

---

## Consequences

### Positive

- Zero infrastructure cost during bootstrap
- Proven technology stack validated by Dify at scale
- Clean separation between Platform and Domain Model storage
- Standard tooling, minimal learning curve
- Easy local development with Docker Compose

### Negative

- Two databases to manage instead of one
- Neo4j Aura free tier limited to 50K nodes (sufficient for bootstrap)
- Need separate backup/restore procedures per service

### Risks

| Risk | Mitigation |
|------|------------|
| Neo4j Aura free tier limit reached | Monitor usage; Apache AGE as fallback; paid tier when funded |
| Supabase/Neon free tier limit reached | Monitor usage; self-host PostgreSQL as fallback |
| Service coordination complexity | Clear MCP boundaries; each server owns its storage |

---

## Implementation Notes

### Phase 1: Platform MCP (Immediate)

1. Provision Supabase project (or Neon database)
2. Run Alembic migrations for existing schema
3. Configure pgvector extension for RAG chunks
4. Deploy Redis via Upstash (or Railway)

### Phase 2: Domain Model MCP (When Needed)

1. Provision Neo4j Aura free instance
2. Design ontology schema (ISDA CDM, CRE)
3. Implement `domain.*` MCP tools with Cypher queries
4. Configure MCP-to-MCP communication pattern

### Local Development

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: dev

  neo4j:
    image: neo4j:5-community
    ports: ["7474:7474", "7687:7687"]
    environment:
      NEO4J_AUTH: neo4j/devpassword

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

---

## Related ADRs

- [ADR-004: Index Service Architecture](./004-index-service-architecture.md) — Uses pgvector backend
- [ADR-008: MCP Tool Architecture](./008-mcp-tool-architecture.md) — Domain Model MCP tools
- [ADR-006: Session Workspace Architecture](./006-session-workspace-architecture.md) — PostgreSQL storage

---

## References

- [Dify Infrastructure Analysis](../../research/dify-analysis/01-infrastructure.md)
- [NYQST vs Dify Comparison](../../research/dify-analysis/COMPARISON-NYQST-VS-DIFY.md)
- [Supabase Free Tier](https://supabase.com/pricing)
- [Neo4j Aura Free Tier](https://neo4j.com/cloud/aura-free/)
- [pgvector Extension](https://github.com/pgvector/pgvector)
