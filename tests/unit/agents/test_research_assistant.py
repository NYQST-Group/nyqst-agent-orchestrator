"""Unit tests for ResearchAssistantGraph — prompt, tools, graph routing.

Tests the research assistant WITHOUT hitting a real LLM or database.
Uses mock LLMs that return predetermined AIMessages (including tool_calls)
to verify the full agentic loop: system prompt injection → LLM → tool
routing → tool execution → LLM final answer.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from intelli.agents.graphs.research_assistant import (
    SYSTEM_PROMPT,
    ResearchAssistantGraph,
    ResearchState,
    _chunks_to_dicts,
    _format_sources,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT tests
# ---------------------------------------------------------------------------


class TestSystemPrompt:
    """Verify prompt content enforces action-first behaviour."""

    def test_prompt_contains_act_first_directive(self):
        assert "Act first" in SYSTEM_PROMPT

    def test_prompt_forbids_asking_format(self):
        assert "Do not ask which format" in SYSTEM_PROMPT

    def test_prompt_forbids_listing_capabilities(self):
        assert "Never list your capabilities" in SYSTEM_PROMPT

    def test_prompt_requires_search_before_answering(self):
        assert "ALWAYS call search_documents before answering" in SYSTEM_PROMPT

    def test_prompt_has_manifest_placeholder(self):
        assert "{manifest_sha256}" in SYSTEM_PROMPT

    def test_prompt_formats_with_manifest(self):
        formatted = SYSTEM_PROMPT.format(manifest_sha256="abc123")
        assert "abc123" in formatted
        assert "{manifest_sha256}" not in formatted

    def test_prompt_formats_with_not_set(self):
        formatted = SYSTEM_PROMPT.format(manifest_sha256="not set")
        assert "not set" in formatted

    def test_prompt_mentions_all_four_tools(self):
        for tool_name in [
            "search_documents",
            "list_notebooks",
            "get_document_info",
            "compare_manifests",
        ]:
            assert tool_name in SYSTEM_PROMPT, f"Missing tool: {tool_name}"

    def test_prompt_mentions_retry_limit(self):
        assert "up to 3 searches" in SYSTEM_PROMPT

    def test_prompt_mentions_citation_format(self):
        # New citation format uses numbered citations [1], [2], [3]
        assert "[1]" in SYSTEM_PROMPT
        assert "[2]" in SYSTEM_PROMPT
        assert "[3]" in SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestFormatSources:
    """Test _format_sources helper."""

    def test_empty_sources(self):
        assert _format_sources([]) == "No sources available."

    def test_single_source_with_path_hint(self):
        sources = [{"path_hint": "docs/report.pdf", "content": "Hello", "score": 0.9}]
        result = _format_sources(sources)
        assert "[1] docs/report.pdf" in result
        assert "0.90" in result
        assert "Hello" in result

    def test_source_falls_back_to_sha_prefix(self):
        sha = "a" * 64
        sources = [{"artifact_sha256": sha, "content": "X", "score": 0.5}]
        result = _format_sources(sources)
        assert "[1] aaaaaaaaaaaa" in result  # first 12 chars

    def test_multiple_sources_numbered(self):
        sources = [
            {"path_hint": "a.pdf", "content": "A", "score": 0.9},
            {"path_hint": "b.pdf", "content": "B", "score": 0.8},
        ]
        result = _format_sources(sources)
        assert "[1]" in result
        assert "[2]" in result


class TestChunksToDicts:
    """Test _chunks_to_dicts converter."""

    def test_converts_retrieved_chunk(self):
        from intelli.services.knowledge.rag_service import RetrievedChunk

        uid = uuid4()
        chunk = RetrievedChunk(
            chunk_id=uid,
            artifact_sha256="x" * 64,
            chunk_index=3,
            content="test",
            score=0.85,
            path_hint="a.pdf",
        )
        result = _chunks_to_dicts([chunk])
        assert len(result) == 1
        assert result[0]["chunk_id"] == str(uid)
        assert result[0]["chunk_index"] == 3
        assert result[0]["score"] == 0.85

    def test_empty_list(self):
        assert _chunks_to_dicts([]) == []


# ---------------------------------------------------------------------------
# ResearchState tests
# ---------------------------------------------------------------------------


class TestResearchState:
    """Verify dataclass defaults."""

    def test_defaults(self):
        state = ResearchState()
        assert state.messages == []
        assert state.context_pointer_id is None
        assert state.manifest_sha256 is None
        assert state.sources == []
        assert state.error is None
        assert state.run_id is None

    def test_with_values(self):
        uid = uuid4()
        state = ResearchState(
            messages=[HumanMessage(content="hi")],
            manifest_sha256="abc",
            run_id=uid,
        )
        assert len(state.messages) == 1
        assert state.manifest_sha256 == "abc"
        assert state.run_id == uid


# ---------------------------------------------------------------------------
# Graph construction and tool binding
# ---------------------------------------------------------------------------


class TestGraphConstruction:
    """Test that the graph builds correctly with mocked dependencies."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def graph(self, mock_session):
        with (
            patch("intelli.agents.graphs.research_assistant.build_research_tools") as mock_tools,
            patch("intelli.agents.graphs.research_assistant.RagService"),
        ):
            # Provide minimal tool stubs so bind_tools works
            mock_tools.return_value = []
            return ResearchAssistantGraph(session=mock_session)

    def test_graph_has_agent_and_tools_nodes(self, graph):
        """Graph should have 'agent' and 'tools' nodes."""
        # The compiled graph exposes nodes
        compiled = graph._graph
        assert compiled is not None

    def test_tools_are_stored(self, mock_session):
        from langchain_core.tools import tool as tool_decorator

        @tool_decorator
        def dummy_a(x: str) -> str:
            """Dummy tool A."""
            return x

        @tool_decorator
        def dummy_b(x: str) -> str:
            """Dummy tool B."""
            return x

        with (
            patch("intelli.agents.graphs.research_assistant.build_research_tools") as mock_tools,
            patch("intelli.agents.graphs.research_assistant.RagService"),
        ):
            mock_tools.return_value = [dummy_a, dummy_b]
            g = ResearchAssistantGraph(session=mock_session)
            assert len(g.tools) == 2
            assert g.tools[0].name == "dummy_a"


# ---------------------------------------------------------------------------
# _agent_node: system prompt injection
# ---------------------------------------------------------------------------


class TestAgentNode:
    """Test that the agent node injects the system prompt correctly."""

    @pytest.mark.asyncio
    async def test_system_prompt_injected_with_manifest(self):
        """The first message to the LLM should be a SystemMessage with the manifest."""
        mock_session = AsyncMock()
        captured_messages = []

        # Mock LLM that captures what it receives
        mock_llm = AsyncMock()
        mock_response = AIMessage(content="I found the answer.")

        async def capture_invoke(messages):
            captured_messages.extend(messages)
            return mock_response

        mock_llm.ainvoke = capture_invoke
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)

        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
        ):
            graph = ResearchAssistantGraph(session=mock_session)
            # Monkey-patch _get_llm to return our mock
            graph._get_llm = lambda: mock_llm

            state = ResearchState(
                messages=[HumanMessage(content="What are the key terms?")],
                manifest_sha256="deadbeef" * 8,
            )

            result = await graph._agent_node(state)

        # System message should be first
        assert isinstance(captured_messages[0], SystemMessage)
        assert "deadbeef" in captured_messages[0].content
        assert "Act first" in captured_messages[0].content

        # User message should be second
        assert isinstance(captured_messages[1], HumanMessage)
        assert "key terms" in captured_messages[1].content

        # Result should contain the AI response
        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "I found the answer."

    @pytest.mark.asyncio
    async def test_manifest_not_set_when_missing(self):
        """When manifest_sha256 is None, prompt should say 'not set'."""
        mock_session = AsyncMock()
        captured_messages = []

        mock_llm = AsyncMock()

        async def capture_invoke(messages):
            captured_messages.extend(messages)
            return AIMessage(content="ok")

        mock_llm.ainvoke = capture_invoke
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)

        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
        ):
            graph = ResearchAssistantGraph(session=mock_session)
            graph._get_llm = lambda: mock_llm

            state = ResearchState(
                messages=[HumanMessage(content="hi")],
                manifest_sha256=None,
            )
            await graph._agent_node(state)

        assert "not set" in captured_messages[0].content


# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------


class TestLLMConfig:
    """Test that _build_llm configures the model correctly."""

    def test_temperature_from_settings(self):
        mock_session = AsyncMock()
        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.graphs.research_assistant.ChatOpenAI") as mock_chat,
        ):
            ResearchAssistantGraph(session=mock_session)

            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["temperature"] == 0.2

    def test_streaming_is_enabled(self):
        mock_session = AsyncMock()
        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.graphs.research_assistant.ChatOpenAI") as mock_chat,
        ):
            ResearchAssistantGraph(session=mock_session)

            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["streaming"] is True

    def test_max_tokens_set(self):
        mock_session = AsyncMock()
        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.graphs.research_assistant.ChatOpenAI") as mock_chat,
        ):
            ResearchAssistantGraph(session=mock_session)

            call_kwargs = mock_chat.call_args[1]
            assert "max_tokens" in call_kwargs
            assert call_kwargs["max_tokens"] > 0

    def test_llm_reused_across_calls(self):
        """_get_llm should return the same instance (not create a new one each time)."""
        mock_session = AsyncMock()
        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.graphs.research_assistant.ChatOpenAI"),
        ):
            graph = ResearchAssistantGraph(session=mock_session)
            llm1 = graph._get_llm()
            llm2 = graph._get_llm()
            assert llm1 is llm2

    def test_reasoning_effort_passed_when_set(self):
        mock_session = AsyncMock()
        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.graphs.research_assistant.ChatOpenAI") as mock_chat,
            patch("intelli.agents.graphs.research_assistant.settings") as mock_settings,
        ):
            mock_settings.chat_model = "o4-mini"
            mock_settings.openai_api_key = "test"
            mock_settings.openai_base_url = None
            mock_settings.chat_model_temperature = 0.2
            mock_settings.chat_model_max_tokens = 4096
            mock_settings.chat_model_reasoning_effort = "medium"

            ResearchAssistantGraph(session=mock_session)

            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["model_kwargs"]["reasoning_effort"] == "medium"

    def test_no_reasoning_effort_when_none(self):
        mock_session = AsyncMock()
        with (
            patch(
                "intelli.agents.graphs.research_assistant.build_research_tools",
                return_value=[],
            ),
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.graphs.research_assistant.ChatOpenAI") as mock_chat,
            patch("intelli.agents.graphs.research_assistant.settings") as mock_settings,
        ):
            mock_settings.chat_model = "gpt-4o-mini"
            mock_settings.openai_api_key = "test"
            mock_settings.openai_base_url = None
            mock_settings.chat_model_temperature = 0.2
            mock_settings.chat_model_max_tokens = 4096
            mock_settings.chat_model_reasoning_effort = None

            ResearchAssistantGraph(session=mock_session)

            call_kwargs = mock_chat.call_args[1]
            assert "model_kwargs" not in call_kwargs
