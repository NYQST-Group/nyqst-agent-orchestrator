"""FastAPI application factory and entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from intelli.config import settings
from intelli.core.exceptions import IntelliError, NotFoundError, ConflictError, ValidationError
from intelli.api.health import router as health_router
from intelli.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    # Note: Database tables are created via Alembic migrations, not here
    yield
    # Shutdown
    # Clean up resources if needed


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

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": exc.code,
                "message": exc.message,
                "resource_type": exc.resource_type,
                "identifier": exc.identifier,
            },
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": exc.code,
                "message": exc.message,
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.code,
                "message": exc.message,
                "field": exc.field,
            },
        )

    @app.exception_handler(IntelliError)
    async def intelli_error_handler(request: Request, exc: IntelliError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": exc.code,
                "message": exc.message,
            },
        )

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
