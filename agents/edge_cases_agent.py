from agents.state import AgentState
from agents.llm_client import get_llm

# Initialize DeepSeek once
llm = get_llm()


def edge_cases_agent(state: AgentState) -> AgentState:
    print("[Edge Cases Agent] Running...")

    prompt = f"""
You are a Senior QA Engineer specializing in software testing.

Your task is to generate comprehensive edge cases for Playwright automation.

Website Requirements:
{state["design_doc"]}

Detected Website Elements:
{state["selectors"]}

Test Plan:
{state["task_plan"]}

Generated Playwright Code:
{state["generated_code"]}

Instructions:
1. Generate important edge case scenarios.
2. Cover:
   - Empty inputs
   - Invalid inputs
   - Boundary values
   - Network failures
   - Browser compatibility
   - Session handling
   - Authentication
   - Security (SQL Injection, XSS)
   - Performance
   - Responsive UI
   - Accessibility
3. Return ONLY one edge case per line.
Do not include numbering or explanations.
"""

    try:
        response = llm.invoke(prompt)

        edge_cases = [
            line.strip("-•1234567890. ")
            for line in response.content.splitlines()
            if line.strip()
        ]

        state["edge_cases"] = edge_cases

        print(f"[Edge Cases Agent] {len(edge_cases)} edge cases generated.")

    except Exception as e:
        print(f"[Edge Cases Agent] Error: {e}")

        state["edge_cases"] = [
            f"Edge case generation failed: {e}"
        ]

    return state