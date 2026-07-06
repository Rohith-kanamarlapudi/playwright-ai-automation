import json


def generate_python_directly(state, llm) -> str:
    """
    Fallback function used when YAML generation or validation fails.

    Generates Python Playwright + Pytest code directly from the
    task plan and detected website elements.
    """

    selectors = state.get("selectors", [])

    buttons = [s for s in selectors if s.get("type") == "button"]
    inputs = [s for s in selectors if s.get("type") == "input"]
    links = [s for s in selectors if s.get("type") == "link"]

    prompt = f"""
You are a Senior Python Playwright Automation Engineer.

Generate production-ready Playwright automation tests.

Website Requirements:
{state["design_doc"]}

Generated Test Plan:
{chr(10).join(state["task_plan"])}

Framework Architecture (follow this POM structure):
{state.get("architecture_notes", "No architecture provided.")}

Detected Buttons:
{json.dumps(buttons[:10], indent=2)}

Detected Inputs:
{json.dumps(inputs[:10], indent=2)}

Detected Links:
{json.dumps(links[:10], indent=2)}

Requirements:

1. Generate Python code only.
2. Use pytest.
3. Use Playwright sync API.
4. Import:

from playwright.sync_api import sync_playwright, expect

5. Create one test function per task.
6. Use page.goto().
7. Use page.click().
8. Use page.fill().
9. Use expect() assertions.
10. Use ONLY the detected selectors.
11. Do NOT invent selectors.
12. Do NOT use time.sleep().
13. Use Playwright waits when required.
14. Add comments where useful.
15. Produce runnable code.

Return ONLY Python code.

Do NOT return Markdown.
Do NOT use code fences.
Do NOT include explanations.
"""

    try:

        response = llm.invoke(prompt)

        return (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

    except Exception as e:

        print("[Python Fallback Error]", e)

        return f'''"""
Fallback code generation failed.

Error:
{e}
"""'''