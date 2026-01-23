# Intelli - Agent-First Document Intelligence Platform

An agent-first platform for document intelligence, research workflows, and knowledge management with full provenance tracking and governance.

## Core Principles

1. **Single source of truth**: Immutable artifacts + manifests + run ledger
2. **Ephemeral compute, persistent outputs**: Sessions are disposable; outputs are published into substrate
3. **Schema-on-read first, promote later**: Accept agent-discovered structures; promote stable ones to schemas
4. **Everything inspectable**: Agent work is structured events + artifacts, not chat logs
5. **Pointers not mutations**: Reversion is moving pointers (Git-like), not rewriting records
6. **Policy-driven governance**: Provenance/gates/permissions driven by policy templates

## Architecture

### Backbone Objects (Stable Kernel)

- **Artifact**: Immutable content-addressed blob (SHA-256)
- **Manifest**: Immutable tree of artifact/manifest references
- **Pointer**: Mutable HEAD reference (bundle_head, corpus_head)
- **Run**: Execution instance with full event logging
- **RunEvent**: Append-only ledger entry for reproducibility

### Module Map

```
Storage/Substrate → Execution/Run Ledger → Knowledge System
       ↓                    ↓                    ↓
   Artifacts            Run Events          KB Indices
   Manifests           Checkpoints         Retrieval Profiles
   Pointers            Tool Calls          Evidence Spans
```

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- PostgreSQL 16+ with pgvector extension

### Development Setup

```bash
# Clone repository
git clone <repo-url>
cd nyqst-intelli-230126

# Start infrastructure
docker compose up -d

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the API server
python -m intelli.main
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Artifacts
- `POST /api/v1/artifacts` - Upload artifact
- `GET /api/v1/artifacts/{sha256}` - Get artifact metadata
- `GET /api/v1/artifacts/{sha256}/content` - Download content
- `GET /api/v1/artifacts/{sha256}/url` - Get pre-signed URL

### Manifests
- `POST /api/v1/manifests` - Create manifest
- `GET /api/v1/manifests/{sha256}` - Get manifest
- `GET /api/v1/manifests/{sha256}/entries` - Get entries
- `GET /api/v1/manifests/{sha256}/history` - Get history chain
- `GET /api/v1/manifests/{old}/diff/{new}` - Compare manifests

### Pointers
- `POST /api/v1/pointers` - Create pointer
- `GET /api/v1/pointers/{namespace}/{name}` - Get pointer
- `GET /api/v1/pointers/{namespace}/{name}/resolve` - Resolve to manifest
- `PUT /api/v1/pointers/{id}/advance` - Advance HEAD
- `GET /api/v1/pointers/{id}/history` - Get change history

### Runs
- `POST /api/v1/runs` - Create run
- `GET /api/v1/runs/{id}` - Get run
- `POST /api/v1/runs/{id}/start` - Start run
- `POST /api/v1/runs/{id}/complete` - Complete run
- `GET /api/v1/runs/{id}/events` - Get run ledger events

## MCP Tools (for Agents)

The platform exposes MCP tools for agent integration:

### Substrate Tools
- `list_pointers` - List pointers in namespace
- `resolve_pointer` - Get current manifest SHA-256
- `checkout_manifest` - Get manifest entries
- `create_manifest` - Create new manifest
- `advance_pointer` - Publish changes
- `get_artifact_info` - Get artifact metadata
- `get_artifact_url` - Get download URL

### Run Tools
- `create_run` - Create execution instance
- `start_run` / `complete_run` / `fail_run` - Lifecycle
- `log_step` - Log step events
- `log_tool_call` - Log tool calls
- `checkpoint` - Save resumable state
- `get_run_events` - Query ledger

## Technology Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0
- **Database**: PostgreSQL 16+ with pgvector
- **Storage**: S3-compatible (MinIO for dev, AWS S3 for prod)
- **Agent Framework**: LangGraph
- **Document Parsing**: Docling
- **Protocol**: MCP (Model Context Protocol)

## Project Structure

```
src/intelli/
├── api/              # HTTP API endpoints
│   └── v1/           # API version 1
├── core/             # Cross-cutting concerns
├── db/               # Database layer
│   └── models/       # SQLAlchemy models
├── repositories/     # Data access layer
├── services/         # Business logic
│   ├── substrate/    # Artifact/manifest/pointer services
│   ├── runs/         # Run and ledger services
│   ├── docir/        # Document IR (Phase 1)
│   ├── knowledge/    # Knowledge bases (Phase 2)
│   └── governance/   # Approvals/policies (Phase 2)
├── schemas/          # Pydantic models
├── storage/          # Storage backends
├── mcp/              # MCP server and tools
│   └── tools/        # Tool definitions
└── agents/           # LangGraph agents
    └── graphs/       # Workflow definitions
```

## Development Roadmap

### Phase 0: Substrate + Run Trace ✅
- [x] Artifact store (content-addressed)
- [x] Manifest store (immutable trees)
- [x] Pointer service (mutable HEADs)
- [x] Run ledger (append-only events)
- [x] HTTP API
- [x] MCP tools

### Phase 1: Research + Analysis
- [ ] Document parsing with Docling
- [ ] DocIR intermediate representation
- [ ] Evidence spans and citations
- [ ] Research session workflows
- [ ] Analysis runs

### Phase 2: KB + Governance
- [ ] Knowledge base indexing
- [ ] Retrieval profiles
- [ ] Corpus promotion workflows
- [ ] Approval gates
- [ ] Diff and degradation hooks

### Phase 3: Business Integration
- [ ] Connector framework
- [ ] Slack/Monday/HubSpot integrations
- [ ] Admin console
- [ ] Quotas and billing

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=intelli

# Run specific test file
pytest tests/integration/api/test_artifacts.py
```

## License

Proprietary
