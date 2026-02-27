"""Pytest configuration and fixtures for DataFlow API tests"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.core.database import Base


@pytest.fixture(scope="function")
def test_engine_sync():
    """Create async SQLite engine for tests (sync wrapper)
    
    Using aiosqlite avoids asyncpg's event loop issues on Windows.
    Each test gets a fresh in-memory database.
    """
    async def _create_engine():
        test_db_url = "sqlite+aiosqlite:///:memory:"
        test_engine = create_async_engine(
            test_db_url,
            connect_args={"timeout": 30},
            echo=False,
            pool_pre_ping=False,
            poolclass=None
        )
        
        # Create all tables
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        return test_engine
    
    # Create engine in new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_engine = loop.run_until_complete(_create_engine())
    
    yield test_engine
    
    # Cleanup
    async def _cleanup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()
    
    loop.run_until_complete(_cleanup())
    loop.close()


@pytest.fixture(scope="function")
async def db_session(test_engine_sync):
    """Async database session for direct repository tests
    
    Provides an AsyncSession for testing repository operations directly
    without going through the HTTP layer.
    """
    TestSessionLocal = sessionmaker(
        test_engine_sync,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
def client(test_engine_sync):
    """FastAPI test client with SQLite database
    
    Each test gets an isolated in-memory SQLite database.
    This avoids asyncpg event loop issues on Windows.
    """
    test_engine = test_engine_sync
    
    # Create AsyncSessionLocal for this test
    TestSessionLocal = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Return test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup overrides
    app.dependency_overrides.clear()

