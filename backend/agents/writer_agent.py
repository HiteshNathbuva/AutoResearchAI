"""
Writer Agent

Responsible for generating the final user-facing report.
"""

import re

from backend.core.agent import BaseAgent
from backend.core.state import WorkflowState

NO_VERIFICATION_CONTEXT = (
    "No verification was requested. Generate the report directly from the research."
)

# Patterns that indicate chain-of-thought or instruction leakage.
# Used only as a defensive layer after fixing prompts.
THINK_TAG_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
LEAKAGE_MARKERS = [
    "Here's a thinking process:",
    "Here's my thinking process:",
    "Thinking process:",
    "Analyze User Input",
    "Check Verification Status",
    "I think the safest is",
    "I'll use the 4 given",
    "I'll use the given",
]


def _sanitize_report(text: str) -> str:
    """Remove common chain-of-thought leakage patterns defensively.

    This is a safety net; primary fix is prompt hardening.
    """
    if not text:
        return text

    # Strip <think>...</think> blocks that some reasoning models emit
    cleaned = THINK_TAG_PATTERN.sub("", text)

    # Remove lines that are exactly leakage markers or contain them as standalone
    # reasoning headers. We keep the rest of the report intact.
    lines = cleaned.splitlines()
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are known leakage markers
        is_leakage = False
        for marker in LEAKAGE_MARKERS:
            if marker.lower() in stripped.lower() and len(stripped) < 200:
                # If line is short and contains marker, likely leakage
                # Check if line is mostly marker vs real content
                if stripped.lower().startswith(marker.lower()[:10]) or marker.lower() in stripped.lower():
                    # Heuristic: if line looks like "Analyze User Input" alone or with colon
                    if len(stripped) < 100 or stripped.lower().startswith("here's a thinking"):
                        is_leakage = True
                        break
        if not is_leakage:
            filtered_lines.append(line)

    cleaned = "\n".join(filtered_lines)

    # Remove excessive blank lines introduced by stripping
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


class WriterAgent(BaseAgent):
    """
    AI agent responsible for generating the final report.
    """

    prompt_file = "writer.md"

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Writer Agent",
            role="Report Writer",
        )

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Generate the final report.

        Args:
            state: Shared workflow state.

        Returns:
            WorkflowState: State updated with the final report.
        """

        self.require_valid(state)

        if not state.research:
            raise ValueError("Research must be completed before generating a report.")

        verification_context = state.verification or NO_VERIFICATION_CONTEXT

        # Simplified user message to avoid triggering chain-of-thought.
        # Explicitly instruct to output only final report, no thinking.
        messages = self.build_messages(
            f"""User Query: {state.query}

Research Plan: {state.plan}

Research Output: {state.research}

Verification Result: {verification_context}

Task: Generate a professional report based on the research above. If verification recommends improvements, apply them silently. The report must be concise, professional, well-structured, easy to read, and suitable for export as Markdown, PDF or DOCX.

Output ONLY the final report, no thinking process, no meta commentary, no internal instructions.
"""
        )

        raw_report = self.llm.chat(messages)
        cleaned_report = _sanitize_report(raw_report)
        # Ensure we never return empty after sanitization; fallback to raw if over-filtered
        final_report = cleaned_report if cleaned_report.strip() else raw_report.strip()

        state.set_final_report(final_report)

        return state
