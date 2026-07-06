# tests/test_core.py
"""
Unit tests for the framework's own pure functions.
No LLM calls — these run fast and reliably in CI.
"""
import pytest
from agents.selector_utils import cap_selectors, prioritise_selectors, SELECTOR_CAP
from agents.scraper_adapter import build_selectors_from_crawl
from app.yaml_validator import validate_yaml


# ─────────────────────────────────────────────
# selector_utils
# ─────────────────────────────────────────────

class TestSelectorUtils:
    def test_cap_selectors_respects_limit(self):
        items = [{"type": "button", "selector": f"#btn{i}", "text": ""} for i in range(30)]
        result = cap_selectors(items, "buttons")
        assert len(result) <= SELECTOR_CAP

    def test_id_selectors_ranked_first(self):
        items = [
            {"selector": "button:has-text('Click')", "type": "button"},
            {"selector": "#submit-btn", "type": "button"},
            {"selector": "input[name='user']", "type": "input"},
        ]
        ranked = prioritise_selectors(items)
        assert ranked[0]["selector"] == "#submit-btn"

    def test_empty_list_returns_empty(self):
        assert cap_selectors([], "buttons") == []


# ─────────────────────────────────────────────
# scraper_adapter
# ─────────────────────────────────────────────

class TestScraperAdapter:
    def test_builds_flat_list(self):
        crawl_data = [
            {
                "url": "https://example.com",
                "buttons": [{"selector": "#login", "text": "Login"}],
                "inputs": [{"selector": "#email", "type": "email", "placeholder": ""}],
                "links": [],
            }
        ]
        result = build_selectors_from_crawl(crawl_data)
        assert len(result) == 2
        types = {s["type"] for s in result}
        assert types == {"button", "input"}

    def test_empty_crawl_returns_empty(self):
        assert build_selectors_from_crawl([]) == []


# ─────────────────────────────────────────────
# yaml_validator
# ─────────────────────────────────────────────

class TestYamlValidator:
    VALID_YAML = """
test_cases:
  - id: TC001
    title: Login Test
    priority: High
    steps:
      - Open login page
      - Enter username
      - Verify dashboard visible
    expected_result: User is logged in
"""

    def test_valid_yaml_passes(self):
        result = validate_yaml(self.VALID_YAML)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_missing_id_fails(self):
        bad = self.VALID_YAML.replace("id: TC001", "")
        result = validate_yaml(bad)
        assert result["valid"] is False

    def test_empty_steps_fails(self):
        bad = self.VALID_YAML.replace(
            "steps:\n      - Open login page\n      - Enter username\n      - Verify dashboard visible",
            "steps: []"
        )
        result = validate_yaml(bad)
        assert result["valid"] is False

    def test_empty_string_fails(self):
        result = validate_yaml("")
        assert result["valid"] is False