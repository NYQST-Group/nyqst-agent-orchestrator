# CLAUDE.md — NYQST Intelli

## Project Overview

NYQST Intelli is a deterministic agentic infrastructure platform for commercial intelligence. It provides AI-powered document processing, knowledge management, and analysis for commercial real estate (PropSygnal) and regulatory compliance (RegSygnal).

**Company:** NYQST AI Limited (pre-funding startup)
**Core concept:** "Strong kernel / weak periphery" — rigid backbone for provenance, sessions, runs, indexing; extensible domain content.

## Tech Stack

### Backend (Python 3.12+)
- **FastAPI** + **uvicorn** — web framework
- **SQLAlchemy 2.0 async** + **asyncpg** — ORM + PostgreSQL driver
- **Alembic** — migrations
- **pgvector** — vector storage
- **LangGraph** + **LangChain** — agent orchestration + LLM integration
- **MCP SDK (mcp>=1.2.0)** — Model Context Protocol server
- **Pydantic v2** — schemas and settings
- **structlog** — structured logging
- **Redis + arq** — caching and background jobs
- **Docling** — document processing

### Frontend (TypeScript)
- **React** + **Vite** + **Tailwind CSS** + **Radix UI** (shadcn pattern)
- **Zustand** — state management

### Infrastructure (dev)
- **PostgreSQL 16 + pgvector** — `docker compose up -d`
- **MinIO** — S3-compatible object storage
- **OpenSearch 2.18** — hybrid search
- **Redis 7** — optional (`--profile full`)
- **Langfuse** — optional (`--profile observability`)

### Infrastructure (production target)
- **Oracle Cloud Always Free** — ARM VM (4 OCPU, 24 GB) + 2 Autonomous DBs
- Oracle Autonomous DB replaces PostgreSQL + OpenSearch (converged: relational + vector + graph + JSON)
- See `~/NYQST-MCP/research/cloud-mcp-infrastructure/` for full plan

## Code Structure

```
src/intelli/
├── core/          # Logging, security, cache, config, exceptions, pubsub
├── db/            # Engine, base model, SQLAlchemy models (substrate, auth, rag, runs)
├── repositories/  # Async data access (artifacts, manifests, pointers, runs)
├── services/      # Business logic (substrate, knowledge/RAG, indexing, runs, audit, governance)
├── api/           # FastAPI routes (/api/v1/*) and middleware (auth, errors, correlation)
├── mcp/           # MCP server + tools (substrate, run, knowledge) + resources
├── schemas/       # Pydantic schemas (substrate, rag, agent, runs)
├── storage/       # Object storage abstraction (local, S3/MinIO)
├── agents/        # LangGraph agent definitions and graphs
├── config.py      # Settings from environment
└── main.py        # Application entry point
```

## Commands

```bash
# Infrastructure
docker compose up -d                              # Start PostgreSQL + MinIO + OpenSearch
docker compose --profile full up -d               # Include Redis
docker compose --profile observability up -d       # Include Langfuse

# Install
pip install -e ".[dev]"

# Run
uvicorn intelli.main:app --reload --port 8000     # API server
python -m intelli.mcp.server                       # MCP server (stdio)

# Database
alembic upgrade head                               # Apply migrations
alembic revision --autogenerate -m "description"   # New migration

# Quality
ruff check src/ tests/                             # Lint
ruff format src/ tests/                            # Format
mypy src/                                          # Type check (strict)
pytest                                             # Tests
pytest --cov=src/intelli                           # Coverage

# Validation
bash scripts/dev/validate.sh                       # Full validation
python scripts/dev/smoke_api.py                    # API smoke test
```

## Code Style

- **Ruff**: Python 3.12 target, line length 100, rules: E, F, I, N, W, UP, B, C4, SIM
- **mypy**: strict mode with pydantic plugin
- **Async everywhere**: all DB/HTTP operations use async/await
- **Repository pattern**: data access in `repositories/`, business logic in `services/`
- **Pydantic v2**: all API schemas
- **MCP tool naming**: `{domain}.{resource}.{action}` (e.g., `substrate.pointer.list`)
- **No hardcoded secrets**: use environment variables / .env

## Architecture Decisions (ADRs)

All ADRs in `docs/adr/`:

| ADR | Decision |
|-----|----------|
| **001** | Domain-first data model, CDM as integration layer only |
| **002** | Code generation from Pydantic schemas → TypeScript |
| **003** | Virtual team architecture for agents |
| **004** | Contract-first Index Service (`ingest/search/explain`), profile-driven, swappable backends (pgvector, OpenSearch, Oracle) |
| **005** | LangGraph agent runtime with checkpointing |
| **006** | Session-workspace architecture (ephemeral compute, persistent outputs) |
| **007** | Document processing pipeline (Docling → canonical DocIR) |
| **008** | MCP as primary tool protocol, namespaced tools, execution pipeline |
| **009** | Human-in-the-loop governance (interrupts, approval gates) |

### Pending ADRs (from cloud infrastructure research)
- **010**: Bootstrap Infrastructure — Oracle Cloud Always Free
- **011**: LangGraph-MCP Bridge — how LangGraph state maps to MCP sessions
- **012**: MCP Server Decomposition — 4-server bootstrap fleet

### ADRs needing update
- **004**: Add Oracle Autonomous DB as third Index Service backend
- **008**: Add MCP Resources + Prompts (not just Tools), fix transport spec

## Task Completion Checklist

Before committing:
1. `ruff check src/ tests/` passes
2. `ruff format src/ tests/` applied
3. `mypy src/` passes (strict)
4. `pytest` passes
5. No hardcoded secrets
6. Async consistency maintained
7. New API inputs/outputs use Pydantic models
8. DB model changes have Alembic migration
9. New MCP tools use namespaced naming and go in `src/intelli/mcp/tools/`
10. Update this file's Pending ADRs section if ADRs are written

## Related Resources

| Resource | Location |
|----------|----------|
| **MCP Infrastructure Research** | `~/NYQST-MCP/research/cloud-mcp-infrastructure/` |
| **Executive Design Doc** | `~/NYQST-MCP/research/cloud-mcp-infrastructure/NYQST-MCP-INFRASTRUCTURE-DESIGN.md` |
| **PRD (10 docs)** | `docs/prd/` |
| **Platform Reference Design** | `docs/PLATFORM_REFERENCE_DESIGN.md` |
| **Research Synthesis** | `docs/RESEARCH_SYNTHESIS.md` |
| **Build Plan** | `docs/planning/BUILD_PLAN_V2.md` |
| **Serena Memories** | `.serena/memories/` (10 files — project context for Serena sessions) |

## Serena Integration

This project is registered with Serena. On session start:
1. Activate project: `activate_project("nyqst-intelli-230126")`
2. Check onboarding: `check_onboarding_performed()` — should return "already performed"
3. Read relevant memories based on your task (e.g., `pending_work`, `architecture_decisions`)
4. After completing work, update `pending_work` memory with what was done/added
