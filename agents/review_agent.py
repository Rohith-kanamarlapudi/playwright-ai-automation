from agents.state import AgentState


def review_agent(state: AgentState) -> AgentState:
    print("[Review Agent] Running...")

    state["review_notes"] = """
    Code Review:
    - Naming is consistent.
    - Missing exception handling.
    - Add more assertions.
    """

    print("[Review Agent] Review completed.")
    return state