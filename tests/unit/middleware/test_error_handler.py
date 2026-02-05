"""Unit tests for error handler middleware — structured error responses."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from intelli.api.middleware.error_handler import (
    ErrorHandlerMiddleware,
    intelli_exception_handler,
)
from intelli.core.exceptions import (
    NotFoundError,
    ValidationError,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def app():
    """Create test app with error handler middleware."""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/intelli-error")
    async def raise_intelli_error():
        raise NotFoundError(resource_type="Widget", identifier="widget-123")

    @app.get("/validation-error")
    async def raise_validation_error():
        raise ValidationError(message="Invalid input", field="email")

    @app.get("/unhandled-error")
    async def raise_unhandled_error():
        raise ValueError("Something went wrong")

    @app.get("/success")
    async def success_endpoint():
        return {"status": "ok"}

    return app


class TestErrorHandlerMiddleware:
    async def test_intelli_error_returns_structured_json(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/intelli-error")

        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert "Widget not found" in data["error"]["message"]
        assert data["error"]["details"]["resource_type"] == "Widget"
        assert data["error"]["details"]["identifier"] == "widget-123"

    async def test_intelli_error_includes_correlation_id(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/intelli-error")

        assert "X-Correlation-ID" in resp.headers

    async def test_validation_error_returns_400(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/validation-error")

        assert resp.status_code == 400
        data = resp.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["message"] == "Invalid input"
        assert data["error"]["details"]["field"] == "email"

    async def test_unhandled_exception_returns_500(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/unhandled-error")

        assert resp.status_code == 500
        data = resp.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert data["error"]["message"] == "An unexpected error occurred"

    async def test_unhandled_exception_hides_details(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/unhandled-error")

        data = resp.json()
        # Should not leak internal error message
        assert "Something went wrong" not in str(data)
        assert data["error"]["details"] == {}

    async def test_success_passes_through(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/success")

        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestIntelliExceptionHandler:
    async def test_exception_handler_function_returns_json(self):
        """Test the standalone exception handler function."""
        from unittest.mock import MagicMock

        request = MagicMock()
        request.url.path = "/test"
        request.method = "GET"

        exc = NotFoundError(resource_type="Artifact", identifier="abc123")

        response = await intelli_exception_handler(request, exc)

        assert response.status_code == 404
        data = response.body.decode()
        assert "NOT_FOUND" in data
        assert "Artifact not found" in data

    async def test_exception_handler_includes_correlation_id(self):
        """Test that correlation ID is included in response headers."""
        from unittest.mock import MagicMock

        request = MagicMock()
        request.url.path = "/test"
        request.method = "GET"

        exc = ValidationError(message="Test error")

        response = await intelli_exception_handler(request, exc)

        assert "X-Correlation-ID" in response.headers
