# Docker Setup

Production-ready Docker configuration with development workflow support.

## Quick Start

### Option 1: Docker only (simple)
```bash
# Build
make docker-build

# Run
make docker-run
```

### Option 2: Docker Compose (recommended)
```bash
# Start all services
make docker-compose-up

# View logs
make docker-compose-logs

# Stop
make docker-compose-down
```

Server will be available at `http://localhost:3001`

## Development Workflows

### 🚀 RECOMMENDED: Local Development (fastest)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Pros:**
- ⚡ Fastest (no Docker overhead)
- 🔄 Instant hot reload
- 🐛 Easy debugging
- 💻 Native IDE integration

**Use when:** Daily development, debugging

### 🐳 Docker Development (prod-like)
```bash
docker-compose up
```

**Pros:**
- 🎯 Exactly like production
- 📦 Isolated environment
- 🗄️ Easy DB/Redis setup (uncomment in docker-compose.yml)
- 👥 Consistent across team

**Use when:** Testing deployment, working with DB/Redis

## Docker Commands

### Build & Run
```bash
# Build image
docker build -t city-helper-backend:latest .

# Run container
docker run -p 3001:3001 \
  --env-file .env/.env \
  city-helper-backend:latest
```

### Docker Compose
```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Debugging
```bash
# Enter running container
docker exec -it city-helper-backend bash

# Check container health
docker ps
docker inspect city-helper-backend

# View container logs
docker logs -f city-helper-backend
```

## Configuration

### Environment Variables

Set in `.env/.env` or pass to Docker:

```bash
docker run -p 3001:3001 \
  -e APP_ENV=production \
  -e APP_PORT=3001 \
  -e SECRET_LOGFIRE_TOKEN=your_token \
  city-helper-backend:latest
```

### Volumes

Mounted in docker-compose.yml:
- `./app:/app/app` - Code (for hot reload)
- `./.env/.env:/app/.env/.env` - Secrets

## Adding Services

### PostgreSQL

Uncomment in `docker-compose.yml`:
```yaml
postgres:
  image: postgres:16-alpine
  # ... configuration
```

Then:
```bash
docker-compose up -d postgres
```

Connection string: `postgresql://cityhelper:changeme@postgres:5432/cityhelper`  # pragma: allowlist secret

### Redis

Uncomment in `docker-compose.yml`:
```yaml
redis:
  image: redis:7-alpine
  # ... configuration
```

Connection: `redis://redis:6379`

## Image Optimization

### Multi-stage Build
Dockerfile uses multi-stage build:
- **Builder stage:** Installs dependencies
- **Final stage:** Minimal runtime (python:3.13-slim)

Result: ~150MB image (vs ~1GB with standard build)

### .dockerignore
Excludes unnecessary files:
- Development files (venv, .git, __pycache__)
- Documentation (*.md except README)
- CI/CD configs

## Production Deployment

### Build for Production
```bash
docker build -t city-helper-backend:v1.0.0 .
docker tag city-helper-backend:v1.0.0 your-registry/city-helper-backend:latest
docker push your-registry/city-helper-backend:latest
```

### Environment-specific Builds
```bash
# Development
docker build -t city-helper-backend:dev --build-arg ENV=development .

# Production
docker build -t city-helper-backend:prod --build-arg ENV=production .
```

### Health Checks

Container has built-in health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:3001/health')"
```

Check status:
```bash
docker inspect --format='{{.State.Health.Status}}' city-helper-backend
```

## CI/CD Integration

GitHub Actions automatically:
- Builds Docker image
- Tests container startup
- Pushes to registry (when configured)

See `.github/workflows/ci.yml`

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs city-helper-backend

# Check with verbose output
docker run --rm city-helper-backend python run.py
```

### Port already in use
```bash
# Find process
lsof -ti:3001 | xargs kill -9

# Or use different port
docker run -p 3002:3001 city-helper-backend
```

### Image too large
```bash
# Check image size
docker images city-helper-backend

# Remove unused layers
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t city-helper-backend .
```

### Hot reload not working
Ensure volume is mounted:
```yaml
volumes:
  - ./app:/app/app:ro  # :ro for read-only
```

## Best Practices

✅ **DO:**
- Use multi-stage builds
- Run as non-root user (appuser)
- Use .dockerignore
- Set health checks
- Use specific Python version (3.13-slim)
- Mount volumes for development
- Use networks for service isolation

❌ **DON'T:**
- Don't use `latest` tag in production
- Don't include secrets in image
- Don't run as root
- Don't use `python:3.13` (too large)
- Don't copy venv into image
- Don't skip .dockerignore

## Comparison: Local vs Docker

| Feature | Local (venv) | Docker | Docker Compose |
|---------|-------------|--------|----------------|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ |
| Setup time | ~2 min | ~5 min | ~5 min |
| Prod parity | ❌ | ✅ | ✅ |
| DB/Redis | Manual | Manual | Automatic |
| Team consistency | ❌ | ✅ | ✅ |
| Hot reload | ✅ | ⚠️ | ⚠️ |
| Debugging | ⚡⚡⚡ | ⚡ | ⚡ |

**Recommendation:**
- **Daily dev:** Use venv (faster)
- **Integration testing:** Use Docker Compose
- **Production:** Use Docker

## Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose](https://docs.docker.com/compose/)
