.PHONY: lint format check run clean test test-unit test-integration test-all

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

# Testing
test:
	@echo "⚠️  This runs ALL tests including OpenAI API calls (~\$$0.03)"
	@echo "Use 'make test-unit' to skip OpenAI tests"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		pytest tests/ -v; \
	fi

test-unit:
	@echo "🧪 Running unit tests (no OpenAI calls)..."
	pytest tests/ -v -m "not openai"

test-integration:
	@echo "🌐 Running integration tests (includes OpenAI API calls)..."
	@echo "⚠️  Cost: ~\$$0.03 for full suite"
	pytest tests/integration/ -v -m "openai"

test-all:
	@echo "🚀 Running ALL tests (unit + integration)..."
	pytest tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage report..."
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Pre-commit hooks
install-hooks:
	pre-commit install

run-hooks:
	pre-commit run --all-files

update-hooks:
	pre-commit autoupdate

# Docker commands (local)
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

# GitHub Container Registry (GHCR)
REGISTRY := ghcr.io
IMAGE_NAME := miron-s-playground/city-helper-ai-backend
TAG := latest

docker-login:
	@echo "Logging in to GitHub Container Registry..."
	@gh auth token | docker login $(REGISTRY) -u Mirong1707 --password-stdin

docker-build-push: docker-login
	docker build -t $(REGISTRY)/$(IMAGE_NAME):$(TAG) .
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)
	@echo "✅ Image pushed to $(REGISTRY)/$(IMAGE_NAME):$(TAG)"

docker-pull:
	docker pull $(REGISTRY)/$(IMAGE_NAME):$(TAG)

docker-run-remote:
	docker run -p 3001:3001 -e APP_ENV=production $(REGISTRY)/$(IMAGE_NAME):$(TAG)

docker-test-pipeline:
	@echo "🧪 Testing complete Docker pipeline..."
	@echo "\n1️⃣  Building image..."
	docker build -t city-helper-backend:test .
	@echo "\n2️⃣  Running local test..."
	docker run -d --name test-backend -p 3001:3001 city-helper-backend:test
	@echo "   Waiting for app to start (15 seconds)..."
	@sleep 15
	@curl -f http://localhost:3001/health && echo "\n✅ Local test passed" || (echo "\n❌ Local test failed" && docker logs test-backend)
	@docker stop test-backend && docker rm test-backend
	@echo "\n3️⃣  Tagging for registry..."
	docker tag city-helper-backend:test $(REGISTRY)/$(IMAGE_NAME):test
	@echo "\n4️⃣  Pushing to registry..."
	docker push $(REGISTRY)/$(IMAGE_NAME):test
	@echo "\n5️⃣  Cleaning local images..."
	docker rmi city-helper-backend:test || true
	docker rmi $(REGISTRY)/$(IMAGE_NAME):test || true
	@echo "\n6️⃣  Pulling from registry..."
	docker pull $(REGISTRY)/$(IMAGE_NAME):test
	@echo "\n7️⃣  Running from registry..."
	docker run -d --name test-remote -p 3001:3001 $(REGISTRY)/$(IMAGE_NAME):test
	@echo "   Waiting for app to start (15 seconds)..."
	@sleep 15
	@curl -f http://localhost:3001/health && echo "\n✅ Remote test passed" || (echo "\n❌ Remote test failed" && docker logs test-remote)
	@echo "\n8️⃣  Viewing logs..."
	@docker logs test-remote | tail -10
	@echo "\n9️⃣  Cleaning up..."
	@docker stop test-remote && docker rm test-remote
	@echo "\n🎉 Pipeline test complete!"

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
	@echo "Testing:"
	@echo "  make test              - Run all tests (with confirmation)"
	@echo "  make test-unit         - Run only unit tests (no API calls)"
	@echo "  make test-integration  - Run integration tests (OpenAI API calls)"
	@echo "  make test-all          - Run all tests without confirmation"
	@echo "  make test-coverage     - Run tests with coverage report"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make install-hooks     - Install pre-commit hooks"
	@echo "  make run-hooks         - Run pre-commit on all files"
	@echo "  make update-hooks      - Update pre-commit hooks"
	@echo ""
	@echo "Docker (Local):"
	@echo "  make docker-build         - Build Docker image"
	@echo "  make docker-run           - Run Docker container"
	@echo "  make docker-compose-up    - Start all services"
	@echo "  make docker-compose-down  - Stop all services"
	@echo "  make docker-compose-logs  - View backend logs"
	@echo "  make docker-clean         - Clean Docker resources"
	@echo ""
	@echo "GitHub Container Registry:"
	@echo "  make docker-login         - Login to GHCR (via GitHub CLI)"
	@echo "  make docker-build-push    - Build and push to GHCR"
	@echo "  make docker-pull          - Pull from GHCR"
	@echo "  make docker-run-remote    - Run image from GHCR"
	@echo "  make docker-test-pipeline - Test complete pipeline (build→push→pull→run)"
