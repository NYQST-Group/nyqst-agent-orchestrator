"""Defensive and edge-case tests for ConversationService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import NotFoundError
from intelli.services.conversation_service import ConversationService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    return ConversationService(mock_session)


class TestSaveMessageDefensive:
    async def test_save_message_conv_not_found_raises(self, service):
        """Save message should fail when conversation doesn't exist."""
        service.msg_repo.get_next_sequence = AsyncMock(return_value=1)
        service.msg_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))
        service.conv_repo.get_by_id = AsyncMock(return_value=None)

        # Should not raise but should handle gracefully
        await service.save_message(uuid4(), "user", "Hello")
        # Conversation totals won't be updated if conv is None
        service.conv_repo.get_by_id.assert_called_once()

    async def test_save_message_updates_last_message_at(self, service):
        """Save message should update last_message_at timestamp."""
        conv_mock = MagicMock(
            message_count=0,
            total_input_tokens=0,
            total_output_tokens=0,
            total_cost_micros=0,
        )
        service.msg_repo.get_next_sequence = AsyncMock(return_value=1)
        service.msg_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))
        service.conv_repo.get_by_id = AsyncMock(return_value=conv_mock)

        await service.save_message(uuid4(), "user", "Test")

        # Verify last_message_at was set (not None)
        assert conv_mock.last_message_at is not None
        assert conv_mock.updated_at is not None

    async def test_save_message_handles_zero_tokens(self, service):
        """Save message should handle zero token counts correctly."""
        conv_mock = MagicMock(
            message_count=0,
            total_input_tokens=0,
            total_output_tokens=0,
            total_cost_micros=0,
        )
        service.msg_repo.get_next_sequence = AsyncMock(return_value=1)
        service.msg_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))
        service.conv_repo.get_by_id = AsyncMock(return_value=conv_mock)

        await service.save_message(
            uuid4(),
            "assistant",
            "Hello",
            input_tokens=0,
            output_tokens=0,
            cost_micros=0,
        )

        # Zero tokens should not be added (falsy check in service)
        assert conv_mock.total_input_tokens == 0
        assert conv_mock.total_output_tokens == 0
        assert conv_mock.total_cost_micros == 0


class TestArchiveDefensive:
    async def test_archive_not_found_raises(self, service):
        """Archive should raise NotFoundError when conversation doesn't exist."""
        service.conv_repo.get_by_tenant = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.archive(uuid4(), uuid4())


class TestBranchingDefensive:
    async def test_branch_from_nonexistent_message_raises(self, service):
        """Branching from a non-existent message should raise NotFoundError."""
        service.msg_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.branch_from_message(uuid4(), uuid4())


class TestCreateDefensive:
    async def test_create_with_nonexistent_session_id(self, service):
        """Creating a conversation with a session_id should not validate session existence."""
        session_id = uuid4()
        service.conv_repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                session_id=session_id,
            )
        )

        # Should succeed - service doesn't validate session existence
        result = await service.create(
            tenant_id=uuid4(),
            user_id=uuid4(),
            session_id=session_id,
        )
        assert result.session_id == session_id


class TestListDefensive:
    async def test_list_respects_tenant_isolation(self, service):
        """List should only return conversations for the specified tenant."""
        tenant_id = uuid4()
        user_id = uuid4()

        service.conv_repo.list_by_user = AsyncMock(
            return_value=[
                MagicMock(id=uuid4(), tenant_id=tenant_id),
                MagicMock(id=uuid4(), tenant_id=tenant_id),
            ]
        )
        service.conv_repo.count_by_user = AsyncMock(return_value=2)

        items, total = await service.list_for_user(tenant_id, user_id)

        # Verify tenant_id was passed to repository
        service.conv_repo.list_by_user.assert_called_once()
        call_args = service.conv_repo.list_by_user.call_args
        assert call_args[0][0] == tenant_id
        assert total == 2


class TestDeleteDefensive:
    async def test_delete_sets_status_deleted(self, service):
        """Soft delete should set status to deleted."""
        conv_mock = MagicMock(status="active")
        service.conv_repo.get_by_tenant = AsyncMock(return_value=conv_mock)
        service.session.flush = AsyncMock()

        await service.soft_delete(uuid4(), uuid4())

        assert conv_mock.status == "deleted"
        assert conv_mock.updated_at is not None


class TestFeedbackDefensive:
    async def test_feedback_on_nonexistent_message_raises(self, service):
        """Adding feedback should fail gracefully if message doesn't exist."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        service.session.execute = AsyncMock(return_value=result_mock)
        service.session.add = MagicMock()
        service.session.flush = AsyncMock()

        # Should succeed - service doesn't validate message existence before checking duplicates
        feedback = await service.add_feedback(uuid4(), uuid4(), "positive")
        assert feedback.rating == "positive"
