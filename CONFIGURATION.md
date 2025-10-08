# Configuration

Modular configuration system with environment and secrets support.

## Structure

```
app/core/config/
├── base.py          # Common settings
├── environments.py  # local/development/staging/production
├── secrets.py       # Secrets (SecretStr)
└── loader.py        # Loader with caching
```

## Environments

```bash
# Switching
APP_ENV=local python run.py         # Default
APP_ENV=development python run.py
APP_ENV=staging python run.py
APP_ENV=production python run.py
```

| Env | Debug | Log Level | Reload | CORS |
|-----|-------|-----------|--------|------|
| local | ✅ | DEBUG | ✅ | * |
| development | ✅ | DEBUG | ✅ | * |
| staging | ❌ | INFO | ❌ | Restricted |
| production | ❌ | WARNING | ❌ | Strict |

## Secrets

Uses `Pydantic SecretStr` - secrets are not logged automatically.

### Available secrets:

```bash
# .env/.env
SECRET_LOGFIRE_TOKEN=          # Logfire
SECRET_DATABASE_URL=           # PostgreSQL
SECRET_OPENAI_API_KEY=         # OpenAI
SECRET_ANTHROPIC_API_KEY=      # Claude
SECRET_JWT_SECRET_KEY=         # JWT signing
SECRET_REDIS_URL=              # Redis
SECRET_SENTRY_DSN=             # Sentry
```

### Usage:

```python
from app.core.config import settings

# Check
if settings.has_logfire():
    token = settings.get_logfire_token()

# Direct access
secrets = settings.secrets
if secrets.has_database_url():
    url = secrets.get_database_url()
```

## Configuration

```python
from app.core.config import settings

# Main
settings.app_name       # str
settings.environment    # Environment enum
settings.debug          # bool
settings.port           # int

# Environment config
config = settings.config
config.host             # str
config.cors_origins     # List[str]
config.auth_delay       # float
config.log_level        # str
```

## Load Priority

1. Environment variables (highest)
2. `.env` file  
3. Default values in code

## Adding Settings

### Common setting (base.py):

```python
class BaseConfig(BaseSettings):
    my_setting: str = Field(
        default="default",
        description="What this does"
    )
```

### Environment-specific (environments.py):

```python
class ProductionConfig(BaseConfig):
    my_setting: str = "production_value"
```

### Secret (secrets.py):

```python
class SecretsConfig(BaseSettings):
    my_token: Optional[SecretStr] = Field(default=None)

    def get_my_token(self) -> Optional[str]:
        return self.my_token.get_secret_value() if self.my_token else None
```

## Validation

Pydantic automatically validates:

```python
port: int = Field(ge=1, le=65535)      # 1-65535
environment: Environment                # Only from enum
cors_origins: List[str]                # List of strings
```

## Files

```bash
# Setup
cp .env/.env.example .env/.env
nano .env/.env

# Structure
.env/                # Hidden folder (gitignored except .env.example)
├── .env.example     # Template (in git)
├── .env             # Main (gitignored)
├── .env.production  # Production (gitignored)
└── .env.staging     # Staging (gitignored)
```

## Production

```bash
# In production require mandatory secrets
if settings.environment == Environment.PRODUCTION:
    if not settings.has_logfire():
        raise ValueError("Logfire required in production")
```

## Security

**IMPORTANT:**
- `.env/` folder fully in `.gitignore` (except `.env.example`)
- Never commit files with real secrets
- Use different secrets for dev/staging/prod
- In production use secret managers (AWS Secrets Manager, etc.)
