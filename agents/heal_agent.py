# agents/heal_agent.py
"""
Healing Agent — reads real pytest failure output and patches
the generated test file to fix selector/assertion errors.
"""
import re
from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker
from agentlens.sdk import trace
@trace(name="heal_agent")
def parse_pytest_failures(stdout: str) -> list:
    """Extract test name + error message from pytest -v output."""
    failures = []
    # Match: FAILED test_xxx::test_login - Error: ...
    for match in re.finditer(
        r"FAILED\s+([^\s]+)\s+-\s+(.+)", stdout
    ):
        failures.append({
            "test": match.group(1).strip(),
            "error": match.group(2).strip(),
        })
    return failures


def heal_agent(state: AgentState) -> AgentState:
    """
    Reads execution failures from the last pytest run and
    asks the LLM to patch the generated code to fix them.
    Only runs if there are failures AND generated code exists.
    """
    tracker = PerformanceTracker(label="heal_agent")
    tracker.start()

    failures = state.get("execution_failures", [])
    code = state.get("generated_code", "")

    if not failures or not code:
        print("[Heal Agent] No failures to heal — skipping.")
        tracker.stop()
        return state
    
    if not code:
        print("[Heal Agent] No generated code found.")
        tracker.stop()
        return state

    print(f"[Heal Agent] Healing {len(failures)} test failure(s)...")
    llm = get_llm()

    failure_text = "\n".join(
        f"- {f['test']}: {f['error']}" for f in failures
    )

    prompt = f"""
You are an expert Playwright automation engineer.
Repair ONLY the failing tests.
Do NOT rewrite the entire file.


You are a Playwright expert fixing failing tests.

These tests are FAILING:
{failure_text}

Current test code:
```python
{code[:3000]}
```

Rules:
- Fix ONLY the failing tests.
- Do NOT modify passing tests.
- Preserve imports.
- Preserve formatting.
- Preserve helper functions.
- If the failure mentions "timeout", improve waits using page.wait_for_selector().
- If the failure mentions "strict mode violation", use locator().first().
- Return ONLY the corrected Python file."""

    response = llm.invoke(prompt)
    fixed_code = response.content if hasattr(response, "content") else str(response)

    # Strip markdown fences if present
    fixed_code = re.sub(
        r"^```python\s*|^```\s*|```$",
        "",
        fixed_code,
        flags=re.MULTILINE,
    ).strip()
    state["best_code"] = state.get("generated_code", "")
    state["generated_code"] = fixed_code
    state["needs_regen"] = False   # healing is a separate pass from review regen

    print(
        f"[Heal Agent] Successfully healed {len(failures)} failing test(s)."
    )
    tracker.stop()
    return state