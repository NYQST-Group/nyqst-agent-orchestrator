"""Unit tests for RAG schemas — validation, required fields, validators."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from intelli.schemas.rag import (
    RagAskRequest,
    RagIndexRequest,
)

pytestmark = pytest.mark.unit


class TestRagIndexRequest:
    def test_rag_index_request_valid_with_pointer(self):
        """Valid request with pointer_id."""
        pointer_id = uuid4()
        data = RagIndexRequest.model_validate(
            {
                "pointer_id": pointer_id,
            }
        )
        assert data.pointer_id == pointer_id
        assert data.manifest_sha256 is None
        assert data.force is False

    def test_rag_index_request_valid_with_manifest(self):
        """Valid request with manifest_sha256."""
        data = RagIndexRequest.model_validate(
            {
                "manifest_sha256": "a" * 64,
            }
        )
        assert data.manifest_sha256 == "a" * 64
        assert data.pointer_id is None
        assert data.force is False

    def test_rag_index_request_with_force(self):
        """force flag can be set to True."""
        pointer_id = uuid4()
        data = RagIndexRequest.model_validate(
            {
                "pointer_id": pointer_id,
                "force": True,
            }
        )
        assert data.force is True

    def test_rag_index_request_missing_both_targets(self):
        """Validator should reject when neither pointer_id nor manifest_sha256 provided."""
        with pytest.raises(ValidationError) as exc_info:
            RagIndexRequest.model_validate({})
        assert "Provide pointer_id or manifest_sha256" in str(exc_info.value)

    def test_rag_index_request_both_targets_allowed(self):
        """Both pointer_id and manifest_sha256 can be provided (pointer wins)."""
        pointer_id = uuid4()
        data = RagIndexRequest.model_validate(
            {
                "pointer_id": pointer_id,
                "manifest_sha256": "b" * 64,
            }
        )
        assert data.pointer_id == pointer_id
        assert data.manifest_sha256 == "b" * 64

    def test_rag_index_request_extra_field_rejected(self):
        """extra='forbid' should reject unknown fields."""
        pointer_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            RagIndexRequest.model_validate(
                {
                    "pointer_id": pointer_id,
                    "bad_field": "nope",
                }
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRagAskRequest:
    def test_rag_ask_request_valid_with_pointer(self):
        """Valid request with pointer_id and question."""
        pointer_id = uuid4()
        data = RagAskRequest.model_validate(
            {
                "pointer_id": pointer_id,
                "question": "What are the key terms?",
            }
        )
        assert data.pointer_id == pointer_id
        assert data.question == "What are the key terms?"
        assert data.manifest_sha256 is None
        assert data.top_k == 8  # default

    def test_rag_ask_request_valid_with_manifest(self):
        """Valid request with manifest_sha256."""
        data = RagAskRequest.model_validate(
            {
                "manifest_sha256": "c" * 64,
                "question": "Summarize this document",
            }
        )
        assert data.manifest_sha256 == "c" * 64
        assert data.question == "Summarize this document"
        assert data.pointer_id is None

    def test_rag_ask_request_question_required(self):
        """question field is required."""
        pointer_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            RagAskRequest.model_validate(
                {
                    "pointer_id": pointer_id,
                }
            )
        assert "Field required" in str(exc_info.value)

    def test_rag_ask_request_question_min_length(self):
        """question must have min_length=1."""
        pointer_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            RagAskRequest.model_validate(
                {
                    "pointer_id": pointer_id,
                    "question": "",
                }
            )
        assert "at least 1 character" in str(exc_info.value)

    def test_rag_ask_request_custom_top_k(self):
        """top_k can be customized."""
        pointer_id = uuid4()
        data = RagAskRequest.model_validate(
            {
                "pointer_id": pointer_id,
                "question": "What is this?",
                "top_k": 20,
            }
        )
        assert data.top_k == 20

    def test_rag_ask_request_top_k_min_constraint(self):
        """top_k must be >= 1."""
        pointer_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            RagAskRequest.model_validate(
                {
                    "pointer_id": pointer_id,
                    "question": "Test",
                    "top_k": 0,
                }
            )
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_rag_ask_request_top_k_max_constraint(self):
        """top_k must be <= 50."""
        pointer_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            RagAskRequest.model_validate(
                {
                    "pointer_id": pointer_id,
                    "question": "Test",
                    "top_k": 100,
                }
            )
        assert "less than or equal to 50" in str(exc_info.value)

    def test_rag_ask_request_missing_both_targets(self):
        """Validator should reject when neither pointer_id nor manifest_sha256 provided."""
        with pytest.raises(ValidationError) as exc_info:
            RagAskRequest.model_validate(
                {
                    "question": "What is this?",
                }
            )
        assert "Provide pointer_id or manifest_sha256" in str(exc_info.value)

    def test_rag_ask_request_extra_field_rejected(self):
        """extra='forbid' should reject unknown fields."""
        pointer_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            RagAskRequest.model_validate(
                {
                    "pointer_id": pointer_id,
                    "question": "Test",
                    "invalid": "field",
                }
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)
