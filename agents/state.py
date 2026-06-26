from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    # Input document (design/requirements)
    design_doc: str

    # Elements scraped from the website
    selectors: List[Dict[str, Any]]

    # Planning agent output
    task_plan: List[str]

    # Architecture agent output
    architecture_notes: str

    # Code generation agent output
    generated_code: str

    # Code review agent output
    review_notes: str

    # Edge case analysis
    edge_cases: List[str]