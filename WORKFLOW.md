# Git Workflow Guide

## 🎯 GitHub Flow (Recommended)

This project uses **GitHub Flow** — a simple and modern workflow for continuous deployment.

### Core Principles

1. **`main` branch** is always deployable
2. **Feature branches** for all changes
3. **Pull Requests** for code review
4. **Automated checks** before merge
5. **Deploy after merge**

---

## 🔄 Step-by-Step Workflow

### 1. Create a Feature Branch

Always create a new branch for your changes:

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Examples:
git checkout -b feature/add-user-profile
git checkout -b fix/auth-bug
git checkout -b docs/update-readme
```

### Branch Naming Convention

Use prefixes to indicate the type of change:

- `feature/` — new features
- `fix/` — bug fixes
- `docs/` — documentation
- `refactor/` — code refactoring
- `test/` — adding tests
- `chore/` — maintenance tasks
- `perf/` — performance improvements

### 2. Make Changes

Work on your feature:

```bash
# Make changes
vim app/services/auth_service.py

# Stage changes
git add app/services/auth_service.py

# Commit with meaningful message
git commit -m "feat: add password reset functionality"
```

### Commit Message Format

Follow **Conventional Commits**:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation
- `style` — formatting, no code change
- `refactor` — code restructuring
- `perf` — performance improvement
- `test` — adding tests
- `build` — build system changes
- `ci` — CI/CD changes
- `chore` — maintenance

**Examples:**
```bash
git commit -m "feat: add user registration endpoint"
git commit -m "fix: resolve auth token expiration bug"
git commit -m "docs: update API documentation"
git commit -m "refactor: simplify chat service logic"
```

### 3. Push to GitHub

Push your branch:

```bash
git push origin feature/your-feature-name

# First time push (sets upstream)
git push -u origin feature/your-feature-name
```

### 4. Create Pull Request

On GitHub:

1. Go to your repository
2. Click **"Compare & pull request"** (appears after push)
3. Fill in PR details:
   - **Title:** Same format as commit messages
   - **Description:** Explain what and why
4. Click **"Create pull request"**

**PR Title Examples:**
```
feat: add user profile management
fix: resolve database connection timeout
docs: add Docker setup guide
```

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Changes
- Added feature X
- Fixed bug Y
- Updated docs Z

## Testing
- [ ] Tested locally
- [ ] All CI checks pass
- [ ] Reviewed code changes

## Related Issues
Closes #123
```

### 5. Automated Checks

After creating PR, GitHub Actions will automatically run:

1. **Code Quality** — Ruff linting & formatting
2. **Pre-commit Hooks** — All configured hooks
3. **Security Scan** — Bandit & Safety checks
4. **Build & Test** — Python 3.11, 3.12, 3.13
5. **Docker Test** — Build and smoke test

**All checks must pass before merge!**

### 6. Code Review (Optional)

If working in a team:

1. Request review from team members
2. Address feedback
3. Push additional commits if needed

```bash
# Make changes based on feedback
git add .
git commit -m "fix: address review comments"
git push
```

### 7. Merge Pull Request

When all checks pass:

1. Click **"Merge pull request"**
2. Choose merge strategy:
   - **Merge commit** (default) — keeps all commits
   - **Squash and merge** — combines into one commit
   - **Rebase and merge** — linear history

**Recommended:** Squash and merge for cleaner history

3. Delete branch after merge

### 8. Update Local Main

After merge:

```bash
git checkout main
git pull origin main
git branch -d feature/your-feature-name  # Delete local branch
```

---

## 🛡️ Branch Protection Rules

### Setting Up Protection

Go to:
```
GitHub → Settings → Branches → Add rule
```

### Recommended Rules for `main`:

1. **Require pull request before merging**
   - ✅ Enable
   - Require approvals: 1 (if team) / 0 (solo)

2. **Require status checks to pass**
   - ✅ Enable
   - Required checks:
     - `Quick Validation`
     - `Code Quality`
     - `Pre-commit Hooks`
     - `Security Scan`
     - `Build & Test (Python 3.13)`
     - `Docker Build Test`

3. **Require conversation resolution**
   - ✅ Enable (if using reviews)

4. **Require linear history**
   - ✅ Enable (cleaner history)

5. **Do not allow bypassing the above settings**
   - ✅ Enable (even admins follow rules)

6. **Allow force pushes**
   - ❌ Disable

7. **Allow deletions**
   - ❌ Disable

### Setting Up (Step-by-step)

**📚 Подробная инструкция:** [BRANCH_PROTECTION_SETUP.md](./BRANCH_PROTECTION_SETUP.md)

**Quick setup:**

```bash
# 1. Go to GitHub repository
open https://github.com/Miron-s-playground/city-helper-ai-backend/settings/branches

# 2. Click "Add branch protection rule"
# 3. Branch name pattern: main
# 4. Enable the checkboxes listed above
# 5. Add required status checks
# 6. Click "Create"
```

---

## 📝 Quick Reference

### Daily Workflow

```bash
# Start new feature
git checkout main
git pull
git checkout -b feature/my-feature

# Work on it
# ... make changes ...
git add .
git commit -m "feat: add feature"
git push -u origin feature/my-feature

# Create PR on GitHub
# Wait for checks to pass
# Merge PR

# Cleanup
git checkout main
git pull
git branch -d feature/my-feature
```

### Check Before Commit

```bash
# Run pre-commit hooks
make run-hooks

# Or manually
pre-commit run --all-files
```

### Check Before Push

```bash
# Run all checks locally
make lint        # Ruff linting
make format      # Ruff formatting
make run-hooks   # Pre-commit hooks
```

### If CI Fails

```bash
# Fix issues locally
make fix         # Auto-fix formatting
make run-hooks   # Run pre-commit

# Push fixes
git add .
git commit -m "fix: resolve CI issues"
git push
```

---

## 🚀 Best Practices

### 1. Small, Focused PRs

- One feature/fix per PR
- Easier to review
- Faster to merge

### 2. Keep Branch Up-to-Date

```bash
# If main has new commits while you work
git checkout feature/my-feature
git fetch origin
git rebase origin/main

# Or merge (if conflicts)
git merge origin/main
```

### 3. Draft PRs

For work in progress:

```bash
# Create draft PR on GitHub
# Mark as "Ready for review" when done
```

### 4. Descriptive Commits

```bash
# ✅ Good
git commit -m "feat: add user authentication with JWT"
git commit -m "fix: resolve memory leak in chat service"

# ❌ Bad
git commit -m "update"
git commit -m "fix"
git commit -m "wip"
```

### 5. Delete Merged Branches

Keep repository clean:

```bash
# Locally
git branch -d feature/merged-feature

# Remotely (if not auto-deleted)
git push origin --delete feature/merged-feature
```

---

## 🔍 Troubleshooting

### PR Checks Failing

**Problem:** CI checks fail on PR

**Solution:**
```bash
# Run checks locally
make lint
make format
make run-hooks

# Fix issues
make fix

# Push fixes
git push
```

### Merge Conflicts

**Problem:** Can't merge PR due to conflicts

**Solution:**
```bash
git checkout feature/my-feature
git fetch origin
git merge origin/main

# Resolve conflicts manually
# ... edit files ...

git add .
git commit -m "chore: resolve merge conflicts"
git push
```

### Branch Protection Blocks Merge

**Problem:** Can't merge even though checks passed

**Solution:**
- Check branch protection rules
- Ensure all required checks are selected
- Wait for all checks to complete

### Accidentally Pushed to Main

**Problem:** Committed directly to `main`

**Prevention:** Set up branch protection rules!

**Solution:**
```bash
# Revert the commit
git checkout main
git revert HEAD
git push

# Or reset (if not shared yet)
git reset --hard HEAD^
git push --force  # DANGEROUS! Only if nobody pulled
```

---

## 📚 Additional Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Writing Good Commit Messages](https://cbea.ms/git-commit/)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

---

## 🎓 Learning Path

### Week 1: Basics
- Create feature branches
- Make commits
- Create PRs

### Week 2: Intermediate
- Use conventional commits
- Handle merge conflicts
- Understand CI checks

### Week 3: Advanced
- Set up branch protection
- Optimize workflow
- Contribute to team projects

---

**Happy coding! 🚀**
