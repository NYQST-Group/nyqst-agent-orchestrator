"""Integration tests for pointers API endpoints."""

from __future__ import annotations

import io

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_headers(test_session):
    tenant = Tenant(name="Ptr Co", slug="ptr-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="ptr@test.com",
        name="Ptr",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


async def _create_manifest(test_client, auth_headers) -> str:
    """Upload artifact + create manifest, return manifest sha."""
    content = b"pointer artifact content"
    art_resp = await test_client.post(
        "/api/v1/artifacts",
        files={"file": ("f.txt", io.BytesIO(content), "text/plain")},
        headers=auth_headers,
    )
    art_sha = art_resp.json()["sha256"]
    man_resp = await test_client.post(
        "/api/v1/manifests",
        json={
            "entries": [{"path": "doc.txt", "artifact_sha256": art_sha}],
        },
        headers=auth_headers,
    )
    return man_resp.json()["sha256"]


class TestPointerCreate:
    async def test_create_pointer(self, test_client, auth_headers):
        man_sha = await _create_manifest(test_client, auth_headers)
        resp = await test_client.post(
            "/api/v1/pointers",
            json={
                "namespace": "notebooks",
                "name": "test-doc",
                "pointer_type": "bundle",
                "manifest_sha256": man_sha,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["namespace"] == "notebooks"
        assert data["name"] == "test-doc"


class TestPointerGet:
    async def test_get_pointer(self, test_client, auth_headers):
        man_sha = await _create_manifest(test_client, auth_headers)
        await test_client.post(
            "/api/v1/pointers",
            json={
                "namespace": "ns",
                "name": "get-me",
                "pointer_type": "bundle",
                "manifest_sha256": man_sha,
            },
            headers=auth_headers,
        )

        resp = await test_client.get("/api/v1/pointers/ns/get-me", headers=auth_headers)
        assert resp.status_code == 200

    async def test_get_missing_pointer(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/pointers/ns/missing", headers=auth_headers)
        assert resp.status_code == 404


class TestPointerList:
    async def test_list_pointers(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/pointers", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_filter_by_namespace(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/pointers?namespace=notebooks", headers=auth_headers)
        assert resp.status_code == 200


class TestPointerDelete:
    async def test_delete_pointer(self, test_client, auth_headers):
        man_sha = await _create_manifest(test_client, auth_headers)
        create_resp = await test_client.post(
            "/api/v1/pointers",
            json={
                "namespace": "ns",
                "name": "del-me",
                "pointer_type": "bundle",
                "manifest_sha256": man_sha,
            },
            headers=auth_headers,
        )
        pid = create_resp.json()["id"]

        resp = await test_client.delete(f"/api/v1/pointers/{pid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True


class TestPointerResolve:
    async def test_resolve_pointer(self, test_client, auth_headers):
        man_sha = await _create_manifest(test_client, auth_headers)
        await test_client.post(
            "/api/v1/pointers",
            json={
                "namespace": "ns",
                "name": "resolve-me",
                "pointer_type": "bundle",
                "manifest_sha256": man_sha,
            },
            headers=auth_headers,
        )

        resp = await test_client.get("/api/v1/pointers/ns/resolve-me/resolve", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["manifest_sha256"] == man_sha

    async def test_resolve_missing(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/pointers/ns/no-exist/resolve", headers=auth_headers)
        assert resp.status_code == 404


class TestPointerAuth:
    """Auth enforcement on pointer routes."""

    async def test_create_requires_auth(self, test_client):
        resp = await test_client.post(
            "/api/v1/pointers",
            json={
                "namespace": "ns",
                "name": "noauth",
                "pointer_type": "bundle",
                "manifest_sha256": "a" * 64,
            },
        )
        assert resp.status_code in (401, 403)

    async def test_list_requires_auth(self, test_client):
        resp = await test_client.get("/api/v1/pointers")
        assert resp.status_code in (401, 403)


class TestPointerInvariants:
    """Pointer naming and uniqueness invariants."""

    async def test_duplicate_name_in_namespace_rejected(self, test_client, auth_headers):
        """Creating two pointers with same namespace+name should conflict."""
        man_sha = await _create_manifest(test_client, auth_headers)
        payload = {
            "namespace": "ns",
            "name": "unique-check",
            "pointer_type": "bundle",
            "manifest_sha256": man_sha,
        }
        r1 = await test_client.post("/api/v1/pointers", json=payload, headers=auth_headers)
        assert r1.status_code == 200
        r2 = await test_client.post("/api/v1/pointers", json=payload, headers=auth_headers)
        assert r2.status_code == 409

    async def test_deleted_pointer_not_in_list(self, test_client, auth_headers):
        """Soft-deleted pointers should not appear in list results."""
        man_sha = await _create_manifest(test_client, auth_headers)
        create_resp = await test_client.post(
            "/api/v1/pointers",
            json={
                "namespace": "ns",
                "name": "del-list-check",
                "pointer_type": "bundle",
                "manifest_sha256": man_sha,
            },
            headers=auth_headers,
        )
        pid = create_resp.json()["id"]
        await test_client.delete(f"/api/v1/pointers/{pid}", headers=auth_headers)

        resp = await test_client.get("/api/v1/pointers?namespace=ns", headers=auth_headers)
        names = [p["name"] for p in resp.json()]
        assert "del-list-check" not in names
