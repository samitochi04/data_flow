from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_database_url

DATABASE_URL = get_database_url()

# async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

# dependency for FastAPI
async def get_db() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session