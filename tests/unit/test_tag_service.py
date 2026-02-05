"""Unit tests for TagService."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from intelli.core.exceptions import ConflictError, NotFoundError
from intelli.services.tag_service import TagService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    return TagService(mock_session)


class TestAddTag:
    async def test_creates_tag(self, service):
        service.repo.find_duplicate = AsyncMock(return_value=None)
        service.repo.create = AsyncMock(
            return_value=MagicMock(
                id=uuid4(),
                namespace="domain",
                key="asset_class",
                value="logistics",
            )
        )

        result = await service.add_tag(
            uuid4(),
            "conversation",
            uuid4(),
            "domain",
            "asset_class",
            "logistics",
        )
        assert result.namespace == "domain"

    async def test_raises_conflict_on_duplicate(self, service):
        service.repo.find_duplicate = AsyncMock(return_value=MagicMock())

        with pytest.raises(ConflictError):
            await service.add_tag(
                uuid4(),
                "conversation",
                uuid4(),
                "domain",
                "asset_class",
                "logistics",
            )


class TestRemoveTag:
    async def test_removes_by_id(self, service):
        tenant_id = uuid4()
        tag = MagicMock(tenant_id=tenant_id)
        service.repo.get_by_id = AsyncMock(return_value=tag)
        service.repo.delete = AsyncMock()

        await service.remove_tag(uuid4(), tenant_id)
        service.repo.delete.assert_called_once_with(tag)

    async def test_raises_not_found(self, service):
        service.repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.remove_tag(uuid4(), uuid4())


class TestSearch:
    async def test_cross_entity_search(self, service):
        tid = uuid4()
        conv_id = uuid4()
        art_id = uuid4()

        tag1 = MagicMock(entity_type="conversation", entity_id=conv_id)
        tag2 = MagicMock(entity_type="artifact", entity_id=art_id)

        service.repo.search_by_tag = AsyncMock(return_value=[tag1, tag2])

        results = await service.search_entities_by_tag(
            tid,
            namespace="domain",
            value="logistics",
        )
        assert len(results) == 2
        entity_types = {r["entity_type"] for r in results}
        assert entity_types == {"conversation", "artifact"}


class TestTagEdgeCases:
    async def test_search_returns_empty_for_nonexistent_namespace(self, service):
        service.repo.search_by_tag = AsyncMock(return_value=[])

        results = await service.search_entities_by_tag(
            uuid4(),
            namespace="nonexistent",
            value="anything",
        )
        assert results == []

    async def test_duplicate_different_namespace_succeeds(self, service):
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
