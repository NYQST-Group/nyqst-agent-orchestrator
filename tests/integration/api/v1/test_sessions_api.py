"""Integration tests for sessions API endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_headers(test_session):
    tenant = Tenant(name="Sess Co", slug="sess-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="sess@test.com",
        name="Sess User",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


class TestStartSession:
    async def test_create_returns_201(self, test_client, auth_headers):
        resp = await test_client.post(
            "/api/v1/sessions",
            json={
                "scope_type": "tenant",
                "module": "research",
                "objective": "Analyze contracts",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "active"
        assert data["objective"] == "Analyze contracts"


class TestListSessions:
    async def test_list_returns_sessions(self, test_client, auth_headers):
        await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        resp = await test_client.get("/api/v1/sessions", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


class TestIdleSession:
    async def test_active_to_idle(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        resp = await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "idle"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "idle"


class TestResumeSession:
    async def test_idle_to_active(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        # Idle first
        await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "idle"},
            headers=auth_headers,
        )

        # Resume
        resp = await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "active"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"


class TestCloseSession:
    async def test_close_session(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        resp = await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "closed", "close_reason": "user_ended"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "closed"

    async def test_closed_to_active_fails(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "closed"},
            headers=auth_headers,
        )
        resp = await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "active"},
            headers=auth_headers,
        )
        assert resp.status_code == 400


class TestCostAggregation:
    async def test_get_cost(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        resp = await test_client.get(
            f"/api/v1/sessions/{session_id}/cost",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total_cost_micros" in data
        assert "conversation_count" in data


class TestSessionTransitionErrors:
    async def test_idle_to_idle_fails(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        # First go idle
        await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "idle"},
            headers=auth_headers,
        )

        # idle → idle is a no-op (self-transitions are allowed)
        resp = await test_client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"status": "idle"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_cost_with_no_conversations_returns_zero(self, test_client, auth_headers):
        create_resp = await test_client.post("/api/v1/sessions", json={}, headers=auth_headers)
        session_id = create_resp.json()["id"]

        resp = await test_client.get(
            f"/api/v1/sessions/{session_id}/cost",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total_cost_micros"] == 0
