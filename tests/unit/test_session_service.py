"""Unit tests for SessionService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import NotFoundError, ValidationError
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


class TestStartSession:
    async def test_creates_active_session(self, service):
        service.repo.create = AsyncMock(
            return_value=MagicMock(
                status="active",
                id=uuid4(),
            )
        )
        result = await service.start(uuid4(), uuid4())
        assert result.status == "active"
        service.repo.create.assert_called_once()


class TestIdleSession:
    async def test_active_to_idle(self, service):
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "idle")
        assert result.status == "idle"


class TestResumeSession:
    async def test_idle_to_active(self, service):
        sess = MagicMock(status="idle")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "active")
        assert result.status == "active"


class TestCloseSession:
    async def test_active_to_closed(self, service):
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.repo.aggregate_cost = AsyncMock(return_value={"total_cost_micros": 5000})
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "closed")
        assert result.status == "closed"
        assert result.total_cost_micros == 5000

    async def test_idle_to_closed(self, service):
        sess = MagicMock(status="idle")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.repo.aggregate_cost = AsyncMock(return_value={"total_cost_micros": 0})
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "closed")
        assert result.status == "closed"


class TestInvalidTransitions:
    async def test_idle_to_idle_is_noop(self, service):
        """Self-transitions are allowed as no-ops."""
        sess = MagicMock(status="idle")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "idle")
        # Should succeed without error, status remains idle
        assert result.status == "idle"

    async def test_closed_to_anything_fails(self, service):
        sess = MagicMock(status="closed")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)

        with pytest.raises(ValidationError):
            await service.transition(uuid4(), uuid4(), "active")

    async def test_closed_to_closed_fails(self, service):
        sess = MagicMock(status="closed")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)

        with pytest.raises(ValidationError):
            await service.transition(uuid4(), uuid4(), "closed")


class TestTransitionEdgeCases:
    async def test_transition_raises_not_found_for_missing_session(self, service):
        service.repo.get_by_tenant = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.transition(uuid4(), uuid4(), "idle")

    async def test_active_to_active_is_noop(self, service):
        """Self-transitions are allowed as no-ops."""
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "active")
        assert result.status == "active"


class TestCostEdgeCases:
    async def test_close_with_no_conversations_returns_zero_cost(self, service):
        sess = MagicMock(status="active")
        service.repo.get_by_tenant = AsyncMock(return_value=sess)
        service.repo.aggregate_cost = AsyncMock(return_value={"total_cost_micros": 0})
        service.session.flush = AsyncMock()

        result = await service.transition(uuid4(), uuid4(), "closed")
        assert result.total_cost_micros == 0
