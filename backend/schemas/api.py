"""
API Schemas

Defines request and response models for the AutoResearchAI API.
"""

from pydantic import BaseModel, Field


# ==========================================================
# Request Models
# ==========================================================

class ResearchRequest(BaseModel):
    """
    Request model for research endpoint.
    """

    query: str = Field(
        ...,
        min_length=3,
        description="User research query"
    )


# ==========================================================
# Response Models
# ==========================================================

class ResearchResponse(BaseModel):
    """
    Response returned after research.
    """

    session_id: str
    status: str
    confidence: str
    reading_time: int
    research: str


class VerificationResponse(BaseModel):
    """
    Response returned after verification.
    """

    session_id: str
    status: str
    verification: str


class ReportResponse(BaseModel):
    """
    Response returned after report generation.
    """

    session_id: str
    status: str
    report: str