# Architecture

Layered Architecture with clear separation of concerns.

## Structure

```
app/
├── api/routes/      # HTTP endpoints
├── services/        # Business logic
├── schemas/         # Pydantic models (validation)
├── core/            # Config, logging
└── utils/           # Helpers
```

## Layers

### API Layer (`api/routes/`)

**Responsibility:** HTTP requests/responses

- Input data validation
- Routing
- Response formatting
- HTTP errors

**Principle:** Thin controllers, logic in services.

### Service Layer (`services/`)

**Responsibility:** Business logic

- Core application logic
- Data processing
- Business rules handling

**Principle:** HTTP-independent, testable.

### Schema Layer (`schemas/`)

**Responsibility:** Data Transfer Objects

- Data validation (Pydantic)
- Serialization/deserialization
- API documentation

### Core Layer (`core/`)

**Responsibility:** Configuration

- Settings (environments, secrets)
- Logging setup
- Constants

### Utils Layer (`utils/`)

**Responsibility:** Helper functions

- Data generators
- Helpers

## Data Flow

```
HTTP Request
    ↓
API Route (validation)
    ↓
Service (business logic)
    ↓
Service (processing)
    ↓
API Route (formatting)
    ↓
HTTP Response
```

## Principles

1. **Separation of Concerns** - each layer has its own task
2. **Dependency Injection** - services as singletons
3. **Single Responsibility** - one module = one task
4. **Type Safety** - type hints everywhere

## Adding an Endpoint

1. Create schema in `schemas/`
2. Create/use service in `services/`
3. Create route in `api/routes/`
4. Register in `main.py`

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
- Thin controllers
- Only HTTP concerns
- Delegate to services

**Services:**
- No HTTP dependencies
- Testable
- Pure business logic

**Schemas:**
- Immutable DTOs
- Type-safe
- Clear contracts
