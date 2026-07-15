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

    # -------------------------------------------------
    # Live App Context (Week 3)
    # -------------------------------------------------

    # Target URL currently being tested
    target_url: str

    # Whether authentication is required for the target application
    auth_required: bool

    # True once the Angular SPA has fully loaded/hydrated
    spa_hydrated: bool
    
    # Prevent duplicate generation cycles
    duplicate_generation: bool
    
    
    # -------------------------------------------------
    # Test Execution Feedback (Self-Healing Loop)
    # -------------------------------------------------

    # Complete pytest stdout from the latest execution
    execution_stdout: str

    # Pytest return code (0 = success)
    execution_return_code: int

    # Parsed execution failures
    # Example:
    # [
    #     {
    #         "test": "test_login",
    #         "error": "Timeout 30000ms exceeded"
    #     }
    # ]
    execution_failures: List[Dict[str, Any]]