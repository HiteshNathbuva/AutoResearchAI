"""Pydantic schemas exposed by the REST API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=4000, description="User research query")


class SessionResponse(BaseModel):
    session_id: str
    query: str = ""
    status: str
    confidence: str
    reading_time: int
    research: str
    plan: str = ""
    verification: str = ""
    report: str = ""
    completed_tasks: List[str] = []
    current_step: str = ""
    # Safe, user-visible failure detail (empty when the run has not failed).
    error: str = ""
    # Phase 2: additive source/diagnostic fields. These default to empty so
    # responses remain understandable to (and compatible with) older clients.
    sources: List[Dict[str, Any]] = []
    diagnostics: Dict[str, Any] = {}
    created_at: str = ""
    updated_at: str = ""


class ResearchResponse(SessionResponse):
    pass


class VerificationResponse(SessionResponse):
    pass


class ReportResponse(SessionResponse):
    pass


class JobAcceptedResponse(BaseModel):
    """Returned with HTTP 202 when a background job is accepted."""

    session_id: str
    status: str
    job_active: bool = True
    poll_url: str
    poll_interval_seconds: float = 1.5


class JobStatusResponse(SessionResponse):
    """Session payload plus whether a background job is still running."""

    job_active: bool = False


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
