"""Global error handling middleware.

Converts exceptions to consistent JSON responses and logs errors.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from intelli.core.exceptions import IntelliError
from intelli.core.logging import get_correlation_id, get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and handle exceptions globally."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            return await call_next(request)
        except IntelliError as e:
            # Our custom exceptions - log and return structured response
            logger.warning(
                "request_failed",
                error_code=e.code,
                error_message=e.message,
                status_code=e.status_code,
                path=request.url.path,
                method=request.method,
                details=e.details,
            )
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict(),
                headers={"X-Correlation-ID": get_correlation_id()},
            )
        except Exception as e:
            # Unexpected exceptions - log full traceback
            logger.exception(
                "unhandled_exception",
                error_type=type(e).__name__,
                error_message=str(e),
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {},
                    }
                },
                headers={"X-Correlation-ID": get_correlation_id()},
            )


async def intelli_exception_handler(request: Request, exc: IntelliError) -> JSONResponse:
    """FastAPI exception handler for IntelliError."""
    logger.warning(
        "request_failed",
        error_code=exc.code,
        error_message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers={"X-Correlation-ID": get_correlation_id()},
    )
