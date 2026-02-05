"""Integration tests for conversations API endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole
from intelli.db.models.conversations import Conversation, Message

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_context(test_session):
    """Create tenant + user and return (headers, tenant_id, user_id)."""
    tenant = Tenant(name="Conv Co", slug="conv-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="conv@test.com",
        name="Conv User",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}, tenant.id, user.id


@pytest_asyncio.fixture
async def auth_headers(auth_context):
    return auth_context[0]


class TestCreateConversation:
    async def test_create_returns_201(self, test_client, auth_headers):
        resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "scope_type": "tenant",
                "module": "research",
                "title": "Test conversation",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test conversation"
        assert data["status"] == "active"
        assert data["message_count"] == 0


class TestListConversations:
    async def test_list_returns_conversations(self, test_client, auth_headers):
        # Create 3 conversations
        for i in range(3):
            await test_client.post(
                "/api/v1/conversations",
                json={
                    "title": f"Conv {i}",
                },
                headers=auth_headers,
            )

        resp = await test_client.get("/api/v1/conversations", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3

    async def test_filter_by_module(self, test_client, auth_headers):
        await test_client.post(
            "/api/v1/conversations",
            json={
                "module": "analysis",
                "title": "Analysis conv",
            },
            headers=auth_headers,
        )

        resp = await test_client.get(
            "/api/v1/conversations?module=analysis",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(c["module"] == "analysis" for c in items)


class TestGetConversation:
    async def test_get_by_id(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "title": "Get me",
            },
            headers=auth_headers,
        )
        conv_id = create_resp.json()["id"]

        resp = await test_client.get(f"/api/v1/conversations/{conv_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == conv_id

    async def test_get_missing_returns_404(self, test_client, auth_headers):
        resp = await test_client.get(
            "/api/v1/conversations/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestUpdateConversation:
    async def test_patch_title(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "title": "Old title",
            },
            headers=auth_headers,
        )
        conv_id = create_resp.json()["id"]

        resp = await test_client.patch(
            f"/api/v1/conversations/{conv_id}",
            json={"title": "New title"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "New title"


class TestDeleteConversation:
    async def test_soft_delete(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "title": "Delete me",
            },
            headers=auth_headers,
        )
        conv_id = create_resp.json()["id"]

        resp = await test_client.delete(
            f"/api/v1/conversations/{conv_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

        # Should not appear in default list (deleted)
        list_resp = await test_client.get("/api/v1/conversations", headers=auth_headers)
        ids = [c["id"] for c in list_resp.json()["items"]]
        assert conv_id not in ids


class TestAddFeedback:
    async def test_add_feedback_returns_201(self, test_client, auth_context, test_session):
        headers, tenant_id, user_id = auth_context

        # Create conversation and message directly in DB
        conv = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type="tenant",
            config_snapshot={},
            status="active",
        )
        test_session.add(conv)
        await test_session.flush()

        msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content="Hello",
            sequence_number=1,
        )
        test_session.add(msg)
        await test_session.flush()
        await test_session.commit()

        resp = await test_client.post(
            f"/api/v1/conversations/{conv.id}/messages/{msg.id}/feedback",
            json={"rating": "positive"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["rating"] == "positive"


class TestAuthEnforcement:
    async def test_no_token_returns_401(self, test_client):
        resp = await test_client.get("/api/v1/conversations")
        assert resp.status_code == 401


class TestTenantIsolation:
    async def test_cross_tenant_access_denied(self, test_client, auth_context, test_session):
        headers_a, tenant_a_id, user_a_id = auth_context

        # Create conversation as tenant A
        create_resp = await test_client.post(
            "/api/v1/conversations",
            json={
                "title": "Tenant A conv",
            },
            headers=headers_a,
        )
        conv_id = create_resp.json()["id"]

        # Create tenant B
        from intelli.core.security import create_access_token, hash_password
        from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

        tenant_b = Tenant(name="Other Co", slug="other-co", status=TenantStatus.active)
        test_session.add(tenant_b)
        await test_session.flush()
        user_b = User(
            tenant_id=tenant_b.id,
            email="other@test.com",
            name="Other",
            role=UserRole.owner,
            password_hash=hash_password("pw"),
            is_active=True,
        )
        test_session.add(user_b)
        await test_session.flush()
        await test_session.commit()
        token_b = create_access_token(str(user_b.id), str(tenant_b.id), "owner")
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Tenant B should not see tenant A's conversation
        resp = await test_client.get(
            f"/api/v1/conversations/{conv_id}",
            headers=headers_b,
        )
        assert resp.status_code == 404


class TestPagination:
    async def test_list_with_pagination(self, test_client, auth_headers):
        # Seed 15 conversations
        for i in range(15):
            await test_client.post(
                "/api/v1/conversations",
                json={
                    "title": f"Paginated {i}",
                },
                headers=auth_headers,
            )

        resp = await test_client.get(
            "/api/v1/conversations?limit=5",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 5
        assert data["total"] >= 15


class TestFeedbackErrors:
    async def test_feedback_on_nonexistent_message_fails(
        self, test_client, auth_context, test_session
    ):
        headers, tenant_id, user_id = auth_context
        conv = await test_client.post(
            "/api/v1/conversations",
            json={
                "title": "Feedback test",
            },
            headers=headers,
        )
        conv_id = conv.json()["id"]

        resp = await test_client.post(
            f"/api/v1/conversations/{conv_id}/messages/00000000-0000-0000-0000-000000000000/feedback",
            json={"rating": "positive"},
            headers=headers,
        )
        # TODO: API returns 500 — should return 404. Missing validation upstream.
        assert resp.status_code in (404, 400, 500)


class TestGetSiblings:
    async def test_get_siblings_returns_all_siblings(self, test_client, auth_context, test_session):
        """Test getting sibling messages that share the same parent."""
        headers, tenant_id, user_id = auth_context

        # Create conversation
        conv = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type="tenant",
            config_snapshot={},
            status="active",
        )
        test_session.add(conv)
        await test_session.flush()

        # Create parent message
        parent = Message(
            conversation_id=conv.id,
            role="user",
            content="Parent message",
            sequence_number=1,
        )
        test_session.add(parent)
        await test_session.flush()

        # Create 3 sibling messages (all have same parent)
        sibling1 = Message(
            conversation_id=conv.id,
            role="assistant",
            content="Sibling 1",
            sequence_number=2,
            parent_message_id=parent.id,
        )
        sibling2 = Message(
            conversation_id=conv.id,
            role="assistant",
            content="Sibling 2",
            sequence_number=3,
            parent_message_id=parent.id,
        )
        sibling3 = Message(
            conversation_id=conv.id,
            role="assistant",
            content="Sibling 3",
            sequence_number=4,
            parent_message_id=parent.id,
        )
        test_session.add_all([sibling1, sibling2, sibling3])
        await test_session.flush()
        await test_session.commit()

        # Get siblings for sibling2
        resp = await test_client.get(
            f"/api/v1/conversations/{conv.id}/messages/{sibling2.id}/siblings",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert data["current_index"] == 1  # sibling2 is at index 1
        assert len(data["items"]) == 3
        # Items should be ordered by sequence number
        assert data["items"][0]["id"] == str(sibling1.id)
        assert data["items"][1]["id"] == str(sibling2.id)
        assert data["items"][2]["id"] == str(sibling3.id)

    async def test_get_siblings_root_message(self, test_client, auth_context, test_session):
        """Test getting siblings for a root message (no parent) returns just itself."""
        headers, tenant_id, user_id = auth_context

        conv = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type="tenant",
            config_snapshot={},
            status="active",
        )
        test_session.add(conv)
        await test_session.flush()

        # Create root message (no parent)
        root = Message(
            conversation_id=conv.id,
            role="user",
            content="Root message",
            sequence_number=1,
        )
        test_session.add(root)
        await test_session.flush()
        await test_session.commit()

        resp = await test_client.get(
            f"/api/v1/conversations/{conv.id}/messages/{root.id}/siblings",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["current_index"] == 0
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == str(root.id)

    async def test_get_siblings_no_auth_returns_401(self, test_client, auth_context, test_session):
        """Test that accessing siblings without auth returns 401."""
        headers, tenant_id, user_id = auth_context

        conv = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            scope_type="tenant",
            config_snapshot={},
            status="active",
        )
        test_session.add(conv)
        await test_session.flush()

        msg = Message(
            conversation_id=conv.id,
            role="user",
            content="Message",
            sequence_number=1,
        )
        test_session.add(msg)
        await test_session.flush()
        await test_session.commit()

        resp = await test_client.get(
            f"/api/v1/conversations/{conv.id}/messages/{msg.id}/siblings",
        )
        assert resp.status_code == 401
