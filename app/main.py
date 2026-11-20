from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import tasks
from app.workers import rabbitmq


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq.init_rabbitmq()
    yield
    await rabbitmq.close_rabbitmq()


app = FastAPI(
    lifespan=lifespan,
    title="Task Manager",
    description="Асинхронный API для управления задачами",
)


app.include_router(tasks.router)
