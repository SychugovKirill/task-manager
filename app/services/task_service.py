from fastapi import Depends, HTTPException, Path, Query
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.task import Task, TaskStatus
from app.db.session import get_db
from app.schemas.task import TaskCreate
from app.workers import rabbitmq

from typing import Optional

import aio_pika, json


async def create_task(db: AsyncSession, task_data: TaskCreate) -> Task:
    task = Task(**task_data.model_dump())
    task.status = TaskStatus.PENDING
    db.add(task)
    await db.commit()
    await db.refresh(task)

    message_body = json.dumps({"task_id": task.id}).encode()

    message = aio_pika.Message(body=message_body, delivery_mode=2, priority=task.priority.to_rabbitmq_priority())

    channel = await rabbitmq.get_channel()
    await channel.default_exchange.publish(message, routing_key="task_queue")

    return task


async def get_tasks_list(
    status: Optional[TaskStatus] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    base_query = select(Task)

    if status is not None:
        base_query = base_query.where(Task.status == status)
    else:
        base_query = base_query.where(Task.status == "COMPLETED")

    if search:
        base_query = base_query.where(or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%")))

    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    paginated_query = base_query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(paginated_query)
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(status_code=204, detail="Нет контента")

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": tasks,
    }


async def get_task(
    task_id: int = Path(..., gt=0, description="ID задачи должен быть > 0"),
    db: AsyncSession = Depends(get_db),
) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return task


async def cancel_task(
    task_id: int = Path(..., gt=0, description="ID задачи должен быть > 0"),
    db: AsyncSession = Depends(get_db),
) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.status = TaskStatus.CANCELLED
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task
