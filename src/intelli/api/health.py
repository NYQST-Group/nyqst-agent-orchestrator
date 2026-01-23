"""Health check endpoints.

Kubernetes-friendly health probes:
- /health/live - Liveness probe (is the process running?)
- /health/ready - Readiness probe (can it accept traffic?)
- /health - Detailed health status for monitoring
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.api.dependencies import get_session
from intelli.config import settings
from intelli.core.logging import get_correlation_id

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness_check() -> dict:
    """Liveness probe - indicates process is running.

    This should always return 200 if the process is alive.
    Kubernetes uses this to decide whether to restart the container.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness_check(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Readiness probe - indicates service can accept traffic.

    Checks database connectivity. Returns 503 if not ready.
    Kubernetes uses this to decide whether to route traffic to the pod.
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        response.status_code = 503
        return {"status": "not_ready", "database": str(e)}


@router.get("")
async def detailed_health(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Detailed health status for monitoring dashboards.

    Returns comprehensive status of all dependencies.
    """
    checks = {
        "database": {"status": "unknown"},
    }

    # Check database
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # Overall status
    all_healthy = all(c["status"] == "healthy" for c in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "correlation_id": get_correlation_id(),
        "app": settings.app_name,
        "version": "0.1.0",
        "checks": checks,
    }
