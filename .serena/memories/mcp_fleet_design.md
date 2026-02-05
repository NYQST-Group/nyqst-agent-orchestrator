# MCP Fleet Design

## Common Backbone (7 layers)
All NYQST MCP servers share:
1. **Transport** — HTTP Streamable (prod) + stdio (dev/Claude Code)
2. **Auth** — API key (bootstrap), OAuth2/OIDC (production), service tokens (inter-MCP)
3. **Database** — Abstract DatabaseBackend (PostgreSQL, Oracle ADB, SQLite)
4. **Data Model** — Tenant, Principal, ApiKey, AccessPolicy, ToolDefinition, RunEvent, AuditLog
5. **Vector/RAG** — Abstract VectorStoreBackend (pgvector, Oracle AI Vector Search, OpenSearch, Qdrant)
6. **Agentic** — Tool execution pipeline (validate → policy → execute → log → return)
7. **Patterns** — NyqstMCPServer base class, @tool decorator, structured errors, health probes

## Server Fleet (Bootstrap = 4 servers)

| Server | Tools | Namespace | RAM | Phase |
|--------|-------|-----------|-----|-------|
| Platform MCP | 12 (bootstrap), 45 (full) | substrate.*, run.*, index.*, knowledge.*, document.*, claim.*, schema.* | 1-2 GB | 1 |
| Project Registry MCP | 4 | registry.* | 512 MB | 1 |
| Domain Model MCP | 8 | domain.* | 1-2 GB | 2 |
| Connector MCP (Slack) | 8 | connector.slack.* | 512 MB | 2 |
| RAG Service MCP | MERGED into Platform | — | — | — |
| Admin/Ops MCP | 10 | admin.* | — | Deferred |

## Key Design Files
- Backbone: `/Users/markforster/NYQST-MCP/research/cloud-mcp-infrastructure/common-mcp-architecture/`
- Specs: `/Users/markforster/NYQST-MCP/research/cloud-mcp-infrastructure/mcp-specifications/`
- Existing code: `/Users/markforster/NYQST-DevinForkByAnyMeans/nyqst-intelli-230126/src/intelli/mcp/`

## Oracle Cloud Deployment
- ARM VM (4 OCPU, 24 GB): Docker Compose with all MCP servers + Redis + Caddy
- Autonomous DB 1: Production (relational + vector + graph + JSON)
- Autonomous DB 2: Dev/staging
- Object Storage: 20 GB for artifacts
- Vault: 150 secrets for API keys/credentials
