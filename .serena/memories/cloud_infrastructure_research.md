# Cloud Infrastructure Research — Session Context

## Date: 2026-01-29

## What Was Done
Comprehensive research into cloud infrastructure for NYQST MCP platform bootstrap (pre-funding, £0/month).

## Research Output Location
`/Users/markforster/NYQST-MCP/research/cloud-mcp-infrastructure/` — 47 files, 748 KB

### Executive Design Document
`NYQST-MCP-INFRASTRUCTURE-DESIGN.md` — the ONE document to read for the full picture.

### Folder Structure
- `oracle-plan/` (7 files) — Primary bootstrap platform: ARM VM + converged Autonomous DB
- `gcp-free-tier/` (5 files) — Serverless supplement evaluation
- `aws-free-tier/` (5 files) — Always-free evaluation (unsuitable for bootstrap)
- `azure-free-tier/` (5 files) — Multi-model DB evaluation
- `common-mcp-architecture/` (10 files) — 7-layer MCP backbone design (Opus)
- `mcp-specifications/` (10 files) — 6 MCP server specs, 72+ tools
- `CLOUD-COMPARISON-SUMMARY.md` — 4-provider comparison
- `REVIEW-MCP-PLUGIN-EXPERT.md` — B+ grade, MCP protocol gaps identified
- `REVIEW-CODE-ARCHITECT.md` — B+ grade, simplification needed

## Key Decisions Made
1. **Oracle Cloud Always Free** is the bootstrap platform (4 OCPU, 24 GB ARM + 2 Autonomous DBs)
2. **Oracle Autonomous DB** replaces PostgreSQL + OpenSearch + Neo4j + Qdrant (converged: relational + vector + graph + JSON)
3. **4-server bootstrap** (not 6): Platform MCP, Project Registry, Domain Model, Connector (Slack)
4. **RAG Service merged into Platform MCP** (eliminated duplication)
5. **Admin/Ops MCP deferred** to post-bootstrap
6. **GCP supplement** for serverless (Cloud Run, Pub/Sub, Firebase Auth)

## Critical Review Findings
- MCP architecture only uses Tools — missing Resources and Prompts
- RAM budget (27-42 GB full fleet) exceeds Oracle free tier (24 GB)
- LangGraph-MCP bridge unspecified — needs ADR-011 before coding
- Oracle ADB limited to 3-6 concurrent connections — needs Redis caching
- 45 Platform tools too many for bootstrap — ship 12 core tools first

## ADRs Pending (not yet written)
- **ADR-010**: Bootstrap Infrastructure (Oracle Cloud)
- **ADR-011**: LangGraph-MCP Bridge
- **ADR-012**: MCP Server Decomposition
- **ADR-004 update**: Add Oracle backend adapter
- **ADR-008 update**: Add MCP Resources + Prompts, fix transport spec

## Git State
- NYQST-MCP: branch `feature/adr-updates-from-cloud-research`, research committed at `f543aca`
- nyqst-intelli: branch `feature/adr-updates-cloud-infrastructure`, Serena memories committed at `361bd23`
- Both branches created for safe rollback
