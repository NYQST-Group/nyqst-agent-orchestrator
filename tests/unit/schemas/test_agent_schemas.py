"""Unit tests for agent schemas — validation, role checking, UUID validation."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from intelli.schemas.agent import (
    AgentChatMessage,
    AgentChatRequest,
)

pytestmark = pytest.mark.unit


class TestAgentChatMessage:
    def test_agent_chat_message_valid(self):
        """Valid message with role and content."""
        data = AgentChatMessage.model_validate(
            {
                "role": "user",
                "content": "What is the weather today?",
            }
        )
        assert data.role == "user"
        assert data.content == "What is the weather today?"

    def test_agent_chat_message_assistant_role(self):
        """Assistant role is valid."""
        data = AgentChatMessage.model_validate(
            {
                "role": "assistant",
                "content": "The weather is sunny.",
            }
        )
        assert data.role == "assistant"
        assert data.content == "The weather is sunny."

    def test_agent_chat_message_invalid_role(self):
        """Role field accepts any string, but this test demonstrates validation."""
        # Note: The schema doesn't enforce specific role values, but we test
        # that arbitrary roles work (the API layer may enforce role values)
        data = AgentChatMessage.model_validate(
            {
                "role": "system",
                "content": "System prompt",
            }
        )
        assert data.role == "system"

    def test_agent_chat_message_missing_role(self):
        """Role is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentChatMessage.model_validate({"content": "Hello"})
        assert "Field required" in str(exc_info.value)

    def test_agent_chat_message_missing_content(self):
        """Content is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentChatMessage.model_validate({"role": "user"})
        assert "Field required" in str(exc_info.value)


class TestAgentChatRequest:
    def test_agent_chat_request_valid_with_pointer(self):
        """Valid request with messages and pointer_id."""
        pointer_id = uuid4()
        data = AgentChatRequest.model_validate(
            {
                "messages": [
                    {"role": "user", "content": "Hello"},
                ],
                "pointer_id": pointer_id,
            }
        )
        assert len(data.messages) == 1
        assert data.messages[0].role == "user"
        assert data.pointer_id == pointer_id
        assert data.manifest_sha256 is None

    def test_agent_chat_request_valid_with_manifest(self):
        """Valid request with manifest_sha256."""
        data = AgentChatRequest.model_validate(
            {
                "messages": [
                    {"role": "user", "content": "Analyze this"},
                ],
                "manifest_sha256": "a" * 64,
            }
        )
        assert len(data.messages) == 1
        assert data.manifest_sha256 == "a" * 64
        assert data.pointer_id is None

    def test_agent_chat_request_multi_turn(self):
        """Request can include conversation history."""
        conv_id = uuid4()
        data = AgentChatRequest.model_validate(
            {
                "messages": [
                    {"role": "user", "content": "First question"},
                    {"role": "assistant", "content": "First answer"},
                    {"role": "user", "content": "Follow-up"},
                ],
                "conversation_id": conv_id,
            }
        )
        assert len(data.messages) == 3
        assert data.conversation_id == conv_id

    def test_agent_chat_request_with_session_id(self):
        """Request can include session_id."""
        session_id = uuid4()
        data = AgentChatRequest.model_validate(
            {
                "messages": [{"role": "user", "content": "Hello"}],
                "session_id": session_id,
            }
        )
        assert data.session_id == session_id

    def test_agent_chat_request_invalid_pointer_uuid(self):
        """Invalid UUID for pointer_id should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            AgentChatRequest.model_validate(
                {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "pointer_id": "not-a-uuid",
                }
            )
        assert "UUID" in str(exc_info.value) or "Input should be a valid UUID" in str(
            exc_info.value
        )

    def test_agent_chat_request_missing_messages(self):
        """messages field is required."""
        with pytest.raises(ValidationError) as exc_info:
            AgentChatRequest.model_validate({})
        assert "Field required" in str(exc_info.value)

    def test_agent_chat_request_empty_messages_allowed(self):
        """Empty messages list is technically valid (though API may reject)."""
        data = AgentChatRequest.model_validate({"messages": []})
        assert data.messages == []

    def test_agent_chat_request_all_optional_fields(self):
        """All context fields are optional."""
        data = AgentChatRequest.model_validate(
            {
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )
        assert data.pointer_id is None
        assert data.manifest_sha256 is None
        assert data.conversation_id is None
        assert data.session_id is None
