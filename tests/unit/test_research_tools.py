"""Unit tests for research tools."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from intelli.agents.tools.research_tools import build_research_tools

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def tools(mock_session):
    with (
        patch("intelli.agents.tools.research_tools.RagService") as rag_cls,
        patch("intelli.agents.tools.research_tools.PointerService") as ptr_cls,
        patch("intelli.agents.tools.research_tools.ManifestService") as mfst_cls,
    ):
        rag_cls.return_value = MagicMock()
        ptr_cls.return_value = MagicMock()
        mfst_cls.return_value = MagicMock()
        return build_research_tools(mock_session)


class TestSearchDocuments:
    async def test_returns_json_array(self, tools, mock_session):
        next(t for t in tools if t.name == "search_documents")

        with patch("intelli.agents.tools.research_tools.RagService") as rag_cls:
            mock_rag = AsyncMock()
            mock_rag.retrieve.return_value = [
                MagicMock(
                    chunk_id=uuid4(),
                    artifact_sha256="abc123",
                    content="test content",
                    score=0.9,
                    path_hint="doc.pdf",
                ),
            ]
            rag_cls.return_value = mock_rag

            # Rebuild tools with mocked service
            rebuilt = build_research_tools(mock_session)
            search_fn = next(t for t in rebuilt if t.name == "search_documents")
            result = await search_fn.ainvoke({"query": "test", "manifest_sha256": "abc"})
            parsed = json.loads(result)
            assert len(parsed) == 1
            assert parsed[0]["content"] == "test content"

    async def test_handles_empty_results(self, tools, mock_session):
        with patch("intelli.agents.tools.research_tools.RagService") as rag_cls:
            mock_rag = AsyncMock()
            mock_rag.retrieve.return_value = []
            rag_cls.return_value = mock_rag

            rebuilt = build_research_tools(mock_session)
            search_fn = next(t for t in rebuilt if t.name == "search_documents")
            result = await search_fn.ainvoke({"query": "nothing", "manifest_sha256": "abc"})
            assert "No relevant" in result


class TestListNotebooks:
    async def test_returns_notebook_list(self, tools, mock_session):
        with patch("intelli.agents.tools.research_tools.PointerService") as ptr_cls:
            mock_ptr = AsyncMock()
            ptr_id = uuid4()
            notebook = MagicMock()
            notebook.id = ptr_id
            notebook.name = "My Notebook"
            notebook.namespace = "default"
            notebook.manifest_sha256 = "abc"
            mock_ptr.list_pointers.return_value = [notebook]
            ptr_cls.return_value = mock_ptr

            rebuilt = build_research_tools(mock_session)
            list_fn = next(t for t in rebuilt if t.name == "list_notebooks")
            result = await list_fn.ainvoke({})
            parsed = json.loads(result)
            assert len(parsed) == 1
            assert parsed[0]["name"] == "My Notebook"

    async def test_handles_no_notebooks(self, tools, mock_session):
        with patch("intelli.agents.tools.research_tools.PointerService") as ptr_cls:
            mock_ptr = AsyncMock()
            mock_ptr.list_pointers.return_value = []
            ptr_cls.return_value = mock_ptr

            rebuilt = build_research_tools(mock_session)
            list_fn = next(t for t in rebuilt if t.name == "list_notebooks")
            result = await list_fn.ainvoke({})
            assert "No notebooks" in result


class TestGetDocumentInfo:
    async def test_returns_artifact_metadata(self, tools, mock_session):
        with patch("intelli.services.substrate.artifact_service.ArtifactService") as art_cls:
            mock_art = AsyncMock()
            mock_art.get_artifact.return_value = MagicMock(
                sha256="abc",
                size_bytes=1024,
                media_type="application/pdf",
                original_path="doc.pdf",
                reference_count=1,
            )
            art_cls.return_value = mock_art

            rebuilt = build_research_tools(mock_session)
            info_fn = next(t for t in rebuilt if t.name == "get_document_info")
            result = await info_fn.ainvoke({"artifact_sha256": "abc"})
            parsed = json.loads(result)
            assert parsed["sha256"] == "abc"
            assert parsed["size_bytes"] == 1024

    async def test_handles_missing_artifact(self, tools, mock_session):
        with patch("intelli.services.substrate.artifact_service.ArtifactService") as art_cls:
            mock_art = AsyncMock()
            mock_art.get_artifact.side_effect = Exception("not found")
            art_cls.return_value = mock_art

            rebuilt = build_research_tools(mock_session)
            info_fn = next(t for t in rebuilt if t.name == "get_document_info")
            result = await info_fn.ainvoke({"artifact_sha256": "missing"})
            assert "not found" in result or "error" in result.lower()


class TestCompareManifests:
    async def test_returns_diff(self, tools, mock_session):
        with patch("intelli.agents.tools.research_tools.ManifestService") as mfst_cls:
            mock_mfst = AsyncMock()
            mock_mfst.diff_manifests.return_value = MagicMock(
                old_sha256="old",
                new_sha256="new",
                added=[],
                removed=[],
                modified=[],
            )
            mfst_cls.return_value = mock_mfst

            rebuilt = build_research_tools(mock_session)
            compare_fn = next(t for t in rebuilt if t.name == "compare_manifests")
            result = await compare_fn.ainvoke({"old_sha256": "old", "new_sha256": "new"})
            parsed = json.loads(result)
            assert parsed["old_sha256"] == "old"
            assert parsed["new_sha256"] == "new"

    async def test_handles_error(self, tools, mock_session):
        with patch("intelli.agents.tools.research_tools.ManifestService") as mfst_cls:
            mock_mfst = AsyncMock()
            mock_mfst.diff_manifests.side_effect = Exception("Manifest not found")
            mfst_cls.return_value = mock_mfst

            rebuilt = build_research_tools(mock_session)
            compare_fn = next(t for t in rebuilt if t.name == "compare_manifests")
            result = await compare_fn.ainvoke({"old_sha256": "x", "new_sha256": "y"})
            assert "failed" in result.lower() or "error" in result.lower()
