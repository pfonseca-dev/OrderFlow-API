dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy app

migration:
	alembic revision --autogenerate -m "$(m)"

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1
