"""
Prompt for the Strategy Agent.

The Strategy Agent analyzes the application description together
with the detected website elements and produces a structured list
of unique Playwright automation tasks.
"""

LIVE_APP_CONTEXT = """
IMPORTANT — This is a LIVE IoT dashboard application.

Special Guidelines:
- Dashboard values (temperature, humidity, device counts, charts, gauges, etc.) change in real time.
- NEVER assert exact numeric values.
- Validate element presence, visibility, structure, navigation, and behavior instead of exact values.
- Live charts, gauges, widgets, and sensor values may auto-refresh.
- Test that dynamic widgets render correctly instead of checking fixed readings.
- Authentication is required before accessing the dashboard.
- Focus on testing navigation, dashboard modules, forms, reports, alerts, alarms, devices, users, filters, search, downloads, and responsive behavior.

Examples

WRONG:
- Verify temperature equals 23.5°C.
- Verify humidity equals 65%.

RIGHT:
- Verify the temperature widget is visible and displays a numeric value.
- Verify the humidity widget updates correctly.
- Verify dashboard cards are displayed.
- Verify reports page loads successfully.
- Verify alerts page loads successfully.
- Verify devices page loads successfully.
"""

STRATEGY_PROMPT = """
{live_app_context}

You are a Senior QA Automation Architect specializing in Python Playwright.

Your job is to create a unique Playwright automation strategy.

Application Requirements
------------------------
{design_doc}

Detected Buttons
----------------
{buttons}

Detected Inputs
---------------
{inputs}

Detected Links
--------------
{links}

STRICT RULES

1. Generate ONLY unique scenarios.
2. Never generate duplicate or equivalent tasks.
3. Never invent buttons, inputs, links, pages or selectors.
4. Ignore selectors with empty text.
5. Every task must describe ONE executable user workflow.
6. Use only selectors supplied above.
7. Every task should be convertible into one Playwright test.
8. Prefer realistic end-to-end workflows.
9. Keep tasks concise.
10. Do not include implementation details.
11. For live dashboards, NEVER verify exact sensor values.
12. Verify widget visibility, page structure, navigation, and behavior instead.
13. Use dynamic assertions such as "is visible", "contains numeric value", or "updates correctly".

Cover these areas whenever possible:

- Authentication / Login
- Dashboard
- Navigation
- Reports
- Alerts
- Devices
- Alarms
- Users
- Forms
- Input validation
- Search
- Filters
- Buttons
- Links
- Tables
- Downloads
- Responsive behavior
- Accessibility
- Error handling
- Empty field validation
- Invalid input validation

DO NOT generate:

- Duplicate scenarios
- Generic statements
- Unsupported Playwright actions
- Imaginary pages
- Imaginary selectors
- Assertions on exact live sensor values

Good Examples

- Login using valid credentials and verify dashboard loads.
- Verify dashboard cards are visible.
- Verify temperature widget displays a numeric value.
- Verify humidity widget is rendered.
- Navigate to Reports and verify scheduled reports table is displayed.
- Navigate to Alerts and verify filters are visible.
- Navigate to Devices and verify device list loads.
- Navigate to Alarms and verify alarm rules table is displayed.
- Navigate to Users and verify user management page opens.
- Submit empty login form and verify validation messages.
- Verify navigation links are accessible.

Bad Examples

- Verify temperature is exactly 23.5°C.
- Verify humidity is exactly 65%.
- Test homepage.
- Check website.
- Verify application.
- Test everything.

Return ONLY a JSON array.

Example

[
    "Login using valid credentials and verify dashboard loads.",
    "Verify dashboard cards are visible.",
    "Navigate to Reports and verify scheduled reports table is displayed.",
    "Navigate to Alerts and verify filters are visible.",
    "Navigate to Devices and verify device list loads."
]

Return JSON only.
Do NOT return Markdown.
Do NOT use code fences.
Do NOT include explanations.
"""