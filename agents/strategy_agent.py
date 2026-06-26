from agents.state import AgentState
from agents.llm_client import get_llm

# Initialize the LLM once
llm = get_llm()


def strategy_agent(state: AgentState) -> AgentState:
    print("[Strategy Agent] Running...")

    selectors = state.get("selectors", {})

    buttons = selectors.get("buttons", [])
    inputs = selectors.get("inputs", [])
    links = selectors.get("links", [])

    prompt = f"""
You are an expert QA Test Strategy Agent specializing in Playwright automation.

Your goal is to generate a practical test strategy for the given website.

Website Description:
{state["design_doc"]}

Detected Website Elements

Buttons:
{buttons}

Inputs:
{inputs}

Links:
{links}

Instructions:

1. Analyze ONLY the detected website elements.
2. Do NOT invent features that are not present.
3. If there is no login form, do NOT generate login tests.
4. Generate Playwright test scenarios for:
   - Navigation
   - Buttons
   - Forms
   - Input validation
   - Links
   - Responsive UI
   - Accessibility
   - Error handling
5. Include both positive and negative test cases.
6. Prefer scenarios based on the detected selectors.
7. Return ONLY one test scenario per line.
Do not number the list.
"""

    try:
        response = llm.invoke(prompt)

        task_plan = []

        for line in response.content.splitlines():

            line = line.strip()

            if not line:
                continue

            line = line.lstrip("-•0123456789. ").strip()

            if line:
                task_plan.append(line)

        state["task_plan"] = task_plan

        print("\n[Strategy Agent] Generated Test Plan:\n")

        for i, task in enumerate(task_plan, start=1):
            print(f"{i}. {task}")

    except Exception as e:

        print(f"[Strategy Agent] Error: {e}")

        state["task_plan"] = []

    return state