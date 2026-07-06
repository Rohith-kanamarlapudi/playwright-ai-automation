import json

from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker
from agents.prompts.strategy_prompt import STRATEGY_PROMPT
from agents.selector_utils import cap_selectors

llm = get_llm()


def strategy_agent(state: AgentState) -> AgentState:
    tracker = PerformanceTracker(label="strategy_agent")
    tracker.start()

    try:
        print("[Strategy Agent] Running...")

        selectors = state.get("selectors", [])

        # -------------------------------------------------
        # Remove selectors with empty text
        # -------------------------------------------------

        clean_selectors = []

        for selector in selectors:
            selector_value = str(selector.get("selector", ""))

            if (
                "has-text('')" in selector_value
                or 'has-text("")' in selector_value
            ):
                continue

            clean_selectors.append(selector)

        buttons = cap_selectors(
            [s for s in clean_selectors if s.get("type") == "button"],
            "buttons",
        )

        inputs = cap_selectors(
            [s for s in clean_selectors if s.get("type") == "input"],
            "inputs",
        )

        links = cap_selectors(
            [s for s in clean_selectors if s.get("type") == "link"],
            "links",
        )

        prompt = STRATEGY_PROMPT.format(
            design_doc=state["design_doc"],
            buttons=buttons,
            inputs=inputs,
            links=links,
        )

        response = llm.invoke(prompt)

        text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        ).strip()

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        try:

            task_plan = json.loads(text)

            if not isinstance(task_plan, list):
                raise ValueError("Expected JSON list.")

            task_plan = [
                str(task).strip()
                for task in task_plan
                if str(task).strip()
            ]

        except Exception:

            print(
                "[Strategy Agent] JSON parsing failed. "
                "Falling back to line parsing."
            )

            task_plan = []

            for line in text.splitlines():

                line = line.strip()

                if not line:
                    continue

                line = line.lstrip("-•0123456789. ").strip()

                if line:
                    task_plan.append(line)

        # -------------------------------------------------
        # Remove duplicate tasks while preserving order
        # -------------------------------------------------

        unique_tasks = []
        seen = set()

        for task in task_plan:

            normalized = task.lower().strip()

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_tasks.append(task)

        task_plan = unique_tasks

        state["task_plan"] = task_plan

        print("\n" + "=" * 70)
        print("GENERATED TASK PLAN")
        print("=" * 70)

        for i, task in enumerate(task_plan, start=1):
            print(f"{i}. {task}")

        print("=" * 70)
        print(f"Total Tasks: {len(task_plan)}")
        print("=" * 70 + "\n")

    except Exception as e:

        print(f"[Strategy Error] {e}")

        state["task_plan"] = []

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state