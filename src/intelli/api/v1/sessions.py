"""Session API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from intelli.api.dependencies import SessionServiceDep
from intelli.api.middleware.auth import AuthContext, WriteContext
from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.schemas.sessions import (
    SessionCostBreakdown,
    SessionCreate,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    ctx: WriteContext,
    service: SessionServiceDep,
    data: SessionCreate,
) -> SessionResponse:
    """Start a new session."""
    sess = await service.start(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        scope_type=data.scope_type,
        scope_id=data.scope_id,
        module=data.module,
        objective=data.objective,
        config_snapshot=data.config_snapshot,
        idle_timeout_minutes=data.idle_timeout_minutes,
    )
    return SessionResponse.model_validate(sess)


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    ctx: AuthContext,
    service: SessionServiceDep,
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> SessionListResponse:
    """List sessions for the authenticated user."""
    items, total = await service.list_for_user(
        ctx.tenant_id,
        ctx.user_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return SessionListResponse(
        items=[SessionResponse.model_validate(s) for s in items],
        total=total,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    ctx: AuthContext,
    session_id: UUID,
    service: SessionServiceDep,
) -> SessionResponse:
    """Get a session by ID."""
    try:
        sess = await service.get(session_id, ctx.tenant_id)
        return SessionResponse.model_validate(sess)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    ctx: WriteContext,
    session_id: UUID,
    service: SessionServiceDep,
    data: SessionUpdate,
) -> SessionResponse:
    """Update session status (idle/resume/close)."""
    try:
        sess = await service.transition(
            session_id,
            ctx.tenant_id,
            data.status,
            data.close_reason,
        )
        return SessionResponse.model_validate(sess)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.get("/{session_id}/cost", response_model=SessionCostBreakdown)
async def get_session_cost(
    ctx: AuthContext,
    session_id: UUID,
    service: SessionServiceDep,
) -> SessionCostBreakdown:
    """Get cost breakdown for a session."""
    try:
        result = await service.get_cost_breakdown(session_id, ctx.tenant_id)
        return SessionCostBreakdown(**result)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
