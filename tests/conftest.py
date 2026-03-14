"""Pytest fixtures for Intelli platform tests."""

# ruff: noqa: E402

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Test database URL - use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://intelli:intelli@localhost:5433/intelli_test"

# Set test-safe defaults before importing application modules that cache settings.
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("STORAGE_BACKEND", "local")
os.environ.setdefault("LOCAL_STORAGE_PATH", "/tmp/intelli-test-storage")

from intelli.api.dependencies import get_session
from intelli.core.security import create_access_token, hash_password
from intelli.db.base import Base
from intelli.db.models.auth import Tenant, TenantStatus, User, UserRole
from intelli.main import create_app


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine and tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create test database session."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def _reset_checkpointer():
    """Reset the checkpointer singleton between tests to avoid stale connections."""
    yield
    import intelli.db.checkpointer as cp

    # Use the new CheckpointerManager-based API
    try:
        await cp._manager.close_checkpointer()
    except Exception:
        pass


@pytest_asyncio.fixture
async def test_client(test_session):
    """Create test HTTP client with dependency overrides."""
    app = create_app()

    # Override the database session dependency
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(test_session):
    """Create a tenant+user and return auth headers."""
    tenant = Tenant(name="Test Tenant", slug="test-tenant", status=TenantStatus.active)
    test_session.add(tenant)
    await test_session.flush()
    user = User(
        tenant_id=tenant.id,
        email="test@example.com",
        name="Test User",
        role=UserRole.owner,
        password_hash=hash_password("pw"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.commit()
    token = create_access_token(str(user.id), str(tenant.id), "owner")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_artifact_content() -> bytes:
    """Sample content for artifact tests."""
    return b"Hello, this is test content for artifact testing."


@pytest.fixture
def sample_pdf_content() -> bytes:
    """Minimal PDF content for testing."""
    # This is a minimal valid PDF
    return b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [] /Count 0 >> endobj
xref
0 3
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
trailer << /Size 3 /Root 1 0 R >>
startxref
115
%%EOF"""
