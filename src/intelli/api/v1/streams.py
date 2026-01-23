"""Server-Sent Events (SSE) streaming endpoints for real-time updates.

These endpoints enable the UI to receive real-time updates for:
- Run events (steps, tool calls, completions)
- Pointer changes (publish/promote)
- Global activity feed
"""

import asyncio
import json
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from intelli.api.dependencies import LedgerServiceDep, SessionDep
from intelli.services.runs.ledger_service import LedgerService

router = APIRouter(prefix="/streams", tags=["streams"])


async def _run_event_generator(
    ledger: LedgerService,
    run_id: UUID,
    poll_interval: float = 0.5,
) -> AsyncGenerator[str, None]:
    """Generate SSE events for a run's event stream.

    Yields events in SSE format: "data: {json}\n\n"
    """
    last_sequence = 0

    # Send initial connection event
    yield f"event: connected\ndata: {json.dumps({'run_id': str(run_id)})}\n\n"

    while True:
        try:
            events = await ledger.get_events(
                run_id=run_id,
                since_sequence=last_sequence,
                limit=100,
            )

            for event in events:
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
                last_sequence = event.sequence_num

            # Send heartbeat to keep connection alive
            yield f"event: heartbeat\ndata: {json.dumps({'sequence': last_sequence})}\n\n"

            await asyncio.sleep(poll_interval)

        except asyncio.CancelledError:
            break
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            break


@router.get("/runs/{run_id}")
async def stream_run_events(
    run_id: UUID,
    ledger: LedgerServiceDep,
    poll_interval: Annotated[float, Query(ge=0.1, le=5.0)] = 0.5,
) -> StreamingResponse:
    """Stream run events via Server-Sent Events (SSE).

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
    ```
    """
    return StreamingResponse(
        _run_event_generator(ledger, run_id, poll_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


async def _activity_generator(
    session: SessionDep,
    poll_interval: float = 2.0,
) -> AsyncGenerator[str, None]:
    """Generate SSE events for global activity feed.

    Includes: new runs, pointer changes, new artifacts (summary).
    """
    from intelli.repositories.runs import RunRepository
    from intelli.repositories.pointers import PointerRepository

    last_check = None

    yield f"event: connected\ndata: {json.dumps({'type': 'activity_feed'})}\n\n"

    while True:
        try:
            run_repo = RunRepository(session)
            pointer_repo = PointerRepository(session)

            # Get recent runs
            recent_runs = await run_repo.list_recent(limit=10)
            runs_data = [
                {
                    "type": "run",
                    "run_id": str(r.id),
                    "run_type": r.run_type,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                }
                for r in recent_runs
            ]

            if runs_data:
                yield f"event: activity\ndata: {json.dumps({'runs': runs_data})}\n\n"

            # Heartbeat
            yield f"event: heartbeat\ndata: {json.dumps({})}\n\n"

            await asyncio.sleep(poll_interval)

        except asyncio.CancelledError:
            break
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            await asyncio.sleep(poll_interval)


@router.get("/activity")
async def stream_activity(
    session: SessionDep,
    poll_interval: Annotated[float, Query(ge=1.0, le=30.0)] = 2.0,
) -> StreamingResponse:
    """Stream global activity feed via SSE.

    Provides a summary of recent activity across the platform:
    - New runs and status changes
    - Pointer advances (publish/promote events)
    - High-level artifact activity

    Useful for dashboards and activity feeds.
    """
    return StreamingResponse(
        _activity_generator(session, poll_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
