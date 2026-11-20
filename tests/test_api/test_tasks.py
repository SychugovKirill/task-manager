import asyncio
from datetime import datetime
import os
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport
from app.db.models.task import TaskStatus
from app.main import app
from app.services.task_service import rabbitmq

now = datetime.now().isoformat()


NEW_TASK_PAYLOAD = {
    "id": 121,
    "title": "Test",
    "description": "Test desc",
    "priority": "MEDIUM",
    "started_at": now,
    "finished_at": now,
    "result": "Не известно",
    "error": "Пусто",
}


@pytest.fixture(autouse=True)
async def reset_rabbitmq_state():
    rabbitmq.connection = None
    rabbitmq.channel = None
    rabbitmq.queue = None
    yield
    await rabbitmq.close_rabbitmq()


@pytest.fixture(scope="session", autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@patch("app.services.task_service.rabbitmq.get_channel", new_callable=AsyncMock)
async def test_create_task(mock_get_channel):
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange
    mock_get_channel.return_value = mock_channel
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/tasks/", json=NEW_TASK_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == NEW_TASK_PAYLOAD["title"]
        assert data["description"] == NEW_TASK_PAYLOAD["description"]
        assert data["priority"] == NEW_TASK_PAYLOAD["priority"]
        assert data["status"] == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_get_tasks():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/tasks/")
        assert response.status_code in (200, 204)

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert isinstance(data["items"], list)


@pytest.mark.asyncio
@patch("app.services.task_service.rabbitmq.get_channel", new_callable=AsyncMock)
async def test_get_single_task(mock_get_channel):
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange
    mock_get_channel.return_value = mock_channel
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/api/v1/tasks/", json=NEW_TASK_PAYLOAD)
        task_id = create_resp.json()["id"]
        get_resp = await ac.get(f"/api/v1/tasks/{task_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == task_id


@pytest.mark.asyncio
@patch("app.services.task_service.rabbitmq.get_channel", new_callable=AsyncMock)
async def test_get_task_status(mock_get_channel):
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange
    mock_get_channel.return_value = mock_channel
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/api/v1/tasks/", json=NEW_TASK_PAYLOAD)
        task_id = create_resp.json()["id"]
        status_resp = await ac.get(f"/api/v1/tasks/{task_id}/status")
        assert status_resp.status_code == 200
        assert status_resp.json() == TaskStatus.PENDING


@pytest.mark.asyncio
@patch("app.services.task_service.rabbitmq.get_channel", new_callable=AsyncMock)
async def test_cancel_task(mock_get_channel):
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange
    mock_get_channel.return_value = mock_channel
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/api/v1/tasks/", json=NEW_TASK_PAYLOAD)
        task_id = create_resp.json()["id"]
        cancel_resp = await ac.delete(f"/api/v1/tasks/{task_id}/")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == TaskStatus.CANCELLED
