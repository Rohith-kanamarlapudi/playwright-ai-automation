from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker
from agents.prompts.strategy_prompt import STRATEGY_PROMPT

llm = get_llm()


def strategy_agent(state: AgentState) -> AgentState:

    tracker = PerformanceTracker(label="strategy_agent")
    tracker.start()

    try:
        print("[Strategy Agent] Running...")

        selectors = state.get("selectors", [])

        buttons = [s for s in selectors if s.get("type") == "button"]
        inputs = [s for s in selectors if s.get("type") == "input"]
        links = [s for s in selectors if s.get("type") == "link"]

        prompt = STRATEGY_PROMPT.format(
            design_doc=state["design_doc"],
            buttons=buttons,
            inputs=inputs,
            links=links
        )

        response = llm.invoke(prompt)

        text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

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

        for i, task in enumerate(task_plan, start=1):
            print(f"{i}. {task}")

    except Exception as e:

        print("[Strategy Error]", e)

        state["task_plan"] = []

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state