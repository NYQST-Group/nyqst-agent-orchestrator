"""FastAPI application factory and entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from intelli.config import settings
from intelli.core.logging import setup_logging, get_logger
from intelli.core.exceptions import IntelliError
from intelli.api.middleware import (
    CorrelationMiddleware,
    ErrorHandlerMiddleware,
    intelli_exception_handler,
)
from intelli.api.health import router as health_router
from intelli.api.v1 import router as v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    setup_logging()
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        debug=settings.debug,
    )
    # Note: Database tables are created via Alembic migrations, not here
    yield
    # Shutdown
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.app_name,
        description="Agent-First Document Intelligence Platform API",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Middleware order matters: outermost runs first on request, last on response
    # 1. Error handler - catches all exceptions and formats responses
    app.add_middleware(ErrorHandlerMiddleware)

    # 2. Correlation ID - adds tracing ID to all requests/responses
    app.add_middleware(CorrelationMiddleware)

    # 3. CORS - handles cross-origin requests
    cors_origins = settings.cors_origins if not settings.debug else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
    )

    # Exception handler for IntelliError (backup for middleware)
    app.add_exception_handler(IntelliError, intelli_exception_handler)

    # Include routers
    app.include_router(health_router)
    app.include_router(v1_router)

    return app


# Create the default application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "intelli.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
