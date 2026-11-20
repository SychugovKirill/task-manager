from datetime import datetime
import asyncio, json, aio_pika
from app.db.session import async_session
from app.db.models.task import Task, TaskStatus
from app.workers import rabbitmq


async def process_task(task_id: int):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            print(f"Задача {task_id} не найдена.")
            return

        task.status = TaskStatus.IN_PROGRESS
        await session.commit()
        print(f"Процесс задачи {task_id}...")

        await asyncio.sleep(5)  # Имитация обработки

        task.status = TaskStatus.COMPLETED
        task.started_at = datetime.now() if not task.started_at else task.started_at
        await session.commit()
        print(f"Задача {task_id} готова.")


async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            task_id = payload["task_id"]
            await process_task(task_id)
        except Exception as e:
            print(f"Ошибка процесса: {e}")


async def main():
    await rabbitmq.init_rabbitmq()
    queue = await rabbitmq.get_queue()
    await queue.consume(on_message)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
