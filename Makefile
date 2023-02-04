all:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

help: all

pre:
	git add .
	pre-commit run -a

lint:
	pylama passbot
	isort --diff --check passbot

deps:
	poetry show --outdated

poetry:
	poetry update
	poetry lock
	poetry export -f requirements.txt --only main -o requirements/prod.txt
	poetry export -f requirements.txt --with test -o requirements/test.txt
	poetry export -f requirements.txt --with test,dev -o requirements/dev.txt

drop_db:
	psql -U postgres -c "DROP DATABASE passbot"

create_db_user:
	psql -U postgres -c "CREATE USER bot WITH encrypted password 'bot' SUPERUSER"

create_db:
	psql -U postgres -c "CREATE DATABASE passbot OWNER bot"

db_upgrade:
	alembic upgrade head

db_downgrade:
	alembic downgrade base

db_revision:
	alembic revision --autogenerate

reset: drop_db create_db
