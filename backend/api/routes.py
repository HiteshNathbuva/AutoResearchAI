"""
API Routes

This module exposes the REST API endpoints for AutoResearchAI.
"""

from fastapi import APIRouter, HTTPException

from backend.core.session import session_manager
from backend.core.workflow import WorkflowOrchestrator

from backend.schemas.api import (
    ResearchRequest,
    ResearchResponse,
    VerificationResponse,
    ReportResponse,
)

router = APIRouter(tags=["AutoResearchAI"])

workflow = WorkflowOrchestrator()


# ==========================================================
# Quick Research
# ==========================================================

@router.post(
    "/research",
    response_model=ResearchResponse,
)
def research(request: ResearchRequest):
    """
    Execute quick research.
    """

    try:

        state = workflow.execute_pipeline(request.query)

        session_id = session_manager.create_session(state)

        return ResearchResponse(
            session_id=session_id,
            status=state.status,
            confidence=state.confidence,
            reading_time=state.reading_time,
            research=state.research,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# AI Fact Check
# ==========================================================

@router.post(
    "/verify/{session_id}",
    response_model=VerificationResponse,
)
def verify(session_id: str):
    """
    Verify an existing research session.
    """

    try:

        state = session_manager.get_session(session_id)

        state = workflow.verify_report(state)

        session_manager.update_session(session_id, state)

        return VerificationResponse(
            session_id=session_id,
            status=state.status,
            verification=state.verification,
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Professional Report
# ==========================================================

@router.post(
    "/report/{session_id}",
    response_model=ReportResponse,
)
def report(session_id: str):
    """
    Generate a professional report.
    """

    try:

        state = session_manager.get_session(session_id)

        state = workflow.generate_report(state)

        session_manager.update_session(session_id, state)

        return ReportResponse(
            session_id=session_id,
            status=state.status,
            report=state.final_report,
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )