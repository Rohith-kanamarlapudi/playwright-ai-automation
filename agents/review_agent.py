from agents.state import AgentState
from agents.llm_client import get_llm

# Initialize DeepSeek once
llm = get_llm()


def review_agent(state: AgentState) -> AgentState:
    print("[Review Agent] Running...")

    prompt = f"""
You are a Senior Playwright Automation Code Reviewer.

Review the following Playwright automation code.

Website Requirements:
{state["design_doc"]}

Generated Test Plan:
{state["task_plan"]}

Framework Architecture:
{state["architecture_notes"]}

Generated Playwright Code:
{state["generated_code"]}

Your review should cover:

1. Code Quality
2. Playwright Best Practices
3. Missing Assertions
4. Exception Handling
5. Wait Strategies
6. Locator Quality
7. Maintainability
8. Readability
9. Performance Improvements
10. Security Considerations

Return the review as well-formatted Markdown.

At the end include:
- Overall Rating (out of 10)
- Strengths
- Weaknesses
- Recommended Improvements
"""

    try:
        response = llm.invoke(prompt)

        state["review_notes"] = response.content

        print("[Review Agent] Review completed successfully.")

    except Exception as e:
        print(f"[Review Agent] Error: {e}")

        state["review_notes"] = (
            "# Review Failed\n\n"
            f"Error: {e}"
        )

    return state