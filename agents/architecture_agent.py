from agents.state import AgentState


def architecture_agent(state: AgentState) -> AgentState:
    print("[Architecture Agent] Running...")

    state["architecture_notes"] = """
    Application Structure:
    - Homepage
    - Authentication
    - Dashboard
    - Contact Form
    """

    print("[Architecture Agent] Architecture created.")
    return state