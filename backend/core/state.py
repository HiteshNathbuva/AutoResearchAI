"""Shared, serializable state passed through the research workflow."""

from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkflowState:
    def __init__(self, query: str = ""):
        self.query = query
        self.user_query = query
        self.plan = ""
        self.research = ""
        self.research_notes = ""
        self.verification = ""
        self.final_report = ""
        self.status = "Initialized"
        self.confidence = "Unverified"
        self.reading_time = 0
        self.memory = {}
        self.completed_tasks = []
        self.current_step = "Initialized"
        timestamp = _now()
        self.metadata = {"created_at": timestamp, "updated_at": timestamp}

    def _update_timestamp(self):
        self.metadata["updated_at"] = _now()

    def update_query(self, query: str):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        self.query = query.strip()
        self.user_query = self.query
        self._update_timestamp()

    def update_plan(self, plan: str):
        self.plan = plan
        self._update_timestamp()

    def add_research_note(self, note: str):
        self.research = note
        self.research_notes = note
        self._update_timestamp()

    def update_verification(self, verification: str):
        self.verification = verification
        self._update_timestamp()

    def set_final_report(self, report: str):
        self.final_report = report
        self._update_timestamp()

    def update_status(self, status: str):
        self.status = status
        self._update_timestamp()

    def set_confidence(self, confidence: str):
        self.confidence = confidence
        self._update_timestamp()

    def set_reading_time(self, minutes: int):
        self.reading_time = max(1, minutes)
        self._update_timestamp()

    def mark_task_complete(self, task_name: str):
        if task_name not in self.completed_tasks:
            self.completed_tasks.append(task_name)
        self.current_step = task_name
        self._update_timestamp()

    def to_dict(self):
        return {"query": self.query, "plan": self.plan, "research": self.research,
                "verification": self.verification, "final_report": self.final_report,
                "status": self.status, "confidence": self.confidence,
                "reading_time": self.reading_time, "current_step": self.current_step,
                "completed_tasks": self.completed_tasks,
                "created_at": self.metadata["created_at"], "updated_at": self.metadata["updated_at"]}

    @classmethod
    def from_dict(cls, data):
        state = cls(data.get("query", ""))
        state.plan = data.get("plan", "")
        state.research = data.get("research", "")
        state.research_notes = state.research
        state.verification = data.get("verification", "")
        state.final_report = data.get("final_report", "")
        state.status = data.get("status", "Initialized")
        state.confidence = data.get("confidence") or "Unverified"
        state.reading_time = data.get("reading_time") or 0
        state.current_step = data.get("current_step", "Initialized")
        state.completed_tasks = data.get("completed_tasks", [])
        state.metadata = {"created_at": data.get("created_at") or _now(),
                          "updated_at": data.get("updated_at") or _now()}
        return state
