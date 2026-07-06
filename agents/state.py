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
    
    
    # Set to True by review_agent when risk is High → triggers regen
    needs_regen: bool

    # -------------------------------------------------
    # Edge Cases Agent
    # -------------------------------------------------

    # Generated edge cases
    edge_cases: List[str]