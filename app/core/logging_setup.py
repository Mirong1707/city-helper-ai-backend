"""Logging configuration with structlog + Logfire"""

import logfire
import structlog

from app.core.config import settings


def configure_logging():
    """
    Configure structured logging with Logfire integration.

    - Dev (no token): logs to console in JSON format
    - Prod (with token): sends logs/traces to Logfire cloud
    """
    # Send to Logfire cloud only if token is present (dev-safe)
    logfire_token = settings.get_logfire_token()
    send_to_logfire = bool(logfire_token)

    # Scrubbing configuration - smart protection of sensitive data
    # Hide real secrets (passwords, tokens in headers/body)
    # Do NOT hide common words in URL paths (e.g. "session" in /api/chat-sessions)
    from logfire import ScrubMatch

    def smart_scrubbing_callback(match: ScrubMatch) -> str | None:
        """
        Smart scrubbing: protects real secrets but doesn't interfere with development.

        Hides:
        - password/passwd/pwd in any fields
        - secret/api_key/apikey in any fields
        - token/authorization in headers and body

        Does NOT hide:
        - "session" in URL paths (it's just an endpoint name)
        - "token" in field names (only values)
        """
        # Get the path to the field (e.g., ('attributes', 'password'))
        path_parts = [str(p).lower() for p in match.path]

        # Get the field name (last part of path)
        field_name = path_parts[-1] if path_parts else ""

        # Get the value being checked
        value_str = str(match.value).lower() if match.value else ""

        # If this is a URL path containing "session" - don't hide it
        if "path" in path_parts and "session" in value_str:
            return None  # Don't scrub

        # Check field name for sensitive patterns
        # Hide passwords everywhere
        if any(keyword in field_name for keyword in ["password", "passwd", "pwd"]):
            return "[REDACTED]"

        # Hide secrets and API keys everywhere
        if any(keyword in field_name for keyword in ["secret", "api_key", "apikey", "token"]):
            return "[REDACTED]"

        # Hide authorization headers
        if "authorization" in field_name or "bearer" in field_name:
            return "[REDACTED]"

        # Leave everything else as is
        return None

    logfire.configure(
        send_to_logfire=send_to_logfire,
        token=logfire_token if send_to_logfire else None,
        environment=settings.environment.value,
        service_name=settings.app_name,
        scrubbing=logfire.ScrubbingOptions(
            callback=smart_scrubbing_callback,
            extra_patterns=[],  # Use only our custom callback
        ),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # merge request-bound context
            structlog.processors.add_log_level,  # adds "level" field
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            logfire.StructlogProcessor(),  # forward to Logfire (if enabled)
            structlog.processors.JSONRenderer(),  # JSON to console (stdout)
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger():
    """Get configured structlog logger instance"""
    return structlog.get_logger()
