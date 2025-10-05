"""Application entry point"""

import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    # Startup banner
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📝 API available at http://{settings.host}:{settings.port}/api")
    print(f"📚 Docs available at http://{settings.host}:{settings.port}/docs")
    print(f"🌍 Environment: {settings.environment.value}")
    print(f"🐛 Debug Mode: {settings.debug}")

    if settings.has_logfire():
        print("📊 Logfire: ENABLED (logs will be sent to cloud)")
    else:
        print("📊 Logfire: DISABLED (local logs only)")

    print(f"📝 Log Level: {settings.log_level}")
    print(f"🔄 Auto-reload: {settings.config.reload}")
    print("-" * 60)

    # Run server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.config.reload,
        access_log=False,  # Using structlog instead
        log_level=settings.log_level.lower(),
    )
