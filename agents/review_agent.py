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

Review ONLY issues that would cause the generated Playwright tests to fail or become unreliable.

Generated Code:
{code}

Evaluate:

1. Assertion quality
2. Locator correctness
3. Wait strategies
4. Playwright best practices
5. Runtime errors
6. Syntax issues
7. Missing assertions
8. Invalid selectors
9. Flaky execution risks
10. Overall maintainability

IMPORTANT RULES

- Ignore formatting/style issues.
- Ignore cosmetic improvements.
- Do NOT recommend regeneration unless the code would likely fail execution.
- Only mark Critical Execution Issues as "Yes" for real execution failures.

Return EXACTLY in this format:

### Issues
- ...

### Improvements
- ...

### Critical Execution Issues
Yes / No

### Reason
...
"""

        response = llm.invoke(prompt)

        notes = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        state["review_notes"] = notes

        # -------------------------------------------------
        # Store review history
        # -------------------------------------------------

        history = state.get("review_history", [])
        history.append(notes)
        state["review_history"] = history

        print("\n" + "=" * 70)
        print("REVIEW REPORT")
        print("=" * 70)
        print(notes)
        print("=" * 70 + "\n")

        notes_lower = notes.lower()

        # -------------------------------------------------
        # Detect critical execution problems
        # -------------------------------------------------

        critical_keywords = [
            "syntax error",
            "invalid syntax",
            "indentationerror",
            "runtime error",
            "playwright error",
            "locator not found",
            "invalid locator",
            "broken test",
            "cannot execute",
            "execution will fail",
            "missing assertion",
            "no assertion",
        ]

        has_critical_keyword = any(
            keyword in notes_lower
            for keyword in critical_keywords
        )

        critical_execution = (
            "critical execution issues" in notes_lower
            and "yes" in notes_lower
        )

        state["needs_regen"] = (
            critical_execution or has_critical_keyword
        )

        if state["needs_regen"]:
            print("[Review Agent] Critical execution issues detected.")
            print("[Review Agent] Requesting regeneration.")
        else:
            print("[Review Agent] Review completed successfully.")
            print("[Review Agent] No regeneration required.")

    except Exception as e:

        print(f"[Review Error] {e}")

        state["review_notes"] = f"Review failed: {e}"

        state["needs_regen"] = False

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state