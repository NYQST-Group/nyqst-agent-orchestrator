"""Tag API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from intelli.api.dependencies import TagServiceDep
from intelli.api.middleware.auth import AuthContext, WriteContext
from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.schemas.tags import TagCreate, TagListResponse, TagResponse, TagSearchResult

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagResponse, status_code=201)
async def add_tag(
    ctx: WriteContext,
    service: TagServiceDep,
    data: TagCreate,
) -> TagResponse:
    """Add a tag to an entity."""
    try:
        tag = await service.add_tag(
            tenant_id=ctx.tenant_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            namespace=data.namespace,
            key=data.key,
            value=data.value,
            source=data.source,
            confidence=data.confidence,
        )
        return TagResponse.model_validate(tag)
    except ConflictError:
        raise HTTPException(status_code=409, detail="Tag already exists")


@router.delete("/{tag_id}", status_code=204)
async def remove_tag(
    ctx: WriteContext,
    tag_id: UUID,
    service: TagServiceDep,
) -> None:
    """Remove a tag."""
    try:
        await service.remove_tag(tag_id, ctx.tenant_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.get("", response_model=TagListResponse)
async def list_tags(
    ctx: AuthContext,
    service: TagServiceDep,
    entity_type: str | None = Query(None),
    entity_id: UUID | None = Query(None),
    namespace: str | None = Query(None),
    key: str | None = Query(None),
    value: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> TagListResponse:
    """List/filter tags."""
    items, total = await service.list_tags(
        ctx.tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        namespace=namespace,
        key=key,
        value=value,
        limit=limit,
        offset=offset,
    )
    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in items],
        total=total,
    )


@router.get("/search", response_model=list[TagSearchResult])
async def search_tags(
    ctx: AuthContext,
    service: TagServiceDep,
    namespace: str | None = Query(None),
    key: str | None = Query(None),
    value: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
) -> list[TagSearchResult]:
    """Cross-entity tag search."""
    results = await service.search_entities_by_tag(
        ctx.tenant_id,
        namespace=namespace,
        key=key,
        value=value,
        limit=limit,
    )
    return [
        TagSearchResult(
            entity_type=r["entity_type"],
            entity_id=r["entity_id"],
            tags=[TagResponse.model_validate(t) for t in r["tags"]],
        )
        for r in results
    ]
