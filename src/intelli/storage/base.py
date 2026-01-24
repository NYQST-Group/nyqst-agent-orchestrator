"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO


@dataclass
class StorageMetadata:
    """Metadata for a stored object."""

    content_type: str
    content_length: int
    etag: str | None = None
    last_modified: datetime | None = None


class StorageBackend(ABC):
    """Abstract storage backend interface.

    All storage operations are content-addressed by key (typically SHA-256).
    """

    @abstractmethod
    async def put(
        self,
        key: str,
        content: BinaryIO | bytes,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        """Store content and return the storage URI.

        Args:
            key: Storage key (usually SHA-256 hash)
            content: File-like object or bytes to store
            content_type: MIME type of the content
            metadata: Optional metadata to store with the object

        Returns:
            Storage URI (e.g., s3://bucket/key)
        """
        pass

    @abstractmethod
    async def get(self, key: str) -> AsyncIterator[bytes]:
        """Stream content by key.

        Args:
            key: Storage key

        Yields:
            Chunks of content bytes
        """
        pass

    @abstractmethod
    async def get_bytes(self, key: str) -> bytes:
        """Get content as bytes.

        Args:
            key: Storage key

        Returns:
            Content bytes
        """
        pass

    @abstractmethod
    async def get_metadata(self, key: str) -> StorageMetadata | None:
        """Get object metadata without content.

        Args:
            key: Storage key

        Returns:
            StorageMetadata or None if not found
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if object exists.

        Args:
            key: Storage key

        Returns:
            True if exists
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete object.

        Args:
            key: Storage key

        Returns:
            True if object existed and was deleted
        """
        pass

    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        expiration_seconds: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a time-limited access URL.

        Args:
            key: Storage key
            expiration_seconds: URL validity duration
            method: HTTP method (GET or PUT)

        Returns:
            Pre-signed URL
        """
        pass
