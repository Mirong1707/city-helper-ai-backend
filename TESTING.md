# Testing

Testing guide for City Helper AI Backend.

## Automated Tests

### Quick Start

```bash
# Run unit tests only (fast, no API calls)
make test-unit

# Run integration tests (includes OpenAI API calls, ~$0.03)
make test-integration

# Run all tests
make test-all
```

### Full Documentation

- **[tests/README.md](tests/README.md)** - Complete testing guide
- **[AGENT_ROUTING_BLUEPRINT.md](AGENT_ROUTING_BLUEPRINT.md)** - Agent routing decision tree with Mermaid diagram
- **[TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md)** - Quick reference for common testing tasks

### Test Coverage

```
✅ Agent Routing (12 tests)
   ├─ NEW REQUEST detection (2 tests)
   ├─ ADD operations (2 tests)
   ├─ REMOVE operations (1 test)
   ├─ REPLACE_LAST operations (1 test)
   ├─ REPLACE_ALL operations (2 tests)
   ├─ REFINE operations (1 test)
   ├─ Edge cases (2 tests)
   └─ Reasoning quality (1 test)

Time: ~53s | Cost: ~$0.03
```

## Manual Testing

### Quick Health Check

```bash
# Запуск
python run.py

# Health check
curl http://localhost:3001/health

# Docs
open http://localhost:3001/docs
```

## Тестирование через cURL

### Auth

```bash
# Register
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "pass123"}'  # pragma: allowlist secret

# Login
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "pass123"}'  # pragma: allowlist secret
```

### Chat

```bash
# Send message
curl -X POST http://localhost:3001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Список дел после переезда"}'
```

Ответ - JSON с чек-листом (7 пунктов, включая питона 🐍).

```bash
curl -X POST http://localhost:3001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Маршрут на 2 часа"}'
```

Ответ - JSON с картой (4 точки, включая Python Cafe).

### Chat Sessions

```bash
# Create
curl -X POST http://localhost:3001/api/chat-sessions \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "messages": [], "workspaceContent": {"type": "empty"}}'

# Get all
curl http://localhost:3001/api/chat-sessions

# Update
curl -X PATCH http://localhost:3001/api/chat-sessions/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"messages": [], "workspaceContent": {"type": "empty"}}'

# Delete
curl -X DELETE http://localhost:3001/api/chat-sessions/SESSION_ID
```

## С фронтендом

```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Frontend
cd ../city-helper-ai
npm run dev:real
```

Откройте http://localhost:5173 и проверьте в консоли:
- `🔧 API Mode: real`

## Troubleshooting

**Port busy:**
```bash
lsof -i :3001
kill -9 PID
```

**CORS errors:**
- Проверьте что фронтенд запущен через `npm run dev:real`
- Очистите кэш браузера

**Backend not responding:**
- Проверьте виртуальное окружение активировано
- `pip install -r requirements.txt`
- Python 3.8+
