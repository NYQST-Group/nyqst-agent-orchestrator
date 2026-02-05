"""Shared test factories and helpers for the Intelli test suite.

Provides deterministic test data builders, fake LLM models, and
reusable fixtures that tests import directly.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import BaseMessage, HumanMessage

from intelli.services.knowledge.rag_service import RetrievedChunk

# ---------------------------------------------------------------------------
# Fake LLM helpers
# ---------------------------------------------------------------------------


class ToolBindableFakeListChatModel(FakeListChatModel):
    """FakeListChatModel that supports bind_tools (no-op, returns self)."""

    def bind_tools(self, tools, **kwargs):
        """No-op bind_tools implementation for testing."""
        return self


def make_fake_llm(responses: list[str] | None = None) -> ToolBindableFakeListChatModel:
    """Create a FakeListChatModel with deterministic responses.

    Args:
        responses: List of string responses the LLM will return in order.
                   Defaults to a single generic research answer.
    """
    if responses is None:
        responses = [
            "Based on the sources, the key findings are: [1] The contract "
            "specifies a 12-month term. [2] Liability is capped at $1M.\n\n"
            "Confidence: High"
        ]
    return ToolBindableFakeListChatModel(responses=responses)


# ---------------------------------------------------------------------------
# Data factories
# ---------------------------------------------------------------------------


def make_retrieved_chunk(
    *,
    chunk_id: UUID | None = None,
    artifact_sha256: str = "abc123def456abc123def456abc123def456abc123def456abc123def456abcd",
    chunk_index: int = 0,
    content: str = "This is test chunk content for retrieval testing.",
    score: float = 0.92,
    path_hint: str | None = "docs/contract.pdf",
) -> RetrievedChunk:
    """Build a RetrievedChunk with sensible defaults."""
    return RetrievedChunk(
        chunk_id=chunk_id or uuid4(),
        artifact_sha256=artifact_sha256,
        chunk_index=chunk_index,
        content=content,
        score=score,
        path_hint=path_hint,
    )


def make_source_dict(
    *,
    chunk_id: str | None = None,
    artifact_sha256: str = "abc123def456abc123def456abc123def456abc123def456abc123def456abcd",
    chunk_index: int = 0,
    content: str = "Test source content.",
    score: float = 0.85,
    path_hint: str | None = "reports/analysis.pdf",
) -> dict[str, Any]:
    """Build a source dict as returned by _chunks_to_dicts."""
    return {
        "chunk_id": chunk_id or str(uuid4()),
        "artifact_sha256": artifact_sha256,
        "chunk_index": chunk_index,
        "content": content,
        "score": score,
        "path_hint": path_hint,
    }


def make_chat_messages(
    user_content: str = "What are the key terms?",
) -> list[BaseMessage]:
    """Build a minimal conversation for graph testing."""
    return [HumanMessage(content=user_content)]


def make_run_id() -> UUID:
    """Return a fresh UUID for run testing."""
    return uuid4()


# ---------------------------------------------------------------------------
# Conversation / Session / Tag factories
# ---------------------------------------------------------------------------

_seq_counter = 0


def make_conversation(
    *,
    tenant_id: UUID | None = None,
    user_id: UUID | None = None,
    scope_type: str = "tenant",
    scope_id: UUID | None = None,
    module: str | None = "research",
    title: str | None = "Test conversation",
    status: str = "active",
    session_id: UUID | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build kwargs dict for creating a Conversation (use with repo.create)."""
    return {
        "tenant_id": tenant_id or uuid4(),
        "user_id": user_id or uuid4(),
        "scope_type": scope_type,
        "scope_id": scope_id,
        "module": module,
        "title": title,
        "status": status,
        "session_id": session_id,
        "config_snapshot": {},
        **kwargs,
    }


def make_message(
    *,
    conversation_id: UUID | None = None,
    role: str = "user",
    content: str = "Test message content",
    sequence_number: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build kwargs dict for creating a Message."""
    global _seq_counter
    if sequence_number is None:
        _seq_counter += 1
        sequence_number = _seq_counter
    return {
        "conversation_id": conversation_id or uuid4(),
        "role": role,
        "content": content,
        "sequence_number": sequence_number,
        **kwargs,
    }


def make_session(
    *,
    tenant_id: UUID | None = None,
    user_id: UUID | None = None,
    scope_type: str = "tenant",
    status: str = "active",
    idle_timeout_minutes: int = 30,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build kwargs dict for creating a Session."""
    from intelli.core.clock import utc_now

    now = utc_now()
    return {
        "tenant_id": tenant_id or uuid4(),
        "user_id": user_id or uuid4(),
        "scope_type": scope_type,
        "status": status,
        "idle_timeout_minutes": idle_timeout_minutes,
        "config_snapshot": {},
        "started_at": now,
        "last_active_at": now,
        "updated_at": now,
        **kwargs,
    }


def make_tag(
    *,
    tenant_id: UUID | None = None,
    entity_type: str = "conversation",
    entity_id: UUID | None = None,
    namespace: str = "domain",
    key: str = "asset_class",
    value: str = "logistics",
    source: str = "manual",
    confidence: float | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build kwargs dict for creating a Tag."""
    return {
        "tenant_id": tenant_id or uuid4(),
        "entity_type": entity_type,
        "entity_id": entity_id or uuid4(),
        "namespace": namespace,
        "key": key,
        "value": value,
        "source": source,
        "confidence": confidence,
        **kwargs,
    }


# ---------------------------------------------------------------------------
# SSE parsing helpers
# ---------------------------------------------------------------------------


def parse_sse_events(raw: str) -> list[dict[str, Any]]:
    """Parse a raw SSE string into a list of JSON event dicts.

    Each SSE event is expected to be: 'data: {json}\\n\\n'
    """
    import json

    events = []
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            payload = line[len("data: ") :]
            events.append(json.loads(payload))
    return events


def collect_event_types(events: list[dict[str, Any]]) -> list[str]:
    """Extract the 'type' field from a list of parsed SSE events."""
    return [e.get("type", "") for e in events]
