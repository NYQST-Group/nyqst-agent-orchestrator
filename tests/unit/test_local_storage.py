"""Unit tests for LocalStorageBackend — content-addressed filesystem storage."""

from __future__ import annotations

import hashlib

import pytest
import pytest_asyncio

from intelli.core.exceptions import NotFoundError, StorageError
from intelli.storage.local_storage import LocalStorageBackend

pytestmark = pytest.mark.unit


@pytest_asyncio.fixture
async def storage(tmp_path):
    """Create a local storage backend in a temp directory."""
    return LocalStorageBackend(base_path=str(tmp_path), verify_on_read=True)


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class TestPut:
    async def test_put_stores_file(self, storage):
        content = b"hello world"
        key = _sha(content)
        uri = await storage.put(key, content, "text/plain")
        assert uri.startswith("file://")

    async def test_put_deduplicates(self, storage):
        content = b"dedup me"
        key = _sha(content)
        uri1 = await storage.put(key, content, "text/plain")
        uri2 = await storage.put(key, content, "text/plain")
        assert uri1 == uri2

    async def test_put_rejects_hash_mismatch(self, storage):
        with pytest.raises(StorageError, match="hash does not match"):
            await storage.put("wrong_key_1234", b"data", "text/plain")


class TestGetBytes:
    async def test_get_bytes_roundtrip(self, storage):
        content = b"round trip content"
        key = _sha(content)
        await storage.put(key, content, "application/octet-stream")
        result = await storage.get_bytes(key)
        assert result == content

    async def test_get_bytes_missing_raises(self, storage):
        with pytest.raises(NotFoundError):
            await storage.get_bytes("nonexistent_key")

    async def test_get_bytes_integrity_check(self, storage, tmp_path):
        content = b"integrity check"
        key = _sha(content)
        await storage.put(key, content, "text/plain")
        # Corrupt the file
        file_path = storage._get_path(key)
        file_path.write_bytes(b"corrupted!")
        with pytest.raises(StorageError, match="integrity"):
            await storage.get_bytes(key)


class TestDelete:
    async def test_delete_existing(self, storage):
        content = b"delete me"
        key = _sha(content)
        await storage.put(key, content, "text/plain")
        assert await storage.delete(key) is True
        assert await storage.exists(key) is False

    async def test_delete_nonexistent(self, storage):
        assert await storage.delete("nope") is False


class TestExists:
    async def test_exists_true(self, storage):
        content = b"exists check"
        key = _sha(content)
        await storage.put(key, content, "text/plain")
        assert await storage.exists(key) is True

    async def test_exists_false(self, storage):
        assert await storage.exists("nope") is False


class TestMetadata:
    async def test_get_metadata(self, storage):
        content = b"metadata test"
        key = _sha(content)
        await storage.put(key, content, "application/pdf")
        meta = await storage.get_metadata(key)
        assert meta is not None
        assert meta.content_type == "application/pdf"
        assert meta.content_length == len(content)

    async def test_metadata_missing_returns_none(self, storage):
        assert await storage.get_metadata("missing") is None


class TestSharding:
    def test_path_uses_two_level_sharding(self, storage):
        key = "abcdef1234567890" * 4
        path = storage._get_path(key)
        parts = path.parts
        assert "ab" in parts
        assert "cd" in parts
