# Pre-commit Hooks

Automated code quality checks before every commit.

## Setup

```bash
# Install (already done if you ran pip install -r requirements.txt)
pip install pre-commit

# Install git hooks
make install-hooks
# or: pre-commit install
```

## What It Does

Pre-commit automatically runs before each `git commit`:

1. **Ruff Linter** - finds bugs, unused code, bad practices
2. **Ruff Formatter** - formats code (spacing, quotes, imports)
3. **Security** - detects secrets, private keys
4. **File Checks** - large files, trailing spaces, merge conflicts
5. **JSON/YAML** - validates syntax

## Usage

### Automatic (on commit)
```bash
git add file.py
git commit -m "message"
# ↑ pre-commit runs automatically
```

If pre-commit finds issues:
- ✅ Auto-fixable issues → fixed automatically
- ❌ Manual fixes needed → commit blocked

After auto-fixes:
```bash
git add .  # Stage the fixes
git commit -m "message"  # Commit again
```

### Manual (test without commit)
```bash
# Run on all files
make run-hooks

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff --all-files
```

### Skip (emergency only)
```bash
# Skip all hooks (NOT RECOMMENDED)
git commit --no-verify -m "message"
```

## Configuration

Config: `.pre-commit-config.yaml`

Update hooks to latest versions:
```bash
make update-hooks
```

## What Gets Checked

✅ **Python code quality**
- Unused variables/imports
- Missing type hints
- Complex/nested code
- Naming conventions

✅ **Code formatting**
- Spacing, indentation
- Quote style (double quotes)
- Import sorting
- Line length (100 chars)

✅ **Security**
- Secrets in code (API keys, passwords)
- Private SSH keys
- High-entropy strings

✅ **File quality**
- Files > 500KB
- Trailing whitespace
- Missing newline at end
- Mixed line endings (LF/CRLF)
- Merge conflict markers

## Examples

### Blocked Commit
```python
# This will be blocked:
password = "secret123"  # pragma: allowlist secret - example only
unused_var = 10         # ❌ Unused variable
def bad(x,y):           # ❌ Bad spacing
    return x+y          # ❌ Bad spacing
```

### After Auto-Fix
```python
# After running pre-commit:
def good(x, y):         # ✅ Proper spacing
    return x + y        # ✅ Proper spacing
# unused_var removed    # ✅ Auto-removed
# password still blocked - manual fix needed
```

## Troubleshooting

**Pre-commit not running:**
```bash
# Check if installed
pre-commit --version

# Reinstall hooks
make install-hooks
```

**False positive secret:**
```python
# Add comment to allow
fake_token = "test123"  # pragma: allowlist secret  # pragma: allowlist secret
```

**Skip single hook:**
```bash
SKIP=detect-secrets git commit -m "message"
```

## CI/CD

Add to GitHub Actions / GitLab CI:
```yaml
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```
