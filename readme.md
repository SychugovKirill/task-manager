# Task Manager

API сервис для работы с задачами

## Установка

- `git clone git@github.com:SychugovKirill/task-manager.git`
- `cd task-manager`

После скачивания репозитория надо сделать:

- `make run` или `cp env.local .env && docker-compose up --build`
- `make migrate` или `docker exec -it cism-web-1 alembic upgrade head`

## Тесты

- `make test` или `docker exec -it cism-web-1 pytest --cov=app --cov-report=term-missing`

## API-endpoints

- **POST** /api/v1/tasks/ - Cоздание задачи
- **GET** /api/v1/tasks/ - Получение списка задач
- **GET** /api/v1/tasks/{task_id} - Возвращает данные по конкретной задаче
- **GET** /api/v1/tasks/{task_id}/status - Возвращает статус конкретной задачи
- **DELETE** /api/v1/tasks/ - Ставит статус CANCELED задаче
