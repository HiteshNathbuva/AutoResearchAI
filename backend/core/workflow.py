"""Sequential orchestration for the research agents."""

import re
from typing import Optional

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.verifier_agent import VerifierAgent
from backend.agents.writer_agent import WriterAgent
from backend.core.logger import get_logger
from backend.core.state import WorkflowState

logger = get_logger(__name__)

WORDS_PER_MINUTE = 200

#: Tolerates markdown emphasis and irregular spacing around the label/value,
#: e.g. "Confidence: High", "**Confidence:** High", "Confidence: **High**".
CONFIDENCE_PATTERN = re.compile(
    r"confidence\s*[:\-]?\s*[*_`\s]*\b(high|medium|low)\b",
    re.IGNORECASE,
)


class WorkflowOrchestrator:
    """Runs the research agents in a fixed sequence over a shared state."""

    def __init__(self, planner_agent: PlannerAgent, research_agent: ResearchAgent,
                 verifier_agent: VerifierAgent, writer_agent: WriterAgent):
        self.planner_agent = planner_agent
        self.research_agent = research_agent
        self.verifier_agent = verifier_agent
        self.writer_agent = writer_agent

    def execute_pipeline(self, query: str, state: Optional[WorkflowState] = None) -> WorkflowState:
        state = state or WorkflowState()
        state.update_query(query)

        state.update_status("Planning")
        state = self.planner_agent.execute(state)
        state.mark_task_complete("Planner")

        state.update_status("Researching")
        state = self.research_agent.execute(state)
        state.mark_task_complete("Research")

        state.update_status("Research completed")
        state.set_confidence("Unverified")
        state.set_reading_time(self._reading_time(state.research))
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
        state.set_reading_time(self._reading_time(state.final_report))
        return state

    def generate_report(self, state: WorkflowState) -> WorkflowState:
        if not state.research:
            raise ValueError("Research must be completed before generating a report.")

        state.update_status("Writing report")
        state = self.writer_agent.execute(state)
        state.mark_task_complete("Writer")

        state.update_status("Report generated")
        state.set_reading_time(self._reading_time(state.final_report))
        return state

    @staticmethod
    def _reading_time(text: str) -> int:
        return max(1, round(len((text or "").split()) / WORDS_PER_MINUTE))

    @staticmethod
    def _confidence_from_verification(verification: str) -> str:
        match = CONFIDENCE_PATTERN.search(verification or "")
        if match:
            return match.group(1).title()
        return "Unverified"
