"""
Simple test for verifying OpenRouter connection.

Run:
    python -m tests.test_llm
"""

from backend.core.llm import LLMClient


def main():
    print("=" * 60)
    print("Testing LLM Connection...")
    print("=" * 60)

    llm = LLMClient()

    messages = [
        {
            "role": "user",
            "content": "Say Hello! AutoResearchAI is connected successfully."
        }
    ]

    response = llm.chat(messages)

    print("\n✅ Response Received:\n")
    print(response)

    print("\n" + "=" * 60)
    print("LLM Test Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()