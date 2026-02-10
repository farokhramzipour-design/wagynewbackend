from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    poolclass=NullPool,
    statement_cache_size=1000,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
