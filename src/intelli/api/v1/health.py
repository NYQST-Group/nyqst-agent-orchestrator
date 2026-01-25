"""Health check endpoints.

Provides:
- Liveness probe (is the app running?)
- Readiness probe (can the app serve traffic?)
- Detailed health status
"""

from datetime import UTC, datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.api.dependencies import get_session
from intelli.config import settings

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    version: str
    checks: dict[str, dict]


@router.get("/health/live")
async def liveness():
    """Liveness probe - is the application running?

    Used by Kubernetes/load balancers to know if the container should be restarted.
    Always returns 200 if the app is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Readiness probe - can the application serve traffic?

    Checks critical dependencies (database, storage).
    Returns 200 if ready, 503 if not.
    """
    try:
        # Check database
        await session.execute(text("SELECT 1"))
        # Check index backend if required
        if settings.index_backend == "opensearch":
            async with httpx.AsyncClient(timeout=2.0, verify=settings.opensearch_verify_certs) as client:
                r = await client.get(settings.opensearch_url.rstrip("/") + "/")
            if r.status_code != 200:
                raise RuntimeError(f"OpenSearch not ready (status {r.status_code})")
        return {"status": "ready"}
    except Exception:
        from fastapi import Response
        return Response(
            content='{"status": "not_ready"}',
            status_code=503,
            media_type="application/json",
        )


@router.get("/health", response_model=HealthStatus)
async def detailed_health(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Detailed health check with component status.

    Returns comprehensive health information for monitoring dashboards.
    """
    checks = {}
    overall_status = "healthy"

    # Database check
    try:
        result = await session.execute(text("SELECT version()"))
        db_version = result.scalar()
        checks["database"] = {
            "status": "healthy",
            "version": db_version,
        }
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        overall_status = "unhealthy"

    # Storage check (basic - just config)
    checks["storage"] = {
        "status": "healthy",
        "backend": settings.storage_backend,
        "bucket": settings.s3_bucket if settings.storage_backend == "s3" else settings.local_storage_path,
    }

    # MCP check (config only)
    checks["mcp"] = {
        "status": "healthy",
        "transport": settings.mcp_transport,
        "port": settings.mcp_port,
    }

    # Index backend (optional)
    if settings.index_backend == "opensearch":
        try:
            async with httpx.AsyncClient(timeout=2.0, verify=settings.opensearch_verify_certs) as client:
                r = await client.get(settings.opensearch_url.rstrip("/") + "/")
            checks["index"] = {
                "status": "healthy" if r.status_code == 200 else "degraded",
                "backend": "opensearch",
                "url": settings.opensearch_url,
                "http_status": r.status_code,
            }
            if r.status_code != 200 and overall_status == "healthy":
                overall_status = "degraded"
        except Exception as e:
            checks["index"] = {"status": "unhealthy", "backend": "opensearch", "error": str(e)}
            overall_status = "unhealthy"
    else:
        checks["index"] = {"status": "healthy", "backend": settings.index_backend}

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(UTC),
        version="0.1.0",
        checks=checks,
    )
