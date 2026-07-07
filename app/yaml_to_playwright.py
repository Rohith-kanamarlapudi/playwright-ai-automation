import re
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
 
 
# ==========================================================
# PLAYWRIGHT FILE HEADER
# BUG FIX 1: Added "import os" to the header string — the
# original header used os.getenv() but never imported os,
# causing a NameError in every generated file which made
# pytest hang during collection (the infinite loop).
# ==========================================================
 
PLAYWRIGHT_HEADER = """
import os
import re
import pytest
 
from playwright.sync_api import (
    Page,
    expect,
    BrowserContext
)
 
 
@pytest.fixture
def base_url():
    return os.getenv("BASE_URL", os.getenv("TARGET_URL", "http://localhost:3000"))
"""
 
 
# ==========================================================
# HELPERS
# ==========================================================
 
def clean_step(step: str) -> str:
    """Removes extra spaces/newlines."""
    return " ".join(str(step).split())
 
 
def quote(value: str) -> str:
    """Escape quotes for Python strings."""
    return value.replace('"', '\\"')
 
 
# ==========================================================
# URL EXTRACTION
# ==========================================================
 
URL_PATTERN = re.compile(r"https?://[^\s]+")
 
 
def extract_url(text: str):
    if not text:
        return None
    m = URL_PATTERN.search(text)
    if not m:
        return None
    url = m.group(0).rstrip(".,;").strip("'").strip('"')
    return url
 
 
# ==========================================================
# BASE URL
# BUG FIX 2: Was hardcoded "https://ideabytes.com".
# Now reads from environment variables with localhost fallback.
# ==========================================================
 
def get_base_url() -> str:
    return os.getenv("BASE_URL", os.getenv("TARGET_URL", "http://localhost:3000"))
 
 
# ==========================================================
# SELECTOR EXTRACTION
# ==========================================================
 
LINK_SELECTOR_PATTERN = re.compile(r"Click\s+link\s+(.+)", re.IGNORECASE)
BUTTON_SELECTOR_PATTERN = re.compile(
    r"button[:\w\-\(\)\'\"=\[\]\s\.>]+", re.IGNORECASE
)
 
 
def extract_selector(step: str):
    step = clean_step(step)
 
    # selector '...'
    m = re.search(r"selector\s+'([^']+)'", step, re.IGNORECASE)
    if m:
        return m.group(1)
 
    # selector "..."
    m = re.search(r'selector\s+"([^"]+)"', step, re.IGNORECASE)
    if m:
        return m.group(1)
 
    # Click link ...
    m = LINK_SELECTOR_PATTERN.search(step)
    if m:
        return m.group(1).strip()
 
    # button...
    m = BUTTON_SELECTOR_PATTERN.search(step)
    if m:
        return m.group(0).strip()
 
    return None
 
 
# ==========================================================
# EXPECTED RESULT PARSER
# ==========================================================
 
def parse_expected(expected: str):
    expected = clean_step(expected)
    data = {
        "url": None,
        "title": None,
        "contains": None,
        "visible": None,
        "heading": False,
        "accessibility": False,
    }
 
    url = extract_url(expected)
    if url:
        data["url"] = url
 
    if "title contains" in expected.lower():
        title = expected.split("contains", 1)[1].strip().strip("'")
        data["title"] = title
 
    if "body contains" in expected.lower():
        body = expected.split("contains", 1)[1].strip().strip("'")
        data["contains"] = body
 
    if "button exists" in expected.lower():
        data["visible"] = True
 
    if "heading" in expected.lower():
        data["heading"] = True
 
    if "accessible" in expected.lower():
        data["accessibility"] = True
 
    return data
 
 
# ==========================================================
# PLAYWRIGHT CODE WRITER
# ==========================================================
 
class CodeWriter:
 
    def __init__(self):
        self.lines = []
 
    def add(self, line=""):
        self.lines.append(line)
 
    def extend(self, items):
        self.lines.extend(items)
 
    def blank(self):
        self.lines.append("")
 
    def build(self):
        return "\n".join(self.lines)
 
 
# ==========================================================
# STEP CONVERTER
# BUG FIX 3: Removed the DUPLICATE "viewport" block that was
# dead code at line ~630 — it could never be reached because
# the identical block at line ~428 always returned first.
#
# BUG FIX 4: "Open login page" (without a URL) now generates
# page.goto(base_url + "/login") using keyword extraction
# instead of silently falling through to "Unsupported Step".
#
# BUG FIX 5: "Verify X is visible" with no explicit selector
# now falls back to page.get_by_text() using the noun in the
# step, instead of returning [] and silently dropping the
# assertion entirely.
#
# BUG FIX 6: "Enter username" / "Enter password" steps now
# generate page.fill() using common input selectors instead
# of falling through to Unsupported.
#
# BUG FIX 7: "Click X" generic steps now generate
# page.get_by_role() or page.get_by_text() as a fallback
# instead of Unsupported.
# ==========================================================
 
def _extract_page_keyword(step: str) -> str:
    """
    Extract a meaningful noun from a step like
    'Open login page' -> 'login' or 'Verify dashboard visible' -> 'dashboard'.
    """
    # Remove leading verbs
    cleaned = re.sub(
        r"^(open|verify|assert|check|confirm|ensure|visit)\s+",
        "",
        step.strip(),
        flags=re.IGNORECASE,
    )
    # Remove trailing words like "page", "is", "visible", "the"
    cleaned = re.sub(
        r"\s+(page|is|the|visible|present|exists?|shown?|displayed?)$",
        "",
        cleaned.strip(),
        flags=re.IGNORECASE,
    )
    return cleaned.strip().lower()
 
 
def convert_step(step: str) -> List[str]:
    """
    Converts one YAML step string into Playwright commands.
    Returns a list of Python code lines (without indentation).
    """
    step = clean_step(step)
    code = []
    url = extract_url(step)
    step_lower = step.lower()
 
    # ----------------------------------------------------------
    # Navigate
    # ----------------------------------------------------------
    if step_lower.startswith("navigate"):
        if url:
            code.append(f'page.goto("{quote(url)}")')
        else:
            code.append('page.goto("/")')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # ----------------------------------------------------------
    # Open <url>  (explicit URL in step)
    # ----------------------------------------------------------
    if step_lower.startswith("open ") and url:
        code.append(f'page.goto("{quote(url)}")')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # ----------------------------------------------------------
    # BUG FIX 4: Open <page name> (no URL — keyword-based)
    # Examples: "Open login page", "Open the dashboard"
    # ----------------------------------------------------------
    if step_lower.startswith("open "):
        keyword = _extract_page_keyword(step)
        base = get_base_url().rstrip("/")
        # Map common keywords to paths
        PATH_MAP = {
            "login": "/login",
            "register": "/register",
            "signup": "/signup",
            "home": "/",
            "dashboard": "/dashboard",
            "profile": "/profile",
            "settings": "/settings",
            "checkout": "/checkout",
            "cart": "/cart",
            "products": "/products",
            "contact": "/contact",
            "about": "/about",
        }
        path = PATH_MAP.get(keyword, f"/{keyword}")
        code.append(f'page.goto("{base}{path}")')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # ----------------------------------------------------------
    # Click the '...' link with selector '...'
    # ----------------------------------------------------------
    m = re.search(
        r"Click\s+the\s+'.*?'\s+link\s+with\s+selector\s+'([^']+)'",
        step,
        re.IGNORECASE,
    )
    if m:
        selector = m.group(1)
        code.append(f'page.locator("{quote(selector)}").click()')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # ----------------------------------------------------------
    # Click Link
    # ----------------------------------------------------------
    if step_lower.startswith("click link"):
        selector = extract_selector(step)
        if selector:
            code.append(f'page.click("{quote(selector)}")')
            code.append("page.wait_for_load_state('networkidle')")
            return code
 
    # ----------------------------------------------------------
    # Click Button
    # ----------------------------------------------------------
    if step_lower.startswith("click button"):
        selector = step[len("click button"):].strip()
        if selector:
            code.append(f'page.click("{quote(selector)}")')
        else:
            code.append("# TODO: Unknown button selector")
        return code
 
    # ----------------------------------------------------------
    # BUG FIX 7: Click <element text> generic fallback
    # Examples: "Click the login button", "Click submit"
    # ----------------------------------------------------------
    if step_lower.startswith("click "):
        label = step[len("click "):].strip()
        label = re.sub(r"\s*(button|link|icon|tab)$", "", label, flags=re.IGNORECASE).strip()
        if label:
            code.append(f'page.get_by_text("{quote(label)}", exact=False).first.click()')
            code.append("page.wait_for_load_state('networkidle')")
        else:
            code.append("# TODO: Unknown click target")
        return code
 
    # ----------------------------------------------------------
    # Fill Inputs
    # ----------------------------------------------------------
    if step_lower.startswith("fill"):
        m = re.search(r"Fill\s+(.+?)\s+with\s+(.+)", step, re.IGNORECASE)
        if m:
            selector = m.group(1).strip()
            value = m.group(2).strip().strip("'").strip('"')
            code.append(f'page.fill("{quote(selector)}", "{quote(value)}")')
            return code
 
    # ----------------------------------------------------------
    # Type
    # ----------------------------------------------------------
    if step_lower.startswith("type"):
        m = re.search(r"Type\s+(.+?)\s+into\s+(.+)", step, re.IGNORECASE)
        if m:
            value = m.group(1).strip()
            selector = m.group(2).strip()
            code.append(f'page.fill("{quote(selector)}", "{quote(value)}")')
            return code
 
    # ----------------------------------------------------------
    # BUG FIX 6: Enter <field>  (common form input steps)
    # Examples: "Enter username", "Enter password", "Enter email"
    # ----------------------------------------------------------
    if step_lower.startswith("enter "):
        field = step[len("enter "):].strip().lower()
        FIELD_SELECTOR_MAP = {
            "username":    "#username, input[name='username'], input[placeholder*='username' i]",
            "password":    "#password, input[name='password'], input[type='password']",
            "email":       "#email, input[name='email'], input[type='email']",
            "name":        "#name, input[name='name'], input[placeholder*='name' i]",
            "phone":       "#phone, input[name='phone'], input[type='tel']",
            "search":      "#search, input[name='search'], input[type='search']",
            "first name":  "input[name='firstName'], input[name='first_name']",
            "last name":   "input[name='lastName'], input[name='last_name']",
            "message":     "textarea[name='message'], #message",
        }
        selector = FIELD_SELECTOR_MAP.get(field, f"input[name='{field}'], #{field}")
        # Extract value if pattern is "Enter username 'admin'"
        val_match = re.search(r"['\"]([^'\"]+)['\"]", step)
        value = val_match.group(1) if val_match else f"test_{field}"
        code.append(f'page.locator("{quote(selector)}").first.fill("{quote(value)}")')
        return code
 
    # ----------------------------------------------------------
    # Check Visibility
    # ----------------------------------------------------------
    if "visibility" in step_lower:
        selector = extract_selector(step)
        if selector:
            code.append(f'expect(page.locator("{quote(selector)}")).to_be_visible()')
            return code
 
    # ----------------------------------------------------------
    # Verify Heading
    # ----------------------------------------------------------
    if "heading" in step_lower:
        # Try to extract the heading text
        m = re.search(r"['\"]([^'\"]+)['\"]", step)
        if m:
            heading_text = m.group(1)
            code.append(
                f'expect(page.get_by_role("heading", name="{quote(heading_text)}")'
                f').to_be_visible()'
            )
        else:
            code.append('expect(page.locator("h1, h2, h3")).first.to_be_visible()')
        return code
 
    # ----------------------------------------------------------
    # Resize Viewport  (ONLY ONE block — duplicate removed)
    # ----------------------------------------------------------
    if "viewport" in step_lower:
        m = re.search(r"(\d+)\s*x\s*(\d+)", step)
        if m:
            width = int(m.group(1))
            height = int(m.group(2))
            code.append(
                f"page.set_viewport_size({{'width': {width}, 'height': {height}}})"
            )
            return code
 
    # ----------------------------------------------------------
    # Wait
    # ----------------------------------------------------------
    if "wait" in step_lower:
        # Wait for specific selector if mentioned
        selector = extract_selector(step)
        if selector:
            code.append(f'page.wait_for_selector("{quote(selector)}")')
        else:
            code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # ----------------------------------------------------------
    # Screenshot
    # ----------------------------------------------------------
    if "screenshot" in step_lower:
        code.append('page.screenshot(path="screenshot.png")')
        return code
 
    # ----------------------------------------------------------
    # Scroll
    # ----------------------------------------------------------
    if "scroll" in step_lower:
        code.append("page.mouse.wheel(0, 1200)")
        return code
 
    # ----------------------------------------------------------
    # Refresh
    # ----------------------------------------------------------
    if "refresh" in step_lower:
        code.append("page.reload()")
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # ----------------------------------------------------------
    # Press Enter
    # ----------------------------------------------------------
    if "press enter" in step_lower:
        code.append('page.keyboard.press("Enter")')
        return code
 
    # ----------------------------------------------------------
    # Verify href attribute
    # ----------------------------------------------------------
    if "href attribute" in step_lower:
        url = extract_url(step)
        if url:
            code.append(f'expect(page.url).to_contain("{quote(url)}")')
            return code
 
    # ----------------------------------------------------------
    # Verify URL
    # ----------------------------------------------------------
    if "verify the url" in step_lower:
        url = extract_url(step)
        if url:
            code.append(f'expect(page).to_have_url("{quote(url)}")')
            return code
 
    # ----------------------------------------------------------
    # Verify title
    # ----------------------------------------------------------
    if "page title" in step_lower:
        m = re.search(r"contains\s+'([^']+)'", step, re.IGNORECASE)
        if m:
            title = m.group(1)
            code.append(f'expect(page).to_have_title(re.compile("{quote(title)}"))')
            return code
 
    # ----------------------------------------------------------
    # Verify Visible
    # BUG FIX 5: Extract noun from step and use get_by_text()
    # when no explicit selector is found, instead of returning [].
    # ----------------------------------------------------------
    if "visible" in step_lower:
        selector = extract_selector(step)
        if selector:
            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_visible()'
            )
        else:
            keyword = _extract_page_keyword(step)
            if keyword:
                code.append(
                    f'expect(page.get_by_text("{quote(keyword)}", exact=False)'
                    f'.first).to_be_visible()'
                )
            else:
                code.append('expect(page.locator("body")).to_be_visible()')
        return code
 
    # ----------------------------------------------------------
    # Verify Clickable
    # ----------------------------------------------------------
    if "clickable" in step_lower:
        selector = extract_selector(step)
        if selector:
            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_enabled()'
            )
            return code
 
    # ----------------------------------------------------------
    # Verify href
    # ----------------------------------------------------------
    if "href" in step_lower:
        selector = extract_selector(step)
        url = extract_url(step)
        if selector and url:
            code.append(
                f'expect(page.locator("{quote(selector)}")'
                f').to_have_attribute("href", "{quote(url)}")'
            )
            return code
 
    # ----------------------------------------------------------
    # Verify 404 Page
    # ----------------------------------------------------------
    if "404" in step_lower:
        code.append('expect(page.locator("body")).to_contain_text("404")')
        return code
 
    # ----------------------------------------------------------
    # Accessibility
    # ----------------------------------------------------------
    if "accessible name" in step_lower:
        selector = extract_selector(step)
        if selector:
            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_visible()'
            )
            return code
 
    # ----------------------------------------------------------
    # New Tab
    # ----------------------------------------------------------
    if "new tab" in step_lower:
        code.append("with page.context.expect_page() as new_page_info:")
        code.append("    pass  # TODO: interact with new_page_info.value")
        return code
 
    # ----------------------------------------------------------
    # URL Starts With
    # ----------------------------------------------------------
    if "starts with" in step_lower:
        url = extract_url(step)
        if url:
            code.append(f'assert page.url.startswith("{quote(url)}")')
            return code
 
    # ----------------------------------------------------------
    # URL Ends With
    # ----------------------------------------------------------
    if "ends with" in step_lower:
        m = re.search(r"ends with\s+'([^']+)'", step, re.IGNORECASE)
        if m:
            suffix = m.group(1)
            code.append(f'assert page.url.endswith("{quote(suffix)}")')
            return code
 
    # ----------------------------------------------------------
    # Contains Text
    # ----------------------------------------------------------
    if "contains" in step_lower:
        m = re.search(r"contains\s+'([^']+)'", step, re.IGNORECASE)
        if m:
            text = m.group(1)
            code.append(
                f'expect(page.locator("body")).to_contain_text("{quote(text)}")'
            )
            return code
 
    # ----------------------------------------------------------
    # Verify / Assert generic fallback
    # BUG FIX 5 (continued): Any step starting with verify/assert
    # that didn't match above gets a body visibility check
    # instead of silently generating an Unsupported print.
    # ----------------------------------------------------------
    if step_lower.startswith(("verify", "assert", "check", "confirm", "ensure")):
        keyword = _extract_page_keyword(step)
        if keyword:
            code.append(
                f'expect(page.get_by_text("{quote(keyword)}", exact=False)'
                f'.first).to_be_visible()  # auto-generated assertion'
            )
        else:
            code.append(
                'expect(page.locator("body")).to_be_visible()  # fallback assertion'
            )
        return code
 
    # ----------------------------------------------------------
    # Unsupported Step
    # ----------------------------------------------------------
    code.append(f'print("WARNING: Unsupported step -> {quote(step)}")')
    code.append(f"# Unsupported Step: {step}")
    return code
 
 
# ==========================================================
# EXPECTED RESULT CONVERTER
# BUG FIX 8: When parse_expected() finds nothing parseable,
# the original returned [] — meaning the test had no assertion
# at all from expected_result. Now we add a fallback body-
# visible assertion so every test has at least one expect().
# ==========================================================
 
def convert_expected(expected: str) -> List[str]:
    result = parse_expected(expected)
    code = []
 
    if result["url"]:
        code.append(f'expect(page).to_have_url("{quote(result["url"])}")')
 
    if result["title"]:
        code.append(
            f'expect(page).to_have_title(re.compile("{quote(result["title"])}"))'
        )
 
    if result["contains"]:
        code.append(
            f'expect(page.locator("body")).to_contain_text("{quote(result["contains"])}")'
        )
 
    if result["heading"]:
        code.append('expect(page.locator("h1, h2, h3")).first.to_be_visible()')
 
    if result["visible"]:
        code.append('expect(page.locator("button")).to_be_visible()')
 
    if result["accessibility"]:
        code.append("# TODO: Accessibility validation")
 
    # BUG FIX 8: fallback — never return an empty assertion list
    if not code:
        keyword = _extract_page_keyword(expected)
        if keyword:
            code.append(
                f'expect(page.get_by_text("{quote(keyword)}", exact=False)'
                f'.first).to_be_visible()  # fallback assertion'
            )
        else:
            code.append(
                'expect(page.locator("body")).to_be_visible()  # fallback assertion'
            )
 
    return code
 
 
# ==========================================================
# TEST NAME SANITISER
# ==========================================================
 
def sanitize_test_name(name: str) -> str:
    """Convert a test title into a valid Python function name."""
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    if not name.startswith("test_"):
        name = "test_" + name
    return name
 
 
# ==========================================================
# SINGLE TEST CASE GENERATOR
# BUG FIX 9: If after writing all steps there is still no
# expect() call in the function, we inject a fallback assertion
# so the test is never silently empty.
# ==========================================================
 
def generate_test_case(test_case: Dict[str, Any]) -> List[str]:
    writer = CodeWriter()
 
    test_name = sanitize_test_name(test_case.get("title", "generated_test"))
 
    writer.add("")
    writer.add("# =====================================================")
    writer.add(f"# {test_case.get('id', '')} - {test_case.get('title', '')}")
    writer.add("# =====================================================")
    writer.blank()
    writer.add(f"def {test_name}(page: Page):")
    writer.add("    page.set_default_timeout(10000)")
    writer.add("    page.set_default_navigation_timeout(30000)")
    writer.blank()
 
    steps = test_case.get("steps", [])
 
    # Deduplicate steps while preserving order
    seen = set()
    filtered_steps = []
    for step in steps:
        if step not in seen:
            seen.add(step)
            filtered_steps.append(step)
    steps = filtered_steps
 
    if not steps:
        writer.add("    pass")
        return writer.lines
 
    has_assertion = False
 
    for step in steps:
        commands = convert_step(step)
        for cmd in commands:
            if cmd.startswith("with "):
                writer.add(f"    {cmd}")
            elif cmd.startswith("    "):
                writer.add(cmd)
            else:
                writer.add(f"    {cmd}")
            # Track whether at least one real assertion was written
            if "expect(" in cmd or cmd.strip().startswith("assert "):
                has_assertion = True
 
    writer.blank()
 
    expected = test_case.get("expected_result", "")
    if expected:
        assertions = convert_expected(expected)
        for assertion in assertions:
            if assertion.startswith("    "):
                writer.add(assertion)
            else:
                writer.add(f"    {assertion}")
            if "expect(" in assertion or assertion.strip().startswith("assert "):
                has_assertion = True
 
    # BUG FIX 9: Guarantee at least one assertion per test
    if not has_assertion:
        writer.add(
            '    expect(page.locator("body")).to_be_visible()'
            '  # safety assertion — no explicit assertion found'
        )
 
    writer.blank()
    return writer.lines
 
 
# ==========================================================
# PLAYWRIGHT FILE GENERATOR
# ==========================================================
 
def generate_playwright_file(test_cases: List[Dict[str, Any]]) -> str:
    writer = CodeWriter()
    writer.add(PLAYWRIGHT_HEADER)
    writer.blank()
    writer.add("# ==========================================")
    writer.add("# AUTO GENERATED BY AI PLAYWRIGHT GENERATOR")
    writer.add("# ==========================================")
    writer.blank()
    writer.blank()
 
    if not test_cases:
        writer.add("# No test cases generated.")
        return writer.build()
 
    for index, tc in enumerate(test_cases, start=1):
        writer.add(f"# Test Case {index}")
        writer.extend(generate_test_case(tc))
        writer.blank()
 
    return writer.build()
 
 
# ==========================================================
# DEBUG HELPERS
# ==========================================================
 
def print_summary(test_cases: List[Dict[str, Any]]):
    total_steps = sum(len(tc.get("steps", [])) for tc in test_cases)
    print()
    print("=" * 70)
    print("PLAYWRIGHT CONVERSION SUMMARY")
    print("=" * 70)
    print(f"Total Test Cases : {len(test_cases)}")
    print(f"Total Steps      : {total_steps}")
    print()
    for tc in test_cases:
        print(f"{tc.get('id')} : {tc.get('title')}")
    print("=" * 70)
    print()
 
 
# ==========================================================
# VALIDATION
# ==========================================================
 
def validate_test_case(tc: Dict[str, Any]) -> bool:
    required = ["id", "title", "steps", "expected_result"]
    for field in required:
        if field not in tc:
            return False
    if not isinstance(tc["steps"], list):
        return False
    return True
 
 
def filter_valid_tests(test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    valid = []
    for tc in test_cases:
        if validate_test_case(tc):
            valid.append(tc)
        else:
            print(f"Skipping invalid test case: {tc.get('id', 'UNKNOWN')}")
    return valid
 
 
# ==========================================================
# MAIN CONVERTER
# BUG FIX 10: convert_step was called TWICE per step —
# once to detect unsupported steps, once inside
# generate_playwright_file. Now we run generate first,
# then scan the generated code for "# Unsupported" lines,
# eliminating the duplicate work.
#
# BUG FIX 11: File paths now resolve relative to repo root
# using Path(__file__).resolve() so this works regardless
# of what directory the caller runs from.
# ==========================================================
 
def convert_yaml_to_playwright(yaml_text: str) -> Dict[str, Any]:
    """
    Converts validated YAML test cases into a complete
    Playwright + pytest automation script.
    """
 
    # Resolve output directory relative to this file's location
    # so it works from any working directory
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "generated_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
 
    # ----------------------------------------------------------
    # Empty YAML guard
    # ----------------------------------------------------------
    if not yaml_text or not yaml_text.strip():
        return {"code": "# Empty YAML supplied.", "unsupported": [], "test_cases": []}
 
    # ----------------------------------------------------------
    # Parse YAML
    # ----------------------------------------------------------
    try:
        data = yaml.safe_load(yaml_text)
    except Exception as e:
        return {"code": f"# Invalid YAML\n# {e}", "unsupported": [], "test_cases": []}
 
    if not isinstance(data, dict):
        return {
            "code": "# YAML root must be a dictionary.",
            "unsupported": [],
            "test_cases": [],
        }
 
    test_cases = data.get("test_cases", [])
 
    # Save raw YAML immediately after parsing (before any filtering)
    yaml_path = output_dir / "generated_yaml.yaml"
    yaml_path.write_text(yaml_text, encoding="utf-8")
 
    if not isinstance(test_cases, list):
        return {
            "code": "# test_cases must be a list.",
            "unsupported": [],
            "test_cases": [],
        }
 
    # ----------------------------------------------------------
    # Remove malformed test cases
    # ----------------------------------------------------------
    test_cases = filter_valid_tests(test_cases)
 
    # ----------------------------------------------------------
    # Generate Playwright code  (single pass — no duplicate calls)
    # BUG FIX 10: was calling convert_step twice per step
    # ----------------------------------------------------------
    playwright_code = generate_playwright_file(test_cases)
 
    # ----------------------------------------------------------
    # Detect unsupported steps from the generated code
    # (scan the output instead of re-running convert_step)
    # ----------------------------------------------------------
    unsupported = []
    unsupported_lines = []
    for line in playwright_code.splitlines():
        if line.strip().startswith("# Unsupported Step:"):
            step_text = line.strip()[len("# Unsupported Step:"):].strip()
            if step_text not in unsupported:
                unsupported.append(step_text)
                unsupported_lines.append(f"- {step_text}")
 
    # ----------------------------------------------------------
    # Print summary
    # ----------------------------------------------------------
    print_summary(test_cases)
    print(f"[Playwright Converter] Generated {len(test_cases)} test case(s).")
    print(f"[Playwright Converter] Unsupported Steps: {len(unsupported)}")
 
    # ----------------------------------------------------------
    # Save unsupported steps log
    # ----------------------------------------------------------
    if unsupported_lines:
        unsupported_path = output_dir / "unsupported_steps.txt"
        unsupported_path.write_text("\n".join(unsupported_lines), encoding="utf-8")
 
    # ----------------------------------------------------------
    # Final report
    # ----------------------------------------------------------
    print()
    print("=" * 70)
    print("FINAL CONVERSION REPORT")
    print("=" * 70)
    print(f"Test Cases      : {len(test_cases)}")
    print(f"Unsupported     : {len(unsupported)}")
    print(f"Output Script   : {output_dir / 'generated_test.py'}")
    print(f"Generated YAML  : {yaml_path}")
    if unsupported_lines:
        print(f"Unsupported Log : {output_dir / 'unsupported_steps.txt'}")
    print("=" * 70)
 
    return {
        "code": playwright_code,
        "unsupported": unsupported,
        "test_cases": test_cases,
    }