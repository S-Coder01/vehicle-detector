#!/bin/bash
set -e

# Проверяем, что переменные окружения установлены
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
    echo "ERROR: DB_HOST and DB_PORT must be set"
    exit 1
fi

# Ждём, пока PostgreSQL запустится
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "PostgreSQL started"

# Применяем миграции
alembic upgrade head

# Запускаем uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000