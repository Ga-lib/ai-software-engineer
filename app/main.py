"""
Entry point for the Multi-Agent AI Software Engineer API.
This will grow to include agent routes, middleware, and startup/shutdown events.
"""

import logging

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.database.session import get_db

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


@app.get("/health/db", tags=["System"])
async def health_check_db(db: AsyncSession = Depends(get_db)) -> dict:
    """Verifies the app can actually talk to the Supabase PostgreSQL database."""
    result = await db.execute(text("SELECT 1"))
    value = result.scalar()
    logger.info("Database health check result: %s", value)
    return {"status": "ok", "database": "connected", "result": value}