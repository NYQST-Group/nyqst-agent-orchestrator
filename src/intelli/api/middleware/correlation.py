"""Correlation ID middleware for request tracing."""

from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from intelli.core.logging import set_correlation_id


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to set up correlation ID for request tracing.

    - Extracts X-Correlation-ID from request headers if present
    - Generates a new one if not
    - Adds correlation ID to response headers
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid4())

        # Set in context for logging
        set_correlation_id(correlation_id)

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response
