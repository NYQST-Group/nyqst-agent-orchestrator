"""Unit tests for storage factory."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from intelli.storage.local_storage import LocalStorageBackend
from intelli.storage.s3_storage import S3StorageBackend

pytestmark = pytest.mark.unit


class TestGetStorageBackend:
    def test_local_backend(self, tmp_path):
        with patch("intelli.storage.factory.settings") as mock_settings:
            mock_settings.storage_backend = "local"
            mock_settings.local_storage_path = str(tmp_path)
            # Clear lru_cache
            from intelli.storage.factory import get_storage_backend

            get_storage_backend.cache_clear()
            backend = get_storage_backend()
            assert isinstance(backend, LocalStorageBackend)
            get_storage_backend.cache_clear()

    def test_unknown_backend_raises(self):
        with patch("intelli.storage.factory.settings") as mock_settings:
            mock_settings.storage_backend = "azure"
            from intelli.storage.factory import get_storage_backend

            get_storage_backend.cache_clear()
            with pytest.raises(ValueError, match="Unknown storage backend"):
                get_storage_backend()
            get_storage_backend.cache_clear()

    def test_s3_backend(self):
        with patch("intelli.storage.factory.settings") as mock_settings:
            mock_settings.storage_backend = "s3"
            mock_settings.s3_endpoint_url = None
            mock_settings.s3_bucket = "test"
            mock_settings.s3_access_key = None
            mock_settings.s3_secret_key = None
            mock_settings.s3_region = "us-east-1"
            from intelli.storage.factory import get_storage_backend

            get_storage_backend.cache_clear()
            backend = get_storage_backend()
            assert isinstance(backend, S3StorageBackend)
            get_storage_backend.cache_clear()
