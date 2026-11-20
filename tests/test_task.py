import pytest
from unittest.mock import AsyncMock, MagicMock

from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from app.db.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate
from app.services.task_service import create_task, get_tasks_list, get_task, cancel_task


@pytest.mark.asyncio
async def test_create_task(mocker):
    db = AsyncMock(spec=AsyncSession)

    task_data = TaskCreate(
        title="Test",
        description="Test desc",
        priority="MEDIUM",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        result="Не известно",
        error="Пусто",
    )

    task_instance = Task(**task_data.model_dump())
    task_instance.id = 123
    task_instance.priority = MagicMock()
    task_instance.priority.to_rabbitmq_priority.return_value = 5

    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()

    mocker.patch("app.services.task_service.Task", return_value=task_instance)

    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange
    mocker.patch("app.services.task_service.rabbitmq.get_channel", return_value=mock_channel)

    mocker.patch("app.services.task_service.aio_pika.Message", return_value="message")

    task = await create_task(db, task_data)

    assert task.id == 123
    db.add.assert_called_once()
    db.commit.assert_called_once()
    mock_exchange.publish.assert_called_once()


@pytest.mark.asyncio
async def test_get_tasks_list_with_data(mocker):
    db = AsyncMock(spec=AsyncSession)
    mock_tasks = [Task(id=1, title="Task", description="desc", status="COMPLETED")]

    base_result = AsyncMock(spec=Result)
    base_result.scalars.return_value.all.return_value = mock_tasks
    db.execute = AsyncMock(side_effect=[AsyncMock(scalar_one=MagicMock(return_value=1)), base_result])

    result = await get_tasks_list(status=None, search=None, limit=10, offset=0, db=db)

    assert result["total"] == 1
    assert result["items"] == mock_tasks


@pytest.mark.asyncio
async def test_get_tasks_list_no_data(mocker):
    db = AsyncMock(spec=AsyncSession)
    empty_result = AsyncMock(spec=Result)
    empty_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(side_effect=[AsyncMock(scalar_one=MagicMock(return_value=0)), empty_result])

    with pytest.raises(HTTPException) as exc:
        await get_tasks_list(status=None, search=None, limit=10, offset=0, db=db)

    assert exc.value.status_code == 204


@pytest.mark.asyncio
async def test_get_task_found(mocker):
    db = AsyncMock(spec=AsyncSession)
    task = Task(
        id=1,
        title="Test",
        description="Test desc",
        priority="MEDIUM",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        result="Не известно",
        error="Пусто",
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    db.execute.return_value = mock_result

    result = await get_task(task_id=1, db=db)
    assert result == task


@pytest.mark.asyncio
async def test_get_task_not_found(mocker):
    db = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await get_task(task_id=999, db=db)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_cancel_task_success(mocker):
    db = AsyncMock(spec=AsyncSession)

    task = Task(id=1, title="Test", description="desc", status=TaskStatus.PENDING)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    db.execute.return_value = mock_result

    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await cancel_task(task_id=1, db=db)

    assert result.status == TaskStatus.CANCELLED
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_task_not_found():
    db = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await cancel_task(task_id=123, db=db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Задача не найдена"
