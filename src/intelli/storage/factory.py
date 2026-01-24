"""Factory for creating storage backends."""

from functools import lru_cache

from intelli.config import settings
from intelli.storage.base import StorageBackend
from intelli.storage.local_storage import LocalStorageBackend
from intelli.storage.s3_storage import S3StorageBackend


@lru_cache
def get_storage_backend() -> StorageBackend:
    """Get the configured storage backend.

    Returns:
        StorageBackend instance based on settings.storage_backend
    """
    if settings.storage_backend == "s3":
        return S3StorageBackend()
    elif settings.storage_backend == "local":
        return LocalStorageBackend()
    else:
        raise ValueError(f"Unknown storage backend: {settings.storage_backend}")
