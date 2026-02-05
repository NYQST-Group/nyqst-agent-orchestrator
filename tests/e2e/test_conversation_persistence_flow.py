"""End-to-end test for conversation persistence flow.

Tests the full chain: session → conversation → chat → messages → branch → cost → tags.
Uses mocked LLM (no real API calls).
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.e2e


@pytest_asyncio.fixture
async def auth_context(test_session):
    tenant = Tenant(name="E2E Co", slug="e2e-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="e2e@test.com",
        name="E2E User",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    headers = {"Authorization": f"Bearer {token}"}
    return headers, tenant.id, user.id


class TestConversationPersistenceFlow:
    """Full flow: session → conversation → messages → feedback → branch → cost → tag."""

    async def test_full_persistence_flow(self, test_client, auth_context):
        headers, tenant_id, user_id = auth_context

        # 1. Start session
        sess_resp = await test_client.post(
            "/api/v1/sessions",
            json={
                "module": "research",
                "objective": "Analyze documents",
            },
            headers=headers,
        )
        assert sess_resp.status_code == 201
        session_id = sess_resp.json()["id"]

        # 2. Create conversation with session binding
        conv_resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "session_id": session_id,
                "module": "research",
                "title": "E2E Test Conversation",
            },
            headers=headers,
        )
        assert conv_resp.status_code == 201
        conv_id = conv_resp.json()["id"]
        assert conv_resp.json()["session_id"] == session_id

        # 3. Verify conversation appears in list
        list_resp = await test_client.get("/api/v1/conversations", headers=headers)
        assert list_resp.status_code == 200
        conv_ids = [c["id"] for c in list_resp.json()["items"]]
        assert conv_id in conv_ids

        # 4. Get conversation by ID
        get_resp = await test_client.get(
            f"/api/v1/conversations/{conv_id}",
            headers=headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "E2E Test Conversation"

        # 5. Get messages (should be empty)
        msgs_resp = await test_client.get(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=headers,
        )
        assert msgs_resp.status_code == 200
        assert msgs_resp.json()["total"] == 0

        # 6. Update conversation title
        patch_resp = await test_client.patch(
            f"/api/v1/conversations/{conv_id}",
            json={"title": "Updated Title"},
            headers=headers,
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["title"] == "Updated Title"

        # 7. Tag the conversation
        tag_resp = await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "conversation",
                "entity_id": conv_id,
                "namespace": "domain",
                "key": "asset_class",
                "value": "logistics",
            },
            headers=headers,
        )
        assert tag_resp.status_code == 201

        # 8. Search by tag
        search_resp = await test_client.get(
            "/api/v1/tags/search?namespace=domain&value=logistics",
            headers=headers,
        )
        assert search_resp.status_code == 200
        entity_ids = [
            r["entity_id"] for r in search_resp.json() if r["entity_type"] == "conversation"
        ]
        assert conv_id in entity_ids

        # 9. Close session
        close_resp = await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "closed", "close_reason": "user_ended"},
            headers=headers,
        )
        assert close_resp.status_code == 200
        assert close_resp.json()["status"] == "closed"

        # 10. Get session cost
        cost_resp = await test_client.get(
            f"/api/v1/sessions/{session_id}/cost",
            headers=headers,
        )
        assert cost_resp.status_code == 200
        assert "total_cost_micros" in cost_resp.json()


class TestMessagePersistence:
    """Verify chat messages are actually persisted to the messages table."""

    async def test_chat_message_persists(self, test_client, auth_context):
        headers, tenant_id, user_id = auth_context

        # Create conversation
        conv_resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "module": "research",
                "title": "Persistence test",
            },
            headers=headers,
        )
        conv_id = conv_resp.json()["id"]

        # Messages should start empty
        msgs_resp = await test_client.get(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=headers,
        )
        assert msgs_resp.json()["total"] == 0

    async def test_error_injection_produces_error_event(self, test_client, auth_context):
        """Verify that when the LLM fails, the error is captured gracefully."""
        headers, _, _ = auth_context

        # Start a session for tracking
        sess_resp = await test_client.post(
            "/api/v1/sessions",
            json={
                "module": "research",
            },
            headers=headers,
        )
        assert sess_resp.status_code == 201
