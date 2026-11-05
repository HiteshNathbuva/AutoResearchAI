"""Vercel Python Serverless entry point for the AutoResearchAI FastAPI backend.

This file is placed in the ``api/`` directory at the repository root so that
``vercel.json`` can reference it as the Function File for every ``/api/*``
route. It reuses the exact same FastAPI application
(:func:`backend.main.create_app`) that runs locally under uvicorn, so
behaviour stays identical between local development and deployment.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables before importing the backend (settings read .env).
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

if not os.getenv("OPENROUTER_API_KEY"):
    os.environ.setdefault("OPENROUTER_API_KEY", "serverless-deployment-key")

# Serverless filesystems are read-only except /tmp; keep SQLite there.
os.environ.setdefault("DATABASE_PATH", "/tmp/autoresearch.sqlite3")

from backend.main import create_app  # noqa: E402

app = create_app()


def handler(event, context):  # noqa: ARG001 - AWS Lambda proxy contract.
    """AWS Lambda / Vercel-style proxy handler for API Gateway v1/v2 events."""

    from mangum import Mangum  # optional dependency, only needed on serverless hosts

    _handler = Mangum(app, lifespan="off")
    return _handler(event, context)
