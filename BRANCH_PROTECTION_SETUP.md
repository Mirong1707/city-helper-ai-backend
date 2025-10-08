# Branch Protection Setup Guide

## 🛡️ Protecting `main` Branch

**Goal:** Prevent direct pushes to `main`, all changes only through Pull Requests.

---

## ⚡ Quick Setup (5 minutes)

### 1. Open Branch Protection Settings

```bash
# Go to repository settings
open https://github.com/Miron-s-playground/city-helper-ai-backend/settings/branches
```

Or manually:
1. GitHub → Your repository
2. Settings → Branches (in left menu)
3. Click **"Add branch protection rule"**

### 2. Fill in Fields

**Branch name pattern:**
```
main
```

**Enable the following options:**

#### ✅ Require a pull request before merging
- ✅ Enable this checkbox
- **Require approvals:** 0 (for solo development) / 1+ (for team)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (optional)

#### ✅ Require status checks to pass before merging
- ✅ Enable this checkbox
- ✅ Require branches to be up to date before merging

**Add required checks (important!):**

Click "Search for status checks" and select:
- `Quick Validation`
- `Code Quality`
- `Pre-commit Hooks`
- `Security Scan`
- `Build & Test (Python 3.13)` (at least one Python version)
- `Docker Build Test`
- `All Checks Passed ✅`

> **Note:** These checks will appear in the list AFTER the first PR. If they're not there yet — create a test PR, then return to settings.

#### ✅ Require conversation resolution before merging
- ✅ Enable (if using code review)

#### ✅ Require linear history
- ✅ Enable (for clean commit history)

#### ✅ Do not allow bypassing the above settings
- ✅ Enable (even admins must follow rules!)

#### ❌ Allow force pushes
- ❌ Disabled (default)

#### ❌ Allow deletions
- ❌ Disabled (default)

### 3. Save

Click **"Create"** or **"Save changes"**

---

## ✅ Verification

### Test 1: Try push to main (should be blocked)

```bash
# Try direct push to main
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test: direct push"
git push

# Should get error:
# remote: error: GH006: Protected branch update failed
```

**If got error** → ✅ Setup works!

**If push succeeded** → ❌ Return to settings, check checkboxes

### Test 2: Create PR (should work)

```bash
# Undo previous commit
git reset --hard origin/main

# Create feature branch
git checkout -b test/branch-protection
echo "test via PR" >> test.txt
git add test.txt
git commit -m "test: via pull request"
git push origin test/branch-protection

# Go to GitHub and create PR
```

✅ PR should be created, CI should run

---

## 📋 Recommended Settings

### For Solo Developer (you now):

```yaml
Branch: main
Require pull request before merging: ✅ (0 approvals)
Require status checks: ✅ (all checks listed above)
Require linear history: ✅
Do not allow bypassing: ✅
```

### For Team:

```yaml
Branch: main
Require pull request before merging: ✅ (1-2 approvals)
Require status checks: ✅ (all checks listed above)
Require conversation resolution: ✅
Require linear history: ✅
Do not allow bypassing: ✅
Restrict who can push: ✅ (only maintainers)
```

---

## 🔥 Emergency Access

If you REALLY need to push to main urgently (not recommended):

1. **Disable Branch Protection:**
   - Settings → Branches → Edit rule
   - Temporarily disable "Do not allow bypassing"
   - Save

2. **Make push**

3. **MUST enable back!**

---

## 🎓 What This Gives?

### Before Branch Protection:
```bash
git commit -m "fix typo"
git push origin main
# ✅ Went through directly (dangerous!)
```

### After Branch Protection:
```bash
git commit -m "fix typo"
git push origin main
# ❌ Blocked!

# Correct way:
git checkout -b fix/typo
git commit -m "fix: typo in documentation"
git push origin fix/typo
# Create PR → CI checks → Merge
```

---

## 📊 CI Checks Statistics

After setup, on each PR will run:

| Check | What it checks | Time |
|-------|---------------|-------|
| Quick Validation | PR title format, conflicts | ~30s |
| Code Quality | Ruff linting & formatting | ~1m |
| Pre-commit Hooks | All pre-commit checks | ~1m |
| Security Scan | Bandit, Safety | ~1m |
| Build & Test | Python 3.11, 3.12, 3.13 | ~3m |
| Docker Build Test | Docker image build & run | ~2m |

**Total:** ~5-8 minutes (run in parallel)

---

## 🆘 Troubleshooting

### "I can't find the status checks"

**Problem:** No checks in the list to select

**Solution:**
1. Create test PR
2. Wait for CI to complete
3. Return to Branch Protection settings
4. Now checks should appear in search

### "My PR is blocked but all checks passed"

**Problem:** Can't merge, though everything is green

**Solution:**
- Check that correct check `All Checks Passed ✅` is selected
- Update branch (Merge/Rebase from main)
- Check there are no unresolved comments

### "I accidentally committed to main before protection"

**Problem:** Made commits to main before setup

**Solution:**
```bash
# Reset main to remote version
git fetch origin
git reset --hard origin/main

# Create feature branch with your changes
git checkout -b feature/my-changes
git cherry-pick <commit-hash>  # For each commit
git push origin feature/my-changes

# Create PR
```

---

## 🔗 Additional Materials

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [WORKFLOW.md](./WORKFLOW.md) - Detailed Git workflow
- [CI_CD.md](./CI_CD.md) - How CI checks work

---

**Done! 🎉 Now `main` is protected, and all changes go through PRs.**
