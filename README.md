# Livars 

Шаблон-сайт на базе FastAPI + PostgreSQL. Реализована базовая система авторизации и JWT-токенизация с использованием классического стека.

- `FastAPI`
- `SQLAlchemy + PostgreSQL`
- `Pydantic`
- `Jinja2`
- `PyJWT`

## Структура проекта

- `src/database.py` — Настройка подключения к БД и описание моделей SQLAlchemy.
- `src/auth.py` — Логика хеширования паролей и взаимодействия с БД для пользователей.
- `src/token.py` — Генерация и валидация JWT-токенов.
- `routes/` — Определение API эндпоинтов (auth, mainpage, posts).
- `templates/` — HTML шаблоны (Jinja2).

В корне проекта присутствует *dockerfile* и *docker-compose.yml* для развертывания контейнеров.

## Установка и запуск


### 1. Клонирование
```
git clone https://github.com/FaggyDiman/livars
cd livars
```
### 2. Установка зависимостей
```
pip install -r requirements.txt
```

### 3. Запуск
```
docker compose build
```

## API Эндпоинты

- `POST /register` — Регистрация нового пользователя.
- `POST /login` — Авторизация и получение кук с токенами.
- `POST /logout` — Удаление токенов из кук.
- `GET /` — Главная страница.