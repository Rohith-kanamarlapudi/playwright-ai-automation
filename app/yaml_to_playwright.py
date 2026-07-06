import re
import yaml
from typing import List
from typing import Dict
from typing import Any
import os



# ==========================================================
# PLAYWRIGHT FILE HEADER
# ==========================================================

PLAYWRIGHT_HEADER = """
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
    """
    Removes extra spaces/newlines.
    """
    return " ".join(str(step).split())


def quote(value: str) -> str:
    """
    Escape quotes for Python strings.
    """
    return value.replace('"', '\\"')


# ==========================================================
# URL EXTRACTION
# ==========================================================

URL_PATTERN = re.compile(
    r"https?://[^\s]+"
)


def extract_url(text: str):

    if not text:
        return None

    m = URL_PATTERN.search(text)

    if not m:
        return None

    url = m.group(0)

    # Remove trailing punctuation
    url = url.rstrip(".,;")

    # Remove quotes
    url = url.strip("'")
    url = url.strip('"')

    return url


# ==========================================================
# SELECTOR EXTRACTION
# ==========================================================

LINK_SELECTOR_PATTERN = re.compile(
    r"Click\s+link\s+(.+)",
    re.IGNORECASE
)

BUTTON_SELECTOR_PATTERN = re.compile(
    r"button[:\w\-\(\)\'\"\=\[\]\s\.>]+",
    re.IGNORECASE
)


def extract_selector(step: str):

    step = clean_step(step)

    #
    # selector '...'
    #

    m = re.search(
        r"selector\s+'([^']+)'",
        step,
        re.IGNORECASE
    )

    if m:
        return m.group(1)

    #
    # selector "..."
    #

    m = re.search(
        r'selector\s+"([^"]+)"',
        step,
        re.IGNORECASE
    )

    if m:
        return m.group(1)

    #
    # Click link ...
    #

    m = LINK_SELECTOR_PATTERN.search(step)

    if m:
        return m.group(1).strip()

    #
    # button...
    #

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
        "accessibility": False
    }

    url = extract_url(expected)

    if url:
        data["url"] = url

    if "title contains" in expected.lower():

        title = expected.split("contains", 1)[1].strip()

        title = title.strip("'")

        data["title"] = title

    if "body contains" in expected.lower():

        body = expected.split("contains", 1)[1].strip()

        body = body.strip("'")

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
# ==========================================================

def convert_step(step: str) -> List[str]:
    """
    Converts one YAML step into Playwright commands.
    """

    step = clean_step(step)

    code = []

    # ------------------------------------------------------
    # Open URL
    # ------------------------------------------------------

    url = extract_url(step)
    # ------------------------------------------------------
    # Navigate
    # ------------------------------------------------------

    if step.lower().startswith("navigate"):

        if url:

            code.append(
                f'page.goto("{quote(url)}")'
            )

        else:

            code.append(
                'page.goto("/")'
            )

        code.append(
            "page.wait_for_load_state('networkidle')"
        )

        return code

    if (
        step.lower().startswith("open ")
        and url
    ):
        code.append(f'page.goto("{quote(url)}")')
        code.append("page.wait_for_load_state('networkidle')")
        return code
    # ------------------------------------------------------
    # Click the 'Contact' link with selector ...
    # ------------------------------------------------------

    m = re.search(

        r"Click\s+the\s+'.*?'\s+link\s+with\s+selector\s+'([^']+)'",

        step,

        re.IGNORECASE

    )

    if m:

        selector = m.group(1)

        code.append(
            f'page.locator("{quote(selector)}").click()'
        )

        code.append(
            "page.wait_for_load_state('networkidle')"
        )

        return code

    # ------------------------------------------------------
    # Click Link
    # ------------------------------------------------------

    if step.lower().startswith("click link"):

        selector = extract_selector(step)

        if selector:
            code.append(
                f'page.click("{quote(selector)}")'
            )
            code.append(
                "page.wait_for_load_state('networkidle')"
            )
            return code

    # ------------------------------------------------------
    # Click Button
    # ------------------------------------------------------

    if step.lower().startswith("click button"):

        selector = step.replace(
            "Click button",
            ""
        ).strip()

        if selector:
            code.append(
                f'page.click("{quote(selector)}")'
            )
        else:
            code.append(
                "# TODO: Unknown button selector"
            )

        return code

    # ------------------------------------------------------
    # Fill Inputs
    # ------------------------------------------------------

    if step.lower().startswith("fill"):

        #
        # Examples:
        #
        # Fill input[name='email'] with test@test.com
        # Fill #username with admin
        #

        m = re.search(
            r"Fill\s+(.+?)\s+with\s+(.+)",
            step,
            re.IGNORECASE
        )

        if m:

            selector = m.group(1).strip()

            value = m.group(2).strip()

            value = value.strip("'")

            value = value.strip('"')

            code.append(
                f'page.fill("{quote(selector)}", "{quote(value)}")'
            )

            return code

    # ------------------------------------------------------
    # Type
    # ------------------------------------------------------

    if step.lower().startswith("type"):

        m = re.search(
            r"Type\s+(.+?)\s+into\s+(.+)",
            step,
            re.IGNORECASE
        )

        if m:

            value = m.group(1).strip()

            selector = m.group(2).strip()

            code.append(
                f'page.fill("{quote(selector)}", "{quote(value)}")'
            )

            return code

    # ------------------------------------------------------
    # Check Visibility
    # ------------------------------------------------------

    if "visibility" in step.lower():

        selector = extract_selector(step)

        if selector:

            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_visible()'
            )

            return code

    # ------------------------------------------------------
    # Verify Heading
    # ------------------------------------------------------

    if "heading" in step.lower():

        code.append(
            'expect(page.locator("h1")).to_be_visible()'
        )

        return code

    # ------------------------------------------------------
    # Resize Viewport
    # ------------------------------------------------------

    if "viewport" in step.lower():

        m = re.search(
            r"(\d+)\s*x\s*(\d+)",
            step
        )

        if m:

            width = int(m.group(1))
            height = int(m.group(2))

            code.append(
                f"page.set_viewport_size({{'width': {width}, 'height': {height}}})"
            )

            return code

    # ------------------------------------------------------
    # Wait
    # ------------------------------------------------------

    if "wait" in step.lower():

        code.append(
            "page.wait_for_load_state('networkidle')"
        )

        return code

    # ------------------------------------------------------
    # Screenshot
    # ------------------------------------------------------

    if "screenshot" in step.lower():

        code.append(
            'page.screenshot(path="screenshot.png")'
        )

        return code

    # ------------------------------------------------------
    # Scroll
    # ------------------------------------------------------

    if "scroll" in step.lower():

        code.append(
            "page.mouse.wheel(0, 1200)"
        )

        return code

    # ------------------------------------------------------
    # Refresh
    # ------------------------------------------------------

    if "refresh" in step.lower():

        code.append(
            "page.reload()"
        )

        code.append(
            "page.wait_for_load_state('networkidle')"
        )

        return code

    # ------------------------------------------------------
    # Press Enter
    # ------------------------------------------------------

    if "press enter" in step.lower():

        code.append(
            'page.keyboard.press("Enter")'
        )

        return code
    # ------------------------------------------------------
    # Verify href attribute
    # ------------------------------------------------------

    if "href attribute" in step.lower():

        url = extract_url(step)

        if url:

            code.append(
                f'expect(page.url).to_contain("{quote(url)}")'
            )

            return code
    # ------------------------------------------------------
    # Verify URL
    # ------------------------------------------------------

    if "verify the url" in step.lower():

        url = extract_url(step)

        if url:

            code.append(
                f'expect(page).to_have_url("{quote(url)}")'
            )

            return code
    # ------------------------------------------------------
    # Verify title
    # ------------------------------------------------------

    if "page title" in step.lower():

        m = re.search(

            r"contains\s+'([^']+)'",

            step,

            re.IGNORECASE

        )

        if m:

            title = m.group(1)

            code.append(
                f'expect(page).to_have_title(re.compile("{quote(title)}"))'
            )

            return code
        
    # ------------------------------------------------------
    # Verify Visible
    # ------------------------------------------------------

    if "visible" in step.lower():

        selector = extract_selector(step)

        if selector:

            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_visible()'
            )

            return code

    # ------------------------------------------------------
    # Verify Clickable
    # ------------------------------------------------------

    if "clickable" in step.lower():

        selector = extract_selector(step)

        if selector:

            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_enabled()'
            )

            return code
    # ------------------------------------------------------
    # Verify href
    # ------------------------------------------------------

    if "href" in step.lower():

        selector = extract_selector(step)

        url = extract_url(step)

        if selector and url:

            code.append(
                f'expect(page.locator("{quote(selector)}")).to_have_attribute("href", "{quote(url)}")'
            )

            return code

    # ------------------------------------------------------
    # Verify 404 Page
    # ------------------------------------------------------

    if "404" in step.lower():

        code.append(
            'expect(page.locator("body")).to_contain_text("404")'
        )

        return code

    # ------------------------------------------------------
    # Set Viewport
    # ------------------------------------------------------

    if "viewport" in step.lower():

        m = re.search(
            r"(\d+)\s*x\s*(\d+)",
            step
        )

        if m:

            width = int(m.group(1))
            height = int(m.group(2))

            code.append(
                f"page.set_viewport_size({{'width': {width}, 'height': {height}}})"
            )

            return code
    # ------------------------------------------------------
    # Accessibility
    # ------------------------------------------------------

    if "accessible name" in step.lower():

        selector = extract_selector(step)

        if selector:

            code.append(
                f'expect(page.locator("{quote(selector)}")).to_be_visible()'
            )

            return code
    # ------------------------------------------------------
    # New Tab
    # ------------------------------------------------------

    if "new tab" in step.lower():

        code.append(
            "with page.context.expect_page() as new_page_info:"
        )

        code.append(
            "    pass"
        )

        return code
    # ------------------------------------------------------
    # URL Starts With
    # ------------------------------------------------------

    if "starts with" in step.lower():

        url = extract_url(step)

        if url:

            code.append(
                f'assert page.url.startswith("{quote(url)}")'
            )

            return code
    # ------------------------------------------------------
    # URL Ends With
    # ------------------------------------------------------

    if "ends with" in step.lower():

        m = re.search(
            r"ends with\s+'([^']+)'",
            step,
            re.IGNORECASE
        )

        if m:

            suffix = m.group(1)

            code.append(
                f'assert page.url.endswith("{quote(suffix)}")'
            )

            return code
    # ------------------------------------------------------
    # Contains Text
    # ------------------------------------------------------

    if "contains" in step.lower():

        m = re.search(
            r"contains\s+'([^']+)'",
            step,
            re.IGNORECASE
        )

        if m:

            text = m.group(1)

            code.append(
                f'expect(page.locator("body")).to_contain_text("{quote(text)}")'
            )

            return code
    # ------------------------------------------------------
    # Unsupported Step
    # ------------------------------------------------------

    code.append(
        f'print("WARNING: Unsupported step -> {quote(step)}")'
    )

    code.append(
        f"# Unsupported Step: {step}"
    )

    return code

# ==========================================================
# EXPECTED RESULT CONVERTER
# ==========================================================

def convert_expected(expected: str) -> List[str]:

    result = parse_expected(expected)

    code = []

    #
    # URL
    #

    if result["url"]:

        code.append(
            f'expect(page).to_have_url("{quote(result["url"])}")'
        )

    #
    # Title
    #

    if result["title"]:

        code.append(
            f'expect(page).to_have_title(re.compile("{quote(result["title"])}"))'
        )

    #
    # Body contains text
    #

    if result["contains"]:

        code.append(
            f'expect(page.locator("body")).to_contain_text("{quote(result["contains"])}")'
        )

    #
    # Heading
    #

    if result["heading"]:

        code.append(
            'expect(page.locator("h1")).to_be_visible()'
        )

    #
    # Visible
    #

    if result["visible"]:

        code.append(
            'expect(page.locator("button")).to_be_visible()'
        )

    #
    # Accessibility placeholder
    #

    if result["accessibility"]:

        code.append(
            "# TODO: Accessibility validation"
        )

    return code

# ==========================================================
# TEST FUNCTION GENERATOR
# ==========================================================

def sanitize_test_name(name: str) -> str:
    """
    Convert a test title into a valid Python function name.
    """

    name = name.lower()

    name = re.sub(
    r"[^a-zA-Z0-9]+",
    "_",
    name
    )

    name = name.lower()

    name = name.strip("_")

    if not name.startswith("test_"):
        name = "test_" + name

    return name


# ==========================================================
# SINGLE TEST GENERATOR
# ==========================================================

def generate_test_case(test_case: Dict[str, Any]) -> List[str]:

    writer = CodeWriter()

    test_name = sanitize_test_name(
        test_case.get("title", "generated_test")
    )

    writer.add("")
    writer.add("# =====================================================")
    writer.add(
        f"# {test_case.get('id','')} - {test_case.get('title','')}"
    )
    writer.add("# =====================================================")
    writer.blank()

    writer.add(
        f"def {test_name}(page: Page):"
    )

    writer.add(
        '    page.set_default_timeout(10000)'
    )

    writer.add(
        '    page.set_default_navigation_timeout(30000)'
    )

    writer.blank()
    steps = test_case.get("steps", [])


    #
    # Skip duplicate steps
    #

    seen = set()

    filtered_steps = []

    for step in steps:

        if step in seen:

            continue

        seen.add(step)

        filtered_steps.append(step)

    steps = filtered_steps

    if not steps:

        writer.add("    pass")

        return writer.lines

    for step in steps:

        commands = convert_step(step)

        for cmd in commands:

            #
            # Auto-indent generated commands
            #

            if cmd.startswith("with "):

                writer.add(f"    {cmd}")

            elif cmd.startswith("    "):

                writer.add(cmd)

            else:

                writer.add(f"    {cmd}")

    writer.blank()

    expected = test_case.get(
        "expected_result",
        ""
    )

    if expected:

        assertions = convert_expected(expected)

        for assertion in assertions:

            if assertion.startswith("    "):

                writer.add(assertion)

            else:

                writer.add(f"    {assertion}")

    writer.blank()

    return writer.lines


# ==========================================================
# PLAYWRIGHT FILE GENERATOR
# ==========================================================

def generate_playwright_file(
    test_cases: List[Dict[str, Any]]
) -> str:

    writer = CodeWriter()

    #
    # Imports
    #

    writer.add(PLAYWRIGHT_HEADER)
    writer.blank()
    writer.add(
    "# Generated Tests"
    )

    writer.blank()

    writer.add(
        "# =========================================="
    )

    writer.add(
        "# AUTO GENERATED BY AI PLAYWRIGHT GENERATOR"
    )

    writer.add(
        "# =========================================="
    )

    writer.blank()

    writer.blank()

    if not test_cases:

        writer.add(
            "# No test cases generated."
        )

        return writer.build()

    #
    # Generate all tests
    #

    for index, tc in enumerate(test_cases, start=1):
        writer.add(
            f"# Test Case {index}"
        )

        writer.extend(
            generate_test_case(tc)
        )

        writer.blank()

    return writer.build()


# ==========================================================
# DEBUG HELPERS
# ==========================================================

def print_summary(
    test_cases: List[Dict[str, Any]]
):

    print()
    print("=" * 70)
    print("PLAYWRIGHT CONVERSION SUMMARY")
    print("=" * 70)

    total_steps = 0

    for tc in test_cases:

        total_steps += len(
            tc.get("steps", [])
        )

    print(f"Total Test Cases : {len(test_cases)}")
    print(f"Total Steps      : {total_steps}")

    print()

    for tc in test_cases:

        print(
            f"{tc.get('id')} : "
            f"{tc.get('title')}"
        )

    print("=" * 70)
    print()

# ==========================================================
# OPTIONAL VALIDATION
# ==========================================================

def validate_test_case(
    tc: Dict[str, Any]
) -> bool:

    required = [
        "id",
        "title",
        "steps",
        "expected_result"
    ]

    for field in required:

        if field not in tc:

            return False

    if not isinstance(
        tc["steps"],
        list
    ):

        return False

    return True


def filter_valid_tests(
    test_cases: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    valid = []

    for tc in test_cases:

        if validate_test_case(tc):

            valid.append(tc)

        else:

            print(
                f"Skipping invalid test case: "
                f"{tc.get('id','UNKNOWN')}"
            )

    return valid
# ==========================================================
# MAIN CONVERTER
# ==========================================================

def convert_yaml_to_playwright(yaml_text: str) -> Dict[str, Any]:
    """
    Converts validated YAML test cases into a complete
    Playwright + pytest automation script.
    """

    unsupported = []
    unsupported_file = []

    # ------------------------------------------------------
    # Empty YAML
    # ------------------------------------------------------

    if not yaml_text or not yaml_text.strip():

        return {
            "code": "# Empty YAML supplied.",
            "unsupported": [],
            "test_cases": []
        }

    # ------------------------------------------------------
    # Parse YAML
    # ------------------------------------------------------

    try:

        data = yaml.safe_load(yaml_text)

    except Exception as e:

        return {
            "code": f"# Invalid YAML\n# {e}",
            "unsupported": [],
            "test_cases": []
        }

    # ------------------------------------------------------
    # Validate root object
    # ------------------------------------------------------

    if not isinstance(data, dict):

        return {
            "code": "# YAML root must be a dictionary.",
            "unsupported": [],
            "test_cases": []
        }

    # ------------------------------------------------------
    # Read test cases
    # ------------------------------------------------------

    test_cases = data.get("test_cases", [])
    import os

    os.makedirs(
        "generated_tests",
        exist_ok=True
    )

    with open(
        "generated_tests/generated_yaml.yaml",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(yaml_text)

    if not isinstance(test_cases, list):

        return {
            "code": "# test_cases must be a list.",
            "unsupported": [],
            "test_cases": []
        }

    # ------------------------------------------------------
    # Remove malformed test cases
    # ------------------------------------------------------

    test_cases = filter_valid_tests(test_cases)

    # ------------------------------------------------------
    # Collect unsupported steps
    # ------------------------------------------------------

    for tc in test_cases:

        for step in tc.get("steps", []):

            commands = convert_step(step)

            for cmd in commands:

                if cmd.startswith("# Unsupported"):

                    unsupported.append(step)

                    unsupported_file.append(
                        f"- {step}"
                    )

    # ------------------------------------------------------
    # Generate Playwright code
    # ------------------------------------------------------

    playwright_code = generate_playwright_file(
        test_cases
    )

    # ------------------------------------------------------
    # Print summary
    # ------------------------------------------------------

    print_summary(test_cases)

    print(
        f"[Playwright Converter] "
        f"Generated {len(test_cases)} test case(s)."
    )

    print(
        f"[Playwright Converter] "
        f"Unsupported Steps: {len(unsupported)}"
    )

    # ------------------------------------------------------
    # Return
    # ------------------------------------------------------
    if unsupported_file:

        with open(
            "generated_tests/unsupported_steps.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "\n".join(unsupported_file)
            )
    print()

    print("=" * 70)

    print("FINAL CONVERSION REPORT")

    print("=" * 70)

    print(
        f"Test Cases      : {len(test_cases)}"
    )

    print(
        f"Unsupported     : {len(unsupported)}"
    )

    print(
        "Output Script   : generated_tests/generated_test.py"
    )

    print(
        "Generated YAML  : generated_tests/generated_yaml.yaml"
    )

    print(
        "Unsupported Log : generated_tests/unsupported_steps.txt"
    )

    print("=" * 70)        
        
    return {

        "code": playwright_code,

        "unsupported": unsupported,

        "test_cases": test_cases
    }