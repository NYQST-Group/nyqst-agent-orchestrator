"""Server-Sent Events (SSE) streaming endpoints for real-time updates.

Uses PostgreSQL LISTEN/NOTIFY for true real-time push notifications
instead of polling. This is much more efficient and provides
sub-millisecond latency for event delivery.

These endpoints enable the UI to receive real-time updates for:
- Run events (steps, tool calls, completions)
- Pointer changes (publish/promote)
- Global activity feed
"""

import asyncio
import json
from typing import Annotated, AsyncGenerator, Optional
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from intelli.api.dependencies import SessionDep
from intelli.config import settings
from intelli.services.runs.ledger_service import LedgerService

router = APIRouter(prefix="/streams", tags=["streams"])


async def _get_listen_connection() -> asyncpg.Connection:
    """Get a dedicated connection for LISTEN.

    LISTEN requires a persistent connection, separate from the
    connection pool used for regular queries.
    """
    db_url = str(settings.database_url).replace("postgresql+asyncpg://", "postgresql://")
    return await asyncpg.connect(db_url)


async def _run_event_generator_notify(
    run_id: UUID,
    initial_events: list = None,
) -> AsyncGenerator[str, None]:
    """Generate SSE events using PostgreSQL LISTEN/NOTIFY.

    True real-time - events are pushed immediately when they occur.
    """
    # Send initial connection event
    yield f"event: connected\ndata: {json.dumps({'run_id': str(run_id)})}\n\n"

    # Send any initial/historical events
    if initial_events:
        for event in initial_events:
            event_data = {
                "id": event.id,
                "run_id": str(event.run_id),
                "event_type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat(),
                "duration_ms": event.duration_ms,
                "sequence_num": event.sequence_num,
            }
            yield f"event: run_event\ndata: {json.dumps(event_data)}\n\n"

    # Connect to PostgreSQL for LISTEN
    conn: Optional[asyncpg.Connection] = None
    try:
        conn = await _get_listen_connection()

        # Queue for notifications
        queue: asyncio.Queue = asyncio.Queue()

        def notification_handler(connection, pid, channel, payload):
            """Handle incoming notifications."""
            try:
                data = json.loads(payload)
                # Only forward events for this run
                if data.get("run_id") == str(run_id):
                    queue.put_nowait(payload)
            except json.JSONDecodeError:
                pass

        # Start listening
        await conn.add_listener("run_events", notification_handler)

        # Yield events as they arrive
        while True:
            try:
                # Wait for event with timeout for heartbeat
                payload = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"event: run_event\ndata: {payload}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                yield f"event: heartbeat\ndata: {json.dumps({'status': 'alive'})}\n\n"
            except asyncio.CancelledError:
                break

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    finally:
        if conn:
            await conn.close()


async def _activity_generator_notify() -> AsyncGenerator[str, None]:
    """Generate SSE events for global activity feed using LISTEN/NOTIFY."""
    yield f"event: connected\ndata: {json.dumps({'type': 'activity_feed'})}\n\n"

    conn: Optional[asyncpg.Connection] = None
    try:
        conn = await _get_listen_connection()
        queue: asyncio.Queue = asyncio.Queue()

        def notification_handler(connection, pid, channel, payload):
            queue.put_nowait(payload)

        # Listen to multiple channels
        await conn.add_listener("run_events", notification_handler)
        await conn.add_listener("pointer_changes", notification_handler)
        await conn.add_listener("activity", notification_handler)

        while True:
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"event: activity\ndata: {payload}\n\n"
            except asyncio.TimeoutError:
                yield f"event: heartbeat\ndata: {json.dumps({})}\n\n"
            except asyncio.CancelledError:
                break

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    finally:
        if conn:
            await conn.close()


@router.get("/runs/{run_id}")
async def stream_run_events(
    run_id: UUID,
    request: Request,
    session: SessionDep,
    since_sequence: Annotated[int, Query(ge=0)] = 0,
) -> StreamingResponse:
    """Stream run events via Server-Sent Events (SSE).

    Uses PostgreSQL LISTEN/NOTIFY for true real-time push.
    No polling - events are delivered sub-millisecond after they occur.

    Connect to this endpoint to receive real-time updates for a run.
    Events include step starts/completions, tool calls, LLM interactions,
    checkpoints, and run lifecycle changes.

    Example client code:
    ```javascript
    const eventSource = new EventSource(`/api/v1/streams/runs/${runId}`);
    eventSource.addEventListener('run_event', (e) => {
        const event = JSON.parse(e.data);
        console.log('Event:', event.event_type, event.payload);
    });
    eventSource.addEventListener('heartbeat', () => {
        console.log('Connection alive');
    });
    ```
    """
    # Fetch historical events first
    ledger = LedgerService(session, publish_events=False)
    initial_events = await ledger.get_events(
        run_id=run_id,
        since_sequence=since_sequence,
        limit=100,
    )

    return StreamingResponse(
        _run_event_generator_notify(run_id, initial_events),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/activity")
async def stream_activity() -> StreamingResponse:
    """Stream global activity feed via SSE.

    Provides a real-time stream of platform activity:
    - New runs and status changes
    - Pointer advances (publish/promote events)
    - High-level artifact activity

    Useful for dashboards and activity feeds.
    """
    return StreamingResponse(
        _activity_generator_notify(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
