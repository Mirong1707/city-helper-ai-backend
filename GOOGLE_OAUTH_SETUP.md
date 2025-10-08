# Google OAuth2 Setup Guide

Пошаговая инструкция для настройки Google OAuth2 аутентификации.

---

## 📋 Часть 1: Google Cloud Console Setup

### Шаг 1: Создай Google Cloud проект

1. Открой: https://console.cloud.google.com
2. Нажми на dropdown вверху (где название проекта)
3. Нажми **"New Project"**
4. Заполни:
   - **Project name**: `city-helper` (или любое название)
   - **Organization**: оставь пустым (No organization)
5. Нажми **"Create"**
6. Подожди 10-15 секунд пока проект создастся

---

### Шаг 2: Включи Google Identity API

1. Открой: https://console.cloud.google.com/apis/library
2. Убедись что выбран твой проект `city-helper` (вверху)
3. В поиске найди: **"Google+ API"** или **"Google Identity Services"**
4. Нажми на результат
5. Нажми **"Enable"** (если кнопка есть)
6. Подожди пока API включится

---

### Шаг 3: Настрой OAuth Consent Screen

1. Открой: https://console.cloud.google.com/apis/credentials/consent
2. Выбери **"External"** (для тестирования)
3. Нажми **"Create"**

#### Шаг 3.1: OAuth consent screen (Страница 1)

Заполни обязательные поля:
- **App name**: `City Helper`
- **User support email**: твой email (выбери из dropdown)
- **App logo**: можешь пропустить (не обязательно)
- **Application home page**: `http://localhost:3001` (пока для разработки)
- **Developer contact information**: твой email

Нажми **"Save and Continue"**

#### Шаг 3.2: Scopes (Страница 2)

1. Нажми **"Add or Remove Scopes"**
2. Найди и отметь:
   - ✅ `.../auth/userinfo.email`
   - ✅ `.../auth/userinfo.profile`
   - ✅ `openid`
3. Нажми **"Update"**
4. Нажми **"Save and Continue"**

#### Шаг 3.3: Test users (Страница 3)

1. Нажми **"Add Users"**
2. Введи свой email (для тестирования)
3. Нажми **"Add"**
4. Нажми **"Save and Continue"**

#### Шаг 3.4: Summary (Страница 4)

Просмотри и нажми **"Back to Dashboard"**

---

### Шаг 4: Создай OAuth2 Credentials

1. Открой: https://console.cloud.google.com/apis/credentials
2. Нажми **"Create Credentials"** → **"OAuth client ID"**
3. Заполни:
   - **Application type**: **"Web application"**
   - **Name**: `City Helper Web Client`

4. **Authorized JavaScript origins** (опционально):
   - `http://localhost:3001`
   - `http://localhost:5173` (если фронтенд на другом порту)

5. **Authorized redirect URIs** (ВАЖНО!):
   Добавь оба URI:
   ```
   http://localhost:3001/api/auth/google/callback
   http://localhost:5173/auth/google/callback
   ```

   ⚠️ **Внимание:** URL должны быть точными (без лишних слэшей)!

6. Нажми **"Create"**

---

### Шаг 5: Сохрани Credentials

После создания откроется окно с credentials:

1. **Client ID** (длинная строка типа `xxxxx.apps.googleusercontent.com`)
   - Скопируй и сохрани

2. **Client secret** (короче, типа `GOCSPX-...`)
   - Скопируй и сохрани

⚠️ **Не теряй эти данные!** (Если потеряешь, можно будет посмотреть в Google Cloud Console)

---

## 📋 Часть 2: Backend Configuration

### Шаг 1: Установи зависимости

```bash
cd /Users/miron/Documents/AI/city-helper/city-helper-ai-backend
source venv/bin/activate
pip install -r requirements.txt
```

---

### Шаг 2: Настрой Environment Variables

#### Вариант A: Через .env файл (рекомендуется)

1. Создай файл `.env/.env`:
   ```bash
   mkdir -p .env
   touch .env/.env
   ```

2. Открой файл и добавь:
   ```bash
   # Google OAuth2 Credentials
   SECRET_GOOGLE_CLIENT_ID=твой-client-id.apps.googleusercontent.com
   SECRET_GOOGLE_CLIENT_SECRET=твой-client-secret
   ```

3. Замени `твой-client-id` и `твой-client-secret` на реальные значения из Шага 5

#### Вариант B: Через terminal (для быстрого теста)

```bash
export SECRET_GOOGLE_CLIENT_ID="твой-client-id.apps.googleusercontent.com"
export SECRET_GOOGLE_CLIENT_SECRET="твой-client-secret"  # pragma: allowlist secret
```

---

### Шаг 3: Перезапусти сервер

```bash
# Останови старый сервер (Ctrl+C если запущен)

# Запусти заново
python run.py
```

Ты должен увидеть в логах:
```
google_oauth_configured   client_id_prefix=xxxxx...
```

Если видишь `google_oauth_not_configured` — проверь `.env/.env` файл.

---

## 🧪 Часть 3: Тестирование

### Метод 1: Через Browser (самый простой)

1. Открой: http://localhost:3001/api/auth/google

2. Ты получишь JSON с `auth_url`:
   ```json
   {
     "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
   }
   ```

3. Скопируй `auth_url` и открой в браузере

4. Залогинься через Google (используй test user email)

5. Google перенаправит тебя на callback URL

6. Ты должен получить JSON с user info и token:
   ```json
   {
     "user": {
       "id": "user-...",
       "email": "your@email.com",
       "name": "Your Name",
       "avatar_url": "https://...",
       "auth_provider": "google",
       "provider_user_id": "..."
     },
     "token": "session-..."
   }
   ```

✅ **Если видишь это — всё работает!**

---

### Метод 2: Через Swagger UI

1. Открой: http://localhost:3001/docs

2. Найди **`GET /api/auth/google`**

3. Нажми **"Try it out"** → **"Execute"**

4. Скопируй `auth_url` из ответа

5. Открой `auth_url` в браузере

6. После логина Google вернёт тебя на callback

---

### Метод 3: Через curl

```bash
# Получи auth URL
curl http://localhost:3001/api/auth/google

# Открой auth_url в браузере, залогинься
# Google вернёт тебя на callback с code в URL

# Пример callback URL:
# http://localhost:3001/api/auth/google/callback?code=4/0AanFFf...&scope=email...

# Backend автоматически обработает callback
```

---

## 🐛 Troubleshooting

### Ошибка: "Google OAuth2 is not configured"

**Причина:** Credentials не загрузились

**Решение:**
```bash
# Проверь что .env/.env существует
cat .env/.env

# Проверь переменные
echo $SECRET_GOOGLE_CLIENT_ID
echo $SECRET_GOOGLE_CLIENT_SECRET

# Перезапусти сервер
python run.py
```

---

### Ошибка: "redirect_uri_mismatch"

**Причина:** redirect_uri не совпадает с настроенным в Google Console

**Решение:**
1. Открой: https://console.cloud.google.com/apis/credentials
2. Нажми на свой OAuth Client ID
3. Проверь **Authorized redirect URIs**
4. Должно быть: `http://localhost:3001/api/auth/google/callback`
5. Если нет — добавь и сохрани

---

### Ошибка: "Access blocked: This app's request is invalid"

**Причина:** OAuth Consent Screen не настроен или не добавлен test user

**Решение:**
1. Открой: https://console.cloud.google.com/apis/credentials/consent
2. Проверь что app status = "Testing"
3. Добавь свой email в **Test users**
4. Попробуй снова через 5 минут (Google кэширует)

---

### Ошибка 401 при callback

**Причина:** Неправильный Client ID или Secret

**Решение:**
1. Проверь `.env/.env` файл
2. Убедись что нет пробелов или кавычек
3. Client ID должен заканчиваться на `.apps.googleusercontent.com`
4. Client Secret должен начинаться с `GOCSPX-`

---

## 📊 Структура OAuth2 Flow

```
1. User → Frontend
   "Хочу войти через Google"

2. Frontend → GET /api/auth/google
   Получает auth_url

3. Frontend → Redirect to Google
   auth_url = https://accounts.google.com/o/oauth2/v2/auth?...

4. User → Логинится в Google
   Разрешает доступ к email & profile

5. Google → Redirect to callback
   /api/auth/google/callback?code=ABC123...

6. Backend → Exchange code for tokens
   POST https://oauth2.googleapis.com/token

7. Backend → Get user info
   GET https://www.googleapis.com/oauth2/v2/userinfo

8. Backend → Create/Find user in DB
   По provider_user_id (Google ID)

9. Backend → Return user + session token
   { user: {...}, token: "session-..." }

10. Frontend → Save token
    localStorage.setItem("auth_token", token)

11. Frontend → Use token for API calls
    Authorization: Bearer session-...
```

---

## 🎯 Next Steps

После успешного тестирования:

1. ✅ Google OAuth2 работает локально
2. 📱 Добавь фронтенд UI для "Sign in with Google"
3. 🔐 Для production: verify domain в Google Console
4. 🍎 (Опционально) Добавь Apple Sign In

---

## 📚 Полезные ссылки

- **Google Cloud Console**: https://console.cloud.google.com
- **OAuth2 Playground**: https://developers.google.com/oauthplayground
- **Google OAuth2 Docs**: https://developers.google.com/identity/protocols/oauth2
- **Backend API Docs**: http://localhost:3001/docs
