# ADR-002: Code Generation and Contract Strategy

**Status:** Proposed  
**Date:** 2026-01-26  
**Deciders:** Mark Forster, Engineering Team  
**PRD Reference:** [06_ARCHITECTURE.md](../prd/06_ARCHITECTURE.md)

---

## Context

NYQST needs a strategy for generating APIs, types, methods, and contracts to avoid writing everything from scratch. The question is which frameworks and tools to adopt for:

1. **API Definition & Generation** - How do we define and generate API endpoints?
2. **Type Safety** - How do we ensure type safety across Python backend and TypeScript frontend?
3. **Database Schema** - How do we manage database schemas and migrations?
4. **Contract Enforcement** - How do we ensure contracts between services are honored?

The current stack is:
- **Backend:** Python (FastAPI, Pydantic, SQLAlchemy, Alembic)
- **Frontend:** TypeScript (React, Vite)
- **Database:** PostgreSQL

---

## Decision

Adopt a **schema-first, code-generation** approach using the following tools:

| Concern | Tool | Rationale |
|---------|------|-----------|
| **API Definition** | OpenAPI (via FastAPI) | FastAPI auto-generates OpenAPI spec from Pydantic models |
| **Backend Types** | Pydantic | Already in use; provides runtime validation + type hints |
| **Frontend Types** | openapi-typescript | Generate TypeScript types from OpenAPI spec |
| **API Client** | openapi-fetch or custom | Type-safe fetch client from OpenAPI spec |
| **Database Schema** | SQLAlchemy + Alembic | Already in use; migrations are version-controlled |
| **Event Contracts** | JSON Schema or AsyncAPI | For event-driven communication (future) |

---

## Recommended Toolchain

### 1. API Types: OpenAPI → TypeScript

**Flow:**
```
Pydantic Models (Python)
        ↓
FastAPI generates OpenAPI spec
        ↓
openapi-typescript generates TypeScript types
        ↓
Frontend uses generated types
```

**Tools:**
- `openapi-typescript` - Generates TypeScript types from OpenAPI 3.x spec
- `openapi-fetch` - Type-safe fetch client that uses generated types

**Benefits:**
- Single source of truth (Pydantic models)
- Type errors caught at compile time in frontend
- API changes automatically reflected in frontend types

**Implementation:**
```bash
# Generate types from running API
npx openapi-typescript http://localhost:8000/openapi.json -o ui/src/types/api-generated.ts

# Or from saved spec file
npx openapi-typescript docs/openapi.json -o ui/src/types/api-generated.ts
```

### 2. Database Types: SQLAlchemy → Pydantic

**Current approach (already in place):**
- SQLAlchemy models define database schema
- Pydantic schemas define API contracts
- Manual mapping between them

**Potential improvement:**
- `sqlmodel` - Combines SQLAlchemy and Pydantic (single model for both)
- Trade-off: Less flexibility, but less duplication

**Recommendation:** Keep current approach (separate SQLAlchemy and Pydantic) for flexibility. The duplication is manageable and provides clear separation between persistence and API concerns.

### 3. Event Contracts: JSON Schema or AsyncAPI

**For future event-driven communication:**
- Define event schemas in JSON Schema
- Generate validators for both Python and TypeScript
- Consider AsyncAPI for full event API documentation

**Tools:**
- `jsonschema` (Python) - Validate against JSON Schema
- `ajv` (TypeScript) - Validate against JSON Schema
- `datamodel-code-generator` - Generate Pydantic models from JSON Schema

### 4. MCP Tool Contracts

**For MCP tools:**
- Define tool schemas using JSON Schema (MCP standard)
- Generate TypeScript types for tool inputs/outputs
- Validate tool calls at runtime

---

## Options Considered

### Option 1: Manual Everything

**Description:** Write all types, APIs, and contracts manually.

**Pros:**
- Full control
- No tooling dependencies

**Cons:**
- Duplication between backend and frontend
- Type drift over time
- More maintenance burden

### Option 2: GraphQL + Code Generation

**Description:** Use GraphQL with code generation (graphql-codegen).

**Pros:**
- Excellent type generation
- Strong ecosystem
- Flexible queries

**Cons:**
- Requires rewriting API layer
- Different paradigm from REST
- Overkill for current needs

### Option 3: tRPC

**Description:** End-to-end typesafe APIs without code generation.

**Pros:**
- No code generation step
- Excellent DX
- Type inference across stack

**Cons:**
- Requires Node.js backend (not Python)
- Would require significant rewrite

### Option 4: OpenAPI + Code Generation (Selected)

**Description:** Use FastAPI's OpenAPI generation + TypeScript code generation.

**Pros:**
- Works with existing stack
- Industry standard (OpenAPI)
- Incremental adoption
- Single source of truth (Pydantic)

**Cons:**
- Requires build step for type generation
- OpenAPI spec can get large

---

## Decision Rationale

Option 4 (OpenAPI + Code Generation) was chosen because:

1. **Existing stack compatibility:** FastAPI already generates OpenAPI specs from Pydantic models. No backend changes needed.

2. **Incremental adoption:** Can add type generation without changing existing code. Start with new endpoints, migrate old ones over time.

3. **Industry standard:** OpenAPI is widely understood and supported. Easy to share API specs with external parties.

4. **Single source of truth:** Pydantic models are the source of truth. Types flow from backend to frontend automatically.

---

## Implementation Plan

### Phase 1: Setup (Immediate)

1. Add npm script to generate TypeScript types:
   ```json
   {
     "scripts": {
       "generate:api-types": "openapi-typescript http://localhost:8000/openapi.json -o ui/src/types/api-generated.ts"
     }
   }
   ```

2. Add to CI pipeline to ensure types are up-to-date

3. Create typed API client wrapper using generated types

### Phase 2: Adoption (Ongoing)

1. Use generated types in new frontend code
2. Migrate existing API calls to use typed client
3. Add pre-commit hook to regenerate types if Pydantic models change

### Phase 3: Events (Future)

1. Define event schemas in JSON Schema
2. Generate validators for Python and TypeScript
3. Consider AsyncAPI for documentation

---

## Consequences

### Positive

- Type safety across full stack
- Single source of truth for API contracts
- Automatic documentation via OpenAPI
- Reduced manual type maintenance

### Negative

- Additional build step for type generation
- Need to keep generated types in sync
- Learning curve for team

### Risks

- **Risk:** Generated types get out of sync with API
  - **Mitigation:** CI check that regenerates types and fails if diff exists

- **Risk:** OpenAPI spec becomes unwieldy
  - **Mitigation:** Organize endpoints into tags; consider splitting spec for large APIs

---

## Related ADRs

- [ADR-001: Data Model Strategy](./001-data-model-strategy.md)

---

## References

- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [openapi-fetch](https://github.com/drwpow/openapi-typescript/tree/main/packages/openapi-fetch)
- [FastAPI OpenAPI](https://fastapi.tiangolo.com/tutorial/first-steps/#openapi)
- [AsyncAPI](https://www.asyncapi.com/)
- [JSON Schema](https://json-schema.org/)
