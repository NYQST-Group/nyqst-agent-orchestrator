"""Audit logging service.

Records all significant actions for compliance and debugging.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.core.context import get_context_or_none, RequestContext
from intelli.db.models.auth import AuditLog


class AuditService:
    """Service for recording audit events."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[dict] = None,
        context: Optional[RequestContext] = None,
    ) -> AuditLog:
        """Record an audit event.

        Args:
            action: Action performed (e.g., "create", "delete", "advance")
            resource_type: Type of resource (e.g., "artifact", "pointer")
            resource_id: ID of the resource
            details: Additional details to record
            context: Request context (uses current context if not provided)
        """
        ctx = context or get_context_or_none()

        if not ctx or not ctx.tenant_id:
            # Skip audit for unauthenticated requests
            return None

        audit_entry = AuditLog(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            api_key_id=ctx.api_key_id,
            action=f"{resource_type}.{action}",
            resource_type=resource_type,
            resource_id=str(resource_id),
            ip_address=ctx.ip_address,
            user_agent=ctx.user_agent,
            request_id=ctx.request_id,
            details=details or {},
        )

        self.session.add(audit_entry)
        await self.session.flush()

        return audit_entry

    async def log_artifact_create(self, sha256: str, size_bytes: int, deduplicated: bool):
        """Log artifact creation."""
        await self.log(
            action="create",
            resource_type="artifact",
            resource_id=sha256,
            details={
                "size_bytes": size_bytes,
                "deduplicated": deduplicated,
            },
        )

    async def log_manifest_create(self, sha256: str, entry_count: int, parent_sha256: Optional[str]):
        """Log manifest creation."""
        await self.log(
            action="create",
            resource_type="manifest",
            resource_id=sha256,
            details={
                "entry_count": entry_count,
                "parent_sha256": parent_sha256,
            },
        )

    async def log_pointer_advance(
        self,
        pointer_id: UUID,
        from_sha256: Optional[str],
        to_sha256: str,
        version: int,
    ):
        """Log pointer advance."""
        await self.log(
            action="advance",
            resource_type="pointer",
            resource_id=str(pointer_id),
            details={
                "from_sha256": from_sha256,
                "to_sha256": to_sha256,
                "version": version,
            },
        )

    async def log_run_lifecycle(self, run_id: UUID, action: str, error_message: Optional[str] = None):
        """Log run lifecycle events."""
        details = {}
        if error_message:
            details["error_message"] = error_message

        await self.log(
            action=action,
            resource_type="run",
            resource_id=str(run_id),
            details=details,
        )

    async def log_api_key_create(self, key_id: UUID, name: str, scopes: list[str]):
        """Log API key creation."""
        await self.log(
            action="create",
            resource_type="api_key",
            resource_id=str(key_id),
            details={
                "name": name,
                "scopes": scopes,
            },
        )

    async def log_api_key_revoke(self, key_id: UUID, name: str):
        """Log API key revocation."""
        await self.log(
            action="revoke",
            resource_type="api_key",
            resource_id=str(key_id),
            details={"name": name},
        )
