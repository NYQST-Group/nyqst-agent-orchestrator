"""MCP tools for substrate operations (artifacts, manifests, pointers).

These tools enable agents to interact with the immutable artifact substrate,
create manifest snapshots, and manage pointers (bundle/corpus heads).
"""

import json
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from intelli.db.engine import AsyncSessionLocal
from intelli.schemas.substrate import ManifestEntry, PointerType
from intelli.services.substrate.artifact_service import ArtifactService
from intelli.services.substrate.manifest_service import ManifestService
from intelli.services.substrate.pointer_service import PointerService

# Tool definitions
SUBSTRATE_TOOLS = [
    Tool(
        name="list_pointers",
        description="List all pointers (bundle/corpus heads) in a namespace. Pointers are mutable references to immutable manifest snapshots.",
        inputSchema={
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Namespace to list pointers from (default: 'default')",
                    "default": "default",
                },
                "pointer_type": {
                    "type": "string",
                    "enum": ["bundle", "corpus", "snapshot"],
                    "description": "Filter by pointer type",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of pointers to return",
                    "default": 100,
                },
            },
        },
    ),
    Tool(
        name="resolve_pointer",
        description="Resolve a pointer to get its current manifest SHA-256. Returns the HEAD manifest that the pointer currently references.",
        inputSchema={
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Pointer namespace",
                },
                "name": {
                    "type": "string",
                    "description": "Pointer name",
                },
            },
            "required": ["namespace", "name"],
        },
    ),
    Tool(
        name="checkout_manifest",
        description="Get the contents of a manifest by SHA-256. Returns all entries (paths and artifact references) in the manifest tree.",
        inputSchema={
            "type": "object",
            "properties": {
                "sha256": {
                    "type": "string",
                    "description": "Manifest SHA-256 hash",
                },
            },
            "required": ["sha256"],
        },
    ),
    Tool(
        name="get_manifest_history",
        description="Get the history of a manifest by walking its parent chain. Useful for understanding how a bundle/corpus evolved.",
        inputSchema={
            "type": "object",
            "properties": {
                "sha256": {
                    "type": "string",
                    "description": "Starting manifest SHA-256",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum history depth",
                    "default": 50,
                },
            },
            "required": ["sha256"],
        },
    ),
    Tool(
        name="diff_manifests",
        description="Compare two manifests to see what changed (added, removed, modified entries).",
        inputSchema={
            "type": "object",
            "properties": {
                "old_sha256": {
                    "type": "string",
                    "description": "Old manifest SHA-256",
                },
                "new_sha256": {
                    "type": "string",
                    "description": "New manifest SHA-256",
                },
            },
            "required": ["old_sha256", "new_sha256"],
        },
    ),
    Tool(
        name="create_manifest",
        description="Create a new manifest from a list of entries. Each entry maps a path to an artifact SHA-256. Returns the new manifest's SHA-256.",
        inputSchema={
            "type": "object",
            "properties": {
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "artifact_sha256": {"type": "string"},
                            "metadata": {"type": "object"},
                        },
                        "required": ["path", "artifact_sha256"],
                    },
                    "description": "List of entries (path -> artifact mapping)",
                },
                "parent_sha256": {
                    "type": "string",
                    "description": "Parent manifest for history chain (optional)",
                },
                "message": {
                    "type": "string",
                    "description": "Commit message describing this snapshot",
                },
            },
            "required": ["entries"],
        },
    ),
    Tool(
        name="advance_pointer",
        description="Advance a pointer to a new manifest. This is how you 'publish' changes to a bundle or promote to a corpus.",
        inputSchema={
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Pointer namespace",
                },
                "name": {
                    "type": "string",
                    "description": "Pointer name",
                },
                "manifest_sha256": {
                    "type": "string",
                    "description": "New manifest SHA-256 to point to",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the change (recorded in history)",
                },
            },
            "required": ["namespace", "name", "manifest_sha256"],
        },
    ),
    Tool(
        name="create_pointer",
        description="Create a new pointer (bundle/corpus head) in a namespace.",
        inputSchema={
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Pointer namespace",
                },
                "name": {
                    "type": "string",
                    "description": "Pointer name",
                },
                "pointer_type": {
                    "type": "string",
                    "enum": ["bundle", "corpus", "snapshot"],
                    "description": "Pointer type (default: bundle)",
                    "default": "bundle",
                },
                "manifest_sha256": {
                    "type": "string",
                    "description": "Initial manifest SHA-256 (optional)",
                },
                "description": {
                    "type": "string",
                    "description": "Human-readable description",
                },
            },
            "required": ["namespace", "name"],
        },
    ),
    Tool(
        name="get_artifact_info",
        description="Get metadata about an artifact by SHA-256 (size, media type, filename, etc.).",
        inputSchema={
            "type": "object",
            "properties": {
                "sha256": {
                    "type": "string",
                    "description": "Artifact SHA-256 hash",
                },
            },
            "required": ["sha256"],
        },
    ),
    Tool(
        name="get_artifact_url",
        description="Get a pre-signed URL to download artifact content.",
        inputSchema={
            "type": "object",
            "properties": {
                "sha256": {
                    "type": "string",
                    "description": "Artifact SHA-256 hash",
                },
                "expiration_seconds": {
                    "type": "integer",
                    "description": "URL validity duration in seconds (default: 3600)",
                    "default": 3600,
                },
            },
            "required": ["sha256"],
        },
    ),
]


def register(server: Server) -> None:
    """Register substrate tools with the MCP server."""

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return SUBSTRATE_TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        async with AsyncSessionLocal() as session:
            try:
                result = await _handle_tool_call(session, name, arguments)
                return [TextContent(type="text", text=json.dumps(result, default=str))]
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def _handle_tool_call(session: Any, name: str, arguments: dict[str, Any]) -> dict:
    """Handle a substrate tool call."""

    if name == "list_pointers":
        service = PointerService(session)
        namespace = arguments.get("namespace", "default")
        pointer_type = arguments.get("pointer_type")
        limit = arguments.get("limit", 100)

        pt = PointerType(pointer_type) if pointer_type else None
        pointers = await service.list_pointers(namespace=namespace, pointer_type=pt, limit=limit)

        return {
            "pointers": [
                {
                    "id": str(p.id),
                    "namespace": p.namespace,
                    "name": p.name,
                    "pointer_type": p.pointer_type,
                    "manifest_sha256": p.manifest_sha256,
                    "description": p.description,
                }
                for p in pointers
            ]
        }

    elif name == "resolve_pointer":
        service = PointerService(session)
        sha256 = await service.resolve(arguments["namespace"], arguments["name"])
        return {
            "namespace": arguments["namespace"],
            "name": arguments["name"],
            "manifest_sha256": sha256,
        }

    elif name == "checkout_manifest":
        service = ManifestService(session)
        entries = await service.get_entries(arguments["sha256"])
        manifest = await service.get_manifest(arguments["sha256"])
        return {
            "sha256": manifest.sha256,
            "entries": [
                {
                    "path": e.path,
                    "artifact_sha256": e.artifact_sha256,
                    "metadata": e.metadata,
                }
                for e in entries
            ],
            "entry_count": manifest.entry_count,
            "total_size_bytes": manifest.total_size_bytes,
            "message": manifest.message,
            "parent_sha256": manifest.parent_sha256,
        }

    elif name == "get_manifest_history":
        service = ManifestService(session)
        limit = arguments.get("limit", 50)
        history = await service.get_history(arguments["sha256"], limit)
        return {
            "history": [
                {
                    "sha256": m.sha256,
                    "message": m.message,
                    "entry_count": m.entry_count,
                    "created_at": m.created_at.isoformat(),
                    "parent_sha256": m.parent_sha256,
                }
                for m in history
            ]
        }

    elif name == "diff_manifests":
        service = ManifestService(session)
        diff = await service.diff_manifests(arguments["old_sha256"], arguments["new_sha256"])
        return {
            "old_sha256": diff.old_sha256,
            "new_sha256": diff.new_sha256,
            "added": [{"path": e.path, "artifact_sha256": e.artifact_sha256} for e in diff.added],
            "removed": [{"path": e.path, "artifact_sha256": e.artifact_sha256} for e in diff.removed],
            "modified": [
                {
                    "path": m["path"],
                    "old_artifact_sha256": m["old"].artifact_sha256,
                    "new_artifact_sha256": m["new"].artifact_sha256,
                }
                for m in diff.modified
            ],
        }

    elif name == "create_manifest":
        service = ManifestService(session)
        entries = [
            ManifestEntry(
                path=e["path"],
                artifact_sha256=e["artifact_sha256"],
                metadata=e.get("metadata"),
            )
            for e in arguments["entries"]
        ]
        result = await service.build_manifest(
            entries=entries,
            parent_sha256=arguments.get("parent_sha256"),
            message=arguments.get("message"),
        )
        return {
            "sha256": result.sha256,
            "entry_count": result.entry_count,
            "total_size_bytes": result.total_size_bytes,
            "is_duplicate": result.is_duplicate,
        }

    elif name == "advance_pointer":
        service = PointerService(session)
        pointer = await service.get_pointer(arguments["namespace"], arguments["name"])
        result = await service.advance(
            pointer_id=pointer.id,
            new_sha256=arguments["manifest_sha256"],
            reason=arguments.get("reason"),
        )
        return {
            "success": result.success,
            "old_sha256": result.old_sha256,
            "new_sha256": result.new_sha256,
            "conflict": result.conflict,
        }

    elif name == "create_pointer":
        service = PointerService(session)
        pt = PointerType(arguments.get("pointer_type", "bundle"))
        pointer = await service.create_pointer(
            namespace=arguments["namespace"],
            name=arguments["name"],
            pointer_type=pt,
            manifest_sha256=arguments.get("manifest_sha256"),
            description=arguments.get("description"),
        )
        return {
            "id": str(pointer.id),
            "namespace": pointer.namespace,
            "name": pointer.name,
            "pointer_type": pointer.pointer_type,
            "manifest_sha256": pointer.manifest_sha256,
        }

    elif name == "get_artifact_info":
        service = ArtifactService(session)
        artifact = await service.get_artifact(arguments["sha256"])
        return {
            "sha256": artifact.sha256,
            "media_type": artifact.media_type,
            "size_bytes": artifact.size_bytes,
            "filename": artifact.filename,
            "storage_uri": artifact.storage_uri,
            "reference_count": artifact.reference_count,
            "created_at": artifact.created_at.isoformat(),
        }

    elif name == "get_artifact_url":
        service = ArtifactService(session)
        expiration = arguments.get("expiration_seconds", 3600)
        url = await service.get_content_url(arguments["sha256"], expiration)
        return {
            "sha256": arguments["sha256"],
            "url": url,
            "expires_in": expiration,
        }

    else:
        return {"error": f"Unknown tool: {name}"}
