"""
Main Entry Point

This module initializes the FastAPI application and serves as the
entry point for the AutoResearchAI backend.

Responsibilities:
- Create the FastAPI application
- Configure application metadata
- Register API routes
- Start the backend server
"""

from fastapi import FastAPI

from backend.core.config import settings

# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade Multi-Agent Research Platform",
)


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/")
def root():
    """
    Health check endpoint.

    Returns:
        Basic API information.
    """

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Welcome to AutoResearchAI API 🚀",
    }