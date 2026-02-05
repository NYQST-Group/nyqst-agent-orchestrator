"""Unit tests for ArtifactService — business logic with mocked repo and storage."""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock

import pytest

from intelli.core.exceptions import NotFoundError
from intelli.services.substrate.artifact_service import ArtifactService

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_by_sha256 = AsyncMock(return_value=None)
    repo.create_artifact = AsyncMock()
    repo.increment_reference_count = AsyncMock()
    repo.exists = AsyncMock(return_value=False)
    repo.delete = AsyncMock()
    repo.list_all = AsyncMock(return_value=[])
    repo.list_by_media_type = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_storage():
    storage = AsyncMock()
    storage.put = AsyncMock(return_value="file:///tmp/test")
    storage.get_bytes = AsyncMock(return_value=b"content")
    storage.generate_presigned_url = AsyncMock(return_value="https://url")
    storage.delete = AsyncMock(return_value=True)
    return storage


@pytest.fixture
def service(mock_repo, mock_storage):
    svc = ArtifactService.__new__(ArtifactService)
    svc.repo = mock_repo
    svc.storage = mock_storage
    return svc


class TestUploadArtifact:
    async def test_upload_new_artifact(self, service, mock_repo, mock_storage):
        content = b"new content"
        result = await service.upload_artifact(content, filename="test.txt")
        assert result.is_duplicate is False
        assert result.sha256 == hashlib.sha256(content).hexdigest()
        mock_repo.create_artifact.assert_called_once()
        mock_storage.put.assert_called_once()

    async def test_upload_duplicate_returns_existing(self, service, mock_repo):
        existing = MagicMock()
        existing.storage_uri = "file:///existing"
        mock_repo.get_by_sha256.return_value = existing

        result = await service.upload_artifact(b"dup content")
        assert result.is_duplicate is True
        mock_repo.increment_reference_count.assert_called_once()

    async def test_upload_with_url_generation(self, service, mock_storage):
        result = await service.upload_artifact(b"data", generate_url=True)
        assert result.content_url == "https://url"
        mock_storage.generate_presigned_url.assert_called_once()


class TestGetArtifact:
    async def test_get_existing(self, service, mock_repo):
        artifact = MagicMock()
        mock_repo.get_by_sha256.return_value = artifact
        result = await service.get_artifact("abc123")
        assert result is artifact

    async def test_get_missing_raises(self, service, mock_repo):
        mock_repo.get_by_sha256.return_value = None
        with pytest.raises(NotFoundError):
            await service.get_artifact("missing")


class TestGetContent:
    async def test_get_content(self, service, mock_repo, mock_storage):
        mock_repo.get_by_sha256.return_value = MagicMock()
        result = await service.get_content("sha")
        assert result == b"content"

    async def test_get_content_missing_artifact_raises(self, service, mock_repo):
        mock_repo.get_by_sha256.return_value = None
        with pytest.raises(NotFoundError):
            await service.get_content("missing")


class TestDeleteArtifact:
    async def test_delete_unreferenced(self, service, mock_repo, mock_storage):
        artifact = MagicMock()
        artifact.reference_count = 0
        mock_repo.get_by_sha256.return_value = artifact
        assert await service.delete_artifact("sha") is True
        mock_storage.delete.assert_called_once()

    async def test_delete_referenced_returns_false(self, service, mock_repo):
        artifact = MagicMock()
        artifact.reference_count = 5
        mock_repo.get_by_sha256.return_value = artifact
        assert await service.delete_artifact("sha") is False

    async def test_delete_force(self, service, mock_repo, mock_storage):
        artifact = MagicMock()
        artifact.reference_count = 5
        mock_repo.get_by_sha256.return_value = artifact
        assert await service.delete_artifact("sha", force=True) is True


class TestListArtifacts:
    async def test_list_all(self, service, mock_repo):
        await service.list_artifacts()
        mock_repo.list_all.assert_called_once_with(100, 0)

    async def test_list_by_media_type(self, service, mock_repo):
        await service.list_artifacts(media_type="application/pdf")
        mock_repo.list_by_media_type.assert_called_once_with("application/pdf", 100, 0)
