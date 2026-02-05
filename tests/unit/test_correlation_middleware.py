"""Unit tests for CorrelationMiddleware — request tracing."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from intelli.api.middleware.correlation import CorrelationMiddleware

pytestmark = pytest.mark.unit


@pytest.fixture
def app():
    app = FastAPI()
    app.add_middleware(CorrelationMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


class TestCorrelationMiddleware:
    async def test_adds_correlation_id(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/test")
        assert "X-Correlation-ID" in resp.headers
        assert len(resp.headers["X-Correlation-ID"]) > 0

    async def test_preserves_existing_correlation_id(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/test", headers={"X-Correlation-ID": "my-trace-id"})
        assert resp.headers["X-Correlation-ID"] == "my-trace-id"

    async def test_generates_uuid_format(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/test")
        cid = resp.headers["X-Correlation-ID"]
        # UUID4 format: 8-4-4-4-12 hex chars
        parts = cid.split("-")
        assert len(parts) == 5

    async def test_different_requests_get_different_ids(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r1 = await client.get("/test")
            r2 = await client.get("/test")
        assert r1.headers["X-Correlation-ID"] != r2.headers["X-Correlation-ID"]
