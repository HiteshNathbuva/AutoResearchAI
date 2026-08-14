"""Pydantic schemas exposed by the REST API."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=4000, description="User research query")


class SessionResponse(BaseModel):
    session_id: str
    status: str
    confidence: str
    reading_time: int
    research: str
    plan: str = ""
    verification: str = ""
    report: str = ""
    completed_tasks: List[str] = []
    current_step: str = ""
    created_at: str = ""
    updated_at: str = ""


class ResearchResponse(SessionResponse):
    pass


class VerificationResponse(SessionResponse):
    pass


class ReportResponse(SessionResponse):
    pass


class SessionSummary(BaseModel):
    session_id: str
    query: str
    status: str
    confidence: Optional[str] = None
    reading_time: Optional[int] = None
    created_at: str
    updated_at: str
    has_report: bool


class SessionListResponse(BaseModel):
    sessions: List[SessionSummary]
