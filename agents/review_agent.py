from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

# Initialize DeepSeek once
llm = get_llm()


def review_agent(state: AgentState) -> AgentState:
    """
    Review Agent:
    Reviews generated Playwright automation code and provides
    improvement suggestions.
    """

    tracker = PerformanceTracker(label="review_agent")
    tracker.start()

    try:

        print("[Review Agent] Running...")

        selectors = state.get("selectors", {})

        buttons = selectors.get("buttons", [])
        inputs = selectors.get("inputs", [])
        links = selectors.get("links", [])

        prompt = f"""
You are a Senior Python Playwright Automation Code Reviewer.

Review the generated automation framework.

Website Description:
{state["design_doc"]}

Detected Website Elements

Buttons:
{buttons}

Inputs:
{inputs}

Links:
{links}

Generated Test Plan:
{state["task_plan"]}

Framework Architecture:
{state["architecture_notes"]}

Generated Playwright Code:
{state["generated_code"]}

Review the following:

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

Return the review in Markdown.

At the end include:

- Overall Rating (/10)
- Strengths
- Weaknesses
- Recommended Improvements
"""

        response = llm.invoke(prompt)

        review = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        state["review_notes"] = review

        print("[Review Agent] Review completed successfully.")

    except Exception as e:

        print(f"[Review Agent] Error: {e}")

        state["review_notes"] = (
            "# Review Failed\n\n"
            f"Error: {e}"
        )

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state