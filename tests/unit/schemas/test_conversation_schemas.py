"""Unit tests for conversation schemas — validation, defaults, extra field rejection."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from intelli.schemas.conversations import (
    BranchCreate,
    ConversationCreate,
    ConversationUpdate,
    FeedbackCreate,
    SiblingResponse,
)

pytestmark = pytest.mark.unit


class TestConversationCreate:
    def test_conversation_create_defaults(self):
        """Default scope_type=tenant, empty config_snapshot."""
        data = ConversationCreate.model_validate({})
        assert data.scope_type == "tenant"
        assert data.scope_id is None
        assert data.module is None
        assert data.title is None
        assert data.session_id is None
        assert data.config_snapshot == {}

    def test_conversation_create_extra_field_rejected(self):
        """extra='forbid' should reject unknown fields."""
        with pytest.raises(ValidationError) as exc_info:
            ConversationCreate.model_validate({"unknown_field": "value"})
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_conversation_create_all_fields(self):
        """All fields can be provided."""
        scope_id = uuid4()
        session_id = uuid4()
        data = ConversationCreate.model_validate(
            {
                "scope_type": "project",
                "scope_id": scope_id,
                "module": "research",
                "title": "Test Conversation",
                "session_id": session_id,
                "config_snapshot": {"model": "gpt-4"},
            }
        )
        assert data.scope_type == "project"
        assert data.scope_id == scope_id
        assert data.module == "research"
        assert data.title == "Test Conversation"
        assert data.session_id == session_id
        assert data.config_snapshot == {"model": "gpt-4"}


class TestConversationUpdate:
    def test_conversation_update_partial(self):
        """Update fields are all optional."""
        data = ConversationUpdate.model_validate({})
        assert data.title is None
        assert data.status is None

    def test_conversation_update_title_only(self):
        data = ConversationUpdate.model_validate({"title": "New Title"})
        assert data.title == "New Title"
        assert data.status is None

    def test_conversation_update_status_only(self):
        data = ConversationUpdate.model_validate({"status": "archived"})
        assert data.status == "archived"
        assert data.title is None

    def test_conversation_update_extra_field_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            ConversationUpdate.model_validate({"invalid": "field"})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestFeedbackCreate:
    def test_feedback_create_requires_rating(self):
        """Rating is required, content is optional."""
        with pytest.raises(ValidationError) as exc_info:
            FeedbackCreate.model_validate({})
        assert "Field required" in str(exc_info.value)

    def test_feedback_create_valid_positive(self):
        data = FeedbackCreate.model_validate({"rating": "positive"})
        assert data.rating == "positive"
        assert data.content is None

    def test_feedback_create_valid_negative_with_content(self):
        data = FeedbackCreate.model_validate(
            {
                "rating": "negative",
                "content": "This answer was incorrect.",
            }
        )
        assert data.rating == "negative"
        assert data.content == "This answer was incorrect."

    def test_feedback_create_extra_field_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            FeedbackCreate.model_validate({"rating": "positive", "extra": "bad"})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBranchCreate:
    def test_branch_create_requires_message_id(self):
        """message_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            BranchCreate.model_validate({})
        assert "Field required" in str(exc_info.value)

    def test_branch_create_valid(self):
        message_id = uuid4()
        data = BranchCreate.model_validate({"message_id": message_id})
        assert data.message_id == message_id

    def test_branch_create_extra_field_rejected(self):
        message_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            BranchCreate.model_validate({"message_id": message_id, "bad_field": "nope"})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestSiblingResponse:
    def test_sibling_response_structure(self):
        """SiblingResponse contains items, total, current_index."""
        data = SiblingResponse.model_validate(
            {
                "items": [],
                "total": 3,
                "current_index": 1,
            }
        )
        assert data.items == []
        assert data.total == 3
        assert data.current_index == 1

    def test_sibling_response_with_message(self):
        """Can include MessageResponse items."""
        message_data = {
            "id": str(uuid4()),
            "conversation_id": str(uuid4()),
            "role": "user",
            "content": "Hello",
            "parts": None,
            "input_tokens": None,
            "output_tokens": None,
            "cost_micros": None,
            "latency_ms": None,
            "model_id": None,
            "status": "complete",
            "parent_message_id": None,
            "sequence_number": 1,
            "created_at": "2026-02-03T12:00:00Z",
        }
        data = SiblingResponse.model_validate(
            {
                "items": [message_data],
                "total": 2,
                "current_index": 0,
            }
        )
        assert len(data.items) == 1
        assert data.items[0].role == "user"
