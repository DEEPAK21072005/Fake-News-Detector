import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from backend.app.core.config import settings
from backend.app.core.logging_config import logger

# Async Engine (for API operations)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sync Engine (for CLI/scripts/training pipelines)
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db():
    """FastAPI async dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Sync session for training or standalone scripts."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_database():
    """Initialize database tables asynchronously."""
    try:
        # Ensure database directory exists
        db_file = Path(settings.DATABASE_URL.split(":///")[-1])
        db_file.parent.mkdir(parents=True, exist_ok=True)
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization deferred or fallback: {e}")
