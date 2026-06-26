from pathlib import Path

from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

# Initialize DeepSeek once
llm = get_llm()


def code_gen_agent(state: AgentState) -> AgentState:
    """
    Code Generation Agent:
    Generates production-ready Python Playwright automation code.
    """

    tracker = PerformanceTracker(label="code_gen_agent")
    tracker.start()

    try:

        print("[Code Generation Agent] Running...")

        selectors = state.get("selectors", {})

        buttons = selectors.get("buttons", [])
        inputs = selectors.get("inputs", [])
        links = selectors.get("links", [])

        prompt = f"""
You are a Senior Python Playwright Automation Engineer.

Generate production-ready Playwright automation code.

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

Requirements:

1. Generate Python code only.
2. Use Playwright with pytest.
3. Use the detected selectors whenever possible.
4. Do NOT invent selectors.
5. Follow the Page Object Model.
6. Add meaningful assertions.
7. Handle waits correctly.
8. Add comments where useful.
9. Produce runnable code.
10. Return ONLY Python code.
11. Do NOT return Markdown.

Return only code.
"""

        response = llm.invoke(prompt)

        generated_code = (
            response.content
            if hasattr(response, "content")
            else str(response)
        ).strip()

        state["generated_code"] = generated_code

        Path("generated_tests").mkdir(exist_ok=True)

        with open(
            "generated_tests/test_generated.py",
            "w",
            encoding="utf-8"
        ) as file:
            file.write(generated_code)

        print("[Code Generation Agent] Playwright code generated successfully.")
        print("[Code Generation Agent] Saved to generated_tests/test_generated.py")

    except Exception as e:

        print(f"[Code Generation Agent] Error: {e}")

        state["generated_code"] = (
            "# Code generation failed\n"
            f"# Error: {e}"
        )

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state