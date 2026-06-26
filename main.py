from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.strategy_agent import strategy_agent
from agents.architecture_agent import architecture_agent
from agents.code_gen_agent import code_gen_agent
from agents.review_agent import review_agent
from agents.edge_cases_agent import edge_cases_agent

from scraper.scraper import main as scrape_website
from performance.engine import PerformanceTracker

from pathlib import Path


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("strategy", strategy_agent)
    graph.add_node("architecture", architecture_agent)
    graph.add_node("code_gen", code_gen_agent)
    graph.add_node("review", review_agent)
    graph.add_node("edge_cases", edge_cases_agent)

    graph.set_entry_point("strategy")
    graph.add_edge("strategy", "architecture")
    graph.add_edge("architecture", "code_gen")
    graph.add_edge("code_gen", "review")
    graph.add_edge("review", "edge_cases")
    graph.add_edge("edge_cases", END)

    return graph.compile()


if __name__ == "__main__":

    Path("reports").mkdir(exist_ok=True)

    print("=" * 70)
    print("STEP 1: Running Website Scraper")
    print("=" * 70)

    selectors = scrape_website()

    if selectors is None:
        print("[Main] Scraper failed. Using empty selectors.")
        selectors = {"buttons": [], "inputs": [], "links": []}

    print("\n" + "=" * 70)
    print("STEP 2: Starting LangGraph Workflow")
    print("=" * 70)

    app = build_graph()

    initial_state: AgentState = {
        "design_doc": """
Generate Playwright automation tests for the website.

Requirements:
- Login functionality
- Form submission
- Navigation
- Validation
- Responsive UI
""",
        "selectors": selectors,
        "task_plan": [],
        "architecture_notes": "",
        "generated_code": "",
        "review_notes": "",
        "edge_cases": []
    }

    # --------------------------------------------
    # Performance Tracking
    # --------------------------------------------
    tracker = PerformanceTracker(label="full_pipeline_run")
    tracker.start()

    result = app.invoke(initial_state)

    metrics = tracker.stop(agents_completed=5)
    tracker.save("reports/perf_baseline.json")

    # --------------------------------------------
    # OUTPUT
    # --------------------------------------------
    print("\n" + "=" * 70)
    print("FINAL STATE")
    print("=" * 70)

    for key, value in result.items():
        print(f"\n{key}:")
        print(value)
        print("-" * 70)

    print("\nWorkflow completed successfully.")

    # --------------------------------------------
    # PERFORMANCE REPORT
    # --------------------------------------------
    print("\n" + "=" * 70)
    print("PERFORMANCE REPORT")
    print("=" * 70)

    for key, value in metrics.items():
        print(f"{key}: {value}")