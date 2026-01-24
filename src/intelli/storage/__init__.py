"""Storage abstraction layer for artifact content."""

from intelli.storage.base import StorageBackend, StorageMetadata
from intelli.storage.factory import get_storage_backend

__all__ = ["StorageBackend", "StorageMetadata", "get_storage_backend"]
