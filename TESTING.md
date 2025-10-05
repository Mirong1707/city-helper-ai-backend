# Testing

Тестирование backend API.

## Быстрая проверка

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
