"""Sequential orchestration for the research agents."""

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.verifier_agent import VerifierAgent
from backend.agents.writer_agent import WriterAgent
from backend.core.state import WorkflowState


class WorkflowOrchestrator:
    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.verifier_agent = VerifierAgent()
        self.writer_agent = WriterAgent()

    def execute_pipeline(self, query: str) -> WorkflowState:
        state = WorkflowState()
        state.update_query(query)
        state.update_status("Planning")
        state.update_plan(self.planner_agent.execute(state.query))
        state.mark_task_complete("Planner")

        state.update_status("Researching")
        state = self.research_agent.execute(state)
        state.mark_task_complete("Research")
        state.update_status("Research completed")
        state.set_confidence("Unverified")
        state.set_reading_time(max(1, round(len(state.research.split()) / 200)))
        return state

    def verify_report(self, state: WorkflowState) -> WorkflowState:
        if not state.research:
            raise ValueError("Research must be completed before verification.")
        state.update_status("Verifying")
        state = self.verifier_agent.execute(state)
        state.mark_task_complete("Verification")
        state.update_status("Writing verified report")
        state = self.writer_agent.execute(state)
        state.mark_task_complete("Writer")
        state.update_status("Verified report generated")
        state.set_confidence(self._confidence_from_verification(state.verification))
        state.set_reading_time(max(1, round(len(state.final_report.split()) / 200)))
        return state

    def generate_report(self, state: WorkflowState) -> WorkflowState:
        if not state.research:
            raise ValueError("Research must be completed before generating a report.")
        state.update_status("Writing report")
        state = self.writer_agent.execute(state)
        state.mark_task_complete("Writer")
        state.update_status("Report generated")
        state.set_reading_time(max(1, round(len(state.final_report.split()) / 200)))
        return state

    @staticmethod
    def _confidence_from_verification(verification: str) -> str:
        lowered = verification.lower()
        for value in ("high", "medium", "low"):
            if f"confidence: {value}" in lowered:
                return value.title()
        return "Unverified"
