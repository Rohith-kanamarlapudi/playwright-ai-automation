from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    """
    Shared state passed between all LangGraph agents.
    """

    # -------------------------------------------------
    # Input
    # -------------------------------------------------

    # Design document / requirements
    design_doc: str

    # Website elements collected by the scraper
    selectors: List[Dict[str, Any]]

    # -------------------------------------------------
    # Strategy Agent
    # -------------------------------------------------

    # Generated task plan
    task_plan: List[str]

    # -------------------------------------------------
    # Architecture Agent
    # -------------------------------------------------

    # Framework architecture
    architecture_notes: str

    # -------------------------------------------------
    # Code Generation Agent
    # -------------------------------------------------

    # YAML generated from the task plan
    generated_yaml: str

    # YAML validation result
    yaml_validation: Dict[str, Any]

    # Final generated Playwright code
    generated_code: str

    # -------------------------------------------------
    # Review Agent
    # -------------------------------------------------

    # Review comments
    review_notes: str

    # True if regeneration is required
    needs_regen: bool

    # Number of regeneration attempts
    regen_count: int

    # History of all review comments
    review_history: List[str]

    # Best valid YAML generated so far
    best_yaml: str

    # Best valid Playwright code generated so far
    best_code: str

    # Whether the generated code passed syntax validation
    syntax_passed: bool

    # -------------------------------------------------
    # Edge Cases Agent
    # -------------------------------------------------

    # Generated edge cases
    edge_cases: List[str]