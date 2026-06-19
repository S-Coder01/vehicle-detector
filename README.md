# Детекция транспортных средств (VisDrone + YOLO)

Веб-приложение для детекции транспортных средств на изображениях с дронов.  
Пользователь может выбрать одну из двух моделей YOLO (быструю или точную), загрузить изображение и получить результат с выделенными объектами. Приложение хранит историю запросов, поддерживает авторизацию, фильтрацию классов, просмотр истории и управление ею.

## Модели и качество

Модели обучены на датасете **VisDrone2019** (только классы транспорта: `car`, `van`, `truck`, `awning-tricycle`, `bus`, `motor`).  
Для обучения использовалась библиотека **Ultralytics YOLO26** (версия 26).

| Модель | Тип | mAP50 (на валидации) | Размер весов | Скорость (относительная) |
|--------|-----|---------------------|--------------|---------------------------|
| **yolo26n_fast** | Nano (быстрая) | **0.40** | ~5 МБ | быстрее |
| **yolo26l_accurate** | Large (точная) | **0.61** | ~52 МБ | медленнее |

> Примечание: использовалась архитектура YOLO26.

## Стек технологий

- **Бэкенд**: FastAPI, SQLAlchemy, Alembic, PostgreSQL, JWT-аутентификация
- **Фронтенд**: Streamlit (интерактивный интерфейс)
- **ML**: Ultralytics YOLO (PyTorch), OpenCV/Pillow для обработки изображений
- **Деплой**: Docker, Docker Compose

## Установка и запуск

### Локальный запуск (без Docker)

1. Клонируйте репозиторий:
   ```bash
    git clone https://github.com/S-Coder01/vehicle-detector.git
    cd vehicle-detector
   ```

2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` на основе `.env.example` и заполните его (пример):
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASS=your_password
   DB_NAME=vehicle_detector_db
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

5. Убедитесь, что PostgreSQL запущен и создана база данных с указанным именем.

6. Примените миграции Alembic:
   ```bash
   alembic upgrade head
   ```

7. Запустите бэкенд (в одном терминале):
   ```bash
   uvicorn main:app --reload
   ```

8. Запустите фронтенд (в другом терминале):
   ```bash
   streamlit run frontend/app.py --server.headless true
   ```

9. Откройте браузер: `http://localhost:8501`

### Запуск в Docker (рекомендуется)

1. Убедитесь, что у вас установлены Docker и Docker Compose.

2. Скопируйте файл `.env.example` в `.env` и заполните его (для Docker `DB_HOST` можно оставить `localhost`, но он будет переопределён).

3. Выполните сборку и запуск:
   ```bash
   docker-compose up --build -d
   ```

4. После запуска приложение будет доступно:
   - Фронтенд: `http://localhost:8501`
   - Бэкенд API: `http://localhost:8000`
   - Swagger документация: `http://localhost:8000/docs`

5. Остановка:
   ```bash
   docker-compose down
   ```

## 📁 Структура проекта

```text
.
├── app/                    # Бэкенд (FastAPI)
│   ├── api/                # Роутеры, схемы Pydantic
│   ├── core/               # Конфигурация, безопасность
│   ├── db/                 # Модели SQLAlchemy, подключение к БД
│   ├── services/           # Бизнес-логика (детекция, хранение файлов)
│   └── __init__.py
├── frontend/               # Фронтенд (Streamlit)
│   ├── components/         # Страницы (auth, detect, history)
│   ├── __init__.py
│   ├── api_client.py       # Клиент для общения с бэкендом
│   ├── app.py              # Главный файл Streamlit
│   └── utils.py            # Вспомогательные функции (отрисовка bbox)
├── migrations/             # Миграции Alembic
├── models/                 # Файлы весов моделей YOLO
│   ├── yolo26l_accurate.pt
│   └── yolo26n_fast.pt
├── tests/                  # Тесты (pytest)
├── uploads/                # Папка для загруженных пользователями изображений (создаётся автоматически)
├── .dockerignore
├── .env.example
├── .gitattributes
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── entrypoint.sh
├── LICENSE
├── main.py
├── pytest.ini
├── README.md
├── requirements-backend.txt
├── requirements-frontend.txt
└── requirements.txt
```

## Тестирование

Перед запуском тестов убедитесь, что создана тестовая база данных PostgreSQL:

- Имя БД: `test_vehicle_detector_db`
- Пользователь: `test_user`
- Пароль: `test_pass`
- Хост: `localhost` (или `db` при использовании Docker)

Тесты используют отдельную БД и не влияют на основную базу приложения. После каждого теста таблицы очищаются.

Запуск тестов (локально, с тестовой БД):

```bash
pytest tests/ -v
```

Все тесты должны проходить (20 passed).

## Возможности приложения

- **Регистрация и вход** с JWT-токеном.
- **Выбор модели** (быстрая или точная) и порога уверенности.
- **Загрузка изображения** и получение результата детекции с bbox.
- **Настройка отображения**:
  - Фильтрация по классам.
  - Показ названий классов и/или номеров.
  - Компактная легенда классов.
- **История запросов**:
  - Просмотр всех записей с датой, моделью.
  - Просмотр деталей записи (изображение с bbox и исходное).
  - Удаление конкретной записи или очистка всей истории.
- **Выход из аккаунта**.

## Примечания

- Для работы с кириллицей в Docker в контейнере устанавливаются шрифты `fonts-dejavu-core` и `fonts-liberation`. На локальной машине шрифты определяются автоматически (Windows, Linux, macOS).
- Модели загружаются в память при первом запросе и кэшируются для ускорения работы.
- Файлы пользователей сохраняются на сервере в папке `uploads/`, пути к ним хранятся в БД.

## Лицензия

MIT License (см. файл `LICENSE`).

## Автор

Артём Мордвинов – amordvinov856@gmail.com – [\[ссылка на GitHub\]](https://github.com/S-Coder01)