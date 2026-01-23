"""Run API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from intelli.api.dependencies import RunServiceDep, LedgerServiceDep
from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.schemas.runs import (
    RunCreate,
    RunEventCreate,
    RunEventListResponse,
    RunEventResponse,
    RunListResponse,
    RunResponse,
    RunStatus,
)

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse)
async def create_run(
    service: RunServiceDep,
    data: RunCreate,
) -> RunResponse:
    """Create a new run."""
    run = await service.create_run(
        run_type=data.run_type,
        name=data.name,
        config=data.config,
        input_manifest_sha256=data.input_manifest_sha256,
        project_id=data.project_id,
        session_id=data.session_id,
        parent_run_id=data.parent_run_id,
    )
    return RunResponse.model_validate(run)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: UUID,
    service: RunServiceDep,
) -> RunResponse:
    """Get run by ID."""
    try:
        run = await service.get_run(run_id)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.post("/{run_id}/start", response_model=RunResponse)
async def start_run(
    run_id: UUID,
    service: RunServiceDep,
) -> RunResponse:
    """Start a pending run."""
    try:
        run = await service.start_run(run_id)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.post("/{run_id}/pause", response_model=RunResponse)
async def pause_run(
    run_id: UUID,
    service: RunServiceDep,
) -> RunResponse:
    """Pause a running run."""
    try:
        run = await service.pause_run(run_id)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.post("/{run_id}/resume", response_model=RunResponse)
async def resume_run(
    run_id: UUID,
    service: RunServiceDep,
) -> RunResponse:
    """Resume a paused run."""
    try:
        run = await service.resume_run(run_id)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.post("/{run_id}/complete", response_model=RunResponse)
async def complete_run(
    run_id: UUID,
    service: RunServiceDep,
    result: dict | None = None,
    output_manifest_sha256: str | None = None,
) -> RunResponse:
    """Mark run as completed."""
    try:
        run = await service.complete_run(run_id, result, output_manifest_sha256)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.post("/{run_id}/fail", response_model=RunResponse)
async def fail_run(
    run_id: UUID,
    service: RunServiceDep,
    error: dict,
) -> RunResponse:
    """Mark run as failed."""
    try:
        run = await service.fail_run(run_id, error)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.post("/{run_id}/cancel", response_model=RunResponse)
async def cancel_run(
    run_id: UUID,
    service: RunServiceDep,
) -> RunResponse:
    """Cancel a run."""
    try:
        run = await service.cancel_run(run_id)
        return RunResponse.model_validate(run)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.get("", response_model=RunListResponse)
async def list_runs(
    service: RunServiceDep,
    status: Annotated[RunStatus | None, Query(description="Filter by status")] = None,
    run_type: Annotated[str | None, Query(description="Filter by type")] = None,
    project_id: Annotated[UUID | None, Query(description="Filter by project")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RunListResponse:
    """List runs with optional filters."""
    status_value = status.value if status else None
    runs = await service.list_runs(
        status=status_value,
        run_type=run_type,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return RunListResponse(
        items=[RunResponse.model_validate(r) for r in runs],
        total=len(runs),  # TODO: Add proper count query
        limit=limit,
        offset=offset,
    )


# Event endpoints


@router.post("/{run_id}/events", response_model=RunEventResponse)
async def create_run_event(
    run_id: UUID,
    service: LedgerServiceDep,
    data: RunEventCreate,
) -> RunEventResponse:
    """Append an event to the run ledger."""
    event = await service.log_event(
        run_id=run_id,
        event_type=data.event_type.value,
        payload=data.payload,
        duration_ms=data.duration_ms,
    )
    return RunEventResponse.model_validate(event)


@router.get("/{run_id}/events", response_model=RunEventListResponse)
async def get_run_events(
    run_id: UUID,
    service: LedgerServiceDep,
    event_types: Annotated[list[str] | None, Query(description="Filter by event types")] = None,
    since_sequence: Annotated[int | None, Query(description="Get events after this sequence")] = None,
    limit: Annotated[int, Query(ge=1, le=10000)] = 1000,
) -> RunEventListResponse:
    """Get events for a run."""
    events = await service.get_events(
        run_id=run_id,
        event_types=event_types,
        since_sequence=since_sequence,
        limit=limit,
    )
    total = await service.count_events(run_id)
    return RunEventListResponse(
        items=[RunEventResponse.model_validate(e) for e in events],
        run_id=run_id,
        total=total,
    )


@router.get("/{run_id}/checkpoint")
async def get_latest_checkpoint(
    run_id: UUID,
    service: LedgerServiceDep,
) -> dict:
    """Get the most recent checkpoint for resumption."""
    checkpoint = await service.get_latest_checkpoint(run_id)
    if not checkpoint:
        return {"has_checkpoint": False}
    return {
        "has_checkpoint": True,
        "checkpoint": RunEventResponse.model_validate(checkpoint),
    }
