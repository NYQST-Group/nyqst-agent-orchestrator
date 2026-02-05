"""Integration tests for manifests API endpoints."""

from __future__ import annotations

import io

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_headers(test_session):
    tenant = Tenant(name="Man Co", slug="man-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="man@test.com",
        name="Man",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


async def _upload_artifact(test_client, auth_headers, content: bytes) -> str:
    """Helper to upload an artifact and return its sha256."""
    resp = await test_client.post(
        "/api/v1/artifacts",
        files={"file": ("f.txt", io.BytesIO(content), "text/plain")},
        headers=auth_headers,
    )
    return resp.json()["sha256"]


class TestManifestCreate:
    async def test_create_manifest(self, test_client, auth_headers):
        sha = await _upload_artifact(test_client, auth_headers, b"manifest art")
        resp = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "doc.txt", "artifact_sha256": sha}],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "sha256" in data
        assert data["entry_count"] == 1

    async def test_create_duplicate_manifest(self, test_client, auth_headers):
        sha = await _upload_artifact(test_client, auth_headers, b"dedup manifest")
        payload = {"entries": [{"path": "a.txt", "artifact_sha256": sha}]}
        r1 = await test_client.post("/api/v1/manifests", json=payload, headers=auth_headers)
        r2 = await test_client.post("/api/v1/manifests", json=payload, headers=auth_headers)
        assert r1.json()["sha256"] == r2.json()["sha256"]


class TestManifestGet:
    async def test_get_manifest(self, test_client, auth_headers):
        sha = await _upload_artifact(test_client, auth_headers, b"get manifest")
        create_resp = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "b.txt", "artifact_sha256": sha}],
            },
            headers=auth_headers,
        )
        manifest_sha = create_resp.json()["sha256"]

        resp = await test_client.get(f"/api/v1/manifests/{manifest_sha}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["sha256"] == manifest_sha

    async def test_get_missing_manifest(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/manifests/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestManifestList:
    async def test_list_manifests(self, test_client, auth_headers):
        resp = await test_client.get("/api/v1/manifests", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestManifestEntries:
    async def test_get_entries(self, test_client, auth_headers):
        sha = await _upload_artifact(test_client, auth_headers, b"entries test")
        create_resp = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "e.txt", "artifact_sha256": sha}],
            },
            headers=auth_headers,
        )
        manifest_sha = create_resp.json()["sha256"]

        resp = await test_client.get(
            f"/api/v1/manifests/{manifest_sha}/entries", headers=auth_headers
        )
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) == 1
        assert entries[0]["path"] == "e.txt"


class TestManifestAuth:
    """Auth enforcement on manifest routes.

    Expected to fail until auth middleware is applied.
    """

    async def test_create_requires_auth(self, test_client):
        resp = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "x.txt", "artifact_sha256": "a" * 64}],
            },
        )
        assert resp.status_code in (401, 403)

    async def test_list_requires_auth(self, test_client):
        resp = await test_client.get("/api/v1/manifests")
        assert resp.status_code in (401, 403)


class TestManifestInvariants:
    """Content-addressable invariants for manifests."""

    async def test_manifest_sha_is_deterministic(self, test_client, auth_headers):
        """Same entries always produce the same manifest hash."""
        sha = await _upload_artifact(test_client, auth_headers, b"invariant-art")
        payload = {"entries": [{"path": "inv.txt", "artifact_sha256": sha}]}
        r1 = await test_client.post("/api/v1/manifests", json=payload, headers=auth_headers)
        r2 = await test_client.post("/api/v1/manifests", json=payload, headers=auth_headers)
        assert r1.json()["sha256"] == r2.json()["sha256"]

    async def test_different_entries_different_sha(self, test_client, auth_headers):
        """Different entry sets must produce different manifest hashes."""
        sha1 = await _upload_artifact(test_client, auth_headers, b"art-alpha")
        sha2 = await _upload_artifact(test_client, auth_headers, b"art-beta")
        r1 = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "a.txt", "artifact_sha256": sha1}],
            },
            headers=auth_headers,
        )
        r2 = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "b.txt", "artifact_sha256": sha2}],
            },
            headers=auth_headers,
        )
        assert r1.json()["sha256"] != r2.json()["sha256"]

    async def test_invalid_sha256_rejected(self, test_client, auth_headers):
        """Entries with non-hex or wrong-length SHA should be rejected."""
        resp = await test_client.post(
            "/api/v1/manifests",
            json={
                "entries": [{"path": "bad.txt", "artifact_sha256": "not-a-sha"}],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 422
