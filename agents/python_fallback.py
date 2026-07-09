import json
from agents.selector_utils import cap_selectors



def generate_python_directly(state, llm) -> str:
    """
    Fallback function used when YAML generation or validation fails.

    Generates Python Playwright + Pytest code directly from the
    task plan and detected website elements.
    """

    selectors = state.get("selectors", [])

    buttons = cap_selectors([s for s in selectors if s.get("type") == "button"], "buttons")
    inputs  = cap_selectors([s for s in selectors if s.get("type") == "input"],  "inputs")
    links   = cap_selectors([s for s in selectors if s.get("type") == "link"],   "links")

    prompt = f"""
You are a Senior Python Playwright Automation Engineer.

Generate production-ready Playwright automation tests.

Website Requirements:
{state["design_doc"]}

Generated Test Plan:
{chr(10).join(state["task_plan"])}

Detected Buttons:
{json.dumps(buttons, indent=2)}

Detected Inputs:
{json.dumps(inputs, indent=2)}

Detected Links:
{json.dumps(links, indent=2)}

Requirements:

Live IoT Dashboard Rules

- Never verify exact numeric values.
- Verify widget visibility only.
- Verify charts are rendered.
- Verify navigation succeeds.
- Use authenticated session.
- Use wait_for_live_data(page) after every page.goto().
- Use wait_for_widget(page, selector) before interacting with widgets.
- Never use expect_page() unless testing a popup.
- Prefer page.locator("#id") over text locators.
- Use the official live application URLs shown below.
- Do not invent additional URLs.
Navigation Rules

Login tests:
page.goto("/")

Dashboard:
page.goto("https://live.ideabytesiot.com/demolive/dashboard/status-list")

Reports:
page.goto("https://live.ideabytesiot.com/demolive/reports/scheduled")

Alerts:
page.goto("https://live.ideabytesiot.com/demolive/alerts")

Devices:
page.goto("https://live.ideabytesiot.com/demolive/devices")

Alarms:
page.goto("https://live.ideabytesiot.com/demolive/alarms")

Users:
page.goto("https://live.ideabytesiot.com/demolive/users/users-management")

Hidden Element Rules

Never generate

wait_for_selector(..., state="visible")

or

expect(locator).to_be_visible()

for

- input[type="hidden"]
- hidden inputs
- hidden framework fields

If the selector is hidden,

either

- skip the selector

or

- use

expect(locator).to_have_attribute(...)

only when explicitly testing hidden metadata.

Route Rules

Generate page.goto() only for routes that were discovered by the crawler.

Never invent application routes.

If a required page was not discovered,
omit that test.

Authentication Rules

The Playwright browser context already loads auth.json.

Assume the user is already authenticated.

DO NOT generate:

page.fill("#username", ...)
page.fill("#password", ...)
page.click("#kc-login")

unless the task explicitly tests login.

Dashboard, Reports, Alerts, Devices, Alarms and Users tests must begin directly from their page.

because BASE_URL is already configured in conftest.py.

1. Generate Python code only.
2. Use pytest.
3. Use Playwright sync API.
4. Import:

from playwright.sync_api import sync_playwright, expect

5. Create one test function per task.
6. Use page.goto().
7. Use page.click().
8. Use page.fill().
9. Every test function MUST include meaningful assertions.
    Good examples:
    expect(page.locator("#username")).to_be_visible()
    expect(page.locator("table")).to_be_visible()
    Assertion Rules
    Every test must contain at least one expect().
    Examples:
    expect(page.locator("table")).to_be_visible()
    expect(page.locator("button")).to_be_enabled()
    expect(page.locator("input")).to_be_editable()
    Never assert exact live IoT values.
    Good assertions
    expect(page.locator("#username")).to_be_visible()
    expect(page.locator("#kc-login")).to_be_visible()
    expect(page.locator("table")).to_be_visible()
    expect(page.locator("button")).to_be_enabled()
    expect(page.locator("input")).to_be_editable()
    expect(page.locator("nav")).to_be_visible()
    expect(page.locator("button")).to_be_enabled()
    expect(page.locator("input")).to_be_editable()
    Avoid asserting exact values from live IoT widgets.
    Bad examples:
    expect(page.locator("body")).to_be_visible()
    expect(page).to_have_url("/")
    Never generate weak assertions.
   Use: expect(page.locator("selector")).to_be_visible()
   Or:  expect(page).to_have_url("/expected-path")
   A function with zero expect() calls is INVALID — do not generate it.
10. Selector Rules
- Use ONLY selectors supplied in the prompt.
- Never invent ids, classes, data-testid values or CSS selectors.
- Never assume selectors such as:
    #temperature-widget
    #humidity-widget
    .dashboard-card
    .device-list
    .sensor-card
    .chart-widget
- If the crawler does not provide a selector for a widget,
  verify the nearest stable parent instead
  (table, heading, navigation link, button, etc.).
- Do NOT write comments such as
  "Assuming a selector..."
    Never generate:
    button:has-text("")
    a:has-text("")
    input[name=""]
    input[id=""]
    If a selector is empty, skip that interaction.
    If a selector is missing, skip the interaction instead of inventing one.
    Always prefer:
    1. #id
    2. data-testid
    3. aria-label
    4. input[name]
    5. link href
    Avoid:
    button:has-text("")
11. Do NOT invent selectors.
12. Do NOT use time.sleep().
13. After every page.goto():
    wait_for_live_data(page)
    Before clicking or filling any widget:
    wait_for_widget(page, selector)
    Do not interact with elements before these waits complete.
14. Add comments where useful.
15. Produce runnable code.


CRITICAL GENERATION RULES
Generate login steps ONLY for authentication tests.
Never login before every test.
Never invent selectors.
Never invent CSS classes.
Never invent IDs.
Never invent buttons.
Never invent pages.
Never invent routes.
If a selector is unavailable,
skip that interaction.

Every generated test must be executable without manual editing.

Return ONLY Python code.

Do NOT return Markdown.
Do NOT use code fences.
Do NOT include explanations.


Convert these actions exactly:

Fill -> page.fill()

Click -> page.click()

Select -> page.select_option()

Check -> page.check()

Uncheck -> page.uncheck()

Press -> page.press()

Hover -> page.hover()

Do not describe actions in comments.

Generate executable Playwright code only.


Never generate:

with page.context.expect_page():

unless a popup window is explicitly opened by clicking a link with target="_blank".


- Return ONLY executable Python code.
- Do NOT wrap the code in Markdown.
- Do NOT use ```python or ``` fences.
- Do NOT include explanations.
- The first line of the output must be a valid Python statement (for example, an import).


Generate at most 30 Playwright test functions.
Prioritize the highest-value scenarios.
"""

    try:

        response = llm.invoke(prompt)

        return (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

    except Exception as e:

        print("[Python Fallback Error]", e)

        return f'''"""
Fallback code generation failed.

Error:
{e}
"""'''