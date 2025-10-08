# Google OAuth2 Setup Guide

Step-by-step instructions for setting up Google OAuth2 authentication.

---

## 📋 Part 1: Google Cloud Console Setup

### Step 1: Create Google Cloud Project

1. Open: https://console.cloud.google.com
2. Click on dropdown at the top (where project name is)
3. Click **"New Project"**
4. Fill in:
   - **Project name**: `city-helper` (or any name)
   - **Organization**: leave empty (No organization)
5. Click **"Create"**
6. Wait 10-15 seconds for project to be created

---

### Step 2: Enable Google Identity API

1. Open: https://console.cloud.google.com/apis/library
2. Make sure your project `city-helper` is selected (at the top)
3. Search for: **"Google+ API"** or **"Google Identity Services"**
4. Click on the result
5. Click **"Enable"** (if button is present)
6. Wait for API to be enabled

---

### Step 3: Configure OAuth Consent Screen

1. Open: https://console.cloud.google.com/apis/credentials/consent
2. Select **"External"** (for testing)
3. Click **"Create"**

#### Step 3.1: OAuth consent screen (Page 1)

Fill in required fields:
- **App name**: `City Helper`
- **User support email**: your email (select from dropdown)
- **App logo**: can skip (optional)
- **Application home page**: `http://localhost:3001` (for development)
- **Developer contact information**: your email

Click **"Save and Continue"**

#### Step 3.2: Scopes (Page 2)

1. Click **"Add or Remove Scopes"**
2. Find and check:
   - ✅ `.../auth/userinfo.email`
   - ✅ `.../auth/userinfo.profile`
   - ✅ `openid`
3. Click **"Update"**
4. Click **"Save and Continue"**

#### Step 3.3: Test users (Page 3)

1. Click **"Add Users"**
2. Enter your email (for testing)
3. Click **"Add"**
4. Click **"Save and Continue"**

#### Step 3.4: Summary (Page 4)

Review and click **"Back to Dashboard"**

---

### Step 4: Create OAuth2 Credentials

1. Open: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Fill in:
   - **Application type**: **"Web application"**
   - **Name**: `City Helper Web Client`

4. **Authorized JavaScript origins** (optional):
   - `http://localhost:3001`
   - `http://localhost:5173` (if frontend on different port)

5. **Authorized redirect URIs** (IMPORTANT!):
   Add both URIs:
   ```
   http://localhost:3001/api/auth/google/callback
   http://localhost:5173/auth/google/callback
   ```

   ⚠️ **Warning:** URLs must be exact (no extra slashes)!

6. Click **"Create"**

---

### Step 5: Save Credentials

After creation, a window with credentials will open:

1. **Client ID** (long string like `xxxxx.apps.googleusercontent.com`)
   - Copy and save

2. **Client secret** (shorter, like `GOCSPX-...`)
   - Copy and save

⚠️ **Don't lose these!** (If lost, can view in Google Cloud Console)

---

## 📋 Part 2: Backend Configuration

### Step 1: Install Dependencies

```bash
cd /Users/miron/Documents/AI/city-helper/city-helper-ai-backend
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

#### Option A: Via .env file (recommended)

1. Create file `.env/.env`:
   ```bash
   mkdir -p .env
   touch .env/.env
   ```

2. Open file and add:
   ```bash
   # Google OAuth2 Credentials
   SECRET_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   SECRET_GOOGLE_CLIENT_SECRET=your-client-secret
   ```

3. Replace `your-client-id` and `your-client-secret` with real values from Step 5

#### Option B: Via terminal (for quick test)

```bash
export SECRET_GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export SECRET_GOOGLE_CLIENT_SECRET="your-client-secret"  # pragma: allowlist secret
```

---

### Step 3: Restart Server

```bash
# Stop old server (Ctrl+C if running)

# Start again
python run.py
```

You should see in logs:
```
google_oauth_configured   client_id_prefix=xxxxx...
```

If you see `google_oauth_not_configured` — check `.env/.env` file.

---

## 🧪 Part 3: Testing

### Method 1: Via Browser (simplest)

1. Open: http://localhost:3001/api/auth/google

2. You'll get JSON with `auth_url`:
   ```json
   {
     "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
   }
   ```

3. Copy `auth_url` and open in browser

4. Login via Google (use test user email)

5. Google will redirect you to callback URL

6. You should get JSON with user info and token:
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

✅ **If you see this — everything works!**

---

### Method 2: Via Swagger UI

1. Open: http://localhost:3001/docs

2. Find **`GET /api/auth/google`**

3. Click **"Try it out"** → **"Execute"**

4. Copy `auth_url` from response

5. Open `auth_url` in browser

6. After login, Google will return you to callback

---

### Method 3: Via curl

```bash
# Get auth URL
curl http://localhost:3001/api/auth/google

# Open auth_url in browser, login
# Google will return you to callback with code in URL

# Example callback URL:
# http://localhost:3001/api/auth/google/callback?code=4/0AanFFf...&scope=email...

# Backend will automatically handle callback
```

---

## 🐛 Troubleshooting

### Error: "Google OAuth2 is not configured"

**Cause:** Credentials not loaded

**Solution:**
```bash
# Check that .env/.env exists
cat .env/.env

# Check variables
echo $SECRET_GOOGLE_CLIENT_ID
echo $SECRET_GOOGLE_CLIENT_SECRET

# Restart server
python run.py
```

---

### Error: "redirect_uri_mismatch"

**Cause:** redirect_uri doesn't match configured in Google Console

**Solution:**
1. Open: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth Client ID
3. Check **Authorized redirect URIs**
4. Should be: `http://localhost:3001/api/auth/google/callback`
5. If not — add and save

---

### Error: "Access blocked: This app's request is invalid"

**Cause:** OAuth Consent Screen not configured or test user not added

**Solution:**
1. Open: https://console.cloud.google.com/apis/credentials/consent
2. Check that app status = "Testing"
3. Add your email to **Test users**
4. Try again in 5 minutes (Google caches)

---

### Error 401 at callback

**Cause:** Wrong Client ID or Secret

**Solution:**
1. Check `.env/.env` file
2. Make sure there are no spaces or quotes
3. Client ID should end with `.apps.googleusercontent.com`
4. Client Secret should start with `GOCSPX-`

---

## 📊 OAuth2 Flow Structure

```
1. User → Frontend
   "I want to sign in with Google"

2. Frontend → GET /api/auth/google
   Gets auth_url

3. Frontend → Redirect to Google
   auth_url = https://accounts.google.com/o/oauth2/v2/auth?...

4. User → Login to Google
   Grants access to email & profile

5. Google → Redirect to callback
   /api/auth/google/callback?code=ABC123...

6. Backend → Exchange code for tokens
   POST https://oauth2.googleapis.com/token

7. Backend → Get user info
   GET https://www.googleapis.com/oauth2/v2/userinfo

8. Backend → Create/Find user in DB
   By provider_user_id (Google ID)

9. Backend → Return user + session token
   { user: {...}, token: "session-..." }

10. Frontend → Save token
    localStorage.setItem("auth_token", token)

11. Frontend → Use token for API calls
    Authorization: Bearer session-...
```

---

## 🎯 Next Steps

After successful testing:

1. ✅ Google OAuth2 works locally
2. 📱 Add frontend UI for "Sign in with Google"
3. 🔐 For production: verify domain in Google Console
4. 🍎 (Optional) Add Apple Sign In

---

## 📚 Useful Links

- **Google Cloud Console**: https://console.cloud.google.com
- **OAuth2 Playground**: https://developers.google.com/oauthplayground
- **Google OAuth2 Docs**: https://developers.google.com/identity/protocols/oauth2
- **Backend API Docs**: http://localhost:3001/docs
