# Security Checklist for .env/

## ✅ Configuration Security Check

### 1. .gitignore Check

```bash
# All secrets should be ignored
git check-ignore -v .env/.env .env/.env.production .env/.env.staging

# Only .env.example should be in git
git ls-files .env/
```

**Expected result:**
- `git check-ignore` shows that all .env files are ignored
- `git ls-files` shows only `.env/.env.example`

### 2. Accidental Commit Check

```bash
# Try to add secret (should be blocked)
echo "SECRET_TEST=value" > .env/.env
git add .env/.env

# Should get error: "The following paths are ignored"
```

### 3. Security Rules

❌ **NEVER:**
- Don't commit files with real secrets
- Don't share .env files in chats/email
- Don't store production secrets in dev environment
- Don't use weak secrets (test, 123, etc.)

✅ **ALWAYS:**
- Use different secrets for each environment
- Rotate secrets regularly
- In production use secret managers (AWS/Azure/Vault)
- Check `.gitignore` before committing secrets

### 4. If Secrets Leaked

1. **Immediately rotate** all compromised secrets
2. Remove from git history:
   ```bash
   # Use BFG Repo-Cleaner
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```
3. Check service access logs
4. Notify team

### 5. .env/ Structure

```
.env/
├── .env.example         ✅ In git (template without secrets)
├── .env                 ❌ Gitignored (local dev)
├── .env.production      ❌ Gitignored (production secrets)
└── .env.staging         ❌ Gitignored (staging secrets)
```

## Current Status

```bash
# Check current configuration
cd city-helper-ai-backend
git check-ignore -v .env/.env  # Should be ignored
git ls-files .env/             # Only .env.example
```

✅ Configuration is secure!
