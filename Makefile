.DEFAULT_GOAL := help
.PHONY: help
.EXPORT_ALL_VARIABLES:

CURRENT_MAKEFILE := $(lastword $(MAKEFILE_LIST))

include .env

help:
	@LC_ALL=C $(MAKE) -pRrq -f $(CURRENT_MAKEFILE) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

pre:
	pre-commit run -a

lint:
	pylama passbot tests
	isort --diff --check passbot tests
	mypy passbot tests


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


db_shell:
	docker exec -it passbot_postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

db_upgrade:
	alembic upgrade head

db_downgrade:
	alembic downgrade base

db_revision:
	alembic revision --autogenerate


app_shell:
	docker exec -it passbot_crawlers /bin/bash


up:
	docker compose up -d

down:
	docker compose down

ps:
	docker compose ps --all

log:
	docker compose logs passbot -f

crawl:
	docker compose exec passbot scrapy crawl vitemonpasseport_44
	docker compose exec passbot scrapy crawl saintherblainhotel

restart:
	docker compose restart


prod_ps:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml ps --all

prod_up:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod_down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down

prod_cron:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -d passbot scrapy crawl vitemonpasseport_44
	docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -d passbot scrapy crawl saintherblainhotel


prune:
	docker image prune --force
	docker volume prune --force

reset: down prune up
