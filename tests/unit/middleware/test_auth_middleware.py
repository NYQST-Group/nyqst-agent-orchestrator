"""Unit tests for authentication middleware — API key and bearer auth."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request

from intelli.api.middleware.auth import (
    authenticate,
    authenticate_optional,
    get_api_key_auth,
    get_bearer_auth,
    require_admin,
    require_scope,
)
from intelli.core.context import RequestContext
from intelli.db.models.auth import APIKey, Tenant, User

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


# ---------------------------------------------------------------------------
# API Key Authentication
# ---------------------------------------------------------------------------


class TestAPIKeyAuth:
    async def test_api_key_auth_valid_key_returns_context(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "TestAgent/1.0"

        api_key_obj = APIKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_hash="fake_hash",
            is_active=True,
            expires_at=None,
            allowed_ips=None,
            rate_limit_rpm=60,
            scopes=["read", "write"],
            use_count=0,
        )
        tenant = Tenant(id=api_key_obj.tenant_id, status="active")

        # Mock the select query result - first() is synchronous
        result = MagicMock()
        result.first.return_value = (api_key_obj, tenant)
        session.execute.return_value = result

        with (
            patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"),
            patch("intelli.api.middleware.auth.rate_limiter.is_allowed", return_value=True),
        ):
            ctx = await get_api_key_auth(session, "test_key", request)

        assert ctx is not None
        assert ctx.tenant_id == api_key_obj.tenant_id
        assert ctx.api_key_id == api_key_obj.id
        assert ctx.scopes == ["read", "write"]
        assert ctx.ip_address == "192.168.1.1"

    async def test_api_key_auth_invalid_key_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        # Mock empty result - first() is synchronous
        result = MagicMock()
        result.first.return_value = None
        session.execute.return_value = result

        with patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"):
            ctx = await get_api_key_auth(session, "invalid_key", request)

        assert ctx is None

    async def test_api_key_auth_expired_key_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"

        expired_time = datetime.now(UTC) - timedelta(hours=1)
        api_key_obj = APIKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_hash="fake_hash",
            is_active=True,
            expires_at=expired_time,
            allowed_ips=None,
            rate_limit_rpm=60,
            scopes=["read"],
            use_count=0,
        )
        tenant = Tenant(id=api_key_obj.tenant_id, status="active")

        result = MagicMock()
        result.first.return_value = (api_key_obj, tenant)
        session.execute.return_value = result

        with patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"):
            ctx = await get_api_key_auth(session, "test_key", request)

        assert ctx is None

    async def test_api_key_auth_ip_not_in_allowlist_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.100"

        api_key_obj = APIKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_hash="fake_hash",
            is_active=True,
            expires_at=None,
            allowed_ips=["10.0.0.1", "10.0.0.2"],
            rate_limit_rpm=60,
            scopes=["read"],
            use_count=0,
        )
        tenant = Tenant(id=api_key_obj.tenant_id, status="active")

        result = MagicMock()
        result.first.return_value = (api_key_obj, tenant)
        session.execute.return_value = result

        with patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"):
            ctx = await get_api_key_auth(session, "test_key", request)

        assert ctx is None

    async def test_api_key_auth_rate_limit_exceeded_raises_429(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"

        api_key_obj = APIKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_hash="fake_hash",
            is_active=True,
            expires_at=None,
            allowed_ips=None,
            rate_limit_rpm=60,
            scopes=["read"],
            use_count=0,
        )
        tenant = Tenant(id=api_key_obj.tenant_id, status="active")

        result = MagicMock()
        result.first.return_value = (api_key_obj, tenant)
        session.execute.return_value = result

        with (
            patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"),
            patch("intelli.api.middleware.auth.rate_limiter.is_allowed", return_value=False),
            pytest.raises(HTTPException) as exc_info,
        ):
            await get_api_key_auth(session, "test_key", request)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    async def test_api_key_auth_inactive_tenant_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        api_key_obj = APIKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_hash="fake_hash",
            is_active=True,
            expires_at=None,
            allowed_ips=None,
            rate_limit_rpm=60,
            scopes=["read"],
            use_count=0,
        )
        # Inactive tenant
        Tenant(id=api_key_obj.tenant_id, status="suspended")

        # Query would filter out inactive tenant, so return None
        result = MagicMock()
        result.first.return_value = None
        session.execute.return_value = result

        with patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"):
            ctx = await get_api_key_auth(session, "test_key", request)

        assert ctx is None

    async def test_api_key_auth_updates_last_used_and_use_count(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "TestAgent/1.0"

        api_key_obj = APIKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_hash="fake_hash",
            is_active=True,
            expires_at=None,
            allowed_ips=None,
            rate_limit_rpm=60,
            scopes=["read"],
            use_count=5,
        )
        tenant = Tenant(id=api_key_obj.tenant_id, status="active")

        result = MagicMock()
        result.first.return_value = (api_key_obj, tenant)
        session.execute.return_value = result

        with (
            patch("intelli.api.middleware.auth.hash_api_key", return_value="fake_hash"),
            patch("intelli.api.middleware.auth.rate_limiter.is_allowed", return_value=True),
        ):
            ctx = await get_api_key_auth(session, "test_key", request)

        # Verify update was called
        assert session.execute.call_count == 2  # Once for select, once for update
        assert ctx is not None


# ---------------------------------------------------------------------------
# Bearer Token Authentication
# ---------------------------------------------------------------------------


class TestBearerAuth:
    async def test_bearer_auth_valid_token_returns_context(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "Mozilla/5.0"

        tenant_id = uuid4()
        user_id = uuid4()

        tenant = Tenant(id=tenant_id, status="active")
        user = User(id=user_id, tenant_id=tenant_id, is_active=True, role="member")

        # Mock decode_access_token
        payload = {
            "sub": str(user_id),
            "tid": str(tenant_id),
            "role": "member",
        }

        # Mock tenant query - scalar_one_or_none is synchronous
        tenant_result = MagicMock()
        tenant_result.scalar_one_or_none.return_value = tenant

        # Mock user query
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = user

        session.execute.side_effect = [tenant_result, user_result]

        with patch("intelli.api.middleware.auth.decode_access_token", return_value=payload):
            ctx = await get_bearer_auth(session, "valid_token", request)

        assert ctx is not None
        assert ctx.tenant_id == tenant_id
        assert ctx.user_id == user_id
        assert ctx.role == "member"
        assert "read" in ctx.scopes

    async def test_bearer_auth_invalid_token_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        with patch("intelli.api.middleware.auth.decode_access_token", return_value=None):
            ctx = await get_bearer_auth(session, "invalid_token", request)

        assert ctx is None

    async def test_bearer_auth_inactive_tenant_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        tenant_id = uuid4()
        user_id = uuid4()

        payload = {
            "sub": str(user_id),
            "tid": str(tenant_id),
            "role": "member",
        }

        # Mock tenant query - returns None (inactive/not found)
        tenant_result = MagicMock()
        tenant_result.scalar_one_or_none.return_value = None
        session.execute.return_value = tenant_result

        with patch("intelli.api.middleware.auth.decode_access_token", return_value=payload):
            ctx = await get_bearer_auth(session, "valid_token", request)

        assert ctx is None

    async def test_bearer_auth_inactive_user_returns_none(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        tenant_id = uuid4()
        user_id = uuid4()

        tenant = Tenant(id=tenant_id, status="active")

        payload = {
            "sub": str(user_id),
            "tid": str(tenant_id),
            "role": "member",
        }

        # Mock tenant query - returns tenant
        tenant_result = MagicMock()
        tenant_result.scalar_one_or_none.return_value = tenant

        # Mock user query - returns None (inactive/not found)
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None

        session.execute.side_effect = [tenant_result, user_result]

        with patch("intelli.api.middleware.auth.decode_access_token", return_value=payload):
            ctx = await get_bearer_auth(session, "valid_token", request)

        assert ctx is None


# ---------------------------------------------------------------------------
# Authenticate Function
# ---------------------------------------------------------------------------


class TestAuthenticate:
    async def test_authenticate_tries_api_key_first(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "TestAgent/1.0"

        tenant_id = uuid4()
        ctx = RequestContext(tenant_id=tenant_id, scopes=["read"])

        with (
            patch("intelli.api.middleware.auth.get_api_key_auth", return_value=ctx) as mock_api,
            patch("intelli.api.middleware.auth.set_context") as mock_set,
        ):
            result = await authenticate(request, session, x_api_key="test_key", bearer=None)

        mock_api.assert_called_once()
        mock_set.assert_called_once_with(ctx)
        assert result == ctx

    async def test_authenticate_falls_back_to_bearer(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "TestAgent/1.0"

        tenant_id = uuid4()
        ctx = RequestContext(tenant_id=tenant_id, scopes=["read"])

        bearer_creds = MagicMock()
        bearer_creds.credentials = "bearer_token"

        with (
            patch("intelli.api.middleware.auth.get_api_key_auth", return_value=None),
            patch("intelli.api.middleware.auth.get_bearer_auth", return_value=ctx) as mock_bearer,
            patch("intelli.api.middleware.auth.set_context") as mock_set,
        ):
            result = await authenticate(request, session, x_api_key=None, bearer=bearer_creds)

        mock_bearer.assert_called_once()
        mock_set.assert_called_once_with(ctx)
        assert result == ctx

    async def test_authenticate_no_credentials_raises_401(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        with pytest.raises(HTTPException) as exc_info:
            await authenticate(request, session, x_api_key=None, bearer=None)

        assert exc_info.value.status_code == 401
        assert "Invalid or missing authentication" in exc_info.value.detail


# ---------------------------------------------------------------------------
# Optional Authentication
# ---------------------------------------------------------------------------


class TestAuthenticateOptional:
    async def test_authenticate_optional_returns_none_on_no_credentials(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        result = await authenticate_optional(request, session, x_api_key=None, bearer=None)

        assert result is None

    async def test_authenticate_optional_returns_context_on_valid_api_key(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "TestAgent/1.0"

        tenant_id = uuid4()
        ctx = RequestContext(tenant_id=tenant_id, scopes=["read"])

        with (
            patch("intelli.api.middleware.auth.get_api_key_auth", return_value=ctx),
            patch("intelli.api.middleware.auth.set_context") as mock_set,
        ):
            result = await authenticate_optional(
                request, session, x_api_key="test_key", bearer=None
            )

        mock_set.assert_called_once_with(ctx)
        assert result == ctx

    async def test_authenticate_optional_handles_rate_limit_exception(self):
        session = AsyncMock()
        request = MagicMock(spec=Request)

        # Simulate rate limit exception
        with patch(
            "intelli.api.middleware.auth.get_api_key_auth",
            side_effect=HTTPException(status_code=429),
        ):
            result = await authenticate_optional(
                request, session, x_api_key="test_key", bearer=None
            )

        assert result is None


# ---------------------------------------------------------------------------
# Scope and Role Checks
# ---------------------------------------------------------------------------


class TestRequireScope:
    async def test_require_scope_passes_with_valid_scope(self):
        ctx = RequestContext(tenant_id=uuid4(), scopes=["read", "write"])

        check_func = require_scope("write")
        result = await check_func(ctx)

        assert result == ctx

    async def test_require_scope_raises_403_without_scope(self):
        ctx = RequestContext(tenant_id=uuid4(), scopes=["read"])

        check_func = require_scope("write")
        with pytest.raises(HTTPException) as exc_info:
            await check_func(ctx)

        assert exc_info.value.status_code == 403
        assert "Missing required scope: write" in exc_info.value.detail


class TestRequireAdmin:
    async def test_require_admin_passes_for_admin_role(self):
        ctx = RequestContext(tenant_id=uuid4(), role="admin", scopes=["read"])

        check_func = require_admin()
        result = await check_func(ctx)

        assert result == ctx

    async def test_require_admin_passes_for_owner_role(self):
        ctx = RequestContext(tenant_id=uuid4(), role="owner", scopes=["read"])

        check_func = require_admin()
        result = await check_func(ctx)

        assert result == ctx

    async def test_require_admin_raises_403_for_member(self):
        ctx = RequestContext(tenant_id=uuid4(), role="member", scopes=["read", "write"])

        check_func = require_admin()
        with pytest.raises(HTTPException) as exc_info:
            await check_func(ctx)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail
