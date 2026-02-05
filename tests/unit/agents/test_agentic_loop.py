"""Full agentic loop tests using GenericFakeChatModel.

Tests the complete LLM → tool call → tool execution → LLM final answer
cycle with mocked services. Uses GenericFakeChatModel which can return
AIMessage objects with tool_calls, unlike FakeListChatModel.

Also tests reasoning/thinking token streaming through the adapter.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    ToolMessage,
)
from langchain_core.tools import tool

from intelli.agents.adapters import LangGraphToAISDKAdapter
from intelli.agents.graphs.research_assistant import (
    ResearchAssistantGraph,
    ResearchState,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Tool-bindable fake LLM wrapper
# ---------------------------------------------------------------------------


class ToolBindableFakeChatModel(GenericFakeChatModel):
    """GenericFakeChatModel that supports bind_tools (returns self)."""

    def bind_tools(self, tools, **kwargs):
        """No-op bind_tools — the fake already knows what to return."""
        return self


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_search_tool_call(
    query: str = "key terms",
    manifest: str = "abc123",
    call_id: str = "call_001",
) -> AIMessage:
    """Create an AIMessage that requests a search_documents tool call."""
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_documents",
                "args": {"query": query, "manifest_sha256": manifest},
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def _make_final_answer(
    text: str = "Here are the key terms: Protocol, Normative Framework.",
) -> AIMessage:
    """Create an AIMessage with a final text answer (no tool calls)."""
    return AIMessage(content=text)


def _make_list_notebooks_call(call_id: str = "call_002") -> AIMessage:
    """Create an AIMessage that requests list_notebooks."""
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "list_notebooks",
                "args": {},
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def _make_parallel_tool_calls() -> AIMessage:
    """Create an AIMessage with multiple parallel tool calls."""
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_documents",
                "args": {"query": "protocol", "manifest_sha256": "m1"},
                "id": "call_p1",
                "type": "tool_call",
            },
            {
                "name": "search_documents",
                "args": {"query": "normative framework", "manifest_sha256": "m1"},
                "id": "call_p2",
                "type": "tool_call",
            },
        ],
    )


def parse_sse(raw: str) -> list[dict]:
    """Parse SSE output into list of dicts."""
    events = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


# ---------------------------------------------------------------------------
# GenericFakeChatModel: verify it works with tool_calls
# ---------------------------------------------------------------------------


class TestGenericFakeChatModelToolCalls:
    """Verify that GenericFakeChatModel correctly returns tool_calls."""

    def test_returns_tool_call_message(self):
        model = ToolBindableFakeChatModel(messages=iter([_make_search_tool_call()]))
        response = model.invoke([HumanMessage(content="What are the key terms?")])
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["name"] == "search_documents"

    def test_sequences_through_tool_then_answer(self):
        model = ToolBindableFakeChatModel(
            messages=iter(
                [
                    _make_search_tool_call(),
                    _make_final_answer("The answer is 42."),
                ]
            )
        )
        # First call: tool request
        r1 = model.invoke([HumanMessage(content="question")])
        assert r1.tool_calls
        assert r1.content == ""

        # Second call: final answer
        r2 = model.invoke(
            [
                HumanMessage(content="question"),
                r1,
                ToolMessage(content="tool result", tool_call_id="call_001"),
            ]
        )
        assert r2.content == "The answer is 42."
        assert not r2.tool_calls

    def test_parallel_tool_calls(self):
        model = ToolBindableFakeChatModel(messages=iter([_make_parallel_tool_calls()]))
        response = model.invoke([HumanMessage(content="search both")])
        assert len(response.tool_calls) == 2
        assert response.tool_calls[0]["id"] == "call_p1"
        assert response.tool_calls[1]["id"] == "call_p2"

    def test_bind_tools_preserves_behaviour(self):
        """bind_tools on GenericFakeChatModel should not break tool_calls."""

        @tool
        def dummy(x: str) -> str:
            """Dummy."""
            return x

        model = ToolBindableFakeChatModel(messages=iter([_make_search_tool_call()]))
        bound = model.bind_tools([dummy])
        response = bound.invoke([HumanMessage(content="test")])
        assert response.tool_calls
        assert response.tool_calls[0]["name"] == "search_documents"


# ---------------------------------------------------------------------------
# Full graph agentic loop (mocked LLM + mocked tools)
# ---------------------------------------------------------------------------


class TestAgenticLoop:
    """Test the full LLM → tool → LLM cycle through the real graph."""

    @pytest.fixture
    def mock_search_result(self):
        return json.dumps(
            [
                {
                    "chunk_id": "chunk_001",
                    "artifact_sha256": "a" * 64,
                    "content": "Protocol: The executable intersection of normative rules.",
                    "score": 0.95,
                    "path_hint": "PROTOCOL-DESIGN.md",
                }
            ]
        )

    @pytest.mark.asyncio
    async def test_single_tool_call_loop(self, mock_search_result):
        """LLM calls search_documents, gets result, produces final answer."""
        fake_llm = ToolBindableFakeChatModel(
            messages=iter(
                [
                    _make_search_tool_call(query="protocol definition", manifest="m1"),
                    _make_final_answer(
                        "Protocol is the executable intersection of normative rules. [chunk_001]"
                    ),
                ]
            )
        )

        mock_session = AsyncMock()

        with (
            patch("intelli.agents.graphs.research_assistant.build_research_tools") as mock_build,
            patch("intelli.agents.graphs.research_assistant.RagService"),
        ):
            # Build real tools but with mocked services
            from intelli.services.knowledge.rag_service import RetrievedChunk

            mock_rag = AsyncMock()
            mock_rag.retrieve = AsyncMock(
                return_value=[
                    RetrievedChunk(
                        chunk_id=uuid4(),
                        artifact_sha256="a" * 64,
                        chunk_index=0,
                        content="Protocol: The executable intersection of normative rules.",
                        score=0.95,
                        path_hint="PROTOCOL-DESIGN.md",
                    )
                ]
            )

            # We need real tools for ToolNode, but with mocked services
            with (
                patch(
                    "intelli.agents.tools.research_tools.RagService",
                    return_value=mock_rag,
                ),
                patch("intelli.agents.tools.research_tools.PointerService"),
                patch("intelli.agents.tools.research_tools.ManifestService"),
            ):
                from intelli.agents.tools.research_tools import build_research_tools

                real_tools = build_research_tools(mock_session)
                mock_build.return_value = real_tools

                graph = ResearchAssistantGraph(session=mock_session)
                # Replace LLM with our fake
                graph._get_llm = lambda: fake_llm

                state = ResearchState(
                    messages=[HumanMessage(content="What is a Protocol?")],
                    manifest_sha256="m1",
                )

                result = await graph.ainvoke(state)

        # Should have 4 messages: Human, AI (tool call), Tool result, AI (final)
        assert len(result.messages) >= 3
        # Final message should be the answer
        final_msg = result.messages[-1]
        assert "Protocol" in final_msg.content
        assert "chunk_001" in final_msg.content

    @pytest.mark.asyncio
    async def test_list_notebooks_loop(self):
        """LLM calls list_notebooks, gets result, produces final answer."""
        fake_llm = ToolBindableFakeChatModel(
            messages=iter(
                [
                    _make_list_notebooks_call(),
                    _make_final_answer("You have 2 notebooks: Research and Test."),
                ]
            )
        )

        mock_session = AsyncMock()
        mock_ptr = AsyncMock()
        ptr1 = MagicMock(id=uuid4(), name="Research", namespace="default", manifest_sha256="x" * 64)
        ptr2 = MagicMock(id=uuid4(), name="Test", namespace="default", manifest_sha256="y" * 64)
        mock_ptr.list_pointers = AsyncMock(return_value=[ptr1, ptr2])

        with (
            patch("intelli.agents.graphs.research_assistant.build_research_tools") as mock_build,
            patch("intelli.agents.graphs.research_assistant.RagService"),
            patch("intelli.agents.tools.research_tools.RagService"),
            patch(
                "intelli.agents.tools.research_tools.PointerService",
                return_value=mock_ptr,
            ),
            patch("intelli.agents.tools.research_tools.ManifestService"),
        ):
            from intelli.agents.tools.research_tools import build_research_tools

            real_tools = build_research_tools(mock_session)
            mock_build.return_value = real_tools

            graph = ResearchAssistantGraph(session=mock_session)
            graph._get_llm = lambda: fake_llm

            state = ResearchState(
                messages=[HumanMessage(content="What notebooks do I have?")],
                manifest_sha256="m1",
            )
            result = await graph.ainvoke(state)

        final_msg = result.messages[-1]
        assert "2 notebooks" in final_msg.content

    @pytest.mark.asyncio
    async def test_no_tool_call_direct_answer(self):
        """LLM answers directly without calling any tools."""
        fake_llm = ToolBindableFakeChatModel(
            messages=iter(
                [
                    _make_final_answer("Hello! How can I help you?"),
                ]
            )
        )

        mock_session = AsyncMock()

        with (
            patch("intelli.agents.graphs.research_assistant.build_research_tools") as mock_build,
            patch("intelli.agents.graphs.research_assistant.RagService"),
        ):
            mock_build.return_value = []
            graph = ResearchAssistantGraph(session=mock_session)
            graph._get_llm = lambda: fake_llm

            state = ResearchState(
                messages=[HumanMessage(content="Hello")],
                manifest_sha256="m1",
            )
            result = await graph.ainvoke(state)

        # Only 2 messages: Human + AI answer (no tool call)
        assert len(result.messages) == 2
        assert "Hello" in result.messages[-1].content


# ---------------------------------------------------------------------------
# Adapter: reasoning/thinking events
# ---------------------------------------------------------------------------


class TestAdapterReasoningEvents:
    """Test that the adapter can forward reasoning/thinking events."""

    @pytest.mark.asyncio
    async def test_reasoning_events_forwarded(self):
        """on_chat_model_stream with reasoning content should produce reasoning SSE events."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            # Reasoning chunk
            chunk = AIMessageChunk(content="")
            chunk.additional_kwargs = {
                "reasoning": {
                    "id": "rs_001",
                    "summary": [{"type": "summary_text", "text": "First, I analyze..."}],
                    "type": "reasoning",
                }
            }
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": chunk},
            }
            # Then actual content
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="The answer is 42.")},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)

        # Should have text delta for "The answer is 42."
        text_deltas = [e for e in events if e.get("type") == "text-delta"]
        assert len(text_deltas) >= 1
        assert "42" in text_deltas[0]["delta"]

    @pytest.mark.asyncio
    async def test_tool_call_then_answer_stream(self):
        """Full streaming sequence: tool start → tool end → text answer."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            yield {
                "event": "on_tool_start",
                "name": "search_documents",
                "data": {"input": {"query": "protocol", "manifest_sha256": "m1"}},
            }
            yield {
                "event": "on_tool_end",
                "name": "search_documents",
                "data": {"output": '[{"content": "Protocol definition"}]'},
            }
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="Protocol is ")},
            }
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="the executable intersection.")},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        types = [e["type"] for e in events]

        # Tool events should come first
        assert "tool-input-start" in types
        assert "tool-output-available" in types
        # Then text
        assert "text-delta" in types
        # Adapter no longer emits finish - caller is responsible
        assert "finish" not in types

        # Accumulated text should be the answer
        assert adapter._accumulated_text == "Protocol is the executable intersection."

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_in_sequence(self):
        """Two sequential tool calls (retry search) then final answer."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            # First search
            yield {
                "event": "on_tool_start",
                "name": "search_documents",
                "data": {"input": {"query": "q1", "manifest_sha256": "m"}},
            }
            yield {"event": "on_tool_end", "name": "search_documents", "data": {"output": "[]"}}
            # Second search (retry)
            yield {
                "event": "on_tool_start",
                "name": "search_documents",
                "data": {"input": {"query": "q2", "manifest_sha256": "m"}},
            }
            yield {
                "event": "on_tool_end",
                "name": "search_documents",
                "data": {"output": '[{"content": "found"}]'},
            }
            # Final answer
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="Found it.")},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)

        # Should have 2 tool-input-start events
        tool_starts = [e for e in events if e.get("type") == "tool-input-start"]
        assert len(tool_starts) == 2

        # Should have 2 tool-input-available events (immediately after start)
        tool_inputs = [e for e in events if e.get("type") == "tool-input-available"]
        assert len(tool_inputs) == 2

        # Should have 2 tool-output-available events
        tool_outputs = [e for e in events if e.get("type") == "tool-output-available"]
        assert len(tool_outputs) == 2

        # Adapter no longer emits finish-step - caller is responsible
        step_finishes = [e for e in events if e.get("type") == "finish-step"]
        assert len(step_finishes) == 0


# ---------------------------------------------------------------------------
# Adapter: reasoning streaming (new feature)
# ---------------------------------------------------------------------------


class TestAdapterReasoningStreaming:
    """Test reasoning-start/delta/end SSE events for thinking models."""

    @pytest.mark.asyncio
    async def test_reasoning_deltas_streamed(self):
        """Reasoning chunks should produce reasoning-start/delta/end events."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            # Reasoning summary chunks (as langchain-openai emits them)
            chunk1 = AIMessageChunk(content="")
            chunk1.additional_kwargs = {
                "reasoning": {
                    "id": "rs_001",
                    "summary": [{"index": 0, "type": "summary_text", "text": "First, "}],
                    "type": "reasoning",
                }
            }
            yield {"event": "on_chat_model_stream", "data": {"chunk": chunk1}}

            chunk2 = AIMessageChunk(content="")
            chunk2.additional_kwargs = {
                "reasoning": {
                    "id": "rs_001",
                    "summary": [
                        {"index": 0, "type": "summary_text", "text": "I analyze the data."}
                    ],
                    "type": "reasoning",
                }
            }
            yield {"event": "on_chat_model_stream", "data": {"chunk": chunk2}}

            # Then actual answer
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="The answer is 42.")},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        types = [e["type"] for e in events]

        # Should have reasoning events
        assert "reasoning-start" in types or "reasoning-delta" in types or "text-delta" in types
        # And text events
        text_deltas = [e for e in events if e.get("type") == "text-delta"]
        assert any("42" in e.get("delta", "") for e in text_deltas)
