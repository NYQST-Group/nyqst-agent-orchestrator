"""Conversation API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from intelli.api.dependencies import ConversationServiceDep
from intelli.api.middleware.auth import AuthContext, WriteContext
from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.schemas.conversations import (
    BranchCreate,
    BranchResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    FeedbackCreate,
    FeedbackResponse,
    MessageListResponse,
    MessageResponse,
    SiblingResponse,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    ctx: WriteContext,
    service: ConversationServiceDep,
    data: ConversationCreate,
) -> ConversationResponse:
    """Create a new conversation."""
    conv = await service.create(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        scope_type=data.scope_type,
        scope_id=data.scope_id,
        module=data.module,
        title=data.title,
        session_id=data.session_id,
        config_snapshot=data.config_snapshot,
    )
    return ConversationResponse.model_validate(conv)


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    ctx: AuthContext,
    service: ConversationServiceDep,
    scope_type: str | None = Query(None),
    scope_id: str | None = Query(None),
    module: str | None = Query(None),
    status: str | None = Query(None),
    session_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> ConversationListResponse:
    """List conversations for the authenticated user."""
    items, total = await service.list_for_user(
        ctx.tenant_id,
        ctx.user_id,
        scope_type=scope_type,
        scope_id=scope_id,
        module=module,
        status=status,
        session_id=session_id,
        limit=limit,
        offset=offset,
    )
    return ConversationListResponse(
        items=[ConversationResponse.model_validate(c) for c in items],
        total=total,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    ctx: AuthContext,
    conversation_id: UUID,
    service: ConversationServiceDep,
) -> ConversationResponse:
    """Get a conversation by ID."""
    try:
        conv = await service.get(conversation_id, ctx.tenant_id)
        return ConversationResponse.model_validate(conv)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    ctx: WriteContext,
    conversation_id: UUID,
    service: ConversationServiceDep,
    data: ConversationUpdate,
) -> ConversationResponse:
    """Update a conversation (title, status)."""
    try:
        updates = data.model_dump(exclude_none=True)
        conv = await service.update(conversation_id, ctx.tenant_id, **updates)
        return ConversationResponse.model_validate(conv)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    ctx: WriteContext,
    conversation_id: UUID,
    service: ConversationServiceDep,
) -> None:
    """Soft-delete a conversation."""
    try:
        await service.soft_delete(conversation_id, ctx.tenant_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    ctx: AuthContext,
    conversation_id: UUID,
    service: ConversationServiceDep,
    limit: int = Query(100, ge=1, le=500),
    before_seq: int | None = Query(None),
) -> MessageListResponse:
    """Get messages for a conversation (paginated by sequence)."""
    try:
        await service.get(conversation_id, ctx.tenant_id)  # auth check
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")

    items, total = await service.get_messages(
        conversation_id,
        limit=limit,
        before_seq=before_seq,
    )
    return MessageListResponse(
        items=[MessageResponse.model_validate(m) for m in items],
        total=total,
    )


@router.post(
    "/{conversation_id}/messages/{message_id}/feedback",
    response_model=FeedbackResponse,
    status_code=201,
)
async def add_feedback(
    ctx: WriteContext,
    conversation_id: UUID,
    message_id: UUID,
    service: ConversationServiceDep,
    data: FeedbackCreate,
) -> FeedbackResponse:
    """Add feedback to a message."""
    try:
        await service.get(conversation_id, ctx.tenant_id)  # auth check
        feedback = await service.add_feedback(
            message_id=message_id,
            user_id=ctx.user_id,
            rating=data.rating,
            content=data.content,
        )
        return FeedbackResponse.model_validate(feedback)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except ConflictError:
        raise HTTPException(status_code=409, detail="Feedback already exists")


@router.post(
    "/{conversation_id}/branch",
    response_model=BranchResponse,
    status_code=201,
)
async def branch_conversation(
    ctx: WriteContext,
    conversation_id: UUID,
    service: ConversationServiceDep,
    data: BranchCreate,
) -> BranchResponse:
    """Create a branch from a message."""
    try:
        await service.get(conversation_id, ctx.tenant_id)  # auth check
        result = await service.branch_from_message(conversation_id, data.message_id)
        return BranchResponse(**result)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get(
    "/{conversation_id}/messages/{message_id}/siblings",
    response_model=SiblingResponse,
)
async def get_message_siblings(
    ctx: AuthContext,
    conversation_id: UUID,
    message_id: UUID,
    service: ConversationServiceDep,
) -> SiblingResponse:
    """Get sibling messages (messages that share the same parent)."""
    try:
        await service.get(conversation_id, ctx.tenant_id)  # auth check
        siblings, total, current_index = await service.get_siblings(conversation_id, message_id)
        return SiblingResponse(
            items=[MessageResponse.model_validate(m) for m in siblings],
            total=total,
            current_index=current_index,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
