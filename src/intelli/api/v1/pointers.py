"""Pointer API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from intelli.api.dependencies import PointerServiceDep
from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.services.indexing.auto_index import auto_index_manifest
from intelli.schemas.substrate import (
    PointerAdvance,
    PointerAdvanceResponse,
    PointerCreate,
    PointerHistoryEntry,
    PointerResponse,
    PointerType,
)

router = APIRouter(prefix="/pointers", tags=["pointers"])


@router.post("", response_model=PointerResponse)
async def create_pointer(
    service: PointerServiceDep,
    data: PointerCreate,
) -> PointerResponse:
    """Create a new pointer."""
    try:
        pointer = await service.create_pointer(
            namespace=data.namespace,
            name=data.name,
            pointer_type=data.pointer_type,
            manifest_sha256=data.manifest_sha256,
            description=data.description,
            metadata=data.metadata,
        )
        return PointerResponse.model_validate(pointer)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e.message))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{namespace}/{name}", response_model=PointerResponse)
async def get_pointer(
    namespace: str,
    name: str,
    service: PointerServiceDep,
) -> PointerResponse:
    """Get pointer by namespace and name."""
    try:
        pointer = await service.get_pointer(namespace, name)
        return PointerResponse.model_validate(pointer)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{namespace}/{name}/resolve")
async def resolve_pointer(
    namespace: str,
    name: str,
    service: PointerServiceDep,
) -> dict:
    """Resolve pointer to current manifest SHA-256."""
    try:
        sha256 = await service.resolve(namespace, name)
        return {"namespace": namespace, "name": name, "manifest_sha256": sha256}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.put("/{pointer_id}/advance", response_model=PointerAdvanceResponse)
async def advance_pointer(
    pointer_id: UUID,
    service: PointerServiceDep,
    data: PointerAdvance,
    background_tasks: BackgroundTasks,
) -> PointerAdvanceResponse:
    """Advance pointer HEAD to a new manifest.

    Use expected_sha256 for optimistic locking.
    """
    try:
        result = await service.advance(
            pointer_id=pointer_id,
            new_sha256=data.manifest_sha256,
            expected_sha256=data.expected_sha256,
            reason=data.reason,
        )

        # Always-on indexing (substrate capability) for pointers that opt in.
        if result.success:
            pointer = await service.get_pointer_by_id(pointer_id)
            index_cfg = (pointer.meta or {}).get("index", {})
            enabled = index_cfg.get("enabled")
            if enabled is True or (enabled is None and pointer.namespace == "notebooks"):
                profile = index_cfg.get("profile") or (
                    "docs.default" if pointer.namespace == "notebooks" else "default"
                )
                background_tasks.add_task(
                    auto_index_manifest,
                    manifest_sha256=result.new_sha256,
                    pointer_id=pointer_id,
                    profile=profile,
                    reason=data.reason or "pointer_advance",
                )

        # Ensure the advance is committed before returning a 200.
        # FastAPI executes dependency cleanup (and our session commit) after the response is sent,
        # which can cause a brief window where a subsequent request cannot see the new HEAD.
        await service.repo.session.commit()

        return PointerAdvanceResponse(
            success=result.success,
            old_sha256=result.old_sha256,
            new_sha256=result.new_sha256,
            conflict=result.conflict,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.put("/{pointer_id}/reset")
async def reset_pointer(
    pointer_id: UUID,
    service: PointerServiceDep,
    target_sha256: Annotated[str | None, Query(description="Target manifest SHA-256")] = None,
    reason: Annotated[str | None, Query(description="Reason for reset")] = None,
) -> dict:
    """Reset pointer HEAD to a specific manifest or clear it."""
    try:
        old_sha256 = await service.reset(
            pointer_id=pointer_id,
            target_sha256=target_sha256,
            reason=reason,
        )
        return {
            "old_sha256": old_sha256,
            "new_sha256": target_sha256,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{pointer_id}/history", response_model=list[PointerHistoryEntry])
async def get_pointer_history(
    pointer_id: UUID,
    service: PointerServiceDep,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[PointerHistoryEntry]:
    """Get pointer change history."""
    try:
        history = await service.get_history(pointer_id, limit)
        return [PointerHistoryEntry.model_validate(h) for h in history]
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.delete("/{pointer_id}")
async def delete_pointer(
    pointer_id: UUID,
    service: PointerServiceDep,
) -> dict:
    """Soft delete a pointer."""
    try:
        await service.delete_pointer(pointer_id)
        return {"deleted": True, "pointer_id": str(pointer_id)}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("", response_model=list[PointerResponse])
async def list_pointers(
    service: PointerServiceDep,
    namespace: Annotated[str | None, Query(description="Filter by namespace")] = None,
    pointer_type: Annotated[PointerType | None, Query(description="Filter by type")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[PointerResponse]:
    """List pointers with optional filters."""
    pointers = await service.list_pointers(
        namespace=namespace,
        pointer_type=pointer_type,
        limit=limit,
        offset=offset,
    )
    return [PointerResponse.model_validate(p) for p in pointers]
