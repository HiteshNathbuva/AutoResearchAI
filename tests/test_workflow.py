"""
Test the Workflow Orchestrator.

Run:
    python -m tests.test_workflow
"""

from backend.core.workflow import WorkflowOrchestrator


def main():
    workflow = WorkflowOrchestrator()

    query = "Explain what AI Agents are in simple terms."

    state = workflow.execute_pipeline(query)

    print("\n" + "=" * 70)
    print("WORKFLOW OUTPUT")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("USER QUERY")
    print("=" * 70)
    print(state.query)

    print("\n" + "=" * 70)
    print("RESEARCH PLAN")
    print("=" * 70)
    print(state.plan)

    print("\n" + "=" * 70)
    print("RESEARCH")
    print("=" * 70)
    print(state.research)

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(state.verification)

    print("\n" + "=" * 70)
    print("COMPLETED TASKS")
    print("=" * 70)
    print(state.completed_tasks)


if __name__ == "__main__":
    main()