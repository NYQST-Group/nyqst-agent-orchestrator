"""Unit tests for auth context middleware — request context resolution."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request

from intelli.api.middleware.context import AuthContextMiddleware
from intelli.core.context import RequestContext

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def app():
    """Create test app with context middleware."""
    app = FastAPI()
    app.add_middleware(AuthContextMiddleware)

    @app.get("/test")
    async def test_endpoint(request: Request):
        # Access the context set by middleware
        ctx = getattr(request.state, "context", None)
        if ctx:
            return {
                "authenticated": True,
                "tenant_id": str(ctx.tenant_id) if ctx.tenant_id else None,
            }
        return {"authenticated": False}

    return app


@asynccontextmanager
async def mock_session_factory():
    """Mock async session factory."""
    session = AsyncMock()
    try:
        yield session
    finally:
        pass


class TestAuthContextMiddleware:
    async def test_no_credentials_sets_context_to_none(self, app):
        """When no auth headers are present, context should be None."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/test")

        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is False

    async def test_api_key_header_triggers_auth(self, app):
        """When X-API-Key header is present, should attempt auth."""
        tenant_id = uuid4()
        ctx = RequestContext(tenant_id=tenant_id, scopes=["read"])

        def get_mock_factory():
            return mock_session_factory

        with (
            patch(
                "intelli.api.middleware.context.get_session_factory",
                return_value=get_mock_factory(),
            ),
            patch("intelli.api.middleware.context.get_api_key_auth", return_value=ctx),
            patch("intelli.api.middleware.context.set_context"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/test", headers={"X-API-Key": "test_key"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert data["tenant_id"] == str(tenant_id)

    async def test_bearer_header_triggers_auth(self, app):
        """When Authorization: Bearer header is present, should attempt auth."""
        tenant_id = uuid4()
        ctx = RequestContext(tenant_id=tenant_id, scopes=["read"])

        def get_mock_factory():
            return mock_session_factory

        with (
            patch(
                "intelli.api.middleware.context.get_session_factory",
                return_value=get_mock_factory(),
            ),
            patch("intelli.api.middleware.context.get_api_key_auth", return_value=None),
            patch("intelli.api.middleware.context.get_bearer_auth", return_value=ctx),
            patch("intelli.api.middleware.context.set_context"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/test", headers={"Authorization": "Bearer test_token"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert data["tenant_id"] == str(tenant_id)

    async def test_auth_exception_sets_context_to_none(self, app):
        """When auth fails with exception, context should be None (non-fatal)."""

        def get_mock_factory():
            return mock_session_factory

        with (
            patch(
                "intelli.api.middleware.context.get_session_factory",
                return_value=get_mock_factory(),
            ),
            patch(
                "intelli.api.middleware.context.get_api_key_auth",
                side_effect=Exception("DB error"),
            ),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/test", headers={"X-API-Key": "test_key"})

        # Should not fail the request
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is False

    async def test_api_key_takes_precedence_over_bearer(self, app):
        """When both headers present, API key should be tried first."""
        tenant_id = uuid4()
        api_ctx = RequestContext(tenant_id=tenant_id, scopes=["read"], api_key_id=uuid4())

        def get_mock_factory():
            return mock_session_factory

        with (
            patch(
                "intelli.api.middleware.context.get_session_factory",
                return_value=get_mock_factory(),
            ),
            patch("intelli.api.middleware.context.get_api_key_auth", return_value=api_ctx),
            patch("intelli.api.middleware.context.get_bearer_auth") as mock_bearer,
            patch("intelli.api.middleware.context.set_context"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get(
                    "/test",
                    headers={
                        "X-API-Key": "test_key",
                        "Authorization": "Bearer token",
                    },
                )

        # Bearer auth should not be called since API key succeeded
        mock_bearer.assert_not_called()
        assert resp.status_code == 200

    async def test_falls_back_to_bearer_when_api_key_fails(self, app):
        """When API key auth returns None, should try bearer."""
        tenant_id = uuid4()
        bearer_ctx = RequestContext(tenant_id=tenant_id, scopes=["read"], user_id=uuid4())

        def get_mock_factory():
            return mock_session_factory

        with (
            patch(
                "intelli.api.middleware.context.get_session_factory",
                return_value=get_mock_factory(),
            ),
            patch("intelli.api.middleware.context.get_api_key_auth", return_value=None),
            patch("intelli.api.middleware.context.get_bearer_auth", return_value=bearer_ctx),
            patch("intelli.api.middleware.context.set_context"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get(
                    "/test",
                    headers={
                        "X-API-Key": "bad_key",
                        "Authorization": "Bearer token",
                    },
                )

        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
