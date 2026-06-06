import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"

from app.cache import cache
from app.database import Base, engine, init_db
from app.main import app


def pytest_configure(config):
    config.option.asyncio_mode = "auto"


@pytest.fixture
async def db():
    await init_db()
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


def pytest_collection_modifyitems(items):
    for item in items:
        if item.module.__name__ in (
            "tests.test_routes",
            "tests.test_scheduler_service",
        ):
            item.fixturenames.append("db")


@pytest.fixture(autouse=True)
async def _clear_cache():
    await cache.clear()
    yield


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
