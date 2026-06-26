from agents.state import AgentState
from agents.llm_client import get_llm

# Initialize DeepSeek once
llm = get_llm()


def architecture_agent(state: AgentState) -> AgentState:
    print("[Architecture Agent] Running...")

    selectors = state.get("selectors", {})

    buttons = selectors.get("buttons", [])
    inputs = selectors.get("inputs", [])
    links = selectors.get("links", [])

    prompt = f"""
You are a Senior Python Playwright Test Automation Architect.

Your task is to design a scalable Playwright automation framework for the given website.

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
4. Recommend Page Object Model (POM).
5. Include reusable fixtures.
6. Suggest utility modules.
7. Include configuration files.
8. Include reporting (pytest-html / Allure).
9. Include logging.
10. Include screenshots on failure.
11. Include folder structure.
12. Mention how selectors should be organized.
13. Keep the architecture suitable for medium to large automation projects.

Return the response in well-formatted Markdown.

Use the following headings:

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

    try:
        response = llm.invoke(prompt)

        state["architecture_notes"] = response.content

        print("[Architecture Agent] Architecture generated successfully.")

    except Exception as e:
        print(f"[Architecture Agent] Error: {e}")

        state["architecture_notes"] = (
            "# Architecture Generation Failed\n\n"
            f"Error: {e}"
        )

    return state