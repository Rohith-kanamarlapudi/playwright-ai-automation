from agents.state import AgentState


def edge_cases_agent(state: AgentState) -> AgentState:
    print("[Edge Cases Agent] Running...")

    state["edge_cases"] = [
        "Empty form submission",
        "Invalid email",
        "Incorrect password",
        "Slow network",
        "Session timeout"
    ]

    print(f"[Edge Cases Agent] {len(state['edge_cases'])} edge cases found.")
    return state