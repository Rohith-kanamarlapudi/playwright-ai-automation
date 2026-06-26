from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

# Initialize DeepSeek once
llm = get_llm()


def architecture_agent(state: AgentState) -> AgentState:
    """
    Architecture Agent:
    Designs a scalable Python Playwright automation framework
    based on the generated strategy and scraped website elements.
    """

    tracker = PerformanceTracker(label="architecture_agent")
    tracker.start()

    try:

        print("[Architecture Agent] Running...")

        selectors = state.get("selectors", {})

        buttons = selectors.get("buttons", [])
        inputs = selectors.get("inputs", [])
        links = selectors.get("links", [])

        prompt = f"""
You are a Senior Python Playwright Test Automation Architect.

Your task is to design a scalable Playwright automation framework
for the given website.

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

Requirements:

1. Design ONLY for Python + Playwright + Pytest.
2. Do NOT generate TypeScript or JavaScript architecture.
3. Base the framework on the detected website elements.
4. Recommend a Page Object Model (POM).
5. Include reusable fixtures.
6. Suggest utility modules.
7. Include configuration files.
8. Include reporting (pytest-html / Allure).
9. Include logging.
10. Capture screenshots on failures.
11. Recommend folder structure.
12. Explain selector organization.
13. Keep the architecture suitable for medium to large automation projects.

Return the response as well-formatted Markdown.

Use these headings:

# Project Structure

# Page Object Model

# Test Organization

# Fixtures

# Utilities

# Configuration

# Reporting

# Logging

# Best Practices
"""

        response = llm.invoke(prompt)

        text = response.content if hasattr(response, "content") else str(response)

        state["architecture_notes"] = text

        print("[Architecture Agent] Architecture generated successfully.")

    except Exception as e:

        print(f"[Architecture Agent] Error: {e}")

        state["architecture_notes"] = (
            "# Architecture Generation Failed\n\n"
            f"Error: {e}"
        )

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state