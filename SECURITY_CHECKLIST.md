# Security Checklist для .env/

## ✅ Проверка безопасности конфигурации

### 1. Проверка .gitignore

```bash
# Все секреты должны игнорироваться
git check-ignore -v .env/.env .env/.env.production .env/.env.staging

# Только .env.example должен быть в git
git ls-files .env/
```

**Ожидаемый результат:**
- `git check-ignore` показывает что все .env файлы игнорируются
- `git ls-files` показывает только `.env/.env.example`

### 2. Проверка случайного коммита

```bash
# Попробовать добавить секрет (должно заблокировать)
echo "SECRET_TEST=value" > .env/.env
git add .env/.env

# Должна быть ошибка: "The following paths are ignored"
```

### 3. Правила безопасности

❌ **НИКОГДА:**
- Не коммитьте файлы с реальными секретами
- Не шарьте .env файлы в чатах/email
- Не храните production секреты в dev окружении
- Не используйте слабые секреты (test, 123, etc.)

✅ **ВСЕГДА:**
- Используйте разные секреты для каждого окружения
- Ротируйте секреты регулярно
- В production используйте secret managers (AWS/Azure/Vault)
- Проверяйте `.gitignore` перед коммитом секретов

### 4. Если секреты утекли

1. **Немедленно ротируйте** все скомпрометированные секреты
2. Удалите из git history:
   ```bash
   # Используйте BFG Repo-Cleaner
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```
3. Проверьте логи доступа к сервисам
4. Уведомите команду

### 5. Структура .env/

```
.env/
├── .env.example         ✅ В git (template без секретов)
├── .env                 ❌ Gitignored (local dev)
├── .env.production      ❌ Gitignored (production secrets)
└── .env.staging         ❌ Gitignored (staging secrets)
```

## Текущий статус

```bash
# Проверка текущей конфигурации
cd city-helper-ai-backend
git check-ignore -v .env/.env  # Должен игнорироваться
git ls-files .env/             # Только .env.example
```

✅ Конфигурация безопасна!
