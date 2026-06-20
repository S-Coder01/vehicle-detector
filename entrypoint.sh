#!/bin/bash
set -e

# Применяем миграции
alembic upgrade head

# Запускаем uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000