"""Unit tests for LangGraphToAISDKAdapter — SSE output formatting.

Verifies the adapter converts LangGraph events into correct Vercel AI SDK
v3 SSE protocol. No LLM, no database — pure formatting logic.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from intelli.agents.adapters import LangGraphToAISDKAdapter

pytestmark = pytest.mark.unit


def parse_sse(raw: str) -> list[dict]:
    """Parse SSE output into list of dicts."""
    events = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


# ---------------------------------------------------------------------------
# Basic formatting
# ---------------------------------------------------------------------------


class TestSSEFormatting:
    def test_sse_format(self):
        adapter = LangGraphToAISDKAdapter()
        result = adapter._sse({"type": "test"})
        assert result == 'event: message\ndata: {"type": "test"}\n\n'

    def test_text_chunk_emits_start_and_delta(self):
        adapter = LangGraphToAISDKAdapter()
        result = adapter._format_text_chunk("Hello")
        events = parse_sse(result)

        types = [e["type"] for e in events]
        assert "start" in types
        assert "start-step" in types
        assert "text-start" in types
        assert "text-delta" in types
        assert events[-1]["delta"] == "Hello"

    def test_consecutive_text_chunks_no_duplicate_start(self):
        adapter = LangGraphToAISDKAdapter()
        r1 = adapter._format_text_chunk("A")
        r2 = adapter._format_text_chunk("B")

        events_1 = parse_sse(r1)
        events_2 = parse_sse(r2)

        # First chunk has start events
        assert any(e["type"] == "start" for e in events_1)
        # Second chunk should NOT have start again
        assert not any(e["type"] == "start" for e in events_2)
        # But both have text-delta
        assert events_2[0]["type"] == "text-delta"

    def test_accumulated_text_requires_convert_stream(self):
        """_format_text_chunk doesn't accumulate — that's convert_events_stream's job."""
        adapter = LangGraphToAISDKAdapter()
        # Manually accumulate like convert_events_stream does
        adapter._accumulated_text += "Hello "
        adapter._format_text_chunk("Hello ")
        adapter._accumulated_text += "world"
        adapter._format_text_chunk("world")
        assert adapter._accumulated_text == "Hello world"


# ---------------------------------------------------------------------------
# Done signal
# ---------------------------------------------------------------------------


class TestDoneSignal:
    def test_done_emits_finish(self):
        adapter = LangGraphToAISDKAdapter()
        result = adapter._format_done()
        events = parse_sse(result)
        assert events[-1]["type"] == "finish"

    def test_done_closes_text_and_step_if_open(self):
        adapter = LangGraphToAISDKAdapter()
        adapter._format_text_chunk("some text")
        result = adapter._format_done()
        events = parse_sse(result)
        types = [e["type"] for e in events]
        assert "text-end" in types
        assert "finish-step" in types
        assert "finish" in types


# ---------------------------------------------------------------------------
# Source documents
# ---------------------------------------------------------------------------


class TestSourceDocuments:
    def test_sources_emit_source_document_events(self):
        adapter = LangGraphToAISDKAdapter()
        result = adapter._format_data_chunk(
            {
                "type": "sources",
                "sources": [
                    {
                        "chunk_id": "abc123",
                        "path_hint": "report.pdf",
                        "content": "test content",
                        "score": 0.9,
                        "artifact_sha256": "x" * 64,
                        "chunk_index": 0,
                    },
                ],
            }
        )
        events = parse_sse(result)
        source_events = [e for e in events if e["type"] == "source-document"]
        assert len(source_events) == 1
        assert source_events[0]["sourceId"] == "abc123"
        assert source_events[0]["title"] == "report.pdf"
        assert source_events[0]["providerMetadata"]["custom"]["score"] == 0.9

    def test_sources_fallback_to_sha_prefix_for_title(self):
        adapter = LangGraphToAISDKAdapter()
        sha = "abcdef" * 11  # 66 chars, will be truncated
        result = adapter._format_data_chunk(
            {
                "type": "sources",
                "sources": [
                    {"chunk_id": "id1", "artifact_sha256": sha, "content": "", "score": 0},
                ],
            }
        )
        events = parse_sse(result)
        source_events = [e for e in events if e["type"] == "source-document"]
        assert source_events[0]["title"] == sha[:12]

    def test_multiple_sources(self):
        adapter = LangGraphToAISDKAdapter()
        result = adapter._format_data_chunk(
            {
                "type": "sources",
                "sources": [
                    {"chunk_id": "a", "path_hint": "a.pdf", "content": "", "score": 0},
                    {"chunk_id": "b", "path_hint": "b.pdf", "content": "", "score": 0},
                ],
            }
        )
        events = parse_sse(result)
        source_events = [e for e in events if e["type"] == "source-document"]
        assert len(source_events) == 2


# ---------------------------------------------------------------------------
# Step boundaries (tool execution)
# ---------------------------------------------------------------------------


class TestStepBoundaries:
    def test_new_step_closes_text_and_opens_new(self):
        adapter = LangGraphToAISDKAdapter()
        adapter._format_text_chunk("thinking...")
        result = adapter._start_new_step()
        events = parse_sse(result)
        types = [e["type"] for e in events]
        assert "text-end" in types
        assert "finish-step" in types
        assert "start-step" in types


# ---------------------------------------------------------------------------
# convert_events_stream (astream_events integration)
# ---------------------------------------------------------------------------


class TestConvertEventsStream:
    @pytest.mark.asyncio
    async def test_chat_model_stream_tokens(self):
        """on_chat_model_stream events should produce text-delta."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            from langchain_core.messages import AIMessageChunk

            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="Hello")},
            }
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content=" world")},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        deltas = [e for e in events if e.get("type") == "text-delta"]
        assert len(deltas) == 2
        assert deltas[0]["delta"] == "Hello"
        assert deltas[1]["delta"] == " world"
        assert adapter._accumulated_text == "Hello world"

    @pytest.mark.asyncio
    async def test_tool_start_and_end_events(self):
        """on_tool_start / on_tool_end should produce tool SSE events."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            yield {
                "event": "on_tool_start",
                "name": "search_documents",
                "data": {"input": {"query": "protocol", "manifest_sha256": "abc"}},
            }
            yield {
                "event": "on_tool_end",
                "name": "search_documents",
                "data": {"output": '[{"content": "result"}]'},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        types = [e["type"] for e in events]
        assert "tool-input-start" in types
        assert "tool-input-available" in types
        assert "tool-output-available" in types
        # Adapter no longer emits finish - caller is responsible
        assert "finish" not in types

    @pytest.mark.asyncio
    async def test_ledger_logging_on_tool_events(self):
        """When ledger is provided, tool events should be logged."""
        mock_ledger = AsyncMock()
        run_id = uuid4()
        adapter = LangGraphToAISDKAdapter(ledger=mock_ledger, run_id=run_id)

        async def fake_events():
            yield {
                "event": "on_tool_start",
                "name": "search_documents",
                "data": {"input": {"query": "test"}},
            }
            yield {
                "event": "on_tool_end",
                "name": "search_documents",
                "data": {"output": "result"},
            }

        async for _ in adapter.convert_events_stream(fake_events()):
            pass

        mock_ledger.log_tool_call_start.assert_called_once()
        mock_ledger.log_tool_call_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_content_skipped(self):
        """Empty string content from LLM should not produce text-delta."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            from langchain_core.messages import AIMessageChunk

            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="")},
            }

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        assert not any(e.get("type") == "text-delta" for e in events)

    @pytest.mark.asyncio
    async def test_stream_ends_with_finish(self):
        """Adapter no longer emits finish - caller is responsible."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_events():
            return
            yield  # empty async generator

        chunks = []
        async for chunk in adapter.convert_events_stream(fake_events()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        # Empty stream produces no events
        assert len(events) == 0


# ---------------------------------------------------------------------------
# convert_stream (astream / updates mode)
# ---------------------------------------------------------------------------


class TestConvertStream:
    @pytest.mark.asyncio
    async def test_agent_node_text(self):
        """Agent node updates with messages produce text chunks."""
        adapter = LangGraphToAISDKAdapter()

        from langchain_core.messages import AIMessage

        async def fake_stream():
            yield {"agent": {"messages": [AIMessage(content="The answer is 42.")]}}

        chunks = []
        async for chunk in adapter.convert_stream(fake_stream()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        deltas = [e for e in events if e.get("type") == "text-delta"]
        assert len(deltas) == 1
        assert "42" in deltas[0]["delta"]

    @pytest.mark.asyncio
    async def test_error_in_node_output(self):
        """Error in node output should be forwarded."""
        adapter = LangGraphToAISDKAdapter()

        async def fake_stream():
            yield {"agent": {"error": "Something went wrong"}}

        chunks = []
        async for chunk in adapter.convert_stream(fake_stream()):
            chunks.append(chunk)

        all_text = "".join(chunks)
        events = parse_sse(all_text)
        # Should contain error data and finish
        types = [e.get("type") for e in events]
        assert "finish" in types
