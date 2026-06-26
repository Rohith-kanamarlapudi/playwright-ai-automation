from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

# Initialize DeepSeek once
llm = get_llm()


def edge_cases_agent(state: AgentState) -> AgentState:
    """
    Edge Cases Agent:
    Generates comprehensive edge cases for the generated
    Playwright automation suite.
    """

    tracker = PerformanceTracker(label="edge_cases_agent")
    tracker.start()

    try:

        print("[Edge Cases Agent] Running...")

        selectors = state.get("selectors", {})

        buttons = selectors.get("buttons", [])
        inputs = selectors.get("inputs", [])
        links = selectors.get("links", [])

        prompt = f"""
You are a Senior QA Engineer specializing in Python Playwright automation.

Your task is to generate comprehensive edge case scenarios.

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

Generated Playwright Code:
{state["generated_code"]}

Instructions:

1. Analyze ONLY the detected website elements.
2. Do NOT invent features that are not present.
3. Generate important edge cases covering:

   • Empty inputs
   • Invalid inputs
   • Boundary values
   • Maximum input lengths
   • Special characters
   • SQL Injection
   • XSS
   • Network failures
   • Browser compatibility
   • Session timeout
   • Multiple browser tabs
   • Responsive layouts
   • Accessibility
   • Slow page loading
   • Broken links
   • Missing elements

4. Return ONLY one edge case per line.
5. Do NOT number the list.
"""

        response = llm.invoke(prompt)

        text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        edge_cases = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            line = line.lstrip("-•0123456789. ").strip()

            if line:
                edge_cases.append(line)

        state["edge_cases"] = edge_cases

        print(
            f"[Edge Cases Agent] {len(edge_cases)} edge cases generated."
        )

    except Exception as e:

        print(f"[Edge Cases Agent] Error: {e}")

        state["edge_cases"] = [
            f"Edge case generation failed: {e}"
        ]

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state