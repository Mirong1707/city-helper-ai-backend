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

# Docker commands
docker-build:
	docker build -t city-helper-backend:latest .

docker-run:
	docker run -p 3001:3001 --env-file .env/.env city-helper-backend:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f backend

docker-clean:
	docker-compose down -v
	docker system prune -f

# Help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              - Check code with Ruff"
	@echo "  make format            - Format code with Ruff"
	@echo "  make check             - Lint + format check"
	@echo "  make fix               - Auto-fix all issues"
	@echo ""
	@echo "Development:"
	@echo "  make run               - Start server (local)"
	@echo "  make clean             - Clean cache files"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make install-hooks     - Install pre-commit hooks"
	@echo "  make run-hooks         - Run pre-commit on all files"
	@echo "  make update-hooks      - Update pre-commit hooks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker image"
	@echo "  make docker-run        - Run Docker container"
	@echo "  make docker-compose-up - Start all services"
	@echo "  make docker-compose-down - Stop all services"
	@echo "  make docker-compose-logs - View backend logs"
	@echo "  make docker-clean      - Clean Docker resources"
