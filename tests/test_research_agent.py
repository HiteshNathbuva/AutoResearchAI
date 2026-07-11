"""
Test the Research Agent.

Run:
    python -m tests.test_research_agent
"""

from backend.agents.research_agent import ResearchAgent


def main():
    agent = ResearchAgent()

    query = "What is Retrieval-Augmented Generation (RAG)? Explain in simple terms."

    response = agent.execute(query)

    print("\n========== Research Agent ==========\n")
    print(response)


if __name__ == "__main__":
    main()