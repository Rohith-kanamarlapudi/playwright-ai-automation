from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker
import re

from agentlens.sdk import trace

@trace(name="review_agent")
def review_agent(state: AgentState) -> AgentState:
    tracker = PerformanceTracker(label="review_agent")
    tracker.start()

    try:
        llm = get_llm()

        print("[Review Agent] Running...")

        code = state.get("generated_code", "")
        
        if not code.strip():
            print("[Review Agent] No generated code to review.")
            state["review_notes"] = "No generated code available."
            state["needs_regen"] = True
            # regen_count is NOT incremented here — code_gen_agent is the
            # single place that does it, to avoid double-counting one cycle.
            print(
                f"[Review Agent] regen_count={state.get('regen_count', 0)}"
            )
            return state
        

        
        prompt = f"""
You are a Senior QA Automation Code Reviewer for Playwright (Python + Pytest).

Review ONLY issues that would cause the generated Playwright tests to fail or become unreliable.
Critical Generation Rules

Mark Critical Execution Issues as Yes if:

- More than one test performs login.
- Credentials are hardcoded.
- Username/password are filled in authenticated tests.
- CSS selectors are invented.
- CSS classes not present in the crawler output are used.
- auth.json is ignored.
- page.goto("/") is used for every workflow.


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
12. Authentication usage
13. SPA wait strategy
14. base_url usage
15. Duplicate waits
16. Unsupported Playwright actions
17. Incorrect popup handling
18. CRITICAL: Count the expect() assertions in the code. If any test function
    has zero expect() calls, set Critical Execution Issues to Yes.
    A test that never calls expect() cannot detect failures — it is not a real test.
19. Duplicate login flows
20. Hardcoded credentials
21. Invented selectors
22. Invented routes
23. Ignoring authenticated browser context
IMPORTANT RULES
Always mark Critical Execution Issues as Yes if any of these occur:

- expect_page() used without a popup.
- Hardcoded https:// URLs.
- Unsupported Playwright actions.
- Missing auth.json usage where required.
- No expect() assertions.
- Invalid selectors.
- Duplicate consecutive networkidle waits.

- Ignore formatting/style issues.
- Ignore cosmetic improvements.
- Do NOT recommend regeneration unless the code would likely fail execution.
- Only mark Critical Execution Issues as "Yes" for real execution failures.

Reject generated tests that
- call wait_for_widget() on hidden inputs
- call to_be_visible() on
input[type="hidden"]
Reject generated code if it contains:
#temperature-widget
#humidity-widget
#sensor-widget
#dashboard-card
#chart-widget
or comments containing
Assuming a
generic selector
Return EXACTLY in this format:

### Issues
- ...

### Improvements

For each issue, include a concrete fix.

Example:

Issue:
expect_page() used incorrectly.

Fix:
Replace with page.goto() followed by wait_for_live_data(page).

Issue:
Weak assertion.

Fix:
Replace expect(body) with expect(real_widget).to_be_visible().- ...

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
        MAX_HISTORY = 5
        state["review_history"] = history[-MAX_HISTORY:]
        print("\n" + "=" * 70)
        print("REVIEW REPORT")
        print("=" * 70)
        print(notes)
        print("=" * 70 + "\n")


        # -------------------------------------------------
        # Detect critical execution problems
        # -------------------------------------------------

        # Parse the structured section the prompt guarantees:
        # ### Critical Execution Issues\nYes / No
        critical_execution = False
        match = re.search(
            r"###\s*Critical Execution Issues\s*[\r\n]+\s*(Yes|No)\b",
            notes,
            re.IGNORECASE,
        )
        if match:
            critical_execution = match.group(1).lower() == "yes"
        else:
            # Fallback: look for the line in isolation to avoid false positives
            for line in notes.splitlines():
                stripped = line.strip().lower()
                if stripped in ("yes", "yes."):
                    critical_execution = True
                    break

        state["needs_regen"] = critical_execution
        print(f"[Review Agent] Critical Execution Issues: {critical_execution}")


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