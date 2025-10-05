# Multi-stage build for smaller final image
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy dependencies from builder to system Python
COPY --from=builder /root/.local /usr/local

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser run.py .
COPY --chown=appuser:appuser .env/.env.example .env/.env

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3001/health')" || exit 1

# Run the application
CMD ["python", "run.py"]
