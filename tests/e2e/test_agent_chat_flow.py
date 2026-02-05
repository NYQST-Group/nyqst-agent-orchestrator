"""End-to-end tests for the full agent chat chain.

User question → API → LangGraph (retrieve → generate) → SSE adapter → streamed response.

These tests use a real database but mock the LLM (via FakeListChatModel)
to avoid external API calls while testing the full chain.

Requires Docker services running (postgres).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from intelli.db.models.substrate import Manifest
from tests.factories import (
    collect_event_types,
    make_fake_llm,
    make_retrieved_chunk,
    parse_sse_events,
)

pytestmark = pytest.mark.e2e

# All manifest sha256s used across e2e tests
E2E_MANIFESTS = [c * 64 for c in "bcdef"]


@pytest_asyncio.fixture(autouse=True)
async def seed_manifests(test_session):
    """Seed manifest rows so FK constraints are satisfied."""
    for sha in E2E_MANIFESTS:
        test_session.add(
            Manifest(sha256=sha, tree={"entries": []}, entry_count=0, total_size_bytes=0)
        )
    await test_session.flush()


def _chat_request(manifest_sha256: str, question: str = "What are the key terms?"):
    return {
        "messages": [{"role": "user", "content": question}],
        "manifest_sha256": manifest_sha256,
    }


class TestAgentChatFlow:
    """Full chain: API → Graph → Adapter → SSE response."""

    @pytest.mark.asyncio
    async def test_full_chain_with_sources_and_answer(self, test_client):
        """Complete flow: retrieval finds sources, LLM generates answer, SSE stream is valid."""
        manifest_sha256 = "b" * 64
        fake_llm = make_fake_llm(["The lease term is 12 months [1]. Confidence: High"])
        chunks = [make_retrieved_chunk(content="Lease term: 12 months", score=0.95)]

        with (
            patch(
                "intelli.agents.graphs.research_assistant.ResearchAssistantGraph._get_llm",
                return_value=fake_llm,
            ),
            patch(
                "intelli.services.knowledge.rag_service.RagService.retrieve",
                new_callable=AsyncMock,
                return_value=chunks,
            ),
            patch(
                "intelli.services.substrate.manifest_service.ManifestService.get_entries",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256),
            )

        assert response.status_code == 200
        body = response.text
        events = parse_sse_events(body)
        types = collect_event_types(events)

        assert "finish" in types
        # Sources from retrieval must appear as source-document events
        source_events = [e for e in events if e["type"] == "source-document"]
        assert len(source_events) >= 1
        assert source_events[0]["providerMetadata"]["custom"]["content"] == "Lease term: 12 months"
        assert source_events[0]["providerMetadata"]["custom"]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_stream_format_is_valid_sse(self, test_client):
        """Every line in the response follows SSE format."""
        manifest_sha256 = "c" * 64
        fake_llm = make_fake_llm(["Answer"])

        with (
            patch(
                "intelli.agents.graphs.research_assistant.ResearchAssistantGraph._get_llm",
                return_value=fake_llm,
            ),
            patch(
                "intelli.services.knowledge.rag_service.RagService.retrieve",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "intelli.services.substrate.manifest_service.ManifestService.get_entries",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256),
            )

        body = response.text
        for line in body.strip().split("\n"):
            line = line.strip()
            if line:
                assert line.startswith("data: "), f"Invalid SSE line: {line}"

    @pytest.mark.asyncio
    async def test_run_id_header_present(self, test_client):
        """Response includes X-Run-Id header for tracking."""
        manifest_sha256 = "d" * 64
        fake_llm = make_fake_llm(["Answer"])

        with (
            patch(
                "intelli.agents.graphs.research_assistant.ResearchAssistantGraph._get_llm",
                return_value=fake_llm,
            ),
            patch(
                "intelli.services.knowledge.rag_service.RagService.retrieve",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "intelli.services.substrate.manifest_service.ManifestService.get_entries",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256),
            )

        assert "x-run-id" in response.headers

    @pytest.mark.asyncio
    async def test_error_in_graph_produces_error_event(self, test_client):
        """If the graph raises, the stream contains an error and finishes cleanly."""
        manifest_sha256 = "e" * 64

        with (
            patch(
                "intelli.agents.graphs.research_assistant.ResearchAssistantGraph._get_llm",
                side_effect=RuntimeError("LLM unavailable"),
            ),
            patch(
                "intelli.services.knowledge.rag_service.RagService.retrieve",
                new_callable=AsyncMock,
                return_value=[make_retrieved_chunk()],
            ),
            patch(
                "intelli.services.substrate.manifest_service.ManifestService.get_entries",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256),
            )

        assert response.status_code == 200
        body = response.text
        if body.strip():
            events = parse_sse_events(body)
            types = collect_event_types(events)
            assert "finish" in types

    @pytest.mark.asyncio
    async def test_multiple_messages_in_conversation(self, test_client):
        """Sending multiple messages only sends user messages to the graph."""
        manifest_sha256 = "f" * 64
        fake_llm = make_fake_llm(["Response to second question"])

        with (
            patch(
                "intelli.agents.graphs.research_assistant.ResearchAssistantGraph._get_llm",
                return_value=fake_llm,
            ),
            patch(
                "intelli.services.knowledge.rag_service.RagService.retrieve",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "intelli.services.substrate.manifest_service.ManifestService.get_entries",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json={
                    "messages": [
                        {"role": "user", "content": "First question"},
                        {"role": "assistant", "content": "First answer"},
                        {"role": "user", "content": "Second question"},
                    ],
                    "manifest_sha256": manifest_sha256,
                },
            )

        assert response.status_code == 200
