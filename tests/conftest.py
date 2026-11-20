import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.models.task import Base
from app.main import app
from app.db.session import get_db

DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(DATABASE_URL_TEST, echo=True, future=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_db():
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
