"""Adapters for bridging agent frameworks to external protocols.

Per ADR-005, LangGraph's streaming output is bridged to the Vercel AI SDK
UI protocol via adapters. This ensures:
1. Frontend gets AI SDK compatible events for useChat hook
2. Platform run ledger receives authoritative audit events
"""

from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from intelli.services.runs.ledger_service import LedgerService


@dataclass
class AISDKTextChunk:
    """A text chunk in Vercel AI SDK format."""

    type: str = "text"
    text: str = ""


@dataclass
class AISDKDataChunk:
    """A data chunk for tool calls, sources, etc."""

    type: str = "data"
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class LangGraphToAISDKAdapter:
    """Adapter that converts LangGraph stream events to Vercel AI SDK format.

    This adapter:
    1. Converts LangGraph node updates to AI SDK text/data chunks
    2. Emits AI SDK v3 tool-call events for ToolNode execution
    3. Emits run ledger events for platform audit
    4. Handles streaming tokens from LLM calls

    AI SDK v3 uses SSE (Server-Sent Events) with JSON payloads:
    - data: {"type":"text-start","id":"..."}
    - data: {"type":"text-delta","id":"...","delta":"..."}
    - data: {"type":"text-end","id":"..."}
    - data: {"type":"tool-call-streaming-start","toolCallId":"...","toolName":"..."}
    - data: {"type":"tool-call","toolCallId":"...","toolName":"...","args":{}}
    - data: {"type":"tool-result","toolCallId":"...","result":"..."}
    - data: {"type":"start-step"}
    - data: {"type":"finish-step"}
    - data: {"type":"finish"}
    """

    def __init__(
        self,
        ledger: LedgerService | None = None,
        run_id: UUID | None = None,
    ):
        self.ledger = ledger
        self.run_id = run_id
        self._accumulated_text = ""
        self._text_started = False
        self._text_id = "text-1"
        self._step_started = False
        self._step_count = 0
        self._reasoning_started = False
        self._reasoning_id = "reasoning-1"
        # Token and latency tracking
        self._start_time: float | None = None
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    def _sse(self, data: dict) -> str:
        """Format a dict as an SSE message event (AI SDK v5 format).

        Per AI SDK spec, all message chunks should use 'event: message' type.
        See: https://github.com/vercel/ai - processUIMessageStream expects this format.
        """
        return f"event: message\ndata: {json.dumps(data)}\n\n"

    def _ensure_start(self) -> str:
        """Emit start + start-step if not yet emitted."""
        out = ""
        if not self._step_started:
            self._step_started = True
            self._step_count += 1
            if self._step_count == 1:
                out += self._sse({"type": "start"})
            out += self._sse({"type": "start-step"})
        return out

    def _start_new_step(self) -> str:
        """Close the current step and start a new one."""
        out = ""
        if self._text_started:
            out += self._sse({"type": "text-end", "id": self._text_id})
            self._text_started = False
        if self._step_started:
            out += self._sse({"type": "finish-step"})
            self._step_started = False
        out += self._ensure_start()
        return out

    def _ensure_text_start(self) -> str:
        """Emit text-start if not yet emitted."""
        out = self._ensure_start()
        if not self._text_started:
            self._text_started = True
            out += self._sse({"type": "text-start", "id": self._text_id})
        return out

    def _end_reasoning(self) -> str:
        """Close reasoning block if open."""
        if not self._reasoning_started:
            return ""
        self._reasoning_started = False
        return self._sse({"type": "reasoning-end", "id": self._reasoning_id})

    def _format_reasoning_chunk(self, text: str) -> str:
        """Format a reasoning/thinking chunk as SSE reasoning-delta."""
        out = self._ensure_start()
        if not self._reasoning_started:
            self._reasoning_started = True
            out += self._sse({"type": "reasoning-start", "id": self._reasoning_id})
        out += self._sse({"type": "reasoning-delta", "id": self._reasoning_id, "delta": text})
        return out

    def _format_text_chunk(self, text: str) -> str:
        """Format a text chunk as SSE text-delta."""
        # Close reasoning block before starting text
        out = self._end_reasoning()
        out += self._ensure_text_start()
        out += self._sse({"type": "text-delta", "id": self._text_id, "delta": text})
        return out

    def _format_data_chunk(self, data: dict) -> str:
        """Format a data chunk as v3 SSE events.

        For sources, emit individual source-document events.
        Other data types are emitted as metadata via providerMetadata on a
        source-document event (v3 has no generic data channel).
        """
        out = self._ensure_start()
        if data.get("type") == "sources":
            for src in data.get("sources", []):
                out += self._sse(
                    {
                        "type": "source-document",
                        "sourceId": src.get("chunk_id", ""),
                        "mediaType": "text/plain",
                        "title": src.get("path_hint") or src.get("artifact_sha256", "")[:12],
                        "providerMetadata": {
                            "custom": {
                                "content": src.get("content", ""),
                                "score": src.get("score", 0),
                                "artifact_sha256": src.get("artifact_sha256", ""),
                                "chunk_index": src.get("chunk_index", 0),
                            }
                        },
                    }
                )
        return out

    def _format_done(self, metadata: dict | None = None) -> str:
        """Format the finish signals.

        Args:
            metadata: Optional metadata to include in the finish event.
                     Will be sent as messageMetadata field per AI SDK v3+ spec.
        """
        out = self._end_reasoning()
        if self._text_started:
            out += self._sse({"type": "text-end", "id": self._text_id})
        if self._step_started:
            out += self._sse({"type": "finish-step"})

        # Build finish event with optional metadata
        finish_event: dict = {"type": "finish"}
        if metadata:
            finish_event["messageMetadata"] = metadata

        out += self._sse(finish_event)
        return out

    def get_latency_ms(self) -> int | None:
        """Get the elapsed time in milliseconds since stream started."""
        if self._start_time is None:
            return None
        return int((time.monotonic() - self._start_time) * 1000)

    def get_token_usage(self) -> dict:
        """Get accumulated token usage statistics."""
        return {
            "input_tokens": self._total_input_tokens,
            "output_tokens": self._total_output_tokens,
        }

    async def convert_stream(
        self,
        langgraph_stream: AsyncIterator[dict[str, Any]],
    ) -> AsyncIterator[str]:
        """Convert a LangGraph stream to AI SDK format.

        Args:
            langgraph_stream: AsyncIterator of LangGraph events

        Yields:
            AI SDK formatted string chunks
        """
        async for event in langgraph_stream:
            async for chunk in self._process_event(event):
                yield chunk

        yield self._format_done()

    async def convert_events_stream(
        self,
        langgraph_events: AsyncIterator[dict[str, Any]],
    ) -> AsyncIterator[str]:
        """Convert LangGraph astream_events to AI SDK format.

        This handles the more detailed event stream including LLM tokens
        and tool call events for the agentic loop.

        Args:
            langgraph_events: AsyncIterator from astream_events

        Yields:
            AI SDK formatted string chunks
        """
        # Start timing
        self._start_time = time.monotonic()

        async for event in langgraph_events:
            event_type = event.get("event", "")
            event_data = event.get("data", {})

            if event_type == "on_chat_model_stream":
                chunk = event_data.get("chunk")
                if not chunk:
                    continue

                # Check for reasoning/thinking content (o1/o3/o4-mini models)
                extra = getattr(chunk, "additional_kwargs", {})
                reasoning = extra.get("reasoning")
                if reasoning and isinstance(reasoning, dict):
                    summaries = reasoning.get("summary", [])
                    for s in summaries:
                        text = s.get("text", "")
                        if text:
                            yield self._format_reasoning_chunk(text)

                # Regular text content
                if hasattr(chunk, "content"):
                    content = chunk.content
                    if content:
                        self._accumulated_text += content
                        yield self._format_text_chunk(content)

            elif event_type == "on_chat_model_end":
                # Extract token usage from the final LLM response
                output = event_data.get("output")
                if output:
                    usage_metadata = getattr(output, "usage_metadata", None)
                    if usage_metadata:
                        self._total_input_tokens += usage_metadata.get("input_tokens", 0)
                        self._total_output_tokens += usage_metadata.get("output_tokens", 0)

            elif event_type == "on_chain_end":
                output = event_data.get("output", {})
                if isinstance(output, dict):
                    sources = output.get("sources", [])
                    if sources:
                        yield self._format_data_chunk(
                            {
                                "type": "sources",
                                "sources": sources,
                            }
                        )

            elif event_type == "on_tool_start":
                tool_name = event.get("name", "unknown")
                tool_input = event_data.get("input", {})
                tool_call_id = str(uuid4())[:8]

                # Close any open text/reasoning before tool
                out = ""
                if self._reasoning_started:
                    out += self._end_reasoning()
                if self._text_started:
                    out += self._sse({"type": "text-end", "id": self._text_id})
                    self._text_started = False

                out += self._ensure_start()

                # AI SDK v3: tool-input-start (tool call begins)
                out += self._sse(
                    {
                        "type": "tool-input-start",
                        "toolCallId": tool_call_id,
                        "toolName": tool_name,
                    }
                )

                # AI SDK v3: tool-input-available (input is known - emit immediately)
                out += self._sse(
                    {
                        "type": "tool-input-available",
                        "toolCallId": tool_call_id,
                        "toolName": tool_name,
                        "input": tool_input if isinstance(tool_input, dict) else {},
                    }
                )

                yield out

                # Store tool_call_id for pairing with on_tool_end
                self._current_tool_call_id = tool_call_id
                self._current_tool_name = tool_name
                self._current_tool_input = tool_input

                if self.ledger and self.run_id:
                    await self.ledger.log_tool_call_start(
                        run_id=self.run_id,
                        tool_name=tool_name,
                        tool_version=None,
                        arguments=tool_input,
                    )

            elif event_type == "on_tool_end":
                tool_name = event.get("name", "unknown")
                tool_output = event_data.get("output", {})
                tool_call_id = getattr(self, "_current_tool_call_id", str(uuid4())[:8])

                # AI SDK v3: tool-output-available (execution complete)
                yield self._sse(
                    {
                        "type": "tool-output-available",
                        "toolCallId": tool_call_id,
                        "output": tool_output
                        if isinstance(tool_output, (dict, str))
                        else str(tool_output),
                    }
                )

                if self.ledger and self.run_id:
                    await self.ledger.log_tool_call_complete(
                        run_id=self.run_id,
                        tool_name=tool_name,
                        result=tool_output
                        if isinstance(tool_output, dict)
                        else {"output": str(tool_output)},
                        duration_ms=0,
                    )

        # Note: Finish event is NOT emitted here
        # The caller (agent.py) is responsible for emitting finish after adding final metadata

    async def _process_event(self, event: dict[str, Any]) -> AsyncIterator[str]:
        """Process a single LangGraph update event.

        Args:
            event: A LangGraph node update dict like {"generate": {...}}

        Yields:
            AI SDK formatted chunks
        """
        for _node_name, node_output in event.items():
            if not isinstance(node_output, dict):
                continue

            messages = node_output.get("messages", [])
            for msg in messages:
                if hasattr(msg, "content"):
                    content = msg.content
                    if content:
                        self._accumulated_text += content
                        yield self._format_text_chunk(content)

            sources = node_output.get("sources", [])
            if sources:
                yield self._format_data_chunk(
                    {
                        "type": "sources",
                        "sources": sources,
                    }
                )

            error = node_output.get("error")
            if error:
                yield self._format_data_chunk(
                    {
                        "type": "error",
                        "message": error,
                    }
                )


__all__ = ["LangGraphToAISDKAdapter", "AISDKTextChunk", "AISDKDataChunk"]
