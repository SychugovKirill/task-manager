from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

# 🔹 Асинхронный движок (для FastAPI)
async_engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with async_session() as session:
        yield session
