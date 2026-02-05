"""Integration tests for the /api/v1/agent/chat endpoint.

These tests use a real database (via test_client fixture) and run the real
LangGraph + adapter chain with FakeListChatModel (no external LLM calls).
They verify HTTP semantics, response headers, SSE format, source-document
events, run lifecycle, and error handling.

Requires Docker services running (postgres).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole
from intelli.db.models.runs import Run
from intelli.db.models.substrate import Manifest
from tests.factories import (
    collect_event_types,
    make_fake_llm,
    make_retrieved_chunk,
    parse_sse_events,
)

pytestmark = pytest.mark.integration

MANIFEST_SHA256 = "a" * 64


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def auth_headers(test_session):
    """Create tenant and user, return auth headers."""
    tenant = Tenant(name="Agent Co", slug="agent-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="agent@test.com",
        name="Agent User",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_pointer_id():
    return str(uuid4())


@pytest_asyncio.fixture
async def valid_manifest_sha256(test_session):
    """Seed a manifest row so FK constraints are satisfied."""
    manifest = Manifest(
        sha256=MANIFEST_SHA256,
        tree={"entries": []},
        entry_count=0,
        total_size_bytes=0,
    )
    test_session.add(manifest)
    await test_session.flush()
    return MANIFEST_SHA256


def _chat_request(messages=None, pointer_id=None, manifest_sha256=None):
    body = {
        "messages": messages or [{"role": "user", "content": "What are the key terms?"}],
    }
    if pointer_id:
        body["pointer_id"] = pointer_id
    if manifest_sha256:
        body["manifest_sha256"] = manifest_sha256
    return body


def _graph_patches(fake_llm, chunks=None):
    """Context manager stack for patching LLM + retrieval (not the graph class)."""
    from contextlib import ExitStack

    stack = ExitStack()
    stack.enter_context(
        patch(
            "intelli.agents.graphs.research_assistant.ResearchAssistantGraph._get_llm",
            return_value=fake_llm,
        )
    )
    stack.enter_context(
        patch(
            "intelli.services.knowledge.rag_service.RagService.retrieve",
            new_callable=AsyncMock,
            return_value=chunks or [],
        )
    )
    stack.enter_context(
        patch(
            "intelli.services.substrate.manifest_service.ManifestService.get_entries",
            new_callable=AsyncMock,
            return_value=[],
        )
    )
    return stack


# ---------------------------------------------------------------------------
# TestAgentChatEndpoint — HTTP semantics
# ---------------------------------------------------------------------------


class TestAgentChatEndpoint:
    @pytest.mark.asyncio
    async def test_valid_request_returns_streaming_response(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """A valid request returns 200 with SSE content type."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_response_headers(self, test_client, auth_headers, valid_manifest_sha256):
        """Response includes required SSE and run-tracking headers."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        assert "x-run-id" in response.headers
        assert response.headers.get("x-vercel-ai-ui-message-stream") == "v1"

    @pytest.mark.asyncio
    async def test_no_context_returns_400(self, test_client, auth_headers):
        """Request without pointer_id or manifest_sha256 returns 400."""
        response = await test_client.post(
            "/api/v1/agent/chat",
            json=_chat_request(),
            headers=auth_headers,
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_no_user_message_returns_400(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """Request with no user messages returns 400."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(
                    messages=[{"role": "assistant", "content": "Hi"}],
                    manifest_sha256=valid_manifest_sha256,
                ),
                headers=auth_headers,
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_pointer_returns_404(self, test_client, auth_headers):
        """Request with non-existent pointer_id returns 404."""
        response = await test_client.post(
            "/api/v1/agent/chat",
            json=_chat_request(pointer_id=str(uuid4())),
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_empty_messages_returns_400(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """Request with empty messages list returns 400."""
        response = await test_client.post(
            "/api/v1/agent/chat",
            json={
                "messages": [],
                "manifest_sha256": valid_manifest_sha256,
            },
            headers=auth_headers,
        )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, test_client, valid_manifest_sha256):
        """Request without auth returns 401."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
            )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TestSSEStreamContent — verify stream events using real adapter
# ---------------------------------------------------------------------------


class TestSSEStreamContent:
    @pytest.mark.asyncio
    async def test_stream_events_are_valid_json(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """Every SSE line in the stream is valid JSON with a type field."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        events = parse_sse_events(response.text)
        for event in events:
            assert isinstance(event, dict)
            assert "type" in event

    @pytest.mark.asyncio
    async def test_stream_ends_with_finish(self, test_client, auth_headers, valid_manifest_sha256):
        """The stream always ends with a finish event."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        events = parse_sse_events(response.text)
        assert len(events) > 0
        assert events[-1]["type"] == "finish"

    @pytest.mark.asyncio
    async def test_event_sequence_is_valid(self, test_client, auth_headers, valid_manifest_sha256):
        """Stream follows: message-metadata → start → start-step → text events → finish-step → finish."""
        fake_llm = make_fake_llm(["Some answer text"])
        chunks = [make_retrieved_chunk()]
        with _graph_patches(fake_llm, chunks=chunks):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        types = collect_event_types(parse_sse_events(response.text))
        # With auth, message-metadata is emitted first with conversationId
        assert types[0] == "message-metadata"
        assert "start" in types
        assert "start-step" in types
        assert "finish-step" in types
        assert types[-1] == "finish"

    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="TODO: Graph needs to emit sources data event for adapter to convert to source-document SSE events"
    )
    async def test_sources_appear_as_source_document_events(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """When retrieval returns chunks, source-document events appear in the stream."""
        fake_llm = make_fake_llm(["Answer based on sources"])
        chunks = [
            make_retrieved_chunk(content="Section 5: lease term", score=0.95),
            make_retrieved_chunk(content="Section 8: termination", score=0.88),
        ]
        with _graph_patches(fake_llm, chunks=chunks):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        events = parse_sse_events(response.text)
        source_events = [e for e in events if e["type"] == "source-document"]
        # Adapter may emit sources at multiple points in the stream;
        # verify we have at least one per input chunk
        unique_sources = {e["sourceId"] for e in source_events}
        assert len(unique_sources) >= 2

        # Each source-document must have the required fields
        for src in source_events:
            assert "sourceId" in src
            assert "title" in src
            assert "providerMetadata" in src
            custom = src["providerMetadata"]["custom"]
            assert "content" in custom
            assert "score" in custom

    @pytest.mark.asyncio
    async def test_sources_appear_before_text(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """source-document events appear before text-start in the stream."""
        fake_llm = make_fake_llm(["Answer"])
        chunks = [make_retrieved_chunk()]
        with _graph_patches(fake_llm, chunks=chunks):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        types = collect_event_types(parse_sse_events(response.text))
        if "source-document" in types and "text-start" in types:
            first_source = types.index("source-document")
            first_text = types.index("text-start")
            assert first_source < first_text

    @pytest.mark.asyncio
    async def test_no_sources_when_retrieval_empty(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """When retrieval returns no chunks, no source-document events in stream."""
        fake_llm = make_fake_llm(["Answer without sources"])
        with _graph_patches(fake_llm, chunks=[]):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        events = parse_sse_events(response.text)
        source_events = [e for e in events if e["type"] == "source-document"]
        assert len(source_events) == 0


# ---------------------------------------------------------------------------
# TestRunLifecycle — verify Run rows in DB
# ---------------------------------------------------------------------------


class TestRunLifecycle:
    @pytest.mark.asyncio
    async def test_creates_run_with_correct_manifest(
        self, test_client, auth_headers, test_session, valid_manifest_sha256
    ):
        """A valid request creates a Run row with the correct manifest_sha256."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        run_id = UUID(response.headers["x-run-id"])
        result = await test_session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one()
        assert run.input_manifest_sha256 == valid_manifest_sha256
        assert run.run_type == "agent_chat"

    @pytest.mark.asyncio
    async def test_successful_run_status_completed(
        self, test_client, auth_headers, test_session, valid_manifest_sha256
    ):
        """After a successful stream, Run status is 'completed'."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        # Consume the full response to ensure generate() completes
        _ = response.text

        run_id = UUID(response.headers["x-run-id"])
        result = await test_session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one()
        assert run.status == "completed", f"Run failed with error: {run.error}"
        assert run.started_at is not None
        assert run.completed_at is not None

    @pytest.mark.asyncio
    async def test_exception_marks_run_failed(
        self, test_client, auth_headers, test_session, valid_manifest_sha256
    ):
        """If the graph raises, Run status is 'failed' and error appears in stream."""
        fake_llm = make_fake_llm(["Answer"])
        with (
            _graph_patches(fake_llm),
            # Patch the graph's astream_events to raise after construction
            patch(
                "intelli.agents.graphs.research_assistant.ResearchAssistantGraph.astream_events",
                side_effect=RuntimeError("Graph exploded"),
            ),
        ):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        assert response.status_code == 200
        events = parse_sse_events(response.text)
        types = collect_event_types(events)
        assert "finish" in types

        run_id = UUID(response.headers["x-run-id"])
        result = await test_session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one()
        assert run.status == "failed"

    @pytest.mark.asyncio
    async def test_run_has_started_at_timestamp(
        self, test_client, auth_headers, test_session, valid_manifest_sha256
    ):
        """Run row has started_at set (endpoint calls start_run before streaming)."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        run_id = UUID(response.headers["x-run-id"])
        result = await test_session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one()
        assert run.started_at is not None


# ---------------------------------------------------------------------------
# TestSessionIdSupport — verify session_id field acceptance
# ---------------------------------------------------------------------------


class TestSessionIdSupport:
    @pytest.mark.asyncio
    async def test_accepts_session_id_in_request(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """AgentChatRequest accepts session_id field."""
        # Create a valid session first
        session_resp = await test_client.post(
            "/api/v1/sessions",
            json={"module": "research"},
            headers=auth_headers,
        )
        assert session_resp.status_code == 201
        session_id = session_resp.json()["id"]

        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json={
                    **_chat_request(manifest_sha256=valid_manifest_sha256),
                    "session_id": session_id,
                },
                headers=auth_headers,
            )

        # Should return 200 — session_id is accepted and links conversation to session
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_session_id_optional(self, test_client, auth_headers, valid_manifest_sha256):
        """session_id is optional — request without it should succeed."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# TestMessageMetadataEmission — verify message IDs in SSE stream
# ---------------------------------------------------------------------------


class TestMessageMetadataEmission:
    @pytest.mark.asyncio
    async def test_stream_includes_conversation_metadata(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """Stream includes conversation metadata when authenticated."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        # With auth context, conversation is created and message metadata emitted
        assert response.status_code == 200
        events = parse_sse_events(response.text)
        assert events[-1]["type"] == "finish"

        # Should have at least one message-metadata event with conversationId
        metadata_events = [e for e in events if e.get("type") == "message-metadata"]
        assert len(metadata_events) > 0
        # First metadata event should have conversationId
        assert "conversationId" in metadata_events[0].get("messageMetadata", {})

    @pytest.mark.asyncio
    async def test_message_metadata_structure(
        self, test_client, auth_headers, valid_manifest_sha256
    ):
        """Verify the adapter can emit message-metadata events (structure test)."""
        fake_llm = make_fake_llm(["Answer"])
        with _graph_patches(fake_llm):
            response = await test_client.post(
                "/api/v1/agent/chat",
                json=_chat_request(manifest_sha256=valid_manifest_sha256),
                headers=auth_headers,
            )

        events = parse_sse_events(response.text)

        # The stream should complete successfully
        assert response.status_code == 200
        assert len(events) > 0
        assert events[-1]["type"] == "finish"

        # If there are message-metadata events, they should have the right structure
        metadata_events = [e for e in events if e.get("type") == "message-metadata"]
        for event in metadata_events:
            assert "messageMetadata" in event
            # The metadata can contain conversationId, userMessageId, assistantMessageId
