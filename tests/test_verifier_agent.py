"""
Test Verifier Agent

Run:
    python -m tests.test_verifier_agent
"""

from backend.agents.verifier_agent import VerifierAgent


def main():

    verifier = VerifierAgent()

    research = """
Artificial Intelligence (AI) is a branch of computer science that
focuses on creating intelligent machines capable of performing
tasks that normally require human intelligence.

Applications include Healthcare,
Finance,
Education,
Transportation,
Robotics.

Advantages:
- Automation
- Better decision making
- Increased productivity

Challenges:
- Bias
- Privacy
- Job displacement
"""

    verification = verifier.execute(research)

    print("\n========== VERIFICATION REPORT ==========\n")

    print(verification)


if __name__ == "__main__":
    main()