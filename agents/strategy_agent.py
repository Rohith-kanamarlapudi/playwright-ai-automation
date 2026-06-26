from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

# Initialize the LLM once
llm = get_llm()


def strategy_agent(state: AgentState) -> AgentState:
    """
    Strategy Agent:
    Generates a Playwright test strategy based on the
    website description and scraped website elements.
    """

    tracker = PerformanceTracker(label="strategy_agent")
    tracker.start()

    try:

        print("[Strategy Agent] Running...")

        selectors = state.get("selectors", {})

        buttons = selectors.get("buttons", [])
        inputs = selectors.get("inputs", [])
        links = selectors.get("links", [])

        prompt = f"""
You are an expert QA Test Strategy Agent specializing in Python Playwright automation.

Your goal is to generate a practical Playwright testing strategy for the given website.

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
2. Do NOT invent pages or features that do not exist.
3. If there is no login form, do NOT generate login tests.
4. Generate Playwright test scenarios covering:

   • Navigation
   • Buttons
   • Forms
   • Input validation
   • Links
   • Responsive UI
   • Accessibility
   • Error handling
   • Browser compatibility

5. Include both positive and negative scenarios.
6. Prefer scenarios using the detected selectors.
7. Return ONLY one test scenario per line.
8. Do NOT number the list.
"""

        response = llm.invoke(prompt)

        text = response.content if hasattr(response, "content") else str(response)

        task_plan = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            line = line.lstrip("-•0123456789. ").strip()

            if line:
                task_plan.append(line)

        state["task_plan"] = task_plan

        print("\n[Strategy Agent] Generated Test Plan:\n")

        for index, task in enumerate(task_plan, start=1):
            print(f"{index}. {task}")

    except Exception as e:

        print(f"[Strategy Agent] Error: {e}")

        state["task_plan"] = []

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state