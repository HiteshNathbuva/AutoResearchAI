"""REST API routes for research workflows and stored history."""

from typing import Type

from fastapi import APIRouter, HTTPException, Query

from backend.api.dependencies import SessionManagerDep, WorkflowDep
from backend.core.logger import get_logger
from backend.core.session import SessionManager
from backend.core.state import WorkflowState
from backend.core.workflow import WorkflowOrchestrator
from backend.schemas.api import (
    ReportResponse,
    ResearchRequest,
    ResearchResponse,
    SessionListResponse,
    SessionResponse,
    SessionSummary,
    VerificationResponse,
)

router = APIRouter(prefix="/api", tags=["AutoResearchAI"])
logger = get_logger(__name__)


def _response(session_id: str, state: WorkflowState,
              response_type: Type[SessionResponse] = SessionResponse) -> SessionResponse:
    data = state.to_dict()
    return response_type(session_id=session_id, status=data["status"], confidence=data["confidence"],
                         reading_time=data["reading_time"], research=data["research"], plan=data["plan"],
                         verification=data["verification"], report=data["final_report"],
                         completed_tasks=data["completed_tasks"], current_step=data["current_step"],
                         created_at=data["created_at"], updated_at=data["updated_at"])


def _not_found(session_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Research session '{session_id}' was not found.")


def _load_session(sessions: SessionManager, session_id: str) -> WorkflowState:
    try:
        return sessions.get_session(session_id)
    except KeyError as error:
        raise _not_found(session_id) from error


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest, workflow: WorkflowOrchestrator = WorkflowDep,
             sessions: SessionManager = SessionManagerDep):
    try:
        state = workflow.execute_pipeline(request.query)
        session_id = sessions.create_session(state)
        return _response(session_id, state, ResearchResponse)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        logger.exception("Research workflow failed")
        raise HTTPException(status_code=502,
                            detail="Research could not be completed. Please try again.") from error


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(limit: int = Query(default=50, ge=1, le=100),
                  sessions: SessionManager = SessionManagerDep):
    summaries = [SessionSummary(session_id=row["id"], query=row["query"], status=row["status"],
                 confidence=row["confidence"], reading_time=row["reading_time"],
                 created_at=row["created_at"], updated_at=row["updated_at"],
                 has_report=bool(row["has_report"])) for row in sessions.list_sessions(limit)]
    return SessionListResponse(sessions=summaries)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, sessions: SessionManager = SessionManagerDep):
    return _response(session_id, _load_session(sessions, session_id))


@router.post("/verify/{session_id}", response_model=VerificationResponse)
def verify(session_id: str, workflow: WorkflowOrchestrator = WorkflowDep,
           sessions: SessionManager = SessionManagerDep):
    state = _load_session(sessions, session_id)
    try:
        state = workflow.verify_report(state)
        sessions.update_session(session_id, state)
        return _response(session_id, state, VerificationResponse)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        logger.exception("Verification workflow failed")
        raise HTTPException(status_code=502,
                            detail="Verification could not be completed. Please try again.") from error


@router.post("/report/{session_id}", response_model=ReportResponse)
def report(session_id: str, workflow: WorkflowOrchestrator = WorkflowDep,
           sessions: SessionManager = SessionManagerDep):
    state = _load_session(sessions, session_id)
    try:
        state = workflow.generate_report(state)
        sessions.update_session(session_id, state)
        return _response(session_id, state, ReportResponse)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=502,
                            detail="The report could not be generated. Please try again.") from error
