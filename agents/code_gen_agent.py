from pathlib import Path

from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker
from agents.prompts.code_gen_prompt import CODE_GEN_PROMPT

llm = get_llm()


def code_gen_agent(state: AgentState) -> AgentState:

    tracker = PerformanceTracker(label="code_gen_agent")
    tracker.start()

    try:
        print("[Code Gen Agent] Running...")

        selectors = state.get("selectors", [])

        buttons = [s for s in selectors if s.get("type") == "button"]
        inputs = [s for s in selectors if s.get("type") == "input"]
        links = [s for s in selectors if s.get("type") == "link"]

        prompt = CODE_GEN_PROMPT.format(
            task_plan=state["task_plan"],
            buttons=buttons,
            inputs=inputs,
            links=links,
            architecture_notes=state["architecture_notes"]
        )

        response = llm.invoke(prompt)

        code = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        state["generated_code"] = code

        # Create output directory if it doesn't exist
        Path("generated_tests").mkdir(exist_ok=True)

        # Save generated Playwright test
        output_path = Path("generated_tests") / "generated_test.py"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(state["generated_code"])

        print(f"[Code Gen Agent] Script saved to {output_path}")

    except Exception as e:

        print("[Code Gen Error]", e)

        state["generated_code"] = ""

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state