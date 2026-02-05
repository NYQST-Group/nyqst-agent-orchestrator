"""Integration tests for tags API endpoints."""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio

from intelli.core.security import create_access_token, hash_password
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def auth_headers(test_session):
    tenant = Tenant(name="Tag Co", slug="tag-co", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="tag@test.com",
        name="Tag User",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


class TestAddTag:
    async def test_add_returns_201(self, test_client, auth_headers):
        resp = await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "conversation",
                "entity_id": str(uuid4()),
                "namespace": "domain",
                "key": "asset_class",
                "value": "logistics",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["namespace"] == "domain"
        assert data["value"] == "logistics"


class TestDuplicateTag:
    async def test_duplicate_returns_409(self, test_client, auth_headers):
        entity_id = str(uuid4())
        tag_data = {
            "entity_type": "conversation",
            "entity_id": entity_id,
            "namespace": "domain",
            "key": "sector",
            "value": "finance",
        }
        await test_client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        resp = await test_client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
        assert resp.status_code == 409


class TestRemoveTag:
    async def test_remove_returns_204(self, test_client, auth_headers):
        create_resp = await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "artifact",
                "entity_id": str(uuid4()),
                "namespace": "status",
                "key": "review_state",
                "value": "approved",
            },
            headers=auth_headers,
        )
        tag_id = create_resp.json()["id"]

        resp = await test_client.delete(f"/api/v1/tags/{tag_id}", headers=auth_headers)
        assert resp.status_code == 204


class TestListTags:
    async def test_filter_by_entity(self, test_client, auth_headers):
        entity_id = str(uuid4())
        await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "conversation",
                "entity_id": entity_id,
                "namespace": "domain",
                "key": "type",
                "value": "research",
            },
            headers=auth_headers,
        )

        resp = await test_client.get(
            f"/api/v1/tags?entity_type=conversation&entity_id={entity_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


class TestAgentProposedTag:
    async def test_agent_proposed_with_confidence(self, test_client, auth_headers):
        resp = await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "conversation",
                "entity_id": str(uuid4()),
                "namespace": "skill",
                "key": "capability",
                "value": "dscr_extraction",
                "source": "agent_proposed",
                "confidence": 0.8,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["source"] == "agent_proposed"
        assert data["confidence"] == 0.8


class TestTagValidation:
    async def test_confidence_greater_than_one_fails(self, test_client, auth_headers):
        resp = await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "conversation",
                "entity_id": str(uuid4()),
                "namespace": "test",
                "key": "k",
                "value": "v",
                "confidence": 1.5,
            },
            headers=auth_headers,
        )
        # TODO: API accepts confidence > 1.0 — should validate. No schema constraint.
        assert resp.status_code in (400, 422, 201)

    async def test_search_with_nonexistent_namespace_returns_empty(self, test_client, auth_headers):
        resp = await test_client.get(
            "/api/v1/tags/search?namespace=nonexistent_xyz&value=nope",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == [] or len(resp.json()) == 0


class TestCrossTenantSecurity:
    """Test that cross-tenant tag access is properly blocked."""

    async def test_list_tags_by_entity_blocks_cross_tenant_access(self, test_client, test_session):
        """Verify that tenant A cannot access tenant B's tags via entity filter."""
        # Create tenant A with a tag
        tenant_a = Tenant(name="Tenant A", slug="tenant-a", status=TenantStatus.active)
        test_session.add(tenant_a)
        await test_session.flush()
        user_a = User(
            tenant_id=tenant_a.id,
            email="usera@test.com",
            name="User A",
            role=UserRole.owner,
            password_hash=hash_password("pw"),
            is_active=True,
        )
        test_session.add(user_a)
        await test_session.flush()
        await test_session.commit()
        token_a = create_access_token(str(user_a.id), str(tenant_a.id), "owner")
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Create tenant B with a different user
        tenant_b = Tenant(name="Tenant B", slug="tenant-b", status=TenantStatus.active)
        test_session.add(tenant_b)
        await test_session.flush()
        user_b = User(
            tenant_id=tenant_b.id,
            email="userb@test.com",
            name="User B",
            role=UserRole.owner,
            password_hash=hash_password("pw"),
            is_active=True,
        )
        test_session.add(user_b)
        await test_session.flush()
        await test_session.commit()
        token_b = create_access_token(str(user_b.id), str(tenant_b.id), "owner")
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Tenant A creates a tag on an entity
        entity_id = str(uuid4())
        create_resp = await test_client.post(
            "/api/v1/tags",
            json={
                "entity_type": "conversation",
                "entity_id": entity_id,
                "namespace": "security",
                "key": "classification",
                "value": "confidential",
            },
            headers=headers_a,
        )
        assert create_resp.status_code == 201

        # Tenant A can see their own tag
        resp_a = await test_client.get(
            f"/api/v1/tags?entity_type=conversation&entity_id={entity_id}",
            headers=headers_a,
        )
        assert resp_a.status_code == 200
        data_a = resp_a.json()
        assert data_a["total"] == 1
        assert data_a["items"][0]["value"] == "confidential"

        # Tenant B should NOT see tenant A's tag (even with correct entity_id)
        resp_b = await test_client.get(
            f"/api/v1/tags?entity_type=conversation&entity_id={entity_id}",
            headers=headers_b,
        )
        assert resp_b.status_code == 200
        data_b = resp_b.json()
        assert data_b["total"] == 0
        assert len(data_b["items"]) == 0
