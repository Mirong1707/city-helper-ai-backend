# City Helper AI Backend

[![CI](https://img.shields.io/github/actions/workflow/status/mirongit/city-helper-ai-backend/ci.yml?branch=main&label=CI&logo=github)](https://github.com/mirongit/city-helper-ai-backend/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

Mock backend server на FastAPI для разработки и тестирования фронтенда.

## 🚀 Быстрый старт

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активация
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Зависимости
pip install -r requirements.txt

# Конфигурация (опционально)
cp .env/.env.example .env/.env
# Отредактируйте .env/.env для секретов

# Запуск
python run.py
```

Сервер запустится на `http://localhost:3001`

## 📁 Структура проекта

```
city-helper-ai-backend/
├── .env/                    # 🔐 Environment variables (скрытая папка)
│   └── .env.example         # Template (единственный файл в git)
├── app/
│   ├── main.py              # FastAPI app
│   ├── api/routes/          # API endpoints
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── chat_sessions.py
│   │   └── health.py
│   ├── core/
│   │   ├── config/          # Configuration system
│   │   │   ├── base.py
│   │   │   ├── environments.py
│   │   │   ├── secrets.py
│   │   │   └── loader.py
│   │   └── logging_setup.py
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── run.py                   # Entry point
├── requirements.txt
└── [documentation]
```

## 🔍 Проверка работы

Откройте в браузере: http://localhost:3001/health

Должны увидеть:
```json
{"status": "ok", "timestamp": "..."}
```

## API Endpoints

### Health Check
- `GET /health` - Проверка состояния сервера

### Аутентификация
- `POST /api/auth/login` - Вход
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/logout` - Выход
- `GET /api/auth/me` - Получить текущего пользователя

### Сессии чата
- `GET /api/chat-sessions` - Получить все сессии
- `POST /api/chat-sessions` - Создать новую сессию
- `PATCH /api/chat-sessions/{id}` - Обновить сессию
- `PATCH /api/chat-sessions/{id}/favorite` - Переключить избранное
- `DELETE /api/chat-sessions/{id}` - Удалить сессию

### Чат
- `POST /api/chat/message` - Отправить сообщение и получить ответ

## 📚 Документация API

После запуска сервера интерактивная документация доступна по адресам:
- **Swagger UI:** http://localhost:3001/docs
- **ReDoc:** http://localhost:3001/redoc

В Swagger UI вы можете тестировать все эндпоинты прямо из браузера!

## ⚙️ Альтернативный запуск

Через uvicorn с авто-перезагрузкой:
```bash
uvicorn main:app --reload --port 3001
```

## ✨ Особенности

- ✅ Все данные хранятся в памяти (перезапуск сервера сбрасывает данные)
- ✅ Имитация задержек сети для реалистичного тестирования
- ✅ Mock-ответы генерируются на основе ключевых слов в сообщениях
- ✅ CORS настроен для работы с фронтендом на любом порту
- ✅ Автоматическая интерактивная документация (Swagger/ReDoc)
- ✅ **Structured Logging** с structlog + Logfire
- ✅ **Request Tracing** - каждый запрос имеет уникальный ID
- ✅ **Cloud Observability** (опционально) через Logfire UI
- ✅ **Environment-specific Configs** - local/dev/staging/production
- ✅ **Secrets Management** с Pydantic SecretStr
- ✅ **Type-safe Configuration** с полной валидацией

## 🔗 Интеграция с фронтендом

После запуска бэкенда, запустите фронтенд в real режиме:

```bash
cd ../city-helper-ai
npm run dev:real
```

Фронтенд автоматически подключится к бэкенду на порту 3001.

## 📖 Документация

- **[LOGFIRE_SETUP.md](./LOGFIRE_SETUP.md)** - ⚡ Быстрая настройка Logfire
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Конфигурация и секреты
- **[SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md)** - Security checklist для .env
- **[LOGGING.md](./LOGGING.md)** - Логирование
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Архитектура проекта
- **[TESTING.md](./TESTING.md)** - Тестирование API
- **[PRE_COMMIT.md](./PRE_COMMIT.md)** - Pre-commit Hooks
- **[CI_CD.md](./CI_CD.md)** - GitHub Actions CI/CD

## 🏗️ Принципы архитектуры

Проект следует **Layered Architecture** с четким разделением ответственности:

- **Routes** (`app/api/routes/`) - HTTP endpoints
- **Services** (`app/services/`) - Бизнес-логика
- **Schemas** (`app/schemas/`) - Data validation
- **Core** (`app/core/`) - Configuration
- **Utils** (`app/utils/`) - Helpers

Подробнее см. [ARCHITECTURE.md](./ARCHITECTURE.md)
