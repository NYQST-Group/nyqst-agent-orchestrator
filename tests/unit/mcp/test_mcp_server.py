"""Unit tests for MCP server initialization and tool registration."""

from unittest.mock import patch

import pytest

from intelli.mcp.server import create_mcp_server
from intelli.mcp.tools import knowledge_tools, run_tools, substrate_tools

pytestmark = pytest.mark.unit


class TestCreateMcpServer:
    def test_create_mcp_server_returns_server_instance(self):
        """Test that create_mcp_server returns a Server instance."""
        server = create_mcp_server()
        assert server is not None
        assert server.name == "intelli-platform"

    @patch.object(substrate_tools, "register")
    @patch.object(run_tools, "register")
    @patch.object(knowledge_tools, "register")
    def test_register_calls_all_tool_modules(
        self, mock_kb_register, mock_run_register, mock_substrate_register
    ):
        """Test that all tool modules are registered."""
        server = create_mcp_server()

        mock_substrate_register.assert_called_once_with(server)
        mock_run_register.assert_called_once_with(server)
        mock_kb_register.assert_called_once_with(server)

    def test_no_duplicate_tool_names(self):
        """Test that there are no duplicate tool names across modules."""
        from intelli.mcp.tools.knowledge_tools import KNOWLEDGE_TOOLS
        from intelli.mcp.tools.run_tools import RUN_TOOLS
        from intelli.mcp.tools.substrate_tools import SUBSTRATE_TOOLS

        substrate_names = {tool.name for tool in SUBSTRATE_TOOLS}
        run_names = {tool.name for tool in RUN_TOOLS}
        kb_names = {tool.name for tool in KNOWLEDGE_TOOLS}

        # Check for duplicates between substrate and run tools
        substrate_run_overlap = substrate_names & run_names
        assert not substrate_run_overlap, (
            f"Duplicate tools between substrate and run: {substrate_run_overlap}"
        )

        # Check for duplicates between substrate and knowledge tools
        substrate_kb_overlap = substrate_names & kb_names
        assert not substrate_kb_overlap, (
            f"Duplicate tools between substrate and knowledge: {substrate_kb_overlap}"
        )

        # Check for duplicates between run and knowledge tools
        run_kb_overlap = run_names & kb_names
        assert not run_kb_overlap, f"Duplicate tools between run and knowledge: {run_kb_overlap}"
