"""Tests for ResearchAssistantGraph — retrieve and generate node logic.

Uses FakeListChatModel for deterministic LLM responses and mocks
the RagService to isolate graph logic from database/embedding calls.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from intelli.agents.graphs.research_assistant import (
    ResearchAssistantGraph,
    ResearchState,
    _chunks_to_dicts,
    _format_sources,
    create_research_assistant,
)
from tests.factories import make_retrieved_chunk

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


class TestFormatSources:
    def test_empty_sources(self):
        assert _format_sources([]) == "No sources available."

    def test_single_source_with_path_hint(self):
        src = {"path_hint": "docs/lease.pdf", "content": "Section 5", "score": 0.95}
        result = _format_sources([src])
        assert "[1] docs/lease.pdf" in result
        assert "Section 5" in result
        assert "0.95" in result

    def test_missing_path_hint_falls_back_to_sha(self):
        src = {"artifact_sha256": "aabbccdd11223344", "content": "text", "score": 0.5}
        result = _format_sources([src])
        assert "[1] aabbccdd1122" in result

    def test_multiple_sources_numbered(self):
        sources = [
            {"path_hint": "a.pdf", "content": "A", "score": 0.9},
            {"path_hint": "b.pdf", "content": "B", "score": 0.8},
        ]
        result = _format_sources(sources)
        assert "[1] a.pdf" in result
        assert "[2] b.pdf" in result


class TestChunksToDicts:
    def test_converts_retrieved_chunks(self):
        chunk = make_retrieved_chunk(content="test content", score=0.88)
        result = _chunks_to_dicts([chunk])
        assert len(result) == 1
        d = result[0]
        assert d["content"] == "test content"
        assert d["score"] == 0.88
        assert "chunk_id" in d
        assert "artifact_sha256" in d

    def test_empty_list(self):
        assert _chunks_to_dicts([]) == []

    def test_preserves_path_hint(self):
        chunk = make_retrieved_chunk(path_hint="reports/q4.pdf")
        result = _chunks_to_dicts([chunk])
        assert result[0]["path_hint"] == "reports/q4.pdf"


# ---------------------------------------------------------------------------
# Graph node tests
# ---------------------------------------------------------------------------


def _make_bindable_fake_llm(responses: list[str]):
    """Create a mock LLM that supports bind_tools and returns canned AIMessages."""
    mock_llm = MagicMock()
    response_msgs = [AIMessage(content=r) for r in responses]
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    mock_llm.ainvoke = AsyncMock(side_effect=response_msgs)
    return mock_llm


class TestAgentNode:
    """Tests for the agentic _agent_node that replaced retrieve/generate."""

    @pytest.mark.asyncio
    async def test_agent_node_returns_messages(self):
        session = AsyncMock()
        graph = ResearchAssistantGraph(session=session)

        fake_llm = _make_bindable_fake_llm(["The answer is 42."])

        with patch.object(graph, "_get_llm", return_value=fake_llm):
            state = ResearchState(
                messages=[HumanMessage(content="What is the answer?")],
                manifest_sha256="abc123",
            )
            result = await graph._agent_node(state)

        assert len(result["messages"]) == 1
        assert "42" in result["messages"][0].content

    @pytest.mark.asyncio
    async def test_agent_node_includes_system_prompt_with_manifest(self):
        session = AsyncMock()
        graph = ResearchAssistantGraph(session=session)

        fake_llm = _make_bindable_fake_llm(["Response"])

        with patch.object(graph, "_get_llm", return_value=fake_llm) as mock_get_llm:
            state = ResearchState(
                messages=[HumanMessage(content="question")],
                manifest_sha256="sha-test-123",
            )
            await graph._agent_node(state)

        mock_get_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_node_handles_no_manifest(self):
        session = AsyncMock()
        graph = ResearchAssistantGraph(session=session)

        fake_llm = _make_bindable_fake_llm(["I don't have document context."])

        with patch.object(graph, "_get_llm", return_value=fake_llm):
            state = ResearchState(
                messages=[HumanMessage(content="question")],
                manifest_sha256=None,
            )
            result = await graph._agent_node(state)

        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_agent_node_with_empty_messages(self):
        session = AsyncMock()
        graph = ResearchAssistantGraph(session=session)

        fake_llm = _make_bindable_fake_llm(["Default answer"])

        with patch.object(graph, "_get_llm", return_value=fake_llm):
            state = ResearchState(messages=[])
            result = await graph._agent_node(state)

        assert "Default answer" in result["messages"][0].content


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------


class TestCreateResearchAssistant:
    @pytest.mark.asyncio
    async def test_factory_returns_graph_instance(self):
        session = AsyncMock()
        graph = await create_research_assistant(session)
        assert isinstance(graph, ResearchAssistantGraph)

    @pytest.mark.asyncio
    async def test_factory_accepts_ledger(self):
        session = AsyncMock()
        ledger = AsyncMock()
        graph = await create_research_assistant(session, ledger=ledger)
        assert graph.ledger is ledger
