"""FastAPI application initialization"""

import uuid

import logfire
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, chat_sessions, health
from app.core.config import settings
from app.core.logging_setup import configure_logging

# Configure logging on module import
configure_logging()
logger = structlog.get_logger()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application

    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Mock backend server for City Helper AI",
    )

    # Auto-instrument FastAPI (requests, timings, errors) if Logfire is enabled
    if settings.has_logfire():
        try:
            logfire.instrument_fastapi(app)
        except TypeError as e:
            # Known issue with version parameter - can be safely ignored
            # Logs are still sent correctly
            if "version" not in str(e):
                logger.warning("logfire_instrumentation_failed", error=str(e))
        except Exception as e:
            logger.warning("logfire_instrumentation_failed", error=str(e))

    # CORS middleware
    config = settings.config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )

    # Request logging middleware
    @app.middleware("http")
    async def bind_request_context(request: Request, call_next):
        """Bind per-request context for filtering in logs/UI"""
        structlog.contextvars.clear_contextvars()
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        logger.debug("request_started")

        try:
            response = await call_next(request)
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=None,  # FastAPI timing is handled by logfire
            )
            return response
        except Exception as exc:
            logger.exception("request_failed", error=str(exc))
            raise

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info(
            "application_startup",
            app_name=settings.app_name,
            version=settings.app_version,
            environment=settings.environment.value,
            debug=settings.debug,
            logfire_enabled=settings.has_logfire(),
        )

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("application_shutdown")

    # Register routes
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(chat_sessions.router)

    return app


# Create app instance
app = create_app()
