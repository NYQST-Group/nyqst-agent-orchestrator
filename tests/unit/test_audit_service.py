"""Unit tests for AuditService — audit logging with mocked session."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from intelli.core.context import RequestContext
from intelli.services.audit_service import AuditService

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = lambda obj: None
    session.flush = AsyncMock()
    return session


@pytest.fixture
def ctx():
    return RequestContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        ip_address="127.0.0.1",
        user_agent="test-agent",
        request_id="req-1",
    )


class TestAuditLog:
    async def test_log_event(self, mock_session, ctx):
        svc = AuditService(mock_session)
        result = await svc.log(
            action="create",
            resource_type="artifact",
            resource_id="sha256",
            context=ctx,
        )
        assert result is not None
        mock_session.flush.assert_called_once()

    async def test_log_skips_unauthenticated(self, mock_session):
        svc = AuditService(mock_session)
        with patch("intelli.services.audit_service.get_context_or_none", return_value=None):
            result = await svc.log("create", "artifact", "sha")
        assert result is None

    async def test_log_artifact_create(self, mock_session, ctx):
        svc = AuditService(mock_session)
        with patch("intelli.services.audit_service.get_context_or_none", return_value=ctx):
            await svc.log_artifact_create(sha256="abc", size_bytes=100, deduplicated=False)
        mock_session.flush.assert_called()

    async def test_log_pointer_advance(self, mock_session, ctx):
        svc = AuditService(mock_session)
        with patch("intelli.services.audit_service.get_context_or_none", return_value=ctx):
            await svc.log_pointer_advance(
                pointer_id=uuid4(),
                from_sha256="old",
                to_sha256="new",
                version=2,
            )
        mock_session.flush.assert_called()

    async def test_log_run_lifecycle(self, mock_session, ctx):
        svc = AuditService(mock_session)
        with patch("intelli.services.audit_service.get_context_or_none", return_value=ctx):
            await svc.log_run_lifecycle(run_id=uuid4(), action="start")
        mock_session.flush.assert_called()
