.PHONY: install run test lint format migrate sync docker-build docker-up docker-down

install:
	pip install -e ".[dev]"

run:
	uvicorn tickethub.main:app --app-dir src --reload

test:
	pytest

lint:
	ruff check src tests

format:
	ruff format src tests

migrate:
	python -m alembic upgrade head

sync:
	python -m tickethub.commands.sync

docker-build:
	docker build -t tickethub-api .

docker-up:
	docker compose up --build

docker-down:
	docker compose down