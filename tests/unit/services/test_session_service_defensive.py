"""Defensive and edge-case tests for SessionService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import NotFoundError
from intelli.services.session_service import SessionService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    return SessionService(mock_session)


class TestTransitionDefensive:
    async def test_transition_not_found_raises(self, service):
        """Transition should raise NotFoundError when session doesn't exist."""
        service.repo.get_by_tenant = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.transition(uuid4(), uuid4(), "idle")

    async def test_active_to_active_is_noop(self, service):
        """Active to active transition should be a no-op (succeed without change)."""
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "active")
        assert result.status == "active"


class TestValidTransitions:
    async def test_paused_to_active_allowed(self, service):
        """Paused to active transition should be allowed."""
        sess = MagicMock(status="paused")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "active")
        assert result.status == "active"
        assert result.last_active_at is not None

    async def test_paused_to_closed_allowed(self, service):
        """Paused to closed transition should be allowed."""
        sess = MagicMock(status="paused")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.repo.aggregate_cost = AsyncMock(return_value={"total_cost_micros": 0})
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "closed")
        assert result.status == "closed"
        assert result.closed_at is not None

    async def test_active_to_paused_allowed(self, service):
        """Active to paused transition should be allowed."""
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "paused")
        assert result.status == "paused"


class TestCloseDefensive:
    async def test_close_with_no_conversations_returns_zero_cost(self, service):
        """Closing a session with no conversations should have zero cost."""
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.repo.aggregate_cost = AsyncMock(return_value={"total_cost_micros": 0})
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "closed")
        assert result.total_cost_micros == 0

    async def test_close_session_sets_closed_at(self, service):
        """Closing a session should set closed_at timestamp."""
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.repo.aggregate_cost = AsyncMock(return_value={"total_cost_micros": 1000})
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "closed")
        assert result.closed_at is not None
        assert result.close_reason == "user_ended"


class TestListDefensive:
    async def test_list_sessions_filters_by_status(self, service):
        """List should respect status filter."""
        tenant_id = uuid4()
        user_id = uuid4()

        service.repo.list_by_user = AsyncMock(
            return_value=[
                MagicMock(id=uuid4(), status="active"),
                MagicMock(id=uuid4(), status="active"),
            ]
        )
        service.repo.count_by_user = AsyncMock(return_value=2)

        items, total = await service.list_for_user(tenant_id, user_id, status="active")

        # Verify filter was passed
        service.repo.list_by_user.assert_called_once()
        call_kwargs = service.repo.list_by_user.call_args[1]
        assert call_kwargs.get("status") == "active"
        assert total == 2
