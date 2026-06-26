from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

llm = get_llm()


def review_agent(state: AgentState) -> AgentState:

    tracker = PerformanceTracker(label="review_agent")
    tracker.start()

    try:
        print("[Review Agent] Running...")

        code = state.get("generated_code", "")

        prompt = f"""
You are a Senior QA Automation Code Reviewer for Playwright (Python + Pytest).

Your task is to review the generated automation code.

Generated Code:
{code}

Check the following:

1. Assertion quality
2. Locator correctness (VERY IMPORTANT)
3. Wait strategies (avoid sleep)
4. Playwright best practices
5. Error handling
6. Code structure and readability
7. Missing test coverage
8. Flaky test risks
9. Security issues (if any)
10. Performance improvements

Rules:
- Be strict
- Be practical
- Focus on real execution issues
- Return clear structured feedback

Return format:

### Issues
- ...

### Improvements
- ...

### Risk Level (Low / Medium / High)
"""

        response = llm.invoke(prompt)

        state["review_notes"] = (
            response.content if hasattr(response, "content") else str(response)
        )

        print("[Review Agent] Review completed successfully.")

    except Exception as e:
        print("[Review Error]", e)

        state["review_notes"] = f"Review failed: {e}"

    finally:
        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state