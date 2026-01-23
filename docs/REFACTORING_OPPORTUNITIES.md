# Refactoring Opportunities

Analysis of where we're reinventing the wheel and what battle-tested solutions could replace custom code.

## High-Impact Replacements

### 1. Content-Addressable Storage → hashfs

**Current**: Custom SHA-256 hashing and file organization in `storage/s3_storage.py`

**Better**: [hashfs](https://github.com/dgilland/hashfs) provides this out of the box.

```python
# Instead of custom implementation
from hashfs import HashFS
fs = HashFS('/data/artifacts', depth=4, width=1, algorithm='sha256')
address = fs.put(stream)  # Returns HashAddress with id (sha256)
```

**Effort**: Low | **Impact**: Medium (less code to maintain)

### 2. SSE Polling → PostgreSQL LISTEN/NOTIFY

**Current**: Polling loop in `api/v1/streams.py` that queries every 0.5s

**Better**: Native PostgreSQL pub/sub with zero polling:

```python
# Producer (in ledger_service.py after insert)
await connection.execute(f"NOTIFY run_events, '{json.dumps(event_data)}'")

# Consumer (in streams.py)
async def stream_events():
    await connection.execute("LISTEN run_events")
    async for notification in connection.notifications():
        yield f"data: {notification.payload}\n\n"
```

**Effort**: Medium | **Impact**: High (eliminates polling, true real-time)

### 3. Run Checkpointing → langgraph-checkpoint-postgres

**Current**: Custom `checkpoint_data` JSONB field in Run model

**Better**: LangGraph's native checkpointing handles state persistence:

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)
graph = workflow.compile(checkpointer=checkpointer)
# State automatically persisted per thread_id
```

**Effort**: Medium | **Impact**: High (robust state management, resume from any point)

### 4. Workflow Orchestration → Consider Prefect/Dagster

**Current**: Custom run ledger with manual state tracking

**Alternative**: Prefect for workflow orchestration:

```python
from prefect import flow, task

@task
def parse_document(artifact_sha: str):
    # Automatic logging, retries, caching
    pass

@flow
def ingest_flow(input_sha: str):
    result = parse_document(input_sha)
    return result
```

**Effort**: High | **Impact**: High (observability, retries, scheduling built-in)

**Trade-off**: Adds dependency but removes significant custom code. Consider for Phase 2.

## Medium-Impact Improvements

### 5. Frontend SSE → @microsoft/fetch-event-source

**Current**: Native EventSource with manual reconnection

**Better**: Microsoft's library handles reconnection, custom headers, POST:

```typescript
import { fetchEventSource } from '@microsoft/fetch-event-source';

fetchEventSource('/api/v1/streams/runs/' + runId, {
    onmessage(ev) { /* handle */ },
    onclose() { /* auto-reconnects */ },
    onerror(err) { /* with backoff */ },
});
```

**Effort**: Low | **Impact**: Medium (better reliability)

### 6. File Tree Component → react-arborist

**Current**: Custom TreeItem component in ExplorerPanel

**Better**: [react-arborist](https://github.com/brimdata/react-arborist) - virtualized, accessible:

```typescript
import { Tree } from 'react-arborist';

<Tree
  data={pointers}
  openByDefault={false}
  width={300}
  height={600}
  indent={24}
>
  {Node}
</Tree>
```

**Effort**: Low | **Impact**: Medium (virtualization for large trees)

### 7. SQLAlchemy + Pydantic → SQLModel

**Current**: Separate SQLAlchemy models and Pydantic schemas

**Alternative**: [SQLModel](https://sqlmodel.tiangolo.com/) combines both:

```python
from sqlmodel import SQLModel, Field

class Artifact(SQLModel, table=True):
    sha256: str = Field(primary_key=True)
    media_type: str
    size_bytes: int
    # Works as both ORM model AND Pydantic schema
```

**Effort**: High (migration) | **Impact**: Medium (less duplication)

**Recommendation**: Keep current approach, but use for new models.

## Lower Priority / Future Considerations

### 8. MinIO Bucket Notifications

Instead of polling for new artifacts, MinIO can push events:

```python
# Configure MinIO webhook to POST to /webhooks/artifacts
# Triggers on s]put events in the artifacts bucket
```

### 9. Background Jobs → ARQ with Redis

For long-running tasks (parsing, analysis):

```python
from arq import create_pool
from arq.connections import RedisSettings

async def parse_document(ctx, artifact_sha: str):
    # Long-running work
    pass

# Enqueue
redis = await create_pool(RedisSettings())
await redis.enqueue_job('parse_document', artifact_sha)
```

### 10. Document Parsing → Docling (Already Planned)

We've identified Docling but haven't integrated. Priority for Phase 1:

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert(source)
doc = result.document
# Access DocIR: doc.texts, doc.tables, doc.pictures
```

## Recommended Immediate Actions

1. **PostgreSQL LISTEN/NOTIFY** - Replace SSE polling (Day 1)
2. **langgraph-checkpoint-postgres** - Use for run state (Day 2)
3. **@microsoft/fetch-event-source** - Frontend SSE (Day 1)
4. **Docling integration** - Start document parsing (Week 1)

## Things We Got Right

- **react-resizable-panels** - Good choice for IDE-like layout
- **TanStack Query** - Excellent for server state
- **Zustand** - Appropriate for UI state
- **FastAPI + SQLAlchemy 2.0** - Solid foundation
- **Content-addressed + pointer model** - DVC-inspired, correct architecture
- **Append-only ledger** - Right pattern for auditability

## Architecture Decisions to Preserve

1. **Immutable artifacts** - Never change, only add
2. **Mutable pointers** - HEAD references, not content
3. **Run ledger** - Append-only event stream
4. **Schema-on-read** - Accept flexible structures
5. **MCP tools** - Agent-first API surface
