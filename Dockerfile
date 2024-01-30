FROM python:3.11

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

RUN apt-get update && apt-get install -y netcat-openbsd
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

COPY . /app/


EXPOSE 8000

