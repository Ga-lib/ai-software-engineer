"""
Entry point for the Multi-Agent AI Software Engineer API.
This will grow to include agent routes, middleware, and startup/shutdown events.
"""

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A production-grade multi-agent system for AI-assisted software engineering.",
    version=settings.app_version,
)


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Simple liveness check used by monitoring and deployment platforms."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "debug_mode": settings.debug,
    }