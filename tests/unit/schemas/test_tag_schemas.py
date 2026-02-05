"""Unit tests for tag schemas — validation, defaults, extra field rejection."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from intelli.schemas.tags import TagCreate

pytestmark = pytest.mark.unit


class TestTagCreate:
    def test_tag_create_all_fields(self):
        """All required fields provided."""
        entity_id = uuid4()
        data = TagCreate.model_validate(
            {
                "entity_type": "document",
                "entity_id": entity_id,
                "namespace": "domain",
                "key": "industry",
                "value": "real_estate",
            }
        )
        assert data.entity_type == "document"
        assert data.entity_id == entity_id
        assert data.namespace == "domain"
        assert data.key == "industry"
        assert data.value == "real_estate"
        assert data.source == "manual"  # default
        assert data.confidence is None

    def test_tag_create_default_source(self):
        """source defaults to 'manual'."""
        entity_id = uuid4()
        data = TagCreate.model_validate(
            {
                "entity_type": "artifact",
                "entity_id": entity_id,
                "namespace": "asset_class",
                "key": "type",
                "value": "lease",
            }
        )
        assert data.source == "manual"

    def test_tag_create_agent_proposed_with_confidence(self):
        """Agent-proposed tag with confidence score."""
        entity_id = uuid4()
        data = TagCreate.model_validate(
            {
                "entity_type": "chunk",
                "entity_id": entity_id,
                "namespace": "topic",
                "key": "subject",
                "value": "insurance",
                "source": "agent_proposed",
                "confidence": 0.85,
            }
        )
        assert data.source == "agent_proposed"
        assert data.confidence == 0.85

    def test_tag_create_system_source(self):
        """System-generated tag."""
        entity_id = uuid4()
        data = TagCreate.model_validate(
            {
                "entity_type": "manifest",
                "entity_id": entity_id,
                "namespace": "metadata",
                "key": "file_count",
                "value": "42",
                "source": "system",
            }
        )
        assert data.source == "system"

    def test_tag_create_missing_required_field(self):
        """Missing entity_type should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate.model_validate(
                {
                    "entity_id": str(uuid4()),
                    "namespace": "domain",
                    "key": "industry",
                    "value": "tech",
                }
            )
        assert "Field required" in str(exc_info.value)

    def test_tag_create_invalid_entity_id(self):
        """Invalid UUID for entity_id should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate.model_validate(
                {
                    "entity_type": "document",
                    "entity_id": "not-a-uuid",
                    "namespace": "domain",
                    "key": "industry",
                    "value": "tech",
                }
            )
        assert "UUID" in str(exc_info.value) or "Input should be a valid UUID" in str(
            exc_info.value
        )

    def test_tag_create_extra_field_rejected(self):
        """extra='forbid' should reject unknown fields."""
        entity_id = uuid4()
        with pytest.raises(ValidationError) as exc_info:
            TagCreate.model_validate(
                {
                    "entity_type": "document",
                    "entity_id": entity_id,
                    "namespace": "domain",
                    "key": "industry",
                    "value": "tech",
                    "unknown_field": "rejected",
                }
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_tag_create_confidence_range(self):
        """Confidence is only valid for agent_proposed source."""
        entity_id = uuid4()
        data = TagCreate.model_validate(
            {
                "entity_type": "document",
                "entity_id": entity_id,
                "namespace": "domain",
                "key": "industry",
                "value": "tech",
                "source": "agent_proposed",
                "confidence": 0.95,
            }
        )
        assert data.confidence == 0.95
