"""Local filesystem storage backend for development and testing."""

import os
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

import aiofiles
import aiofiles.os

from intelli.config import settings
from intelli.core.exceptions import NotFoundError, StorageError
from intelli.storage.base import StorageBackend, StorageMetadata


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend.

    Useful for development, testing, and single-node deployments.
    """

    def __init__(self, base_path: str | None = None):
        """Initialize local storage backend.

        Args:
            base_path: Base directory for storage (defaults to settings)
        """
        self.base_path = Path(base_path or settings.local_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        """Get the filesystem path for a key.

        Uses first 2 characters of key as subdirectory to avoid too many
        files in a single directory.
        """
        if len(key) >= 2:
            subdir = key[:2]
            return self.base_path / subdir / key
        return self.base_path / key

    def _get_uri(self, key: str) -> str:
        """Get the file URI for a key."""
        return f"file://{self._get_path(key)}"

    def _get_metadata_path(self, key: str) -> Path:
        """Get the metadata file path for a key."""
        return self._get_path(key).with_suffix(".meta")

    async def put(
        self,
        key: str,
        content: BinaryIO | bytes,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        """Store content on local filesystem."""
        try:
            file_path = self._get_path(key)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            body = content if isinstance(content, bytes) else content.read()
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(body)

            # Write metadata
            meta = {
                "content_type": content_type,
                "content_length": len(body),
                "created_at": datetime.now(timezone.utc).isoformat(),
                **(metadata or {}),
            }
            meta_path = self._get_metadata_path(key)
            async with aiofiles.open(meta_path, "w") as f:
                import json

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
        """Get content as bytes from local filesystem."""
        file_path = self._get_path(key)
        if not file_path.exists():
            raise NotFoundError(resource_type="artifact", identifier=key)

        try:
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()
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
                import json

                async with aiofiles.open(meta_path, "r") as f:
                    meta = json.loads(await f.read())
                return StorageMetadata(
                    content_type=meta.get("content_type", "application/octet-stream"),
                    content_length=meta.get("content_length", 0),
                    etag=None,
                    last_modified=datetime.fromisoformat(meta["created_at"])
                    if "created_at" in meta
                    else None,
                )

            # Fallback to file stats
            stat = await aiofiles.os.stat(file_path)
            return StorageMetadata(
                content_type="application/octet-stream",
                content_length=stat.st_size,
                etag=None,
                last_modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
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
