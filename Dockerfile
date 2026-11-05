# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 — build the static React SPA
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2 — FastAPI backend serving the API and the built SPA
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS backend

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    FRONTEND_DIST_DIR=/app/frontend/dist \
    DATABASE_PATH=/data/autoresearch.sqlite3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY prompts ./prompts
COPY --from=frontend /app/frontend/dist ./frontend/dist

RUN mkdir -p /data && \
    addgroup --system app && adduser --system --ingroup app app && \
    chown -R app:app /app /data
USER app

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
