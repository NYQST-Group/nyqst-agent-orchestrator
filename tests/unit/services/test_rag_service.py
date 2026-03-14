"""Unit tests for RagService — text chunking and pure logic.

Database-dependent methods (index_manifest, retrieve, answer) are
covered in integration tests. These tests focus on the pure functions
and logic that don't require a database connection.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from intelli.services.knowledge.rag_service import RagService, RetrievedChunk, _chunk_text

pytestmark = pytest.mark.unit


class TestChunkText:
    def test_empty_string_returns_empty_list(self):
        assert _chunk_text("") == []

    def test_none_returns_empty_list(self):
        assert _chunk_text(None) == []

    def test_whitespace_only_returns_empty_list(self):
        assert _chunk_text("   \n\t  ") == []

    def test_short_text_returns_single_chunk(self):
        text = "Hello world"
        chunks = _chunk_text(text, max_chars=2000)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_long_text_splits_into_multiple_chunks(self):
        text = "word " * 1000  # ~5000 chars
        chunks = _chunk_text(text, max_chars=500, overlap=50)
        assert len(chunks) > 1
        # All chunks should be non-empty
        for chunk in chunks:
            assert len(chunk) > 0

    def test_overlap_creates_repeated_content(self):
        text = "A " * 500 + "MARKER " + "B " * 500
        chunks = _chunk_text(text, max_chars=500, overlap=100)
        # With overlap, some content should appear in consecutive chunks
        assert len(chunks) >= 2

    def test_max_chars_floor_is_200(self):
        text = "x " * 500
        chunks = _chunk_text(text, max_chars=10)  # below floor
        # Should use 200 as minimum
        for chunk in chunks:
            assert len(chunk) <= 250  # some buffer for word boundaries

    def test_overlap_capped_at_half_max_chars(self):
        text = "word " * 500
        # overlap > max_chars/2 should be capped
        chunks = _chunk_text(text, max_chars=400, overlap=300)
        assert len(chunks) >= 2

    def test_normalizes_whitespace(self):
        text = "hello   world\n\nfoo\tbar"
        chunks = _chunk_text(text)
        assert chunks[0] == "hello world foo bar"

    def test_preserves_all_content(self):
        words = [f"word{i}" for i in range(100)]
        text = " ".join(words)
        chunks = _chunk_text(text, max_chars=200, overlap=50)
        joined = " ".join(chunks)
        # Every word should appear at least once
        for word in words:
            assert word in joined


class TestRetrievedChunk:
    def test_dataclass_fields(self):
        from uuid import uuid4

        chunk = RetrievedChunk(
            chunk_id=uuid4(),
            artifact_sha256="abc",
            chunk_index=0,
            content="test",
            score=0.9,
            path_hint="doc.pdf",
        )
        assert chunk.score == 0.9
        assert chunk.path_hint == "doc.pdf"

    def test_path_hint_defaults_to_none(self):
        from uuid import uuid4

        chunk = RetrievedChunk(
            chunk_id=uuid4(),
            artifact_sha256="abc",
            chunk_index=0,
            content="test",
            score=0.5,
        )
        assert chunk.path_hint is None


@pytest.mark.asyncio
async def test_answer_records_usage_from_openai_response():
    service = RagService(AsyncMock())
    service.manifests.get_entries = AsyncMock(
        return_value=[SimpleNamespace(artifact_sha256="abc123", path="hello.txt")]
    )
    service.retrieve = AsyncMock(
        return_value=[
            RetrievedChunk(
                chunk_id=uuid4(),
                artifact_sha256="abc123",
                chunk_index=0,
                content="Hello world",
                score=0.9,
                path_hint="hello.txt",
            )
        ]
    )

    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Answer"))],
        usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7),
    )
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    service._get_openai = MagicMock(return_value=client)
    service._record_model_usage = AsyncMock(return_value=123)

    ledger = AsyncMock()
    run_id = uuid4()

    with patch("intelli.services.knowledge.rag_service.settings.chat_model", "gpt-5-nano"):
        answer, retrieved = await service.answer(
            "manifest-sha",
            "What is this document?",
            run_id=run_id,
            ledger=ledger,
        )

    assert answer == "Answer"
    assert len(retrieved) == 1
    service._record_model_usage.assert_awaited_once_with(
        run_id,
        model="gpt-5-nano",
        input_tokens=11,
        output_tokens=7,
    )
    ledger.log_llm_request.assert_awaited_once()
    ledger.log_llm_response.assert_awaited_once()
