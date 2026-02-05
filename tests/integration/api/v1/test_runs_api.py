"""Integration tests for runs API endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_headers(test_session):
    tenant = Tenant(name="Run Co", slug="run-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="run@test.com",
        name="Runner",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


class TestRunCreate:
    async def test_create_run(self, test_client, auth_headers):
        resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Test Run",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["run_type"] == "agent_chat"
        assert data["status"] == "pending"


class TestRunGet:
    async def test_get_run(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Get Me",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]

        resp = await test_client.get(f"/api/v1/runs/{run_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == run_id

    async def test_get_missing_run(self, test_client, auth_headers):
        from uuid import uuid4

        resp = await test_client.get(f"/api/v1/runs/{uuid4()}", headers=auth_headers)
        assert resp.status_code == 404


class TestRunList:
    async def test_list_runs(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/runs", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data


class TestRunLifecycle:
    async def test_start_run(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Start Me",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]

        resp = await test_client.post(f"/api/v1/runs/{run_id}/start", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"

    async def test_cancel_run(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Cancel Me",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]

        resp = await test_client.post(f"/api/v1/runs/{run_id}/cancel", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"


class TestRunComplete:
    async def test_complete_run(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Complete Me",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]

        # Start first
        await test_client.post(f"/api/v1/runs/{run_id}/start", headers=auth_headers)
        # Then complete
        resp = await test_client.post(f"/api/v1/runs/{run_id}/complete", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"


class TestRunAuth:
    """Auth enforcement on run routes."""

    async def test_create_requires_auth(self, test_client):
        resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "No Auth",
            },
        )
        assert resp.status_code in (401, 403)

    async def test_list_requires_auth(self, test_client):
        resp = await test_client.get("/api/v1/runs")
        assert resp.status_code in (401, 403)


class TestRunStateInvariants:
    """Run state machine invariants."""

    async def test_complete_pending_run_rejected(self, test_client, auth_headers):
        """Cannot complete a run that hasn't been started."""
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Skip Start",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]

        resp = await test_client.post(f"/api/v1/runs/{run_id}/complete", headers=auth_headers)
        assert resp.status_code in (400, 409, 422)

    async def test_start_already_running_rejected(self, test_client, auth_headers):
        """Cannot start a run that is already running."""
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Double Start",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]
        await test_client.post(f"/api/v1/runs/{run_id}/start", headers=auth_headers)

        resp = await test_client.post(f"/api/v1/runs/{run_id}/start", headers=auth_headers)
        assert resp.status_code in (400, 409, 422)

    async def test_cancel_completed_run_rejected(self, test_client, auth_headers):
        """Cannot cancel a run that has already completed (terminal state)."""
        create_resp = await test_client.post(
            "/api/v1/runs",
            json={
                "run_type": "agent_chat",
                "name": "Cancel After Done",
            },
            headers=auth_headers,
        )
        run_id = create_resp.json()["id"]
        await test_client.post(f"/api/v1/runs/{run_id}/start", headers=auth_headers)
        await test_client.post(f"/api/v1/runs/{run_id}/complete", headers=auth_headers)

        resp = await test_client.post(f"/api/v1/runs/{run_id}/cancel", headers=auth_headers)
        assert resp.status_code in (400, 409, 422)
