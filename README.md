# City Helper AI Backend

[![CI](https://img.shields.io/github/actions/workflow/status/mirongit/city-helper-ai-backend/ci.yml?branch=main&label=CI&logo=github)](https://github.com/mirongit/city-helper-ai-backend/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

AI-powered backend service built with FastAPI for discovering places and planning routes in any city.

## 🚀 Quick Start

### Option 1: Local Development (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configuration (optional)
cp .env/.env.example .env/.env
# Edit .env/.env for secrets

# Run
python run.py
```

### Option 2: Docker (Production-like)

```bash
# With Docker Compose (recommended)
make docker-compose-up

# Or directly
make docker-build
make docker-run
```

Server will be available at `http://localhost:3001`

---

## 🔄 Git Workflow

**⚠️ IMPORTANT:** Never work directly in `main` branch!

### Proper Development Process:

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add something"

# 3. Push to GitHub
git push origin feature/your-feature

# 4. Create Pull Request on GitHub
# ✅ Automated checks will run

# 5. After all checks pass → Merge
```

**📚 More details:** [WORKFLOW.md](./WORKFLOW.md) — complete Git workflow guide

## 📁 Project Structure

```
city-helper-ai-backend/
├── .env/                    # 🔐 Environment variables (hidden folder)
│   └── .env.example         # Template (only file in git)
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

## 🔍 Health Check

Open in browser: http://localhost:3001/health

You should see:
```json
{"status": "ok", "timestamp": "..."}
```

## API Endpoints

### Health Check
- `GET /health` - Server health check

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Chat Sessions
- `GET /api/chat-sessions` - Get all sessions
- `POST /api/chat-sessions` - Create new session
- `PATCH /api/chat-sessions/{id}` - Update session
- `PATCH /api/chat-sessions/{id}/favorite` - Toggle favorite
- `DELETE /api/chat-sessions/{id}` - Delete session

### Chat
- `POST /api/chat/message` - Send message and get response

## 📚 API Documentation

After starting the server, interactive documentation is available at:
- **Swagger UI:** http://localhost:3001/docs
- **ReDoc:** http://localhost:3001/redoc

In Swagger UI you can test all endpoints directly from the browser!

## ⚙️ Alternative Launch

With uvicorn and auto-reload:
```bash
uvicorn main:app --reload --port 3001
```

## ✨ Features

- ✅ OpenAI GPT-4 integration for intelligent query understanding
- ✅ Google Places API (New) for real place data
- ✅ Google Maps integration for routes and directions
- ✅ Agent-based routing for context-aware conversations
- ✅ Smart place suggestions with retry logic
- ✅ Route optimization (greedy nearest-neighbor)
- ✅ City name normalization (Moscow/Moskva, Lisbon/Lisboa)
- ✅ **Structured Logging** with structlog + Logfire
- ✅ **Request Tracing** - each request has unique ID
- ✅ **Cloud Observability** (optional) via Logfire UI
- ✅ **Environment-specific Configs** - local/dev/staging/production
- ✅ **Secrets Management** with Pydantic SecretStr
- ✅ **Type-safe Configuration** with full validation
- ✅ **Comprehensive Integration Tests** with pytest
- ✅ **Pre-commit Hooks** (ruff, detect-secrets)

## 🔗 Frontend Integration

After starting backend, run frontend in real mode:

```bash
cd ../city-helper-ai
npm run dev:real
```

Frontend will automatically connect to backend on port 3001.

## 📖 Documentation

### Getting Started
- **[WORKFLOW.md](./WORKFLOW.md)** - 🔄 Git Workflow & Pull Requests (START HERE!)
- **[DOCKER.md](./DOCKER.md)** - 🐳 Docker Setup & Deployment
- **[GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)** - 🔑 Google OAuth Setup

### Development
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Project architecture
- **[TESTING.md](./TESTING.md)** - API testing guide
- **[AGENT_ROUTING_BLUEPRINT.md](./AGENT_ROUTING_BLUEPRINT.md)** - 🤖 Agent routing logic

### Configuration & Security
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Configuration and secrets
- **[SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md)** - Security checklist for .env
- **[LOGGING.md](./LOGGING.md)** - Logging setup

### CI/CD
- **[CI_CD.md](./CI_CD.md)** - GitHub Actions CI/CD
- **[BRANCH_PROTECTION_SETUP.md](./BRANCH_PROTECTION_SETUP.md)** - 🛡️ Main branch protection setup

## 🏗️ Architecture Principles

This project follows **Layered Architecture** with clear separation of concerns:

- **Routes** (`app/api/routes/`) - HTTP endpoints
- **Services** (`app/services/`) - Business logic
- **Schemas** (`app/schemas/`) - Data validation
- **Core** (`app/core/`) - Configuration
- **Utils** (`app/utils/`) - Helpers

See [ARCHITECTURE.md](./ARCHITECTURE.md) for details

## 🧪 Testing

Run tests:
```bash
# All tests
make test-all

# Unit tests only
make test-unit

# Integration tests only (requires OpenAI API key)
make test-integration

# With coverage report
make test-coverage
```

See [TESTING.md](./TESTING.md) for more details.

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for production deployment instructions.

Recommended:
- **Backend:** Railway.app
- **Frontend:** Vercel
