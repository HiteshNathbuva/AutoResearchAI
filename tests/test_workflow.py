"""
Test the Workflow Orchestrator.

Run:
    python -m tests.test_workflow
"""

from backend.core.workflow import WorkflowOrchestrator


def main():
    workflow = WorkflowOrchestrator()

    query = "Explain what AI Agents are in simple terms."

    # =====================================================
    # STEP 1 : QUICK RESEARCH (DEFAULT)
    # =====================================================

    state = workflow.execute_pipeline(query)

    print("\n" + "=" * 70)
    print("QUICK RESEARCH")
    print("=" * 70)

    print(f"\nStatus      : {state.status}")
    print(f"Confidence  : {state.confidence}")
    print(f"Reading Time: {state.reading_time} min")

    print("\n" + "=" * 70)
    print("RESEARCH OUTPUT")
    print("=" * 70)

    print(state.research)

    # =====================================================
    # STEP 2 : OPTIONAL DEEP VERIFICATION
    # =====================================================

    verify = input(
        "\nDo you want to perform AI Fact Check? (y/n): "
    ).strip().lower()

    if verify == "y":

        state = workflow.verify_report(state)

        print("\n" + "=" * 70)
        print("VERIFIED REPORT")
        print("=" * 70)

        print(state.final_report)

    # =====================================================
    # STEP 3 : OPTIONAL PROFESSIONAL REPORT
    # =====================================================

    report = input(
        "\nGenerate Professional Report? (y/n): "
    ).strip().lower()

    if report == "y":

        state = workflow.generate_report(state)

        print("\n" + "=" * 70)
        print("PROFESSIONAL REPORT")
        print("=" * 70)

        print(state.final_report)

    # =====================================================
    # DEBUG INFO
    # =====================================================

    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)

    print(f"Completed Tasks : {state.completed_tasks}")
    print(f"Current Status  : {state.status}")


if __name__ == "__main__":
    main()