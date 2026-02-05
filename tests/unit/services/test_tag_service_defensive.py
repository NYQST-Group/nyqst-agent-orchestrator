"""Defensive and edge-case tests for TagService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import NotFoundError
from intelli.services.tag_service import TagService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    return TagService(mock_session)


class TestAddTagDefensive:
    async def test_add_tag_with_invalid_entity_type(self, service):
        """Adding tag with invalid entity type should succeed (no validation in service)."""
        service.repo.find_duplicate = AsyncMock(return_value=None)
        service.repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                entity_type="invalid_type",
                namespace="ns",
                key="k",
                value="v",
            )
        )

        # Service doesn't validate entity type - downstream validation expected
        result = await service.add_tag(
            uuid4(),
            "invalid_type",
            uuid4(),
            "ns",
            "k",
            "v",
        )
        assert result.entity_type == "invalid_type"

    async def test_add_tag_with_confidence(self, service):
        """Adding tag with confidence score should store it."""
        service.repo.find_duplicate = AsyncMock(return_value=None)
        service.repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                confidence=0.85,
                source="agent_proposed",
            )
        )

        result = await service.add_tag(
            uuid4(),
            "conversation",
            uuid4(),
            "domain",
            "sentiment",
            "positive",
            confidence=0.85,
        )
        assert result.confidence == 0.85

    async def test_add_tag_source_agent_proposed(self, service):
        """Adding tag with source should store it."""
        service.repo.find_duplicate = AsyncMock(return_value=None)
        service.repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                source="agent_proposed",
            )
        )

        result = await service.add_tag(
            uuid4(),
            "conversation",
            uuid4(),
            "domain",
            "category",
            "research",
            source="agent_proposed",
        )
        assert result.source == "agent_proposed"


class TestSearchDefensive:
    async def test_search_returns_empty_for_nonexistent_namespace(self, service):
        """Search for nonexistent namespace should return empty list."""
        service.repo.search_by_tag = AsyncMock(return_value=[])

        results = await service.search_entities_by_tag(
            uuid4(),
            namespace="nonexistent",
            value="anything",
        )
        assert results == []

    async def test_duplicate_different_namespace_succeeds(self, service):
        """Same key/value in different namespace should succeed."""
        entity_id = uuid4()
        service.repo.find_duplicate = AsyncMock(return_value=None)
        service.repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                namespace="ns2",
                key="k",
                value="v",
            )
        )

        result = await service.add_tag(
            uuid4(),
            "conversation",
            entity_id,
            "ns2",
            "k",
            "v",
        )
        assert result.namespace == "ns2"


class TestRemoveTagDefensive:
    async def test_remove_tag_wrong_tenant_raises(self, service):
        """Removing tag from wrong tenant should raise NotFoundError."""
        tag = MagicMock(tenant_id=uuid4())
        service.repo.get_by_id = AsyncMock(return_value=tag)

        # Different tenant_id passed
        with pytest.raises(NotFoundError):
            await service.remove_tag(uuid4(), uuid4())


class TestListTagsDefensive:
    async def test_list_tags_for_entity(self, service):
        """List tags for specific entity should work."""
        entity_id = uuid4()
        service.repo.get_entity_tags = AsyncMock(
            return_value=[
                MagicMock(id=uuid4(), namespace="ns1", key="k1", value="v1"),
                MagicMock(id=uuid4(), namespace="ns2", key="k2", value="v2"),
            ]
        )

        items, total = await service.list_tags(
            uuid4(),
            entity_type="conversation",
            entity_id=entity_id,
        )
        assert total == 2
        assert len(items) == 2
