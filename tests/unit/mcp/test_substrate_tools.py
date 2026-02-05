"""Unit tests for substrate MCP tools."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from intelli.mcp.tools.substrate_tools import _handle_tool_call

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


def _make_pointer(namespace="default", name="test", pointer_type="bundle", manifest_sha="abc123"):
    """Create a mock Pointer object."""
    pointer = MagicMock()
    pointer.id = uuid4()
    pointer.namespace = namespace
    pointer.name = name
    pointer.pointer_type = pointer_type
    pointer.manifest_sha256 = manifest_sha
    pointer.description = "Test pointer"
    return pointer


def _make_manifest(sha256="abc123", entry_count=5, total_size=1000):
    """Create a mock Manifest object."""
    manifest = MagicMock()
    manifest.sha256 = sha256
    manifest.entry_count = entry_count
    manifest.total_size_bytes = total_size
    manifest.message = "Test commit"
    manifest.parent_sha256 = None
    manifest.created_at = datetime.now()
    return manifest


def _make_manifest_entry(path="test.txt", artifact_sha="def456"):
    """Create a mock ManifestEntry object."""
    entry = MagicMock()
    entry.path = path
    entry.artifact_sha256 = artifact_sha
    entry.metadata = {}
    return entry


def _make_artifact(sha256="def456", size=100):
    """Create a mock Artifact object."""
    artifact = MagicMock()
    artifact.sha256 = sha256
    artifact.media_type = "text/plain"
    artifact.size_bytes = size
    artifact.filename = "test.txt"
    artifact.storage_uri = f"s3://bucket/{sha256}"
    artifact.reference_count = 1
    artifact.created_at = datetime.now()
    return artifact


class TestListPointers:
    async def test_list_pointers_delegates_to_service(self):
        """Test list_pointers calls PointerService.list_pointers."""
        session = AsyncMock()
        pointers = [_make_pointer()]

        with patch("intelli.mcp.tools.substrate_tools.PointerService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.list_pointers = AsyncMock(return_value=pointers)

            result = await _handle_tool_call(
                session,
                "list_pointers",
                {"namespace": "default", "limit": 100},
            )

            assert "pointers" in result
            assert len(result["pointers"]) == 1
            assert result["pointers"][0]["name"] == "test"
            service_instance.list_pointers.assert_awaited_once()


class TestResolvePointer:
    async def test_resolve_pointer_delegates_to_service(self):
        """Test resolve_pointer calls PointerService.resolve."""
        session = AsyncMock()

        with patch("intelli.mcp.tools.substrate_tools.PointerService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.resolve = AsyncMock(return_value="abc123")

            result = await _handle_tool_call(
                session,
                "resolve_pointer",
                {"namespace": "default", "name": "test"},
            )

            assert result["manifest_sha256"] == "abc123"
            assert result["namespace"] == "default"
            assert result["name"] == "test"
            service_instance.resolve.assert_awaited_once_with("default", "test")


class TestCheckoutManifest:
    async def test_checkout_manifest_returns_entries(self):
        """Test checkout_manifest returns manifest entries."""
        session = AsyncMock()
        manifest = _make_manifest()
        entries = [_make_manifest_entry()]

        with patch("intelli.mcp.tools.substrate_tools.ManifestService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.get_manifest = AsyncMock(return_value=manifest)
            service_instance.get_entries = AsyncMock(return_value=entries)

            result = await _handle_tool_call(
                session,
                "checkout_manifest",
                {"sha256": "abc123"},
            )

            assert result["sha256"] == "abc123"
            assert len(result["entries"]) == 1
            assert result["entries"][0]["path"] == "test.txt"
            assert result["entry_count"] == 5
            assert result["total_size_bytes"] == 1000


class TestGetManifestHistory:
    async def test_get_manifest_history_returns_chain(self):
        """Test get_manifest_history returns manifest history."""
        session = AsyncMock()
        history = [_make_manifest(sha256=f"sha{i}") for i in range(3)]

        with patch("intelli.mcp.tools.substrate_tools.ManifestService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.get_history = AsyncMock(return_value=history)

            result = await _handle_tool_call(
                session,
                "get_manifest_history",
                {"sha256": "abc123", "limit": 50},
            )

            assert "history" in result
            assert len(result["history"]) == 3
            assert result["history"][0]["sha256"] == "sha0"
            service_instance.get_history.assert_awaited_once_with("abc123", 50)


class TestDiffManifests:
    async def test_diff_manifests_returns_diff_structure(self):
        """Test diff_manifests returns added, removed, modified."""
        session = AsyncMock()

        diff = MagicMock()
        diff.old_sha256 = "old123"
        diff.new_sha256 = "new123"
        diff.added = [_make_manifest_entry(path="added.txt")]
        diff.removed = [_make_manifest_entry(path="removed.txt")]
        diff.modified = [
            {
                "path": "modified.txt",
                "old": _make_manifest_entry(artifact_sha="old_sha"),
                "new": _make_manifest_entry(artifact_sha="new_sha"),
            }
        ]

        with patch("intelli.mcp.tools.substrate_tools.ManifestService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.diff_manifests = AsyncMock(return_value=diff)

            result = await _handle_tool_call(
                session,
                "diff_manifests",
                {"old_sha256": "old123", "new_sha256": "new123"},
            )

            assert result["old_sha256"] == "old123"
            assert result["new_sha256"] == "new123"
            assert len(result["added"]) == 1
            assert len(result["removed"]) == 1
            assert len(result["modified"]) == 1
            assert result["modified"][0]["path"] == "modified.txt"


class TestCreateManifest:
    async def test_create_manifest_builds_and_returns_sha(self):
        """Test create_manifest builds manifest and returns SHA."""
        session = AsyncMock()

        build_result = MagicMock()
        build_result.sha256 = "new_manifest_sha"
        build_result.entry_count = 2
        build_result.total_size_bytes = 500
        build_result.is_duplicate = False

        with patch("intelli.mcp.tools.substrate_tools.ManifestService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.build_manifest = AsyncMock(return_value=build_result)

            result = await _handle_tool_call(
                session,
                "create_manifest",
                {
                    "entries": [
                        {"path": "file1.txt", "artifact_sha256": "a" * 64},
                        {
                            "path": "file2.txt",
                            "artifact_sha256": "b" * 64,
                            "metadata": {"type": "doc"},
                        },
                    ],
                    "message": "Initial commit",
                },
            )

            assert result["sha256"] == "new_manifest_sha"
            assert result["entry_count"] == 2
            assert result["total_size_bytes"] == 500
            assert result["is_duplicate"] is False
            service_instance.build_manifest.assert_awaited_once()


class TestAdvancePointer:
    async def test_advance_pointer_success(self):
        """Test advance_pointer updates pointer to new manifest."""
        session = AsyncMock()
        pointer = _make_pointer()

        advance_result = MagicMock()
        advance_result.success = True
        advance_result.old_sha256 = "old123"
        advance_result.new_sha256 = "new123"
        advance_result.conflict = None

        with patch("intelli.mcp.tools.substrate_tools.PointerService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.get_pointer = AsyncMock(return_value=pointer)
            service_instance.advance = AsyncMock(return_value=advance_result)

            result = await _handle_tool_call(
                session,
                "advance_pointer",
                {
                    "namespace": "default",
                    "name": "test",
                    "manifest_sha256": "new123",
                    "reason": "Update bundle",
                },
            )

            assert result["success"] is True
            assert result["old_sha256"] == "old123"
            assert result["new_sha256"] == "new123"
            service_instance.advance.assert_awaited_once()


class TestCreatePointer:
    async def test_create_pointer_delegates_to_service(self):
        """Test create_pointer creates new pointer."""
        session = AsyncMock()
        pointer = _make_pointer()

        with patch("intelli.mcp.tools.substrate_tools.PointerService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.create_pointer = AsyncMock(return_value=pointer)

            result = await _handle_tool_call(
                session,
                "create_pointer",
                {
                    "namespace": "default",
                    "name": "new_bundle",
                    "pointer_type": "bundle",
                    "description": "Test bundle",
                },
            )

            assert result["namespace"] == "default"
            assert result["name"] == "test"
            assert result["pointer_type"] == "bundle"
            service_instance.create_pointer.assert_awaited_once()


class TestGetArtifactInfo:
    async def test_get_artifact_info_returns_metadata(self):
        """Test get_artifact_info returns artifact metadata."""
        session = AsyncMock()
        artifact = _make_artifact()

        with patch("intelli.mcp.tools.substrate_tools.ArtifactService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.get_artifact = AsyncMock(return_value=artifact)

            result = await _handle_tool_call(
                session,
                "get_artifact_info",
                {"sha256": "def456"},
            )

            assert result["sha256"] == "def456"
            assert result["media_type"] == "text/plain"
            assert result["size_bytes"] == 100
            assert result["filename"] == "test.txt"
            service_instance.get_artifact.assert_awaited_once_with("def456")


class TestGetArtifactUrl:
    async def test_get_artifact_url_returns_presigned_url(self):
        """Test get_artifact_url returns pre-signed URL."""
        session = AsyncMock()

        with patch("intelli.mcp.tools.substrate_tools.ArtifactService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.get_content_url = AsyncMock(
                return_value="https://example.com/artifact"
            )

            result = await _handle_tool_call(
                session,
                "get_artifact_url",
                {"sha256": "def456", "expiration_seconds": 3600},
            )

            assert result["sha256"] == "def456"
            assert result["url"] == "https://example.com/artifact"
            assert result["expires_in"] == 3600
            service_instance.get_content_url.assert_awaited_once_with("def456", 3600)


class TestUnknownTool:
    async def test_unknown_tool_returns_error_dict(self):
        """Test that unknown tool name returns error."""
        session = AsyncMock()

        result = await _handle_tool_call(
            session,
            "nonexistent_tool",
            {},
        )

        assert "error" in result
        assert "Unknown tool" in result["error"]


class TestToolException:
    async def test_tool_exception_returns_error_json(self):
        """Test that exceptions in tool handlers are caught and returned as errors."""
        session = AsyncMock()

        with patch("intelli.mcp.tools.substrate_tools.PointerService") as mock_service_cls:
            service_instance = mock_service_cls.return_value
            service_instance.resolve = AsyncMock(side_effect=Exception("Test error"))

            # The exception is caught by the call_tool decorator, not _handle_tool_call
            # So we test that _handle_tool_call raises and the decorator catches it
            with pytest.raises(Exception, match="Test error"):
                await _handle_tool_call(
                    session,
                    "resolve_pointer",
                    {"namespace": "default", "name": "test"},
                )
