# Logging

Structured logging с structlog + Logfire.

## Setup

```bash
# .env/.env
SECRET_LOGFIRE_TOKEN=your_token  # Опционально
```

Без токена - только локальные JSON логи.
С токеном - логи + трейсы в Logfire UI.

## Использование

```python
import structlog

logger = structlog.get_logger()

# Structured log
logger.info("event_name", user_id="123", action="purchase")

# With exception
try:
    risky()
except Exception:
    logger.exception("failed", task_id="abc")
```

## Автоматически логируется

- HTTP запросы (метод, путь, статус, request_id)
- Старт/остановка приложения
- Ошибки и исключения
- IP клиента
- Время выполнения (через Logfire)

## Формат логов

```json
{
  "event": "request_completed",
  "level": "info",
  "timestamp": "2025-10-05T14:23:45.123Z",
  "request_id": "550e8400-...",
  "method": "POST",
  "path": "/api/chat/message",
  "status_code": 200
}
```

## Контекст запроса

Каждый запрос автоматически имеет:
- `request_id` - уникальный ID
- `method` - HTTP метод
- `path` - путь
- `client_ip` - IP клиента

Доступны во всех логах внутри обработки запроса.

## Уровни

```bash
APP_LOG_LEVEL=DEBUG   # Development
APP_LOG_LEVEL=INFO    # Default
APP_LOG_LEVEL=WARNING # Production
```

## Best Practices

**DO:**
- Используйте структурированные поля
- Добавляйте контекст (user_id, task_id)
- Используйте `.exception()` для ошибок

**DON'T:**
- НЕ логируйте пароли, токены, ключи
- НЕ логируйте персональные данные
- НЕ используйте string formatting в event

```python
# Good
logger.info("user_login", user_id="123", success=True)

# Bad
logger.info(f"User {user_id} logged in")  # Не структурировано
logger.info("login", password=pwd)         # Секрет в логах!
```

## Logfire UI

При наличии токена доступны:
- Фильтрация по полям
- Трейсы запросов
- Метрики производительности
- Поиск по request_id

Регистрация: https://logfire.pydantic.dev
