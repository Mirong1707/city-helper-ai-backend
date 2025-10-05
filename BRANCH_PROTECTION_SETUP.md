# Branch Protection Setup Guide

## 🛡️ Защита `main` ветки

**Цель:** Запретить прямые push в `main`, все изменения только через Pull Request.

---

## ⚡ Quick Setup (5 минут)

### 1. Открой настройки Branch Protection

```bash
# Перейди в настройки репозитория
open https://github.com/Miron-s-playground/city-helper-ai-backend/settings/branches
```

Или вручную:
1. GitHub → Твой репозиторий
2. Settings → Branches (в левом меню)
3. Нажми **"Add branch protection rule"**

### 2. Заполни поля

**Branch name pattern:**
```
main
```

**Включи следующие опции:**

#### ✅ Require a pull request before merging
- ✅ Включи эту галочку
- **Require approvals:** 0 (для solo-разработки) / 1+ (для команды)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (опционально)

#### ✅ Require status checks to pass before merging
- ✅ Включи эту галочку
- ✅ Require branches to be up to date before merging

**Добавь required checks (важно!):**

Нажми "Search for status checks" и выбери:
- `Quick Validation`
- `Code Quality`
- `Pre-commit Hooks`
- `Security Scan`
- `Build & Test (Python 3.13)` (минимум одна версия Python)
- `Docker Build Test`
- `All Checks Passed ✅`

> **Примечание:** Эти checks появятся в списке ПОСЛЕ первого PR. Если их еще нет — создай тестовый PR, затем вернись к настройкам.

#### ✅ Require conversation resolution before merging
- ✅ Включи (если используешь code review)

#### ✅ Require linear history
- ✅ Включи (для чистой истории коммитов)

#### ✅ Do not allow bypassing the above settings
- ✅ Включи (даже admin'ы должны следовать правилам!)

#### ❌ Allow force pushes
- ❌ Выключено (по умолчанию)

#### ❌ Allow deletions
- ❌ Выключено (по умолчанию)

### 3. Сохрани

Нажми **"Create"** или **"Save changes"**

---

## ✅ Проверка настройки

### Тест 1: Попробуй push в main (должен заблокироваться)

```bash
# Попробуй сделать прямой push в main
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test: direct push"
git push

# Должна быть ошибка:
# remote: error: GH006: Protected branch update failed
```

**Если получил ошибку** → ✅ Настройка работает!

**Если push прошел** → ❌ Вернись к настройкам, проверь чекбоксы

### Тест 2: Создай PR (должен работать)

```bash
# Отмени прошлый коммит
git reset --hard origin/main

# Создай feature branch
git checkout -b test/branch-protection
echo "test via PR" >> test.txt
git add test.txt
git commit -m "test: via pull request"
git push origin test/branch-protection

# Перейди на GitHub и создай PR
```

✅ PR должен создаться, CI должен запуститься

---

## 📋 Рекомендуемые настройки

### Для Solo Developer (ты сейчас):

```yaml
Branch: main
Require pull request before merging: ✅ (0 approvals)
Require status checks: ✅ (all checks listed above)
Require linear history: ✅
Do not allow bypassing: ✅
```

### Для команды:

```yaml
Branch: main
Require pull request before merging: ✅ (1-2 approvals)
Require status checks: ✅ (all checks listed above)
Require conversation resolution: ✅
Require linear history: ✅
Do not allow bypassing: ✅
Restrict who can push: ✅ (только maintainers)
```

---

## 🔥 Экстренный доступ

Если ОЧЕНЬ нужно срочно push в main (не рекомендуется):

1. **Отключи Branch Protection:**
   - Settings → Branches → Edit rule
   - Временно отключи "Do not allow bypassing"
   - Save

2. **Сделай push**

3. **ОБЯЗАТЕЛЬНО включи обратно!**

---

## 🎓 Что это даёт?

### До Branch Protection:
```bash
git commit -m "fix typo"
git push origin main
# ✅ Прошло напрямую (опасно!)
```

### После Branch Protection:
```bash
git commit -m "fix typo"
git push origin main
# ❌ Заблокировано!

# Правильно:
git checkout -b fix/typo
git commit -m "fix: typo in documentation"
git push origin fix/typo
# Создай PR → CI проверит → Merge
```

---

## 📊 Статистика CI Checks

После настройки, на каждом PR будут запускаться:

| Check | Что проверяет | Время |
|-------|---------------|-------|
| Quick Validation | PR title format, conflicts | ~30s |
| Code Quality | Ruff linting & formatting | ~1m |
| Pre-commit Hooks | All pre-commit checks | ~1m |
| Security Scan | Bandit, Safety | ~1m |
| Build & Test | Python 3.11, 3.12, 3.13 | ~3m |
| Docker Build Test | Docker image build & run | ~2m |

**Total:** ~5-8 минут (запускаются параллельно)

---

## 🆘 Troubleshooting

### "I can't find the status checks"

**Проблема:** В списке нет checks для выбора

**Решение:**
1. Создай тестовый PR
2. Дождись завершения CI
3. Вернись в настройки Branch Protection
4. Теперь checks должны появиться в поиске

### "My PR is blocked but all checks passed"

**Проблема:** Не могу merge, хотя все зелёное

**Решение:**
- Проверь что выбран правильный чек `All Checks Passed ✅`
- Обнови ветку (Merge/Rebase from main)
- Проверь что нет неразрешенных комментариев

### "I accidentally committed to main before protection"

**Проблема:** Сделал коммиты в main до настройки

**Решение:**
```bash
# Откати main на remote версию
git fetch origin
git reset --hard origin/main

# Создай feature branch с твоими изменениями
git checkout -b feature/my-changes
git cherry-pick <commit-hash>  # Для каждого коммита
git push origin feature/my-changes

# Создай PR
```

---

## 🔗 Дополнительные материалы

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [WORKFLOW.md](./WORKFLOW.md) - Подробный Git workflow
- [CI_CD.md](./CI_CD.md) - Как работают CI checks

---

**Готово! 🎉 Теперь `main` защищён, и все изменения идут через PR.**
