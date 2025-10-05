# Architecture

Layered Architecture с разделением ответственности.

## Структура

```
app/
├── api/routes/      # HTTP endpoints
├── services/        # Business logic
├── schemas/         # Pydantic models (validation)
├── core/            # Config, logging
└── utils/           # Helpers
```

## Слои

### API Layer (`api/routes/`)

**Ответственность:** HTTP запросы/ответы

- Валидация входных данных
- Маршрутизация
- Форматирование ответов
- HTTP errors

**Принцип:** Тонкие контроллеры, логика в services.

### Service Layer (`services/`)

**Ответственность:** Бизнес-логика

- Основная логика приложения
- Работа с данными
- Обработка бизнес-правил

**Принцип:** Независимость от HTTP, тестируемость.

### Schema Layer (`schemas/`)

**Ответственность:** Data Transfer Objects

- Валидация данных (Pydantic)
- Сериализация/десериализация
- API документация

### Core Layer (`core/`)

**Ответственность:** Конфигурация

- Settings (окружения, секреты)
- Logging setup
- Constants

### Utils Layer (`utils/`)

**Ответственность:** Вспомогательные функции

- Генераторы данных
- Хелперы

## Поток данных

```
HTTP Request
    ↓
API Route (валидация)
    ↓
Service (бизнес-логика)
    ↓
Service (обработка)
    ↓
API Route (форматирование)
    ↓
HTTP Response
```

## Принципы

1. **Separation of Concerns** - каждый слой свою задачу
2. **Dependency Injection** - services как синглтоны
3. **Single Responsibility** - один модуль = одна задача
4. **Type Safety** - type hints везде

## Добавление endpoint

1. Создать schema в `schemas/`
2. Создать/использовать service в `services/`
3. Создать route в `api/routes/`
4. Зарегистрировать в `main.py`

```python
# 1. Schema
class MyRequest(BaseModel):
    data: str

# 2. Service method
class MyService:
    def process(self, data: str) -> str:
        return data.upper()

# 3. Route
@router.post("/endpoint")
async def my_endpoint(req: MyRequest):
    result = my_service.process(req.data)
    return {"result": result}

# 4. Register in main.py
app.include_router(my_router)
```

## Best Practices

**Routes:**
- Тонкие контроллеры
- Только HTTP concerns
- Делегируйте в services

**Services:**
- Без HTTP зависимостей
- Тестируемые
- Чистая бизнес-логика

**Schemas:**
- Immutable DTOs
- Type-safe
- Clear contracts
