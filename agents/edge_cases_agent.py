from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

llm = get_llm()


def edge_cases_agent(state: AgentState) -> AgentState:

    tracker = PerformanceTracker(label="edge_cases_agent")
    tracker.start()

    try:
        print("[Edge Cases Agent] Running...")

        task_plan = state.get("task_plan", [])
        generated_code = state.get("generated_code", "")

        prompt = f"""
You are a Senior QA Automation Engineer specializing in Playwright testing.

Your task is to generate high-quality edge cases for the automation test suite.

Test Plan:
{task_plan}

Generated Playwright Code:
{generated_code}

Instructions:

Generate edge cases covering:

- Empty inputs
- Invalid inputs
- Boundary values
- Large data inputs
- Special characters
- SQL Injection attempts
- XSS attempts
- Network failures
- Slow response scenarios
- Browser compatibility issues
- Session expiration
- Authentication failures
- UI responsiveness issues
- Missing elements
- Click failures
- Form validation failures

Rules:
- One edge case per line
- No numbering
- No explanations
- Be practical and execution-focused
"""

        response = llm.invoke(prompt)

        text = response.content if hasattr(response, "content") else str(response)

        edge_cases = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            # clean numbering if model adds it
            line = line.lstrip("-•0123456789. ").strip()

            if line:
                edge_cases.append(line)

        state["edge_cases"] = edge_cases

        print(f"[Edge Cases Agent] Generated {len(edge_cases)} edge cases.")

    except Exception as e:

        print("[Edge Cases Error]", e)

        state["edge_cases"] = [
            f"Edge case generation failed: {e}"
        ]

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state