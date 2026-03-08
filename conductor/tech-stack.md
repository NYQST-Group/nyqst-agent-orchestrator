# Tech Stack

## Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL 16+ with pgvector, SQLAlchemy 2.0 (async), Alembic
- **Agent Framework**: LangGraph, LangChain, MCP (Model Context Protocol)
- **Background Jobs/Caching**: Redis, arq

## Frontend
- **Language**: TypeScript, React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand, React Query
- **UI Components**: Radix UI

## Infrastructure & Storage
- **Storage**: S3-compatible (MinIO/AWS S3) via aioboto3
- **Observability**: OpenTelemetry, Langfuse