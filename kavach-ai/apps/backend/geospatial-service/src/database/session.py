import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config.settings import settings
import structlog
from src.database.models import Base

logger = structlog.get_logger()

# We only create engine if not testing
if os.environ.get("TESTING") != "1":
    engine = create_async_engine(settings.POSTGRES_URL, echo=False)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
else:
    engine = None
    async_session_factory = None

async def init_db():
    if os.environ.get("TESTING") == "1":
        return
        
    try:
        # For postgis, extension must exist. 
        # Typically created during DB init script, but we ensure tables are made.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))

async def get_db() -> AsyncSession:
    if os.environ.get("TESTING") == "1":
        yield None
        return
        
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
