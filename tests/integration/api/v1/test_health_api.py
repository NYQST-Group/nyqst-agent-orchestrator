"""Integration tests for health check endpoints."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


class TestHealthEndpoints:
    async def test_liveness(self, test_client):
        resp = await test_client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "alive"

    async def test_readiness(self, test_client):
        resp = await test_client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"

    async def test_detailed_health(self, test_client):
        resp = await test_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "healthy"

    async def test_health_includes_app_name(self, test_client):
        resp = await test_client.get("/health")
        data = resp.json()
        assert "app" in data

    async def test_health_includes_correlation_id(self, test_client):
        resp = await test_client.get("/health")
        data = resp.json()
        assert "correlation_id" in data
