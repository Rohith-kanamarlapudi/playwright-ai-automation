from pathlib import Path
import py_compile

from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker

from agents.prompts.yaml_prompt import YAML_PROMPT
from agents.python_fallback import generate_python_directly

from app.yaml_validator import validate_yaml
from app.yaml_to_playwright import convert_yaml_to_playwright

llm = get_llm()


def verify_generated_code(filepath: str) -> bool:
    """
    Verify that the generated Python code is syntactically valid.
    """
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"[Code Gen] Syntax check PASSED: {filepath}")
        return True

    except py_compile.PyCompileError as e:
        print(f"[Code Gen] Syntax check FAILED:\n{e}")
        return False


def code_gen_agent(state: AgentState) -> AgentState:
    tracker = PerformanceTracker(label="code_gen_agent")
    tracker.start()

    try:

        print("[Code Gen Agent] Running...")

        selectors = state.get("selectors", [])

        buttons = [
            s for s in selectors
            if s.get("type") == "button"
        ]

        inputs = [
            s for s in selectors
            if s.get("type") == "input"
        ]

        links = [
            s for s in selectors
            if s.get("type") == "link"
        ]

        # -------------------------------------------------
        # Step 1 : Generate YAML
        # -------------------------------------------------
        
        
        # If this is a regen pass, prepend review feedback to the task plan
        review_notes = state.get("review_notes", "")
        is_regen = state.get("needs_regen", False)
        regen_prefix = ""
        if is_regen and review_notes:
            regen_prefix = (
                f"PREVIOUS REVIEW FEEDBACK (fix these issues):\n{review_notes}\n\n"
            )
            print("[Code Gen Agent] Regen pass — injecting review feedback into prompt.")
            
            
            
        yaml_prompt = YAML_PROMPT.format(
            task_plan="\n".join(state.get("task_plan", [])),
            architecture_notes=state.get("architecture_notes", "No architecture provided."),
            buttons=buttons[:10],
            inputs=inputs[:10],
            links=links[:10]
        )

        yaml_response = llm.invoke(yaml_prompt)

        yaml_text = (
            yaml_response.content
            if hasattr(yaml_response, "content")
            else str(yaml_response)
        )

        state["generated_yaml"] = yaml_text

        print("\n" + "=" * 80)
        print("GENERATED YAML")
        print("=" * 80)
        print(yaml_text)
        print("=" * 80 + "\n")

        # -------------------------------------------------
        # Step 2 : Validate YAML
        # -------------------------------------------------

        validation = validate_yaml(yaml_text)

        state["yaml_validation"] = validation

        print(f"[Code Gen] YAML valid: {validation['valid']}")

        # -------------------------------------------------
        # Step 3 : YAML -> Playwright
        # -------------------------------------------------

        if validation["valid"]:

            # No selectors argument until the converter supports it
            playwright = convert_yaml_to_playwright(yaml_text)

            code = playwright.get("code", "")

            print(
                "[Code Gen] YAML successfully converted to Playwright."
            )

        else:

            print("[Code Gen] YAML validation failed.")
            print("[Code Gen] Falling back to direct Python generation...")

            code = generate_python_directly(
                state,
                llm
            )

        # -------------------------------------------------
        # Step 4 : Save generated code
        # -------------------------------------------------

        state["generated_code"] = code

        Path("generated_tests").mkdir(exist_ok=True)

        output_path = (
            Path("generated_tests")
            / "generated_test.py"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(code)

        print(f"[Code Gen] Script saved to {output_path}")

        # -------------------------------------------------
        # Step 5 : Syntax Check
        # -------------------------------------------------

        verify_generated_code(str(output_path))

    except Exception as e:

        print("[Code Gen Error]", e)

        state["generated_code"] = ""
        state["generated_yaml"] = ""
        state["yaml_validation"] = {
            "valid": False,
            "errors": [str(e)]
        }

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state