"""Integration tests for artifacts API endpoints."""

from __future__ import annotations

import hashlib
import io

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_headers(test_session):
    """Create a tenant+user and return auth headers."""
    tenant = Tenant(name="Art Co", slug="art-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="art@test.com",
        name="Art",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


class TestArtifactUpload:
    async def test_upload_artifact(self, test_client, auth_headers):
        content = b"test artifact content"
        resp = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["sha256"] == hashlib.sha256(content).hexdigest()
        assert data["size_bytes"] == len(content)
        assert data["is_duplicate"] is False

    async def test_upload_duplicate(self, test_client, auth_headers):
        content = b"duplicate content"
        await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("a.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        resp = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("b.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_duplicate"] is True


class TestArtifactGet:
    async def test_get_artifact(self, test_client, auth_headers):
        content = b"get me"
        sha = hashlib.sha256(content).hexdigest()
        await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("f.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        resp = await test_client.get(f"/api/v1/artifacts/{sha}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["sha256"] == sha

    async def test_get_missing_artifact(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/artifacts/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestArtifactList:
    async def test_list_empty(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/artifacts", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestArtifactDelete:
    async def test_delete_artifact(self, test_client, auth_headers):
        content = b"delete me"
        sha = hashlib.sha256(content).hexdigest()
        await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("d.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        resp = await test_client.delete(f"/api/v1/artifacts/{sha}", headers=auth_headers)
        assert resp.status_code == 200

    async def test_delete_missing(self, test_client, auth_headers):
        resp = await test_client.delete("/api/v1/artifacts/missing", headers=auth_headers)
        assert resp.status_code == 404


class TestArtifactContent:
    async def test_get_content(self, test_client, auth_headers):
        content = b"content download test"
        sha = hashlib.sha256(content).hexdigest()
        await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("c.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        resp = await test_client.get(f"/api/v1/artifacts/{sha}/content", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.content == content


class TestArtifactAuth:
    """Auth enforcement on artifact routes."""

    async def test_upload_requires_auth(self, test_client):
        resp = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("t.txt", io.BytesIO(b"x"), "text/plain")},
        )
        assert resp.status_code in (401, 403)

    async def test_list_requires_auth(self, test_client):
        resp = await test_client.get("/api/v1/artifacts")
        assert resp.status_code in (401, 403)

    async def test_delete_requires_auth(self, test_client):
        resp = await test_client.delete("/api/v1/artifacts/abc")
        assert resp.status_code in (401, 403)


class TestArtifactInvariants:
    """Tests for content-addressable storage invariants."""

    async def test_sha256_is_deterministic(self, test_client, auth_headers):
        """Same content always produces the same hash."""
        content = b"deterministic"
        sha = hashlib.sha256(content).hexdigest()
        r1 = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("a.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        r2 = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("b.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        assert r1.json()["sha256"] == r2.json()["sha256"] == sha

    async def test_different_content_different_sha(self, test_client, auth_headers):
        """Different content must produce different hashes."""
        r1 = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("a.txt", io.BytesIO(b"alpha"), "text/plain")},
            headers=auth_headers,
        )
        r2 = await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("b.txt", io.BytesIO(b"beta"), "text/plain")},
            headers=auth_headers,
        )
        assert r1.json()["sha256"] != r2.json()["sha256"]

    async def test_content_roundtrip_integrity(self, test_client, auth_headers):
        """Downloaded content must be byte-identical to uploaded content."""
        content = b"\x00\x01\x02\xff" * 1000  # binary content
        sha = hashlib.sha256(content).hexdigest()
        await test_client.post(
            "/api/v1/artifacts",
            files={"file": ("bin", io.BytesIO(content), "application/octet-stream")},
            headers=auth_headers,
        )
        resp = await test_client.get(f"/api/v1/artifacts/{sha}/content", headers=auth_headers)
        assert resp.content == content
