from agents.state import AgentState


def strategy_agent(state: AgentState) -> AgentState:
    print("[Strategy Agent] Running...")

    state["task_plan"] = [
        "Test login flow",
        "Test form submission",
        "Test navigation links"
    ]

    print(f"[Strategy Agent] Task plan: {state['task_plan']}")
    return state