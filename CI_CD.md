# CI/CD with GitHub Actions

Automated code checking on every push and pull request.

## Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

Runs on:
- Push to `main`, `master`, `develop`
- Pull Request creation
- Manual trigger (Actions → CI → Run workflow)

**Jobs:**

#### 🔍 Lint & Format Check
- Checks code with Ruff
- Checks formatting
- Time: ~30 seconds

#### 🪝 Pre-commit Hooks
- Runs all pre-commit hooks
- Checks files, secrets, formatting
- Time: ~1 minute

#### 🔒 Security Checks
- **Bandit** - finds code vulnerabilities
- **Safety** - checks dependencies for known CVEs
- Time: ~30 seconds

#### 🏗️ Build & Test
- Tests on Python 3.11, 3.12, 3.13
- Checks imports
- Smoke test (server start)
- Time: ~1 minute per version

**Total: ~3-4 minutes**

### 2. Dependency Review (`.github/workflows/dependency-review.yml`)

Runs only for Pull Requests.

**What it checks:**
- New dependencies with vulnerabilities
- Licenses (compatibility)
- Outdated packages
- Leaves comment in PR with results

### 3. Dependabot (`.github/dependabot.yml`)

Automatic dependency updates:
- **Python**: check every Monday at 09:00
- **GitHub Actions**: check every Monday at 09:00
- Creates PRs with updates
- Maximum 10 PRs at once

## How to Use

### During Development

1. **Create branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write code:**
   ```bash
   # Local check
   make check
   make run-hooks
   ```

3. **Commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit will check automatically
   ```

4. **Push:**
   ```bash
   git push origin feature/my-feature
   ```

5. **Create PR:**
   - Go to GitHub
   - Create Pull Request
   - CI will run automatically
   - Wait for ✅ green checks

### Viewing Results

GitHub → Repository → Actions

**Green checkmark** ✅ - all good, can merge
**Red cross** ❌ - there are issues, need to fix
**Yellow circle** 🟡 - running

Click on workflow → click on job → view logs

### Manual CI Run

GitHub → Actions → CI → Run workflow → select branch → Run

Useful for:
- Checking after setup
- CI debugging
- Re-running after fix

## Local Checks

Before push, recommended:

```bash
# Full check (like in CI)
make check
make run-hooks

# Linter only
make lint

# Auto-fix
make fix

# Pre-commit on all files
pre-commit run --all-files
```

## Status and Badges

Add to README to display status:

```markdown
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
```

## Setup for New Repository

1. **Create repository on GitHub**

2. **Add files:**
   ```bash
   git add .github/
   git commit -m "ci: add GitHub Actions"
   git push origin main
   ```

3. **Enable Actions:**
   - GitHub → Settings → Actions → Allow all actions

4. **Configure Dependabot:**
   - GitHub → Settings → Security → Enable Dependabot

5. **First run:**
   - Make any commit
   - CI will run automatically

## Debugging Issues

### CI Fails on Lint
```bash
# Fix locally
make fix
git add .
git commit --amend --no-edit
git push --force-with-lease
```

### CI Fails on Security
Check `bandit-report.json` in Artifacts:
- GitHub → Actions → your workflow → Artifacts → security-reports

### CI Fails on Build
Check compatibility with Python 3.11+:
```bash
# Test locally
python run.py
```

## Speed Optimization

CI is already optimized:
- ✅ Pip dependencies caching
- ✅ Pre-commit hooks caching
- ✅ Parallel job execution
- ✅ Matrix strategy for Python versions

Average time: **3-4 minutes**

## Security

**Secrets:**
If you need secrets (API keys):
- GitHub → Settings → Secrets and variables → Actions → New secret
- In workflow: `${{ secrets.SECRET_NAME }}`

**Permissions:**
Workflow has minimal permissions:
- `contents: read` - read code
- `pull-requests: write` - comment on PR (dependency review)

## Extending CI

### Add Tests (pytest)

Uncomment in `ci.yml`:
```yaml
test:
  name: Run Tests
  runs-on: ubuntu-latest
  steps:
    # ... pytest steps
```

### Add Coverage

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
```

### Add Deployment

Create new workflow `.github/workflows/deploy.yml`:
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

**Workflow doesn't run:**
- Check file is in `.github/workflows/`
- Check YAML syntax (spaces, not tabs)
- Check Actions are enabled in Settings

**Permission denied:**
- GitHub → Settings → Actions → Workflow permissions → Read and write

**Takes too long:**
- Check logs
- Make sure caching works
- Optimize dependency list

## Best Practices

✅ **DO:**
- Check locally before push
- Read logs on errors
- Use meaningful commit messages
- Merge only with green CI

❌ **DON'T:**
- Don't push directly to main (use PR)
- Don't ignore red CI
- Don't skip pre-commit (`--no-verify`)
- Don't store secrets in code
