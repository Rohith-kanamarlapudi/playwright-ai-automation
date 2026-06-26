from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

llm = get_llm()


def architecture_agent(state: AgentState) -> AgentState:

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

Your task is to design a scalable Playwright automation framework.

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
2. Follow the Page Object Model (POM).
3. Base the framework on the detected website elements.
4. Recommend reusable fixtures.
5. Suggest utility modules.
6. Include configuration files.
7. Include reporting (pytest-html / Allure).
8. Include logging.
9. Include screenshots on failure.
10. Suggest how selectors should be organized.
11. Keep the framework scalable for medium to large projects.

Return the response using the following sections:

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

        state["architecture_notes"] = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        print("[Architecture Agent] Architecture generated successfully.")

    except Exception as e:

        print("[Architecture Error]", e)

        state["architecture_notes"] = (
            f"Architecture generation failed.\nError: {e}"
        )

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state