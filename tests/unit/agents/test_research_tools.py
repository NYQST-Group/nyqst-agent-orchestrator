"""Unit tests for research tools — tool definitions and service delegation.

Tests that each tool correctly delegates to the underlying service, handles
errors gracefully, and returns well-formed JSON strings. All services are
mocked — no database or external calls.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from intelli.services.knowledge.rag_service import RetrievedChunk

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session():
    return AsyncMock()


class ToolBundle:
    """Wrapper to hold tool list + service mocks."""

    def __init__(self, tools, mock_rag, mock_ptr, mock_man):
        self._tools = tools
        self._mock_rag = mock_rag
        self._mock_ptr = mock_ptr
        self._mock_man = mock_man

    def __iter__(self):
        return iter(self._tools)

    def __len__(self):
        return len(self._tools)


@pytest.fixture
def tools(mock_session):
    """Build research tools with mocked services."""
    with (
        patch("intelli.agents.tools.research_tools.RagService") as mock_rag_cls,
        patch("intelli.agents.tools.research_tools.PointerService") as mock_ptr_cls,
        patch("intelli.agents.tools.research_tools.ManifestService") as mock_man_cls,
    ):
        mock_rag = mock_rag_cls.return_value
        mock_ptr = mock_ptr_cls.return_value
        mock_man = mock_man_cls.return_value

        from intelli.agents.tools.research_tools import build_research_tools

        tool_list = build_research_tools(mock_session)

        return ToolBundle(tool_list, mock_rag, mock_ptr, mock_man)


def _get_tool(bundle, name: str):
    """Find a tool by name from the tool list/bundle."""
    items = bundle._tools if hasattr(bundle, "_tools") else bundle
    for t in items:
        if t.name == name:
            return t
    raise ValueError(f"Tool {name} not found in {[t.name for t in items]}")


# ---------------------------------------------------------------------------
# Tool inventory
# ---------------------------------------------------------------------------


class TestToolInventory:
    def test_four_tools_returned(self, tools):
        assert len(tools) == 4

    def test_tool_names(self, tools):
        names = {t.name for t in tools}
        assert names == {
            "search_documents",
            "list_notebooks",
            "get_document_info",
            "compare_manifests",
        }

    def test_search_documents_has_two_params(self, tools):
        tool = _get_tool(tools, "search_documents")
        schema = tool.args_schema.schema() if tool.args_schema else {}
        props = schema.get("properties", {})
        assert "query" in props
        assert "manifest_sha256" in props


# ---------------------------------------------------------------------------
# search_documents
# ---------------------------------------------------------------------------


class TestSearchDocuments:
    @pytest.mark.asyncio
    async def test_returns_json_array_of_chunks(self, tools):
        chunk = RetrievedChunk(
            chunk_id=uuid4(),
            artifact_sha256="a" * 64,
            chunk_index=0,
            content="Key term: Protocol",
            score=0.95,
            path_hint="design.md",
        )
        tools._mock_rag.retrieve = AsyncMock(return_value=[chunk])

        tool = _get_tool(tools, "search_documents")
        result = await tool.ainvoke({"query": "protocol", "manifest_sha256": "abc"})

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["content"] == "Key term: Protocol"
        assert parsed[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_empty_results(self, tools):
        tools._mock_rag.retrieve = AsyncMock(return_value=[])

        tool = _get_tool(tools, "search_documents")
        result = await tool.ainvoke({"query": "nonexistent", "manifest_sha256": "abc"})
        assert result == "No relevant documents found."

    @pytest.mark.asyncio
    async def test_handles_exception(self, tools):
        tools._mock_rag.retrieve = AsyncMock(side_effect=RuntimeError("connection lost"))

        tool = _get_tool(tools, "search_documents")
        result = await tool.ainvoke({"query": "fail", "manifest_sha256": "abc"})
        assert "Search failed" in result
        assert "connection lost" in result

    @pytest.mark.asyncio
    async def test_passes_top_k_8(self, tools):
        tools._mock_rag.retrieve = AsyncMock(return_value=[])

        tool = _get_tool(tools, "search_documents")
        await tool.ainvoke({"query": "test", "manifest_sha256": "m"})

        tools._mock_rag.retrieve.assert_called_once_with(manifest_sha256="m", query="test", top_k=8)


# ---------------------------------------------------------------------------
# list_notebooks
# ---------------------------------------------------------------------------


class TestListNotebooks:
    @pytest.mark.asyncio
    async def test_returns_notebooks_with_manifest(self, tools):
        ptr = MagicMock()
        ptr.id = uuid4()
        ptr.name = "Research Notebook"
        ptr.namespace = "default"
        ptr.manifest_sha256 = "b" * 64
        tools._mock_ptr.list_pointers = AsyncMock(return_value=[ptr])

        tool = _get_tool(tools, "list_notebooks")
        result = await tool.ainvoke({})

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Research Notebook"

    @pytest.mark.asyncio
    async def test_filters_out_empty_manifests(self, tools):
        ptr_with = MagicMock()
        ptr_with.id = uuid4()
        ptr_with.name = "Has content"
        ptr_with.namespace = "ns"
        ptr_with.manifest_sha256 = "c" * 64

        ptr_without = MagicMock()
        ptr_without.id = uuid4()
        ptr_without.name = "Empty"
        ptr_without.namespace = "ns"
        ptr_without.manifest_sha256 = None

        tools._mock_ptr.list_pointers = AsyncMock(return_value=[ptr_with, ptr_without])

        tool = _get_tool(tools, "list_notebooks")
        result = await tool.ainvoke({})

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Has content"

    @pytest.mark.asyncio
    async def test_no_notebooks(self, tools):
        tools._mock_ptr.list_pointers = AsyncMock(return_value=[])

        tool = _get_tool(tools, "list_notebooks")
        result = await tool.ainvoke({})
        assert result == "No notebooks found."

    @pytest.mark.asyncio
    async def test_handles_exception(self, tools):
        tools._mock_ptr.list_pointers = AsyncMock(side_effect=RuntimeError("db down"))

        tool = _get_tool(tools, "list_notebooks")
        result = await tool.ainvoke({})
        assert "Failed to list notebooks" in result


# ---------------------------------------------------------------------------
# get_document_info
# ---------------------------------------------------------------------------


class TestGetDocumentInfo:
    @pytest.mark.asyncio
    async def test_returns_artifact_metadata(self, tools):
        artifact = MagicMock()
        artifact.sha256 = "d" * 64
        artifact.size_bytes = 1024
        artifact.media_type = "application/pdf"
        artifact.original_path = "docs/report.pdf"
        artifact.reference_count = 3

        with patch(
            "intelli.services.substrate.artifact_service.ArtifactService",
            return_value=MagicMock(get_artifact=AsyncMock(return_value=artifact)),
        ):
            tool = _get_tool(tools, "get_document_info")
            result = await tool.ainvoke({"artifact_sha256": "d" * 64})

        parsed = json.loads(result)
        assert parsed["size_bytes"] == 1024
        assert parsed["media_type"] == "application/pdf"

    @pytest.mark.asyncio
    async def test_handles_not_found(self, tools):
        with patch(
            "intelli.services.substrate.artifact_service.ArtifactService",
            return_value=MagicMock(get_artifact=AsyncMock(side_effect=ValueError("not found"))),
        ):
            tool = _get_tool(tools, "get_document_info")
            result = await tool.ainvoke({"artifact_sha256": "x" * 64})

        assert "not found" in result


# ---------------------------------------------------------------------------
# compare_manifests
# ---------------------------------------------------------------------------


class TestCompareManifests:
    @pytest.mark.asyncio
    async def test_returns_diff(self, tools):
        diff = MagicMock()
        diff.old_sha256 = "old"
        diff.new_sha256 = "new"
        diff.added = []
        diff.removed = []
        diff.modified = []
        tools._mock_man.diff_manifests = AsyncMock(return_value=diff)

        tool = _get_tool(tools, "compare_manifests")
        result = await tool.ainvoke({"old_sha256": "old", "new_sha256": "new"})

        parsed = json.loads(result)
        assert parsed["old_sha256"] == "old"
        assert parsed["new_sha256"] == "new"
        assert parsed["added"] == []

    @pytest.mark.asyncio
    async def test_handles_exception(self, tools):
        tools._mock_man.diff_manifests = AsyncMock(side_effect=RuntimeError("bad sha"))

        tool = _get_tool(tools, "compare_manifests")
        result = await tool.ainvoke({"old_sha256": "x", "new_sha256": "y"})
        assert "Comparison failed" in result
