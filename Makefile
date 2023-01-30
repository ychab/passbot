all:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

help: all

check_deps:
	poetry show --outdated

poetry:
	poetry update
	poetry lock
	poetry export -f requirements.txt --only main -o requirements/prod.txt
	poetry export -f requirements.txt --with test -o requirements/test.txt
	poetry export -f requirements.txt --with test,dev -o requirements/dev.txt

drop_db:
	psql -U postgres -c "DROP DATABASE passport"

create_db_user:
	psql -U postgres -c "CREATE USER bot WITH encrypted password 'bot' SUPERUSER"

create_db:
	psql -U postgres -c "CREATE DATABASE passport OWNER bot"

lint:
	isort passport
	pylama passport

reset: drop_db create_db
