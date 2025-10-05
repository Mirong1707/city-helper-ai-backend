# Configuration

Модульная система конфигурации с поддержкой окружений и секретов.

## Структура

```
app/core/config/
├── base.py          # Общие настройки
├── environments.py  # local/development/staging/production
├── secrets.py       # Секреты (SecretStr)
└── loader.py        # Загрузчик с кэшированием
```

## Окружения

```bash
# Переключение
APP_ENV=local python run.py         # По умолчанию
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

## Секреты

Используется `Pydantic SecretStr` - секреты не логируются автоматически.

### Доступные секреты:

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

### Использование:

```python
from app.core.config import settings

# Проверка
if settings.has_logfire():
    token = settings.get_logfire_token()

# Прямой доступ
secrets = settings.secrets
if secrets.has_database_url():
    url = secrets.get_database_url()
```

## Конфигурация

```python
from app.core.config import settings

# Основное
settings.app_name       # str
settings.environment    # Environment enum
settings.debug          # bool
settings.port           # int

# Конфиг окружения
config = settings.config
config.host             # str
config.cors_origins     # List[str]
config.auth_delay       # float
config.log_level        # str
```

## Приоритет загрузки

1. Environment variables (высший)
2. `.env` файл  
3. Default values в коде

## Добавление настроек

### Общая настройка (base.py):

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

### Секрет (secrets.py):

```python
class SecretsConfig(BaseSettings):
    my_token: Optional[SecretStr] = Field(default=None)

    def get_my_token(self) -> Optional[str]:
        return self.my_token.get_secret_value() if self.my_token else None
```

## Валидация

Pydantic автоматически валидирует:

```python
port: int = Field(ge=1, le=65535)      # 1-65535
environment: Environment                # Только из enum
cors_origins: List[str]                # Список строк
```

## Файлы

```bash
# Setup
cp .env/.env.example .env/.env
nano .env/.env

# Structure
.env/                # Скрытая папка (gitignored кроме .env.example)
├── .env.example     # Template (в git)
├── .env             # Main (gitignored)
├── .env.production  # Production (gitignored)
└── .env.staging     # Staging (gitignored)
```

## Production

```bash
# В production требуйте обязательные секреты
if settings.environment == Environment.PRODUCTION:
    if not settings.has_logfire():
        raise ValueError("Logfire required in production")
```

## Безопасность

**ВАЖНО:**
- Папка `.env/` полностью в `.gitignore` (кроме `.env.example`)
- Никогда не коммитьте файлы с реальными секретами
- Используйте разные секреты для dev/staging/prod
- В production используйте secret managers (AWS Secrets Manager, etc.)
