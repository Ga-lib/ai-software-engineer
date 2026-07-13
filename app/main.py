"""
Entry point for the Multi-Agent AI Software Engineer API.
This will grow to include agent routes, middleware, and startup/shutdown events.
"""

import logging

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging_config import configure_logging

settings = get_settings()
configure_logging(debug=settings.debug)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="A production-grade multi-agent system for AI-assisted software engineering.",
    version=settings.app_version,
)


@app.on_event("startup")
async def on_startup() -> None:
    """Runs once when the application starts. Good place for startup logs/checks."""
    logger.info("Starting up '%s' v%s (debug=%s)", settings.app_name, settings.app_version, settings.debug)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Runs once when the application is shutting down."""
    logger.info("Shutting down '%s'", settings.app_name)


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Simple liveness check used by monitoring and deployment platforms."""
    logger.debug("Health check endpoint was called")
    return {
        "status": "ok",
        "service": settings.app_name,
        "debug_mode": settings.debug,
    }