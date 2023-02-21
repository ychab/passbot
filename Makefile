.DEFAULT_GOAL := help
.PHONY: help
.EXPORT_ALL_VARIABLES:

CURRENT_MAKEFILE := $(lastword $(MAKEFILE_LIST))

include .env

help:
	@LC_ALL=C $(MAKE) -pRrq -f $(CURRENT_MAKEFILE) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

pre:
	git add .
	pre-commit run -a

lint:
	pylama passbot tests
	isort --diff --check passbot tests
	mypy passbot tests

clean:
	isort passbot tests

deps:
	poetry show --outdated

poetry:
	poetry update
	poetry lock
	poetry export -f requirements.txt --only main -o requirements/prod.txt
	poetry export -f requirements.txt --with test -o requirements/test.txt
	poetry export -f requirements.txt --with test,dev -o requirements/dev.txt

test:
	tox -e report

db_drop:
	docker exec -it passbot_postgres psql -U ${DB_USER} -c "DROP DATABASE ${DB_NAME};"

db_create:
	docker exec -it passbot_postgres psql -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};"

db_shell:
	docker exec -it passbot_postgres psql -U ${DB_USER} -d ${DB_NAME}

db_upgrade:
	alembic upgrade head

db_downgrade:
	alembic downgrade base

db_revision:
	alembic revision --autogenerate

up:
	docker compose up -d

down:
	docker compose down

ps:
	docker compose ps --all

restart:
	docker compose restart

reset: db_drop db_create
