"""Artifact API endpoints."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from intelli.api.dependencies import ArtifactServiceDep
from intelli.core.exceptions import NotFoundError
from intelli.schemas.substrate import ArtifactResponse, ArtifactUploadResponse

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.post("", response_model=ArtifactUploadResponse)
async def upload_artifact(
    service: ArtifactServiceDep,
    file: Annotated[UploadFile, File(description="File to upload")],
    media_type: Annotated[str | None, Form(description="MIME type override")] = None,
) -> ArtifactUploadResponse:
    """Upload a new artifact.

    Computes SHA-256 hash and deduplicates automatically.
    Returns existing artifact if content already exists.
    """
    content = await file.read()
    result = await service.upload_artifact(
        content=content,
        filename=file.filename,
        media_type=media_type or file.content_type or "application/octet-stream",
        generate_url=True,
    )

    return ArtifactUploadResponse(
        sha256=result.sha256,
        size_bytes=result.size_bytes,
        is_duplicate=result.is_duplicate,
        content_url=result.content_url,
    )


@router.get("/{sha256}", response_model=ArtifactResponse)
async def get_artifact(
    sha256: str,
    service: ArtifactServiceDep,
) -> ArtifactResponse:
    """Get artifact metadata by SHA-256."""
    try:
        artifact = await service.get_artifact(sha256)
        return ArtifactResponse.model_validate(artifact)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{sha256}/content")
async def get_artifact_content(
    sha256: str,
    service: ArtifactServiceDep,
) -> StreamingResponse:
    """Get artifact content by SHA-256.

    Returns the raw file content with appropriate content type.
    """
    try:
        artifact = await service.get_artifact(sha256)
        content = await service.get_content(sha256)

        return StreamingResponse(
            iter([content]),
            media_type=artifact.media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{artifact.filename or sha256}"',
                "Content-Length": str(artifact.size_bytes),
            },
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("/{sha256}/url")
async def get_artifact_url(
    sha256: str,
    service: ArtifactServiceDep,
    expiration_seconds: Annotated[int, Query(ge=60, le=86400)] = 3600,
) -> dict:
    """Get pre-signed URL for artifact content.

    URL is valid for the specified duration (default 1 hour).
    """
    try:
        url = await service.get_content_url(sha256, expiration_seconds)
        return {"url": url, "expires_in": expiration_seconds}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))


@router.get("", response_model=list[ArtifactResponse])
async def list_artifacts(
    service: ArtifactServiceDep,
    media_type: Annotated[str | None, Query(description="Filter by MIME type")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ArtifactResponse]:
    """List artifacts with optional filters."""
    artifacts = await service.list_artifacts(
        media_type=media_type,
        limit=limit,
        offset=offset,
    )
    return [ArtifactResponse.model_validate(a) for a in artifacts]


@router.delete("/{sha256}")
async def delete_artifact(
    sha256: str,
    service: ArtifactServiceDep,
    force: Annotated[bool, Query(description="Delete even if referenced")] = False,
) -> dict:
    """Delete artifact if not referenced.

    Use force=true to delete regardless of references (admin only).
    """
    try:
        deleted = await service.delete_artifact(sha256, force=force)
        if deleted:
            return {"deleted": True, "sha256": sha256}
        return {"deleted": False, "reason": "Artifact is still referenced"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
