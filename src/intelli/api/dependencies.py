"""FastAPI dependency injection providers."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.db.engine import get_session as db_get_session
from intelli.services.runs.ledger_service import LedgerService
from intelli.services.runs.run_service import RunService
from intelli.services.substrate.artifact_service import ArtifactService
from intelli.services.substrate.manifest_service import ManifestService
from intelli.services.substrate.pointer_service import PointerService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in db_get_session():
        yield session


# Type alias for session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_artifact_service(
    session: SessionDep,
) -> ArtifactService:
    """Get artifact service dependency."""
    return ArtifactService(session)


async def get_manifest_service(
    session: SessionDep,
) -> ManifestService:
    """Get manifest service dependency."""
    return ManifestService(session)


async def get_pointer_service(
    session: SessionDep,
) -> PointerService:
    """Get pointer service dependency."""
    return PointerService(session)


async def get_run_service(
    session: SessionDep,
) -> RunService:
    """Get run service dependency."""
    return RunService(session)


async def get_ledger_service(
    session: SessionDep,
) -> LedgerService:
    """Get ledger service dependency."""
    return LedgerService(session)


# Type aliases for service dependencies
ArtifactServiceDep = Annotated[ArtifactService, Depends(get_artifact_service)]
ManifestServiceDep = Annotated[ManifestService, Depends(get_manifest_service)]
PointerServiceDep = Annotated[PointerService, Depends(get_pointer_service)]
RunServiceDep = Annotated[RunService, Depends(get_run_service)]
LedgerServiceDep = Annotated[LedgerService, Depends(get_ledger_service)]
