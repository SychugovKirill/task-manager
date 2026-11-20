run:
	cp env.local .env
	docker-compose up --build

migrate:
	docker exec -it cism-web-1 alembic upgrade head

bash:
	docker exec -it cism-web-1 /bin/bash

test:
	docker exec -it cism-web-1 pytest --cov=app --cov-report=term-missing
