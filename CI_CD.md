# CI/CD с GitHub Actions

Автоматическая проверка кода при каждом push и pull request.

## Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

Запускается при:
- Push в `main`, `master`, `develop`
- Создании Pull Request
- Ручном запуске (Actions → CI → Run workflow)

**Jobs:**

#### 🔍 Lint & Format Check
- Проверяет код с Ruff
- Проверяет форматирование
- Время: ~30 секунд

#### 🪝 Pre-commit Hooks
- Запускает все pre-commit хуки
- Проверяет файлы, секреты, форматирование
- Время: ~1 минута

#### 🔒 Security Checks
- **Bandit** - находит уязвимости в коде
- **Safety** - проверяет зависимости на известные CVE
- Время: ~30 секунд

#### 🏗️ Build & Test
- Тестирует на Python 3.11, 3.12, 3.13
- Проверяет импорты
- Smoke test (запуск сервера)
- Время: ~1 минута на версию

**Всего: ~3-4 минуты**

### 2. Dependency Review (`.github/workflows/dependency-review.yml`)

Запускается только для Pull Requests.

**Что проверяет:**
- Новые зависимости с уязвимостями
- Лицензии (совместимость)
- Устаревшие пакеты
- Оставляет комментарий в PR с результатами

### 3. Dependabot (`.github/dependabot.yml`)

Автоматические обновления зависимостей:
- **Python**: проверка каждый понедельник в 09:00
- **GitHub Actions**: проверка каждый понедельник в 09:00
- Создаёт PR с обновлениями
- Максимум 10 PR одновременно

## Как использовать

### При разработке

1. **Создай ветку:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Пиши код:**
   ```bash
   # Локальная проверка
   make check
   make run-hooks
   ```

3. **Закоммить:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit автоматически проверит
   ```

4. **Запуш:**
   ```bash
   git push origin feature/my-feature
   ```

5. **Создай PR:**
   - Зайди на GitHub
   - Создай Pull Request
   - CI автоматически запустится
   - Дождись ✅ зелёных галочек

### Просмотр результатов

GitHub → Repository → Actions

**Зелёная галочка** ✅ - всё ок, можно мерджить
**Красный крестик** ❌ - есть проблемы, нужно исправить
**Жёлтый кружок** 🟡 - выполняется

Кликни на workflow → кликни на job → смотри логи

### Ручной запуск CI

GitHub → Actions → CI → Run workflow → выбери ветку → Run

Полезно для:
- Проверки после настройки
- Отладки CI
- Повторного запуска после фикса

## Проверка локально

Перед push рекомендуется:

```bash
# Полная проверка (как в CI)
make check
make run-hooks

# Только линтер
make lint

# Автоисправление
make fix

# Pre-commit на всех файлах
pre-commit run --all-files
```

## Статусы и badges

Добавь в README для отображения статуса:

```markdown
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
```

## Настройка для нового репозитория

1. **Создай репозиторий на GitHub**

2. **Добавь файлы:**
   ```bash
   git add .github/
   git commit -m "ci: add GitHub Actions"
   git push origin main
   ```

3. **Включи Actions:**
   - GitHub → Settings → Actions → Allow all actions

4. **Настрой Dependabot:**
   - GitHub → Settings → Security → Enable Dependabot

5. **Первый запуск:**
   - Сделай любой commit
   - CI запустится автоматически

## Отладка проблем

### CI падает на Lint
```bash
# Локально исправь
make fix
git add .
git commit --amend --no-edit
git push --force-with-lease
```

### CI падает на Security
Смотри `bandit-report.json` в Artifacts:
- GitHub → Actions → твой workflow → Artifacts → security-reports

### CI падает на Build
Проверь совместимость с Python 3.11+:
```bash
# Локально протестируй
python run.py
```

## Оптимизация скорости

CI уже оптимизирован:
- ✅ Кэширование pip зависимостей
- ✅ Кэширование pre-commit hooks
- ✅ Параллельный запуск jobs
- ✅ Matrix strategy для Python версий

Среднее время: **3-4 минуты**

## Безопасность

**Secrets:**
Если нужны секреты (API keys):
- GitHub → Settings → Secrets and variables → Actions → New secret
- В workflow: `${{ secrets.SECRET_NAME }}`

**Permissions:**
Workflow имеет минимальные права:
- `contents: read` - читать код
- `pull-requests: write` - комментировать PR (dependency review)

## Расширение CI

### Добавить тесты (pytest)

Раскомментируй в `ci.yml`:
```yaml
test:
  name: Run Tests
  runs-on: ubuntu-latest
  steps:
    # ... pytest steps
```

### Добавить coverage

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
```

### Добавить deployment

Создай новый workflow `.github/workflows/deploy.yml`:
```yaml
name: Deploy
on:
  push:
    tags: ['v*']
jobs:
  deploy:
    # ... deployment steps
```

## Troubleshooting

**Workflow не запускается:**
- Проверь, что файл в `.github/workflows/`
- Проверь синтаксис YAML (spaces, not tabs)
- Проверь, что Actions включены в Settings

**Permission denied:**
- GitHub → Settings → Actions → Workflow permissions → Read and write

**Долго выполняется:**
- Проверь логи
- Убедись, что кэширование работает
- Оптимизируй список зависимостей

## Best Practices

✅ **DO:**
- Проверяй локально перед push
- Читай логи при ошибках
- Используй осмысленные commit messages
- Merge только с зелёными CI

❌ **DON'T:**
- Не пушь напрямую в main (используй PR)
- Не игнорируй красные CI
- Не пропускай pre-commit (`--no-verify`)
- Не храни секреты в коде
