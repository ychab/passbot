FROM python:3.11-slim-buster

WORKDIR /code

COPY requirements/dev.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["sleep", "infinity"]
