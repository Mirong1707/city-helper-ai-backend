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
# Start server
python run.py

# Health check
curl http://localhost:3001/health

# API docs
open http://localhost:3001/docs
```

## Testing with cURL

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
  -d '{"message": "Things to do after moving"}'
```

Response - JSON with checklist (7 items, including the python 🐍).

```bash
curl -X POST http://localhost:3001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "2 hour route"}'
```

Response - JSON with map (4 points, including Python Cafe).

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

## With Frontend

```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Frontend
cd ../city-helper-ai
npm run dev:real
```

Open http://localhost:5173 and check in console:
- `🔧 API Mode: real`

## Troubleshooting

**Port busy:**
```bash
lsof -i :3001
kill -9 PID
```

**CORS errors:**
- Check that frontend is running via `npm run dev:real`
- Clear browser cache

**Backend not responding:**
- Check virtual environment is activated
- `pip install -r requirements.txt`
- Python 3.8+
