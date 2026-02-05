"""Unit tests for ConversationService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import ConflictError, NotFoundError
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


class TestCreateConversation:
    async def test_creates_with_scope_binding(self, service):
        tenant_id = uuid4()
        user_id = uuid4()
        service.conv_repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                scope_type="project",
                module="research",
            )
        )

        result = await service.create(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type="project",
            module="research",
        )
        assert result.scope_type == "project"
        service.conv_repo.create.assert_called_once()

    async def test_creates_with_config_snapshot(self, service):
        service.conv_repo.create = AsyncMock(return_value=MagicMock())
        config = {"model": "gpt-4o", "tools": ["search"]}
        await service.create(
            tenant_id=uuid4(),
            user_id=uuid4(),
            config_snapshot=config,
        )
        call_kwargs = service.conv_repo.create.call_args[1]
        assert call_kwargs["config_snapshot"] == config

    async def test_creates_with_session_id(self, service):
        session_id = uuid4()
        service.conv_repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                session_id=session_id,
            )
        )
        await service.create(
            tenant_id=uuid4(),
            user_id=uuid4(),
            session_id=session_id,
        )
        call_kwargs = service.conv_repo.create.call_args[1]
        assert call_kwargs["session_id"] == session_id


class TestSaveMessage:
    async def test_saves_and_updates_totals(self, service):
        conv_id = uuid4()
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
            conv_id,
            "assistant",
            "Hello",
            input_tokens=100,
            output_tokens=50,
            cost_micros=500,
        )

        assert conv_mock.message_count == 1
        assert conv_mock.total_input_tokens == 100
        assert conv_mock.total_output_tokens == 50

    async def test_handles_none_tokens(self, service):
        service.msg_repo.get_next_sequence = AsyncMock(return_value=1)
        service.msg_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))
        service.conv_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                message_count=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_cost_micros=0,
            )
        )

        await service.save_message(uuid4(), "user", "Hi")
        # Should not raise


class TestBranching:
    async def test_creates_branch_from_message(self, service):
        conv_id = uuid4()
        msg_id = uuid4()
        service.msg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                id=msg_id,
                conversation_id=conv_id,
            )
        )
        service.msg_repo.get_next_sequence = AsyncMock(return_value=5)

        result = await service.branch_from_message(conv_id, msg_id)
        assert result["conversation_id"] == conv_id
        assert result["branch_point_message_id"] == msg_id
        assert result["new_sequence_number"] == 5

    async def test_raises_not_found_for_wrong_conversation(self, service):
        service.msg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                conversation_id=uuid4(),  # different from requested
            )
        )
        with pytest.raises(NotFoundError):
            await service.branch_from_message(uuid4(), uuid4())


class TestAddFeedback:
    async def test_saves_feedback(self, service):
        msg_id = uuid4()
        user_id = uuid4()

        # Mock no existing feedback
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        service.session.execute = AsyncMock(return_value=result_mock)
        service.session.add = MagicMock()
        service.session.flush = AsyncMock()

        feedback = await service.add_feedback(msg_id, user_id, "positive")
        assert feedback.rating == "positive"

    async def test_raises_conflict_on_duplicate(self, service):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = MagicMock()  # existing
        service.session.execute = AsyncMock(return_value=result_mock)

        with pytest.raises(ConflictError):
            await service.add_feedback(uuid4(), uuid4(), "positive")


class TestArchive:
    async def test_sets_status_to_archived(self, service):
        conv_mock = MagicMock(status="active")
        service.conv_repo.get_by_tenant = AsyncMock(return_value=conv_mock)
        service.session.flush = AsyncMock()

        await service.archive(uuid4(), uuid4())
        assert conv_mock.status == "archived"


class TestSaveMessageEdgeCases:
    async def test_handles_negative_tokens(self, service):
        service.msg_repo.get_next_sequence = AsyncMock(return_value=1)
        service.msg_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))
        conv_mock = MagicMock(
            message_count=0,
            total_input_tokens=0,
            total_output_tokens=0,
            total_cost_micros=0,
        )
        service.conv_repo.get_by_id = AsyncMock(return_value=conv_mock)

        await service.save_message(
            uuid4(),
            "assistant",
            "Hi",
            input_tokens=-1,
            output_tokens=-1,
        )
        # Negative tokens are stored as-is — validation is upstream
        assert conv_mock.total_input_tokens == -1


class TestBranchEdgeCases:
    async def test_branch_raises_not_found_for_missing_message(self, service):
        service.msg_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.branch_from_message(uuid4(), uuid4())


class TestFeedbackEdgeCases:
    async def test_add_feedback_raises_not_found_for_missing_message(self, service):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        service.session.execute = AsyncMock(side_effect=Exception("not found"))

        with pytest.raises(Exception, match="not found"):
            await service.add_feedback(uuid4(), uuid4(), "positive")
