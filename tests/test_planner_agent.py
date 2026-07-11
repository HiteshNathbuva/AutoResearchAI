"""
Test Planner Agent

Run:
    python -m tests.test_planner_agent
"""

from backend.agents.planner_agent import PlannerAgent


def main():
    agent = PlannerAgent()

    query = "Explain the impact of Artificial Intelligence in Healthcare."

    response = agent.execute(query)

    print("\n========== Research Plan ==========\n")
    print(response)


if __name__ == "__main__":
    main()