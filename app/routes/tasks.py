from fastapi import APIRouter, Depends
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, PaginatedTasks, TaskStatus
from app.services.task_service import create_task, get_tasks_list, get_task, cancel_task

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.post(
    "/",
    response_model=TaskRead,
    summary="Создание задачи",
    description="Создает новую задачу и возвращает её данные.",
)
async def create(task: TaskCreate, db: AsyncSession = Depends(get_db)) -> Task:
    return await create_task(db, task)


@router.get(
    "/",
    response_model=PaginatedTasks,
    summary="Получение списка задач с фильтрацией и пагинацией",
    description="Возвращает список всех задач подходящи по фильтрам и пагинации",
)
async def get_tasks(task: Task = Depends(get_tasks_list)) -> Task:
    return task


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Получение информации о задаче",
    description="Возвращает данные по конкретной задаче",
)
async def get_task_info(task: Task = Depends(get_task)) -> Task:
    return task


@router.get(
    "/{task_id}/status",
    response_model=TaskStatus,
    summary="Получение статуса задачи",
    description="Возвращает статус конкретной задачи",
)
async def get_task_status(task: Task = Depends(get_task)) -> Column[str]:
    return task.status


@router.delete(
    "/{task_id}/",
    response_model=TaskRead,
    summary="Отмена задачи",
    description="Ставит статус CANCELED задаче",
)
async def cancelled_task(task: Task = Depends(cancel_task)) -> Task:
    return task
