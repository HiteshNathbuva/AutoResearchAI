"""
Test the Workflow Orchestrator.

Run:
    python -m tests.test_workflow
"""

from backend.core.workflow import WorkflowOrchestrator


def main():
    workflow = WorkflowOrchestrator()

    query = "Explain what AI Agents are in simple terms."

    response = workflow.execute_pipeline(query)

    print("\n========== Workflow Output ==========\n")
    print(response)


if __name__ == "__main__":
    main()