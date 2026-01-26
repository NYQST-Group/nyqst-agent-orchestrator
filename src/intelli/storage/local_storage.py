"""Local filesystem storage backend using hashfs pattern.

Content-addressable storage with:
- 2-level directory sharding (ab/cd/abcdefgh...)
- Automatic deduplication
- Integrity verification on read
"""

import hashlib
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

import aiofiles
import aiofiles.os

from intelli.config import settings
from intelli.core.exceptions import NotFoundError, StorageError
from intelli.storage.base import StorageBackend, StorageMetadata


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend with hashfs pattern.

    Uses 2-level directory sharding for efficient file distribution:
    - Level 1: First 2 hex chars
    - Level 2: Next 2 hex chars
    - Filename: Full hash

    Example: sha256 "abcd1234..." -> ab/cd/abcd1234...

    This is inspired by the hashfs library and git's object store pattern.
    """

    def __init__(self, base_path: str | None = None, verify_on_read: bool = True):
        """Initialize local storage backend.

        Args:
            base_path: Base directory for storage (defaults to settings)
            verify_on_read: Verify content hash on read operations
        """
        self.base_path = Path(base_path or settings.local_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.verify_on_read = verify_on_read

    def _get_path(self, key: str) -> Path:
        """Get the filesystem path for a key using 2-level sharding.

        Uses first 4 characters of key split into 2 levels (ab/cd/full_key)
        to distribute files and avoid filesystem bottlenecks.
        """
        if len(key) >= 4:
            level1 = key[:2]
            level2 = key[2:4]
            return self.base_path / level1 / level2 / key
        elif len(key) >= 2:
            return self.base_path / key[:2] / key
        return self.base_path / key

    def _get_uri(self, key: str) -> str:
        """Get the file URI for a key."""
        return f"file://{self._get_path(key)}"

    def _get_metadata_path(self, key: str) -> Path:
        """Get the metadata file path for a key."""
        return self._get_path(key).with_suffix(".meta")

    def _verify_hash(self, key: str, content: bytes) -> bool:
        """Verify content matches expected hash.

        Args:
            key: Expected SHA-256 hash (hex encoded)
            content: Content to verify

        Returns:
            True if hash matches
        """
        actual_hash = hashlib.sha256(content).hexdigest()
        return actual_hash == key

    async def put(
        self,
        key: str,
        content: BinaryIO | bytes,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        """Store content on local filesystem.

        If content already exists (same hash), skips write (deduplication).
        """
        try:
            file_path = self._get_path(key)

            # Deduplication: if file already exists with matching hash, skip write
            if file_path.exists():
                return self._get_uri(key)

            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Get content bytes
            body = content if isinstance(content, bytes) else content.read()

            # Verify hash matches key (content-addressable invariant)
            if not self._verify_hash(key, body):
                raise StorageError(
                    message="Content hash does not match key",
                    operation="put",
                    details={"key": key, "actual_hash": hashlib.sha256(body).hexdigest()},
                )

            # Write content
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(body)

            # Write metadata
            meta = {
                "content_type": content_type,
                "content_length": len(body),
                "created_at": datetime.now(UTC).isoformat(),
                **(metadata or {}),
            }
            meta_path = self._get_metadata_path(key)
            async with aiofiles.open(meta_path, "w") as f:
                await f.write(json.dumps(meta))

            return self._get_uri(key)
        except OSError as e:
            raise StorageError(
                message=f"Failed to put object: {e}",
                operation="put",
            ) from e

    async def get(self, key: str) -> AsyncIterator[bytes]:
        """Stream content from local filesystem."""
        file_path = self._get_path(key)
        if not file_path.exists():
            raise NotFoundError(resource_type="artifact", identifier=key)

        try:
            async with aiofiles.open(file_path, "rb") as f:
                while chunk := await f.read(65536):  # 64KB chunks
                    yield chunk
        except OSError as e:
            raise StorageError(
                message=f"Failed to get object: {e}",
                operation="get",
            ) from e

    async def get_bytes(self, key: str) -> bytes:
        """Get content as bytes from local filesystem.

        Verifies content hash matches key if verify_on_read is enabled.
        """
        file_path = self._get_path(key)
        if not file_path.exists():
            raise NotFoundError(resource_type="artifact", identifier=key)

        try:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()

            # Verify integrity
            if self.verify_on_read and not self._verify_hash(key, content):
                raise StorageError(
                    message="Content integrity check failed: hash mismatch",
                    operation="get_bytes",
                    details={"key": key},
                )

            return content
        except OSError as e:
            raise StorageError(
                message=f"Failed to get object: {e}",
                operation="get_bytes",
            ) from e

    async def get_metadata(self, key: str) -> StorageMetadata | None:
        """Get object metadata from local filesystem."""
        file_path = self._get_path(key)
        meta_path = self._get_metadata_path(key)

        if not file_path.exists():
            return None

        try:
            # Read metadata file if exists
            if meta_path.exists():
                async with aiofiles.open(meta_path) as f:
                    meta = json.loads(await f.read())
                return StorageMetadata(
                    content_type=meta.get("content_type", "application/octet-stream"),
                    content_length=meta.get("content_length", 0),
                    etag=key,  # Use content hash as ETag
                    last_modified=datetime.fromisoformat(meta["created_at"])
                    if "created_at" in meta
                    else None,
                )

            # Fallback to file stats
            stat = await aiofiles.os.stat(file_path)
            return StorageMetadata(
                content_type="application/octet-stream",
                content_length=stat.st_size,
                etag=key,
                last_modified=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
            )
        except OSError as e:
            raise StorageError(
                message=f"Failed to get metadata: {e}",
                operation="get_metadata",
            ) from e

    async def exists(self, key: str) -> bool:
        """Check if object exists on local filesystem."""
        return self._get_path(key).exists()

    async def delete(self, key: str) -> bool:
        """Delete object from local filesystem."""
        file_path = self._get_path(key)
        meta_path = self._get_metadata_path(key)

        if not file_path.exists():
            return False

        try:
            await aiofiles.os.remove(file_path)
            if meta_path.exists():
                await aiofiles.os.remove(meta_path)
            return True
        except OSError as e:
            raise StorageError(
                message=f"Failed to delete object: {e}",
                operation="delete",
            ) from e

    async def generate_presigned_url(
        self,
        key: str,
        expiration_seconds: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate file URL (no actual signing for local storage).

        Note: For local storage, this just returns the file path.
        In a real deployment, you'd need a web server to serve these files.
        """
        file_path = self._get_path(key)
        if not file_path.exists():
            raise NotFoundError(resource_type="artifact", identifier=key)
        return f"file://{file_path}"

    async def cleanup_empty_dirs(self) -> int:
        """Clean up empty directories from the storage tree.

        Returns:
            Number of directories removed
        """
        removed = 0
        for level1 in self.base_path.iterdir():
            if not level1.is_dir():
                continue
            for level2 in level1.iterdir():
                if not level2.is_dir():
                    continue
                # Remove empty level2 directories
                if not any(level2.iterdir()):
                    level2.rmdir()
                    removed += 1
            # Remove empty level1 directories
            if not any(level1.iterdir()):
                level1.rmdir()
                removed += 1
        return removed
