"""Unit tests for session schemas — validation, defaults, extra field rejection."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from intelli.schemas.sessions import (
    SessionCostBreakdown,
    SessionCreate,
    SessionUpdate,
)

pytestmark = pytest.mark.unit


class TestSessionCreate:
    def test_session_create_defaults(self):
        """Default scope_type=tenant, config_snapshot={}, idle_timeout_minutes=30."""
        data = SessionCreate.model_validate({})
        assert data.scope_type == "tenant"
        assert data.scope_id is None
        assert data.module is None
        assert data.objective is None
        assert data.config_snapshot == {}
        assert data.idle_timeout_minutes == 30

    def test_session_create_extra_field_rejected(self):
        """extra='forbid' should reject unknown fields."""
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate.model_validate({"unknown": "field"})
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_session_create_all_fields(self):
        """All fields can be provided."""
        scope_id = uuid4()
        data = SessionCreate.model_validate(
            {
                "scope_type": "project",
                "scope_id": scope_id,
                "module": "analysis",
                "objective": "Analyze market trends",
                "config_snapshot": {"model": "claude-3"},
                "idle_timeout_minutes": 60,
            }
        )
        assert data.scope_type == "project"
        assert data.scope_id == scope_id
        assert data.module == "analysis"
        assert data.objective == "Analyze market trends"
        assert data.config_snapshot == {"model": "claude-3"}
        assert data.idle_timeout_minutes == 60


class TestSessionUpdate:
    def test_session_update_requires_status(self):
        """Status field is required."""
        with pytest.raises(ValidationError) as exc_info:
            SessionUpdate.model_validate({})
        assert "Field required" in str(exc_info.value)

    def test_session_update_status_only(self):
        data = SessionUpdate.model_validate({"status": "closed"})
        assert data.status == "closed"
        assert data.close_reason is None

    def test_session_update_with_close_reason(self):
        data = SessionUpdate.model_validate(
            {
                "status": "closed",
                "close_reason": "User requested",
            }
        )
        assert data.status == "closed"
        assert data.close_reason == "User requested"

    def test_session_update_extra_field_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            SessionUpdate.model_validate({"status": "active", "bad": "field"})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestSessionCostBreakdown:
    def test_session_cost_breakdown_structure(self):
        """SessionCostBreakdown has required fields and default conversations list."""
        session_id = uuid4()
        data = SessionCostBreakdown.model_validate(
            {
                "session_id": session_id,
                "total_cost_micros": 5000,
                "conversation_count": 2,
                "total_input_tokens": 100,
                "total_output_tokens": 150,
            }
        )
        assert data.session_id == session_id
        assert data.total_cost_micros == 5000
        assert data.conversation_count == 2
        assert data.total_input_tokens == 100
        assert data.total_output_tokens == 150
        assert data.conversations == []

    def test_session_cost_breakdown_with_conversations(self):
        """Conversations field can contain per-conversation cost data."""
        session_id = uuid4()
        conv_id = uuid4()
        data = SessionCostBreakdown.model_validate(
            {
                "session_id": session_id,
                "total_cost_micros": 10000,
                "conversation_count": 1,
                "total_input_tokens": 200,
                "total_output_tokens": 300,
                "conversations": [
                    {
                        "id": str(conv_id),
                        "title": "Test Conversation",
                        "cost_micros": 10000,
                        "input_tokens": 200,
                        "output_tokens": 300,
                    }
                ],
            }
        )
        assert len(data.conversations) == 1
        assert data.conversations[0].id == conv_id
        assert data.conversations[0].cost_micros == 10000
