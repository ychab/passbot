FROM python:3.11-slim-buster

WORKDIR /app

COPY passbot /app/passbot
COPY requirements /app/requirements
COPY alembic.ini scrapy.cfg /app/

RUN pip install --upgrade pip
RUN pip install -r requirements/prod.txt

CMD ["sleep", "infinity"]
