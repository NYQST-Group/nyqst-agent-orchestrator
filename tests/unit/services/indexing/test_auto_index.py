"""Unit tests for auto_index service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from intelli.services.indexing.auto_index import auto_index_manifest

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    """Mock database session."""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock()
    return session


@pytest.fixture
def mock_run_service():
    """Mock RunService."""
    service = MagicMock()
    run = MagicMock()
    run.id = uuid4()
    service.create_run = AsyncMock(return_value=run)
    service.start_run = AsyncMock()
    service.complete_run = AsyncMock()
    service.fail_run = AsyncMock()
    return service


@pytest.fixture
def mock_ledger_service():
    """Mock LedgerService."""
    return MagicMock()


@pytest.fixture
def mock_rag_service():
    """Mock RagService."""
    service = MagicMock()
    stats = MagicMock()
    stats.manifest_sha256 = "abc123"
    stats.artifacts_total = 10
    stats.artifacts_indexed = 8
    stats.artifacts_skipped = 2
    stats.chunks_created = 50
    service.index_manifest = AsyncMock(return_value=stats)
    return service


class TestAutoIndexManifest:
    async def test_skips_when_no_openai_key(self):
        with patch("intelli.services.indexing.auto_index.settings") as mock_settings:
            mock_settings.openai_api_key = None

            result = await auto_index_manifest(manifest_sha256="abc123")

            assert result is None

    async def test_returns_none_when_skipped(self):
        with patch("intelli.services.indexing.auto_index.settings") as mock_settings:
            mock_settings.openai_api_key = ""

            result = await auto_index_manifest(manifest_sha256="abc123")

            assert result is None

    async def test_creates_run_and_indexes_manifest(
        self,
        mock_session,
        mock_run_service,
        mock_ledger_service,
        mock_rag_service,
    ):
        with (
            patch("intelli.services.indexing.auto_index.settings") as mock_settings,
            patch("intelli.services.indexing.auto_index.AsyncSessionLocal") as mock_session_local,
            patch("intelli.services.indexing.auto_index.RunService") as mock_run_cls,
            patch("intelli.services.indexing.auto_index.LedgerService") as mock_ledger_cls,
            patch("intelli.services.indexing.auto_index.RagService") as mock_rag_cls,
        ):
            mock_settings.openai_api_key = "test-key"
            mock_settings.embedding_model = "text-embedding-3-small"
            # Mock the session context manager properly
            mock_session_cm = MagicMock()
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session_cm
            mock_run_cls.return_value = mock_run_service
            mock_ledger_cls.return_value = mock_ledger_service
            mock_rag_cls.return_value = mock_rag_service

            pointer_id = uuid4()
            result = await auto_index_manifest(
                manifest_sha256="abc123",
                pointer_id=pointer_id,
                profile="docs.default",
                reason="pointer_advance",
            )

            # Should create a run
            mock_run_service.create_run.assert_called_once()
            create_call = mock_run_service.create_run.call_args
            assert create_call[1]["run_type"] == "index_ingest"
            assert create_call[1]["config"]["profile"] == "docs.default"
            assert create_call[1]["config"]["reason"] == "pointer_advance"
            assert create_call[1]["input_manifest_sha256"] == "abc123"

            # Should start the run
            mock_run_service.start_run.assert_called_once()

            # Should index the manifest
            mock_rag_service.index_manifest.assert_called_once_with(
                "abc123",
                force=False,
                run_id=mock_run_service.create_run.return_value.id,
                ledger=mock_ledger_service,
            )

            # Should complete the run
            mock_run_service.complete_run.assert_called_once()
            complete_call = mock_run_service.complete_run.call_args
            # complete_run is called as: complete_run(run_id, result={...})
            assert complete_call.args[0] == mock_run_service.create_run.return_value.id
            assert "manifest_sha256" in complete_call.kwargs["result"]

            # Should return the run ID
            assert result == mock_run_service.create_run.return_value.id

    async def test_records_run_failure_on_exception(
        self,
        mock_session,
        mock_run_service,
        mock_ledger_service,
        mock_rag_service,
    ):
        # Create a proper async context manager
        async def mock_session_context():
            yield mock_session

        with (
            patch("intelli.services.indexing.auto_index.settings") as mock_settings,
            patch("intelli.services.indexing.auto_index.AsyncSessionLocal") as mock_session_local,
            patch("intelli.services.indexing.auto_index.RunService") as mock_run_cls,
            patch("intelli.services.indexing.auto_index.LedgerService") as mock_ledger_cls,
            patch("intelli.services.indexing.auto_index.RagService") as mock_rag_cls,
        ):
            mock_settings.openai_api_key = "test-key"
            mock_settings.embedding_model = "text-embedding-3-small"
            # Mock the session context manager properly
            mock_session_cm = MagicMock()
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session_cm
            mock_run_cls.return_value = mock_run_service
            mock_ledger_cls.return_value = mock_ledger_service
            mock_rag_cls.return_value = mock_rag_service

            # Make index_manifest raise an exception
            mock_rag_service.index_manifest.side_effect = ValueError("Test error")

            with pytest.raises(ValueError, match="Test error"):
                await auto_index_manifest(manifest_sha256="abc123")

            # Should mark the run as failed
            mock_run_service.fail_run.assert_called_once()
            fail_call = mock_run_service.fail_run.call_args
            assert fail_call.args[0] == mock_run_service.create_run.return_value.id
            assert fail_call.args[1]["type"] == "ValueError"
            assert fail_call.args[1]["message"] == "Test error"

    async def test_commits_on_success(
        self,
        mock_session,
        mock_run_service,
        mock_ledger_service,
        mock_rag_service,
    ):
        with (
            patch("intelli.services.indexing.auto_index.settings") as mock_settings,
            patch("intelli.services.indexing.auto_index.AsyncSessionLocal") as mock_session_local,
            patch("intelli.services.indexing.auto_index.RunService") as mock_run_cls,
            patch("intelli.services.indexing.auto_index.LedgerService") as mock_ledger_cls,
            patch("intelli.services.indexing.auto_index.RagService") as mock_rag_cls,
        ):
            mock_settings.openai_api_key = "test-key"
            mock_settings.embedding_model = "text-embedding-3-small"
            # Mock the session context manager properly
            mock_session_cm = MagicMock()
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session_cm
            mock_run_cls.return_value = mock_run_service
            mock_ledger_cls.return_value = mock_ledger_service
            mock_rag_cls.return_value = mock_rag_service

            await auto_index_manifest(manifest_sha256="abc123")

            # Should commit the session
            mock_session.commit.assert_called_once()
            mock_session.rollback.assert_not_called()

    async def test_rollbacks_on_failure(
        self,
        mock_session,
        mock_run_service,
        mock_ledger_service,
        mock_rag_service,
    ):
        with (
            patch("intelli.services.indexing.auto_index.settings") as mock_settings,
            patch("intelli.services.indexing.auto_index.AsyncSessionLocal") as mock_session_local,
            patch("intelli.services.indexing.auto_index.RunService") as mock_run_cls,
            patch("intelli.services.indexing.auto_index.LedgerService") as mock_ledger_cls,
            patch("intelli.services.indexing.auto_index.RagService") as mock_rag_cls,
        ):
            mock_settings.openai_api_key = "test-key"
            mock_settings.embedding_model = "text-embedding-3-small"
            # Mock the session context manager properly
            mock_session_cm = MagicMock()
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session_cm
            mock_run_cls.return_value = mock_run_service
            mock_ledger_cls.return_value = mock_ledger_service
            mock_rag_cls.return_value = mock_rag_service

            # Make index_manifest raise an exception
            mock_rag_service.index_manifest.side_effect = RuntimeError("Test error")

            with pytest.raises(RuntimeError):
                await auto_index_manifest(manifest_sha256="abc123")

            # Should rollback the session
            mock_session.rollback.assert_called_once()

    async def test_returns_run_id_on_success(
        self,
        mock_session,
        mock_run_service,
        mock_ledger_service,
        mock_rag_service,
    ):
        with (
            patch("intelli.services.indexing.auto_index.settings") as mock_settings,
            patch("intelli.services.indexing.auto_index.AsyncSessionLocal") as mock_session_local,
            patch("intelli.services.indexing.auto_index.RunService") as mock_run_cls,
            patch("intelli.services.indexing.auto_index.LedgerService") as mock_ledger_cls,
            patch("intelli.services.indexing.auto_index.RagService") as mock_rag_cls,
        ):
            mock_settings.openai_api_key = "test-key"
            mock_settings.embedding_model = "text-embedding-3-small"
            # Mock the session context manager properly
            mock_session_cm = MagicMock()
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session_cm
            mock_run_cls.return_value = mock_run_service
            mock_ledger_cls.return_value = mock_ledger_service
            mock_rag_cls.return_value = mock_rag_service

            expected_run_id = mock_run_service.create_run.return_value.id

            result = await auto_index_manifest(manifest_sha256="abc123")

            assert result == expected_run_id
