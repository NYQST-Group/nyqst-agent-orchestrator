"""Unit tests for RAG API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from intelli.api.dependencies import get_session
from intelli.api.middleware.auth import authenticate
from intelli.core.context import RequestContext
from intelli.main import create_app

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

_TEST_TENANT_ID = uuid4()
_TEST_USER_ID = uuid4()


@pytest.fixture
async def mock_client():
    """Create test client without database setup."""
    app = create_app()

    # Mock the get_session dependency to avoid database
    async def mock_get_session():
        mock_session = AsyncMock()
        yield mock_session

    # Mock authentication to bypass auth middleware
    async def mock_authenticate():
        return RequestContext(
            tenant_id=_TEST_TENANT_ID,
            user_id=_TEST_USER_ID,
            role="admin",
            scopes=["read", "write"],
        )

    app.dependency_overrides[get_session] = mock_get_session
    app.dependency_overrides[authenticate] = mock_authenticate

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


class TestIndexEndpoint:
    """Tests for POST /rag/index endpoint."""

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_index_with_pointer_id_resolves_and_indexes(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test indexing with pointer_id resolves pointer and indexes manifest."""
        pointer_id = uuid4()
        manifest_sha256 = "abc123"
        run_id = uuid4()

        # Mock pointer resolution
        mock_pointer = MagicMock()
        mock_pointer.manifest_sha256 = manifest_sha256
        mock_pointer_instance = mock_pointer_service.return_value
        mock_pointer_instance.get_pointer_by_id = AsyncMock(return_value=mock_pointer)

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.complete_run = AsyncMock()

        # Mock RAG indexing
        mock_stats = MagicMock()
        mock_stats.manifest_sha256 = manifest_sha256
        mock_stats.artifacts_total = 10
        mock_stats.artifacts_indexed = 8
        mock_stats.artifacts_skipped = 2
        mock_stats.chunks_created = 50
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.index_manifest = AsyncMock(return_value=mock_stats)

        resp = await mock_client.post(
            "/api/v1/rag/index",
            json={"pointer_id": str(pointer_id), "force": False},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["run_id"] == str(run_id)
        assert data["manifest_sha256"] == manifest_sha256
        assert data["artifacts_total"] == 10
        assert data["artifacts_indexed"] == 8
        assert data["artifacts_skipped"] == 2
        assert data["chunks_created"] == 50

        # Verify service calls
        mock_pointer_instance.get_pointer_by_id.assert_awaited_once_with(pointer_id)
        mock_rag_instance.index_manifest.assert_awaited_once()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_index_with_manifest_sha256_directly(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test indexing directly with manifest_sha256 (no pointer lookup)."""
        manifest_sha256 = "def456"
        run_id = uuid4()

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.complete_run = AsyncMock()

        # Mock RAG indexing
        mock_stats = MagicMock()
        mock_stats.manifest_sha256 = manifest_sha256
        mock_stats.artifacts_total = 5
        mock_stats.artifacts_indexed = 5
        mock_stats.artifacts_skipped = 0
        mock_stats.chunks_created = 25
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.index_manifest = AsyncMock(return_value=mock_stats)

        resp = await mock_client.post(
            "/api/v1/rag/index",
            json={"manifest_sha256": manifest_sha256, "force": True},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["manifest_sha256"] == manifest_sha256
        assert data["artifacts_total"] == 5

        # Pointer service should NOT be called
        mock_pointer_instance = mock_pointer_service.return_value
        mock_pointer_instance.get_pointer_by_id.assert_not_called()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_index_empty_pointer_returns_400(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test indexing pointer with null manifest_sha256 returns 400."""
        pointer_id = uuid4()

        # Mock pointer with empty manifest
        mock_pointer = MagicMock()
        mock_pointer.manifest_sha256 = None
        mock_pointer_instance = mock_pointer_service.return_value
        mock_pointer_instance.get_pointer_by_id = AsyncMock(return_value=mock_pointer)

        resp = await mock_client.post(
            "/api/v1/rag/index",
            json={"pointer_id": str(pointer_id)},
        )

        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_index_value_error_returns_400(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test that ValueError from RagService returns 400."""
        manifest_sha256 = "bad_manifest"
        run_id = uuid4()

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.fail_run = AsyncMock()

        # Mock RAG service to raise ValueError
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.index_manifest = AsyncMock(
            side_effect=ValueError("Invalid manifest format")
        )

        resp = await mock_client.post(
            "/api/v1/rag/index",
            json={"manifest_sha256": manifest_sha256},
        )

        assert resp.status_code == 400
        assert "Invalid manifest format" in resp.json()["detail"]

        # Verify run was marked failed
        mock_run_instance.fail_run.assert_awaited_once()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_index_unexpected_error_returns_500(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test that unexpected errors return 500."""
        manifest_sha256 = "error_manifest"
        run_id = uuid4()

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.fail_run = AsyncMock()

        # Mock RAG service to raise unexpected error
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.index_manifest = AsyncMock(
            side_effect=RuntimeError("Database connection failed")
        )

        resp = await mock_client.post(
            "/api/v1/rag/index",
            json={"manifest_sha256": manifest_sha256},
        )

        assert resp.status_code == 500
        assert "Database connection failed" in resp.json()["detail"]

        # Verify run was marked failed
        mock_run_instance.fail_run.assert_awaited_once()


class TestAskEndpoint:
    """Tests for POST /rag/ask endpoint."""

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_ask_with_pointer_id_resolves_and_answers(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test asking with pointer_id resolves pointer and generates answer."""
        pointer_id = uuid4()
        manifest_sha256 = "ghi789"
        run_id = uuid4()
        question = "What is this document about?"

        # Mock pointer resolution
        mock_pointer = MagicMock()
        mock_pointer.manifest_sha256 = manifest_sha256
        mock_pointer_instance = mock_pointer_service.return_value
        mock_pointer_instance.get_pointer_by_id = AsyncMock(return_value=mock_pointer)

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.complete_run = AsyncMock()

        # Mock RAG answer
        answer = "This document is about testing."
        retrieved = [
            MagicMock(
                chunk_id=uuid4(),
                score=0.95,
                artifact_sha256="art123",
                path_hint="test.txt",
                chunk_index=0,
                content="Test content chunk 1",
            ),
            MagicMock(
                chunk_id=uuid4(),
                score=0.88,
                artifact_sha256="art123",
                path_hint="test.txt",
                chunk_index=1,
                content="Test content chunk 2",
            ),
        ]
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.answer = AsyncMock(return_value=(answer, retrieved))

        resp = await mock_client.post(
            "/api/v1/rag/ask",
            json={
                "pointer_id": str(pointer_id),
                "question": question,
                "top_k": 8,
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["run_id"] == str(run_id)
        assert data["answer"] == answer
        assert len(data["sources"]) == 2
        assert data["sources"][0]["score"] == 0.95
        assert data["sources"][0]["path"] == "test.txt"
        assert data["sources"][1]["score"] == 0.88

        # Verify service calls
        mock_pointer_instance.get_pointer_by_id.assert_awaited_once_with(pointer_id)
        mock_rag_instance.answer.assert_awaited_once()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_ask_with_manifest_sha256_directly(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test asking directly with manifest_sha256 (no pointer lookup)."""
        manifest_sha256 = "jkl012"
        run_id = uuid4()
        question = "Explain the architecture."

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.complete_run = AsyncMock()

        # Mock RAG answer
        answer = "The architecture uses microservices."
        retrieved = []
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.answer = AsyncMock(return_value=(answer, retrieved))

        resp = await mock_client.post(
            "/api/v1/rag/ask",
            json={
                "manifest_sha256": manifest_sha256,
                "question": question,
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["answer"] == answer
        assert data["sources"] == []

        # Pointer service should NOT be called
        mock_pointer_instance = mock_pointer_service.return_value
        mock_pointer_instance.get_pointer_by_id.assert_not_called()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_ask_empty_pointer_returns_400(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test asking with empty pointer returns 400."""
        pointer_id = uuid4()

        # Mock pointer with empty manifest
        mock_pointer = MagicMock()
        mock_pointer.manifest_sha256 = None
        mock_pointer_instance = mock_pointer_service.return_value
        mock_pointer_instance.get_pointer_by_id = AsyncMock(return_value=mock_pointer)

        resp = await mock_client.post(
            "/api/v1/rag/ask",
            json={
                "pointer_id": str(pointer_id),
                "question": "What is this?",
            },
        )

        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_ask_value_error_returns_400(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test that ValueError from RagService returns 400."""
        manifest_sha256 = "bad_manifest"
        run_id = uuid4()

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.fail_run = AsyncMock()

        # Mock RAG service to raise ValueError
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.answer = AsyncMock(side_effect=ValueError("No chunks found for manifest"))

        resp = await mock_client.post(
            "/api/v1/rag/ask",
            json={
                "manifest_sha256": manifest_sha256,
                "question": "What is this?",
            },
        )

        assert resp.status_code == 400
        assert "No chunks found" in resp.json()["detail"]

        # Verify run was marked failed
        mock_run_instance.fail_run.assert_awaited_once()

    @patch("intelli.api.v1.rag.PointerService")
    @patch("intelli.api.v1.rag.RunService")
    @patch("intelli.api.v1.rag.LedgerService")
    @patch("intelli.api.v1.rag.RagService")
    async def test_ask_returns_sources_list(
        self,
        mock_rag_service,
        mock_ledger_service,
        mock_run_service,
        mock_pointer_service,
        mock_client,
    ):
        """Test that sources list is properly formatted in response."""
        manifest_sha256 = "mno345"
        run_id = uuid4()

        # Mock run creation
        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run_instance = mock_run_service.return_value
        mock_run_instance.create_run = AsyncMock(return_value=mock_run)
        mock_run_instance.start_run = AsyncMock()
        mock_run_instance.complete_run = AsyncMock()

        # Mock RAG answer with multiple sources
        chunk1_id = uuid4()
        chunk2_id = uuid4()
        chunk3_id = uuid4()
        retrieved = [
            MagicMock(
                chunk_id=chunk1_id,
                score=0.95,
                artifact_sha256="art1",
                path_hint="doc1.md",
                chunk_index=0,
                content="First chunk",
            ),
            MagicMock(
                chunk_id=chunk2_id,
                score=0.90,
                artifact_sha256="art1",
                path_hint="doc1.md",
                chunk_index=1,
                content="Second chunk",
            ),
            MagicMock(
                chunk_id=chunk3_id,
                score=0.85,
                artifact_sha256="art2",
                path_hint=None,  # Test null path_hint
                chunk_index=0,
                content="Third chunk",
            ),
        ]
        mock_rag_instance = mock_rag_service.return_value
        mock_rag_instance.answer = AsyncMock(return_value=("Answer with three sources", retrieved))

        resp = await mock_client.post(
            "/api/v1/rag/ask",
            json={
                "manifest_sha256": manifest_sha256,
                "question": "Tell me everything",
                "top_k": 10,
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["sources"]) == 3

        # Verify first source
        assert data["sources"][0]["chunk_id"] == str(chunk1_id)
        assert data["sources"][0]["score"] == 0.95
        assert data["sources"][0]["artifact_sha256"] == "art1"
        assert data["sources"][0]["path"] == "doc1.md"
        assert data["sources"][0]["chunk_index"] == 0
        assert data["sources"][0]["content"] == "First chunk"

        # Verify third source (null path should become None)
        assert data["sources"][2]["path"] is None
