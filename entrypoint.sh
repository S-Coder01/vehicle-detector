#!/bin/bash
set -e

# Ждём, пока PostgreSQL запустится
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Применяем миграции
alembic upgrade head

# Запускаем uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000