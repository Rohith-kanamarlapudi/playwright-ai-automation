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

        selectors = state.get("selectors", {})

        buttons = selectors.get("buttons", [])
        inputs = selectors.get("inputs", [])
        links = selectors.get("links", [])

        prompt = STRATEGY_PROMPT.format(
            design_doc=state["design_doc"],
            buttons=buttons,
            inputs=inputs,
            links=links
        )

        response = llm.invoke(prompt)

        text = response.content if hasattr(response, "content") else str(response)

        task_plan = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            # clean numbering like 1. 2. -
            line = line.lstrip("-•0123456789. ").strip()

            if line:
                task_plan.append(line)

        state["task_plan"] = task_plan

        print("\n[Strategy Agent] Generated Test Plan:\n")

        for i, t in enumerate(task_plan, 1):
            print(f"{i}. {t}")

    except Exception as e:
        print("[Strategy Error]", e)
        state["task_plan"] = []

    finally:
        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state