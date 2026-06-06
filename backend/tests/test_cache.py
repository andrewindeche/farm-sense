import time

import pytest

from app.cache import cache


@pytest.mark.asyncio
async def test_get_missing_key_returns_none():
    assert await cache.get("nonexistent") is None


@pytest.mark.asyncio
async def test_set_and_get():
    await cache.set("key1", {"value": 42}, ttl=60)
    result = await cache.get("key1")
    assert result == {"value": 42}


@pytest.mark.asyncio
async def test_ttl_expiry():
    await cache.set("key2", "data", ttl=1)
    assert await cache.get("key2") == "data"
    time.sleep(1.1)
    assert await cache.get("key2") is None


@pytest.mark.asyncio
async def test_delete():
    await cache.set("key3", "to-delete", ttl=60)
    await cache.delete("key3")
    assert await cache.get("key3") is None


@pytest.mark.asyncio
async def test_clear():
    await cache.set("a", 1, ttl=60)
    await cache.set("b", 2, ttl=60)
    await cache.clear()
    assert await cache.get("a") is None
    assert await cache.get("b") is None


@pytest.mark.asyncio
async def test_overwrite_existing_key():
    await cache.set("key4", "old", ttl=60)
    await cache.set("key4", "new", ttl=60)
    assert await cache.get("key4") == "new"


@pytest.mark.asyncio
async def test_cache_isolation_between_keys():
    await cache.set("x", 100, ttl=60)
    await cache.set("y", 200, ttl=60)
    assert await cache.get("x") == 100
    assert await cache.get("y") == 200
