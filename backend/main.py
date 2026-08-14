"""FastAPI entry point for AutoResearchAI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
              description="Multi-agent research platform")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.get("/")
def root():
    return {"application": settings.APP_NAME, "version": settings.APP_VERSION,
            "status": "running", "api": "/docs"}
