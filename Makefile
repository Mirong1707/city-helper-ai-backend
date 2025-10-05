.PHONY: lint format check run clean

# Lint code
lint:
	ruff check app/

# Format code
format:
	ruff format app/

# Check code (lint + format check)
check:
	ruff check app/
	ruff format --check app/

# Fix all auto-fixable issues
fix:
	ruff check app/ --fix
	ruff format app/

# Run server
run:
	python run.py

# Clean cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Pre-commit hooks
install-hooks:
	pre-commit install

run-hooks:
	pre-commit run --all-files

update-hooks:
	pre-commit autoupdate

# Help
help:
	@echo "Available commands:"
	@echo "  make lint           - Check code with Ruff"
	@echo "  make format         - Format code with Ruff"
	@echo "  make check          - Lint + format check"
	@echo "  make fix            - Auto-fix all issues"
	@echo "  make run            - Start server"
	@echo "  make clean          - Clean cache files"
	@echo "  make install-hooks  - Install pre-commit hooks"
	@echo "  make run-hooks      - Run pre-commit on all files"
	@echo "  make update-hooks   - Update pre-commit hooks"
