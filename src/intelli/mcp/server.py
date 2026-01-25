"""MCP Server for exposing platform tools to agents.

This server exposes the core substrate operations (artifacts, manifests, pointers)
and run management as MCP tools that can be used by LangGraph agents and other
MCP-compatible clients.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server

from intelli.mcp.tools import (
    knowledge_tools,
    run_tools,
    substrate_tools,
)


def create_mcp_server() -> Server:
    """Create and configure the MCP server.

    Returns:
        Configured MCP Server instance
    """
    server = Server("intelli-platform")

    # Register all tool modules
    substrate_tools.register(server)
    run_tools.register(server)
    knowledge_tools.register(server)

    return server


async def run_stdio_server() -> None:
    """Run the MCP server over stdio transport."""
    server = create_mcp_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_stdio_server())
