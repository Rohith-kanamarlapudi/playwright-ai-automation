from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.strategy_agent import strategy_agent
from agents.architecture_agent import architecture_agent
from agents.code_gen_agent import code_gen_agent
from agents.review_agent import review_agent
from agents.edge_cases_agent import edge_cases_agent


def build_graph():
    graph = StateGraph(AgentState)

    # Add agent nodes
    graph.add_node("strategy", strategy_agent)
    graph.add_node("architecture", architecture_agent)
    graph.add_node("code_gen", code_gen_agent)
    graph.add_node("review", review_agent)
    graph.add_node("edge_cases", edge_cases_agent)

    # Define workflow
    graph.set_entry_point("strategy")
    graph.add_edge("strategy", "architecture")
    graph.add_edge("architecture", "code_gen")
    graph.add_edge("code_gen", "review")
    graph.add_edge("review", "edge_cases")
    graph.add_edge("edge_cases", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    initial_state: AgentState = {
        "design_doc": "A login page with username, password fields and submit button.",
        "selectors": [],
        "task_plan": [],
        "architecture_notes": "",
        "generated_code": "",
        "review_notes": "",
        "edge_cases": []
    }

    result = app.invoke(initial_state)

    print("\n========== FINAL STATE ==========\n")

    for key, value in result.items():
        print(f"{key}:")
        print(value)
        print("-" * 50)