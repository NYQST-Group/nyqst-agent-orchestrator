"""Manifest API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from intelli.api.dependencies import ManifestServiceDep
from intelli.api.middleware.auth import AuthContext
from intelli.core.exceptions import NotFoundError, ValidationError
from intelli.schemas.substrate import (
    ManifestCreate,
    ManifestDiff,
    ManifestEntry,
    ManifestResponse,
    ManifestTree,
)

router = APIRouter(prefix="/manifests", tags=["manifests"])


@router.post("", response_model=dict)
async def create_manifest(
    ctx: AuthContext,
    service: ManifestServiceDep,
    data: ManifestCreate,
) -> dict:
    """Create a new manifest.

    Computes SHA-256 of canonical JSON. Returns existing manifest
    if content already exists (content-addressed).
    """
    try:
        result = await service.build_manifest(
            entries=data.entries,
            parent_sha256=data.parent_sha256,
            message=data.message,
            metadata=data.metadata,
        )

        return {
            "sha256": result.sha256,
            "entry_count": result.entry_count,
            "total_size_bytes": result.total_size_bytes,
            "is_duplicate": result.is_duplicate,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message))


@router.get("/{sha256}", response_model=ManifestResponse)
async def get_manifest(
    ctx: AuthContext,
    sha256: str,
    service: ManifestServiceDep,
) -> ManifestResponse:
    """Get manifest by SHA-256."""
    try:
        manifest = await service.get_manifest(sha256)
        return ManifestResponse(
            sha256=manifest.sha256,
            tree=ManifestTree(
                entries=[
                    ManifestEntry(
                        path=e["path"],
                        artifact_sha256=e["artifact_sha256"],
                        metadata=e.get("metadata"),
                    )
                    for e in manifest.tree.get("entries", [])
                ],
                metadata=manifest.tree.get("metadata"),
            ),
            parent_sha256=manifest.parent_sha256,
            entry_count=manifest.entry_count,
            total_size_bytes=manifest.total_size_bytes,
            message=manifest.message,
            created_at=manifest.created_at,
            created_by=manifest.created_by,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{sha256}/entries", response_model=list[ManifestEntry])
async def get_manifest_entries(
    ctx: AuthContext,
    sha256: str,
    service: ManifestServiceDep,
) -> list[ManifestEntry]:
    """Get entries from a manifest."""
    try:
        return await service.get_entries(sha256)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{sha256}/history", response_model=list[ManifestResponse])
async def get_manifest_history(
    ctx: AuthContext,
    sha256: str,
    service: ManifestServiceDep,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[ManifestResponse]:
    """Get manifest history by walking parent chain."""
    try:
        history = await service.get_history(sha256, limit)
        return [
            ManifestResponse(
                sha256=m.sha256,
                tree=ManifestTree(
                    entries=[
                        ManifestEntry(
                            path=e["path"],
                            artifact_sha256=e["artifact_sha256"],
                            metadata=e.get("metadata"),
                        )
                        for e in m.tree.get("entries", [])
                    ],
                    metadata=m.tree.get("metadata"),
                ),
                parent_sha256=m.parent_sha256,
                entry_count=m.entry_count,
                total_size_bytes=m.total_size_bytes,
                message=m.message,
                created_at=m.created_at,
                created_by=m.created_by,
            )
            for m in history
        ]
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{old_sha256}/diff/{new_sha256}", response_model=ManifestDiff)
async def diff_manifests(
    ctx: AuthContext,
    old_sha256: str,
    new_sha256: str,
    service: ManifestServiceDep,
) -> ManifestDiff:
    """Compute diff between two manifests."""
    try:
        diff = await service.diff_manifests(old_sha256, new_sha256)
        return ManifestDiff(
            old_sha256=diff.old_sha256,
            new_sha256=diff.new_sha256,
            added=diff.added,
            removed=diff.removed,
            modified=[
                {
                    "path": m["path"],
                    "old": m["old"].model_dump() if hasattr(m["old"], "model_dump") else m["old"],
                    "new": m["new"].model_dump() if hasattr(m["new"], "model_dump") else m["new"],
                }
                for m in diff.modified
            ],
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("", response_model=list[ManifestResponse])
async def list_manifests(
    ctx: AuthContext,
    service: ManifestServiceDep,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ManifestResponse]:
    """List recent manifests."""
    manifests = await service.list_manifests(limit, offset)
    return [
        ManifestResponse(
            sha256=m.sha256,
            tree=ManifestTree(
                entries=[
                    ManifestEntry(
                        path=e["path"],
                        artifact_sha256=e["artifact_sha256"],
                        metadata=e.get("metadata"),
                    )
                    for e in m.tree.get("entries", [])
                ],
                metadata=m.tree.get("metadata"),
            ),
            parent_sha256=m.parent_sha256,
            entry_count=m.entry_count,
            total_size_bytes=m.total_size_bytes,
            message=m.message,
            created_at=m.created_at,
            created_by=m.created_by,
        )
        for m in manifests
    ]
