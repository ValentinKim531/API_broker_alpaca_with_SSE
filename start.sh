#!/bin/bash
# Применяем миграции
python manage.py migrate

# Запускаем Uvicorn в фоновом режиме
poetry run uvicorn backend.asgi:application --host 0.0.0.0 --port 8000 &

# Ждем, пока не станет доступен
while ! nc -z localhost 8000; do
  sleep 1
done

# Запускаем SSE задачу
python manage.py start_sse_task

# Ждем завершения работы Uvicorn
wait
