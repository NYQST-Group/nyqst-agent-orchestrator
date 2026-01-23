"""MCP tools for knowledge base operations.

These tools will enable agents to query knowledge bases, retrieve evidence,
and work with claims/citations. This is a stub for Phase 2 implementation.
"""

from mcp.server import Server
from mcp.types import Tool


# Placeholder tools for future KB operations
KNOWLEDGE_TOOLS = [
    Tool(
        name="kb_query",
        description="[Phase 2] Query a knowledge base with semantic search. Returns relevant chunks with evidence spans.",
        inputSchema={
            "type": "object",
            "properties": {
                "kb_id": {
                    "type": "string",
                    "description": "Knowledge base ID",
                },
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "profile": {
                    "type": "string",
                    "enum": ["fast-skim", "legal-citations", "strict-evidence"],
                    "description": "Retrieval profile to use",
                    "default": "fast-skim",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 10,
                },
            },
            "required": ["kb_id", "query"],
        },
    ),
]


def register(server: Server) -> None:
    """Register knowledge tools with the MCP server.

    Note: These are placeholder tools for Phase 2 implementation.
    They are registered but return "not implemented" errors.
    """
    pass
