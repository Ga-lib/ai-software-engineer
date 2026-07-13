"""
Database session management using SQLAlchemy's async engine.
Provides a reusable async engine, session factory, and a FastAPI dependency
for getting a database session inside route handlers.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# The async engine manages the pool of connections to Supabase's PostgreSQL.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # logs SQL statements when debug mode is on
    future=True,
    pool_pre_ping=True,  # checks connections are alive before using them (important for hosted DBs)
)

# Factory for creating new async sessions bound to the engine above.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session and guarantees
    it gets closed after the request finishes, even if an error occurs.
    """
    async with AsyncSessionLocal() as session:
        yield session