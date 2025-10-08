# Logging

Structured logging with structlog + Logfire.

## Setup

```bash
# .env/.env
SECRET_LOGFIRE_TOKEN=your_token  # Optional
```

Without token - only local JSON logs.
With token - logs + traces in Logfire UI.

## Usage

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

## Auto-logged Events

- HTTP requests (method, path, status, request_id)
- App startup/shutdown
- Errors and exceptions
- Client IP
- Execution time (via Logfire)

## Log Format

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

## Request Context

Each request automatically has:
- `request_id` - unique ID
- `method` - HTTP method
- `path` - path
- `client_ip` - client IP

Available in all logs within request handling.

## Log Levels

```bash
APP_LOG_LEVEL=DEBUG   # Development
APP_LOG_LEVEL=INFO    # Default
APP_LOG_LEVEL=WARNING # Production
```

## Best Practices

**DO:**
- Use structured fields
- Add context (user_id, task_id)
- Use `.exception()` for errors

**DON'T:**
- DON'T log passwords, tokens, keys
- DON'T log personal data
- DON'T use string formatting in event

```python
# Good
logger.info("user_login", user_id="123", success=True)

# Bad
logger.info(f"User {user_id} logged in")  # Not structured
logger.info("login", password=pwd)         # Secret in logs!
```

## Logfire UI

With token available:
- Field filtering
- Request traces
- Performance metrics
- Search by request_id

Register: https://logfire.pydantic.dev
