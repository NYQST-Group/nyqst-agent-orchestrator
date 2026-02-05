"""Integration tests for authentication API endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio

from intelli.core.security import hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def seeded_tenant_and_user(test_session):
    """Create a tenant and user for auth tests."""
    tenant = Tenant(name="Test Co", slug="test-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()

    user = User(
        tenant_id=tenant.id,
        email="alice@test.com",
        name="Alice",
        role=UserRole.owner,
        password_hash=hash_password("correct-password"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()

    return tenant, user


class TestLogin:
    async def test_login_success(self, test_client, seeded_tenant_and_user):
        resp = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "alice@test.com",
                "password": "correct-password",
                "tenant_slug": "test-co",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, test_client, seeded_tenant_and_user):
        resp = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "alice@test.com",
                "password": "wrong",
                "tenant_slug": "test-co",
            },
        )
        assert resp.status_code == 401

    async def test_login_wrong_tenant(self, test_client, seeded_tenant_and_user):
        resp = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "alice@test.com",
                "password": "correct-password",
                "tenant_slug": "nonexistent",
            },
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, test_client, seeded_tenant_and_user):
        resp = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nobody@test.com",
                "password": "pw",
                "tenant_slug": "test-co",
            },
        )
        assert resp.status_code == 401

    async def test_login_invalid_email_format(self, test_client):
        resp = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "not-an-email",
                "password": "pw",
                "tenant_slug": "test-co",
            },
        )
        assert resp.status_code == 422


class TestDevBootstrap:
    async def test_dev_bootstrap_creates_tenant_and_user(self, test_client):
        resp = await test_client.post(
            "/api/v1/auth/dev-bootstrap",
            json={
                "tenant_slug": "bootstrap-test",
                "tenant_name": "Bootstrap",
                "email": "dev@example.com",
                "user_name": "Dev",
                "password": "dev123",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    async def test_dev_bootstrap_idempotent(self, test_client):
        payload = {
            "tenant_slug": "idempotent",
            "tenant_name": "Idempotent",
            "email": "repeat@example.com",
            "user_name": "Repeat",
            "password": "pw",
        }
        r1 = await test_client.post("/api/v1/auth/dev-bootstrap", json=payload)
        r2 = await test_client.post("/api/v1/auth/dev-bootstrap", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200


class TestCurrentUser:
    async def test_me_requires_auth(self, test_client):
        resp = await test_client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)

    async def test_me_with_token(self, test_client, seeded_tenant_and_user):
        # Login first
        login_resp = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "alice@test.com",
                "password": "correct-password",
                "tenant_slug": "test-co",
            },
        )
        token = login_resp.json()["access_token"]

        resp = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "owner"
