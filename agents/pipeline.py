from agents.state import AgentState
from main import build_graph

from scraper.scraper import main as crawl_site
from agents.scraper_adapter import build_selectors_from_crawl


def run_agent_pipeline(
    design_doc: str,
    target_url: str = None,
    selectors: list = None,
) -> dict:
    """
    Unified entry point for the LangGraph agent pipeline.
    Can be called from FastAPI, CLI, or other scripts.
    """

    # --------------------------------------------------
    # Scrape website if URL is provided
    # --------------------------------------------------
    if selectors is None and target_url:

        print(f"[Pipeline] Scraping {target_url}...")

        crawl_data = crawl_site(
            url=target_url,
            max_pages=5
        )

        if crawl_data:
            selectors = build_selectors_from_crawl(crawl_data)
        else:
            selectors = []

    elif selectors is None:

        selectors = []

    # --------------------------------------------------
    # Build LangGraph
    # --------------------------------------------------
    app = build_graph()

    initial_state: AgentState = {
        "design_doc": design_doc,
        "selectors": selectors,
        "task_plan": [],
        "architecture_notes": "",
        "generated_code": "",
        "review_notes": "",
        "edge_cases": []
    }

    result = app.invoke(initial_state)

    return {
        "task_plan": result.get("task_plan", []),
        "architecture_notes": result.get("architecture_notes", ""),
        "generated_code": result.get("generated_code", ""),
        "review_notes": result.get("review_notes", ""),
        "edge_cases": result.get("edge_cases", []),
        "selectors": result.get("selectors", [])
    }