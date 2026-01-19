"""
Database setup and session management for async SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .config import get_settings

settings = get_settings()


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    future=True,
    poolclass=NullPool,  # Disable connection pooling for better resource management
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncSession:
    """
    Get a new async database session.
    
    This function should be used as a dependency in FastAPI routes.
    """
    async with async_session() as session:
        yield session


async def init_db():
    """
    Initialize database (create all tables).
    
    Should be called on application startup if tables don't exist.
    """
    from app.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connection.
    
    Should be called on application shutdown.
    """
    await engine.dispose()
