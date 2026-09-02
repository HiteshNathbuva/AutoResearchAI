"""Shared, serializable state passed through the research workflow."""

from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkflowState:
    """Mutable state carried through the agent pipeline."""

    def __init__(self, query: str = ""):
        self.query = query
        self.plan = ""
        self.research = ""
        self.verification = ""
        self.final_report = ""
        self.status = "Initialized"
        self.confidence = "Unverified"
        self.reading_time = 0
        self.memory: Dict[str, Any] = {}
        self.completed_tasks: List[str] = []
        self.current_step = "Initialized"
        timestamp = _now()
        self.metadata = {"created_at": timestamp, "updated_at": timestamp}

    # ------------------------------------------------------------------
    # Backwards-compatible aliases (deprecated, kept for existing callers)
    # ------------------------------------------------------------------

    @property
    def user_query(self) -> str:
        """Deprecated alias for :attr:`query`."""

        return self.query

    @property
    def research_notes(self) -> str:
        """Deprecated alias for :attr:`research`."""

        return self.research

    def _update_timestamp(self) -> None:
        self.metadata["updated_at"] = _now()

    def update_query(self, query: str) -> None:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        self.query = query.strip()
        self._update_timestamp()

    def update_plan(self, plan: str) -> None:
        self.plan = plan
        self._update_timestamp()

    def add_research_note(self, note: str) -> None:
        self.research = note
        self._update_timestamp()

    def update_verification(self, verification: str) -> None:
        self.verification = verification
        self._update_timestamp()

    def set_final_report(self, report: str) -> None:
        self.final_report = report
        self._update_timestamp()

    def update_status(self, status: str) -> None:
        self.status = status
        self._update_timestamp()

    def set_confidence(self, confidence: str) -> None:
        self.confidence = confidence
        self._update_timestamp()

    def set_reading_time(self, minutes: int) -> None:
        self.reading_time = max(1, minutes)
        self._update_timestamp()

    def mark_task_complete(self, task_name: str) -> None:
        if task_name not in self.completed_tasks:
            self.completed_tasks.append(task_name)
        self.current_step = task_name
        self._update_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {"query": self.query, "plan": self.plan, "research": self.research,
                "verification": self.verification, "final_report": self.final_report,
                "status": self.status, "confidence": self.confidence,
                "reading_time": self.reading_time, "current_step": self.current_step,
                "completed_tasks": list(self.completed_tasks),
                "created_at": self.metadata["created_at"], "updated_at": self.metadata["updated_at"]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        state = cls(data.get("query", "") or "")
        state.plan = data.get("plan") or ""
        state.research = data.get("research") or ""
        state.verification = data.get("verification") or ""
        state.final_report = data.get("final_report") or ""
        state.status = data.get("status") or "Initialized"
        state.confidence = data.get("confidence") or "Unverified"
        state.reading_time = data.get("reading_time") or 0
        state.current_step = data.get("current_step") or "Initialized"
        state.completed_tasks = list(data.get("completed_tasks") or [])
        state.metadata = {"created_at": data.get("created_at") or _now(),
                          "updated_at": data.get("updated_at") or _now()}
        return state
