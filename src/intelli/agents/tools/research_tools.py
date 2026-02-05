"""LangGraph-compatible tools wrapping substrate services.

These tools expose the same operations as the MCP tools (ADR-005) but
as LangChain ``@tool`` decorated functions that LangGraph's ToolNode
can invoke.  Each tool receives a database session via a closure so
the graph can inject it at construction time.
"""

from __future__ import annotations

import json

from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.services.knowledge.rag_service import RagService
from intelli.services.substrate.manifest_service import ManifestService
from intelli.services.substrate.pointer_service import PointerService


def build_research_tools(session: AsyncSession) -> list:
    """Build research tool instances bound to *session*.

    Returns a list of LangChain tools ready for ``llm.bind_tools()``.
    """
    rag = RagService(session)
    pointers = PointerService(session)
    manifests = ManifestService(session)

    @tool
    async def search_documents(query: str, manifest_sha256: str) -> str:
        """Search documents in the current notebook for relevant information.

        Args:
            query: The search query describing what to look for.
            manifest_sha256: SHA-256 of the manifest to search within.

        Returns:
            JSON array of matching document chunks with content and relevance scores.

        Examples:
            Input: query="tenant notice period", manifest_sha256="abc123..."
            Output: [
                {
                    "chunk_id": "chunk-001",
                    "artifact_sha256": "def456...",
                    "content": "The tenant must provide 30 days written notice...",
                    "score": 0.87,
                    "path_hint": "lease-agreement.pdf"
                },
                {
                    "chunk_id": "chunk-002",
                    "artifact_sha256": "def456...",
                    "content": "Notice period may be extended to 60 days...",
                    "score": 0.72,
                    "path_hint": "lease-agreement.pdf"
                }
            ]

            When citing these results:
            - First result = [1]
            - Second result = [2]
            - Example: "The tenant must provide 30 days notice [1]..."
        """
        try:
            chunks = await rag.retrieve(manifest_sha256=manifest_sha256, query=query, top_k=8)
            results = [
                {
                    "chunk_id": str(c.chunk_id),
                    "artifact_sha256": c.artifact_sha256,
                    "content": c.content,
                    "score": c.score,
                    "path_hint": c.path_hint,
                }
                for c in chunks
            ]
            return json.dumps(results, indent=2) if results else "No relevant documents found."
        except Exception as e:
            return f"Search failed: {e!s}"

    @tool
    async def list_notebooks() -> str:
        """List available notebooks (pointers) the user has access to.

        Returns:
            JSON array of notebooks with id, name, and current manifest SHA-256.
        """
        try:
            ptrs = await pointers.list_pointers(limit=50)
            results = [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "namespace": p.namespace,
                    "manifest_sha256": p.manifest_sha256,
                }
                for p in ptrs
                if p.manifest_sha256  # only notebooks with content
            ]
            return json.dumps(results, indent=2) if results else "No notebooks found."
        except Exception as e:
            return f"Failed to list notebooks: {e!s}"

    @tool
    async def get_document_info(artifact_sha256: str) -> str:
        """Get metadata about a specific document by its artifact SHA-256.

        Args:
            artifact_sha256: The SHA-256 hash identifying the artifact.

        Returns:
            JSON object with artifact metadata (size, type, path).
        """
        try:
            from intelli.services.substrate.artifact_service import ArtifactService

            artifacts = ArtifactService(session)
            artifact = await artifacts.get_artifact(artifact_sha256)
            return json.dumps(
                {
                    "sha256": artifact.sha256,
                    "size_bytes": artifact.size_bytes,
                    "media_type": artifact.media_type,
                    "original_path": artifact.original_path,
                    "reference_count": artifact.reference_count,
                },
                indent=2,
            )
        except Exception as e:
            return f"Artifact not found or error: {e!s}"

    @tool
    async def compare_manifests(old_sha256: str, new_sha256: str) -> str:
        """Compare two versions of a notebook to see what changed.

        Args:
            old_sha256: SHA-256 of the older manifest version.
            new_sha256: SHA-256 of the newer manifest version.

        Returns:
            JSON object with added, removed, and modified entries.
        """
        try:
            diff = await manifests.diff_manifests(old_sha256, new_sha256)
            return json.dumps(
                {
                    "old_sha256": diff.old_sha256,
                    "new_sha256": diff.new_sha256,
                    "added": [e.__dict__ if hasattr(e, "__dict__") else str(e) for e in diff.added],
                    "removed": [
                        e.__dict__ if hasattr(e, "__dict__") else str(e) for e in diff.removed
                    ],
                    "modified": [
                        e.__dict__ if hasattr(e, "__dict__") else str(e) for e in diff.modified
                    ],
                },
                indent=2,
                default=str,
            )
        except Exception as e:
            return f"Comparison failed: {e!s}"

    return [search_documents, list_notebooks, get_document_info, compare_manifests]
