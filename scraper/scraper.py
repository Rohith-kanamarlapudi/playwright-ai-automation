from wsgiref import headers

import requests
import json
from bs4 import BeautifulSoup

# ---------------------------------------------------------
# Import Playwright helper functions.
# These functions render Angular pages before BeautifulSoup
# extracts the HTML.
# ---------------------------------------------------------
try:
    from scraper.playwright_check import (
        check_page,
        get_rendered_html,
        wait_for_dashboard,
        wait_for_widget,
        find_widget,
        click_with_retry,
        crawl_dashboard_sections,
        DASHBOARD_WIDGET_SELECTORS
    )

except ModuleNotFoundError:

    from playwright_check import (
        check_page,
        get_rendered_html,
        wait_for_dashboard,
        wait_for_widget,
        find_widget,
        click_with_retry,
        crawl_dashboard_sections,
        DASHBOARD_WIDGET_SELECTORS
    )

from urllib.parse import urljoin, urlparse
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# Live IoT Dashboard Configuration
# ---------------------------------------------------------

URL = os.getenv(
    "TARGET_URL",
    "https://live.ideabytesiot.com/demolive"
)

MAX_PAGES = int(
    os.getenv(
        "MAX_PAGES",
        "10"
    )
)

OUTPUT_FILE = "reports/website_elements.json"

# ---------------------------------------------------------
# Live widget keywords.
#
# These are used while scanning the rendered HTML to detect
# dashboard widgets, charts, gauges and cards.
# ---------------------------------------------------------

LIVE_WIDGET_KEYWORDS = [

    "widget",

    "dashboard",

    "chart",

    "graph",

    "gauge",

    "card",

    "tile",

    "status",

    "device",

    "alarm",

    "sensor"

]

# ---------------------------------------------------------
# HTML tags commonly used by IoT dashboards.
# ---------------------------------------------------------

LIVE_WIDGET_TAGS = [

    "canvas",

    "svg",

    "mat-card",

    "ib-card",

    "ib-widget",

    "ib-gauge",

    "ib-chart"

]

# ---------------------------------------------------------
# Class name fragments used by live dashboards.
# ---------------------------------------------------------

LIVE_WIDGET_CLASSES = [

    "widget",

    "chart",

    "graph",

    "gauge",

    "dashboard",

    "card",

    "tile",

    "status"

]

print("=" * 60)
print("IoT Dashboard Scraper")
print("=" * 60)
print(f"Target URL : {URL}")
print(f"Max Pages  : {MAX_PAGES}")
print("=" * 60)


# ----------------------------------------
# Download page using Requests
# ----------------------------------------
def get_page(url):
    """
    Downloads a page using Requests.

    Note:
    For the live IoT application the scraper mainly uses
    Playwright because Angular renders the page using
    JavaScript. This function is kept for compatibility.
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        print(f"Downloading page: {url}")

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        print("Download successful.")

        return BeautifulSoup(
            response.text,
            "html.parser"
        )

    except requests.exceptions.Timeout:

        print("Request timed out.")
        return None

    except requests.exceptions.HTTPError:

        print(
            "HTTP Error:",
            response.status_code
        )
        return None

    except requests.exceptions.RequestException as e:

        print(
            "Request Error:",
            e
        )
        return None


# ----------------------------------------
# Extract Live Dashboard Widgets
# ----------------------------------------
def extract_live_widgets(soup):
    """
    Detect live dashboard widgets.

    This function looks for common IoT dashboard
    components such as:

    - Charts
    - Gauges
    - Dashboard Cards
    - Canvas widgets
    - SVG widgets
    - Angular dashboard components

    These widgets are stored separately so that
    Playwright can use retry logic when interacting
    with them.
    """

    widgets = []

    seen_selectors = set()

    print("Scanning for live widgets...")

    # ------------------------------------
    # Scan using HTML tags
    # ------------------------------------
    for tag_name in LIVE_WIDGET_TAGS:

        for element in soup.find_all(tag_name):

            selector = ""

            if element.get("id"):

                selector = f"#{element.get('id')}"

            elif element.get("class"):

                selector = "." + ".".join(
                    element.get("class")
                )

            else:

                selector = tag_name

            if selector in seen_selectors:
                continue

            seen_selectors.add(selector)

            widgets.append({

                "type": tag_name,

                "selector": selector,

                "id": element.get(
                    "id",
                    ""
                ),

                "class": " ".join(
                    element.get(
                        "class",
                        []
                    )
                )

            })

    # ------------------------------------
    # Scan every HTML element
    # ------------------------------------
    for element in soup.find_all(True):

        classes = " ".join(
            element.get(
                "class",
                []
            )
        ).lower()

        element_name = element.name.lower()

        for keyword in LIVE_WIDGET_CLASSES:

            if (
                keyword in classes
                or keyword in element_name
            ):

                selector = ""

                if element.get("id"):

                    selector = f"#{element.get('id')}"

                elif element.get("class"):

                    selector = "." + ".".join(
                        element.get(
                            "class",
                            []
                        )
                    )

                else:

                    selector = element.name

                if selector in seen_selectors:
                    break

                seen_selectors.add(selector)

                widgets.append({

                    "type": keyword,

                    "selector": selector,

                    "id": element.get(
                        "id",
                        ""
                    ),

                    "class": " ".join(
                        element.get(
                            "class",
                            []
                        )
                    )

                })

                break

    print(
        f"Detected {len(widgets)} live widgets."
    )

    return widgets

# ----------------------------------------
# Extract Elements
# ----------------------------------------
def extract_elements(soup, url):
    """
    Extract all useful page elements.

    This function collects:

    - Buttons
    - Inputs
    - Links
    - Live dashboard widgets

    The extracted selectors are later used by the
    Playwright generator to create automation scripts.
    """

    print(f"\nExtracting elements from: {url}")

    # ----------------------------------------
    # Store different element types
    # ----------------------------------------
    buttons = []
    inputs = []
    links = []

    # Detect live IoT widgets.
    widgets = extract_live_widgets(soup)

    print(
        f"Found {len(widgets)} live widgets."
    )

    # ----------------------------------------
    # Extract Buttons
    # ----------------------------------------
    print("Scanning buttons...")

    for button in soup.find_all("button"):

        text = button.get_text(
            strip=True
        ).replace(
            "'",
            "\\'"
        )

        # Build multiple selectors so Playwright
        # can retry different selectors if the
        # dashboard refreshes.
        retry_selectors = []

        if button.get("id"):

            retry_selectors.append(
                f"#{button.get('id')}"
            )

        if text:

            retry_selectors.append(
                f"button:has-text('{text}')"
            )

        if button.get("name"):

            retry_selectors.append(
                f"button[name='{button.get('name')}']"
            )

        if button.get("class"):

            retry_selectors.append(
                "." + ".".join(
                    button.get("class")
                )
            )

        # Keep the first selector for backward
        # compatibility with the existing project.
        selector = (
            retry_selectors[0]
            if retry_selectors
            else "button"
        )

        buttons.append({

            "text":
            text,

            "type":
            button.get(
                "type",
                "button"
            ),

            "id":
            button.get(
                "id",
                ""
            ),

            "class":
            " ".join(
                button.get(
                    "class",
                    []
                )
            ),

            "name":
            button.get(
                "name",
                ""
            ),

            # Existing selector.
            "selector":
            selector,

            # New retry selectors for live widgets.
            "retry_selectors":
            retry_selectors,

            # Mark whether this button belongs to
            # a live dashboard.
            "dynamic":
            True if widgets else False

        })

    print(
        f"Buttons found: {len(buttons)}"
    )

    # ----------------------------------------
    # Input Buttons
    # ----------------------------------------
    print("Scanning input buttons...")

    for inp in soup.find_all("input"):

        if inp.get(
            "type",
            ""
        ).lower() not in [
            "submit",
            "button"
        ]:
            continue

        retry_selectors = []

        if inp.get("id"):

            retry_selectors.append(
                f"#{inp.get('id')}"
            )

        if inp.get("name"):

            retry_selectors.append(
                f"input[name='{inp.get('name')}']"
            )

        if inp.get("value"):

            retry_selectors.append(
                f"input[value='{inp.get('value')}']"
            )

        if inp.get("class"):

            retry_selectors.append(
                "." + ".".join(
                    inp.get("class")
                )
            )

        selector = (
            retry_selectors[0]
            if retry_selectors
            else "input"
        )

        buttons.append({

            "text":
            inp.get(
                "value",
                ""
            ),

            "type":
            inp.get(
                "type",
                "button"
            ),

            "id":
            inp.get(
                "id",
                ""
            ),

            "class":
            " ".join(
                inp.get(
                    "class",
                    []
                )
            ),

            "name":
            inp.get(
                "name",
                ""
            ),

            "selector":
            selector,

            "retry_selectors":
            retry_selectors,

            "dynamic":
            True if widgets else False

        })

    print(
        f"Buttons after input scan: {len(buttons)}"
    )

    # ----------------------------------------
    # Inputs
    # ----------------------------------------
    print("Scanning input fields...")

    SKIP_INPUT_TYPES = {
        "submit",
        "button"
    }

    for inp in soup.find_all("input"):

        input_type = inp.get(
            "type",
            "text"
        ).lower()

        if input_type in SKIP_INPUT_TYPES:
            continue

        retry_selectors = []

        if inp.get("id"):

            retry_selectors.append(
                f"#{inp.get('id')}"
            )

        if inp.get("name"):

            retry_selectors.append(
                f"input[name='{inp.get('name')}']"
            )

        if inp.get("placeholder"):

            retry_selectors.append(
                f"input[placeholder='{inp.get('placeholder')}']"
            )

        if inp.get("class"):

            retry_selectors.append(
                "." + ".".join(
                    inp.get("class")
                )
            )

        selector = (
            retry_selectors[0]
            if retry_selectors
            else "input"
        )

        inputs.append({

            "type":
            input_type,

            "name":
            inp.get(
                "name",
                ""
            ),

            "id":
            inp.get(
                "id",
                ""
            ),

            "class":
            " ".join(
                inp.get(
                    "class",
                    []
                )
            ),

            "placeholder":
            inp.get(
                "placeholder",
                ""
            ),

            "selector":
            selector,

            "retry_selectors":
            retry_selectors,

            "dynamic":
            True if widgets else False

        })

    print(
        f"Input fields found: {len(inputs)}"
    )

    # ----------------------------------------
    # Links
    # ----------------------------------------
    print("Scanning links...")

    links = []

    seen_links = set()

    for link in soup.find_all(["a", "button"]):

        href = (
            link.get("href")
            or link.get("routerLink")
            or link.get("routerlink")
            or ""
        ).strip()

        if "logout" in href.lower():
            continue

        if not href:
            continue

        if href == "#":
            continue

        full_url = urljoin(
            url,
            href
        )

        if full_url in seen_links:
            continue

        seen_links.add(
            full_url
        )

        text = link.get_text(
            strip=True
        )

        lid = link.get(
            "id",
            ""
        )

        retry_selectors = []

        # -----------------------------
        # Highest priority selector
        # -----------------------------
        if lid:

            retry_selectors.append(
                f"#{lid}"
            )

        # -----------------------------
        # Text selector
        # -----------------------------
        if text:

            retry_selectors.append(
                f"a:has-text('{text}')"
            )

        # -----------------------------
        # href selector
        # -----------------------------
        retry_selectors.append(
            f"a[href='{full_url}']"
        )

        # -----------------------------
        # Class selector
        # -----------------------------
        if link.get("class"):

            retry_selectors.append(
                "." + ".".join(
                    link.get(
                        "class",
                        []
                    )
                )
            )

        selector = (
            retry_selectors[0]
            if retry_selectors
            else "a"
        )

        links.append({

            "text":
            text or "",

            "href":
            full_url,

            "id":
            lid,

            "class":
            " ".join(
                link.get(
                    "class",
                    []
                )
            ),

            "selector":
            selector,

            # New retry selector list
            "retry_selectors":
            retry_selectors,

            # Live dashboard indicator
            "dynamic":
            True if widgets else False

        })

    print(
        f"Links found: {len(links)}"
    )

    # ----------------------------------------
    # Update Widget Selectors
    # ----------------------------------------
    print("Building widget selectors...")

    for widget in widgets:

        retry_selectors = []

        selector = widget.get(
            "selector",
            ""
        )

        if selector:
            retry_selectors.append(
                selector
            )

        widget_type = widget.get(
            "type",
            ""
        )

        if widget_type:

            retry_selectors.append(
                widget_type
            )

        widget["retry_selectors"] = retry_selectors

        widget["dynamic"] = True

    print(
        f"Live widgets: {len(widgets)}"
    )

    # ----------------------------------------
    # Build Final JSON
    # ----------------------------------------
    total_elements = (

        len(buttons)

        + len(inputs)

        + len(links)

        + len(widgets)

    )

    print(
        f"Total Elements: {total_elements}"
    )

    return {

        "url":
        url,

        "scraped_at":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "total_elements":
        total_elements,

        "buttons":
        buttons,

        "inputs":
        inputs,

        "links":
        links,

        # ---------------------------------
        # New Section
        # ---------------------------------
        # Stores dashboard widgets so
        # generated Playwright scripts can
        # wait for them before interacting.
        # ---------------------------------
        "widgets":
        widgets

    }

# ----------------------------------------
# Save JSON
# ----------------------------------------
def save_json(data, filename):

    Path(filename).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ----------------------------------------
# Crawl Website
# ----------------------------------------
def main(url: str = None, max_pages: int = None):

    url = url or os.getenv(
        "TARGET_URL",
        URL
    )

    max_pages = max_pages or int(
        os.getenv(
            "MAX_PAGES",
            "10"
        )
    )

    print("=" * 60)
    print("Starting Live IoT Dashboard Crawl (single browser session)")
    print("=" * 60)

    if not url.startswith(
        (
            "http://",
            "https://"
        )
    ):

        print("Invalid URL")
        return []

    BASE = "https://live.ideabytesiot.com/demolive/"

    # ----------------------------------------
    # CHANGED (requirements #5/#6/#7):
    #
    # This used to be a "to_visit" queue of URLs, discovered
    # by scanning <a> tags on every page (get_internal_links).
    # Angular SPA navigation doesn't work that way in practice
    # -- the sidebar is fixed, so we already know every section
    # up front. This list is exactly the same as the old
    # KNOWN_ROUTES list, just re-used as the click order instead
    # of a URL queue.
    #
    # "url" here is kept only as a LABEL for the JSON output
    # (so website_elements.json still has a familiar "url" per
    # page, for llm_playwright_generator.py). We do NOT
    # page.goto() any of these except the very first one
    # ("Dashboard") -- every section after that is reached by
    # clicking the sidebar inside crawl_dashboard_sections().
    # ----------------------------------------
    SECTIONS = [

        {"name": "Dashboard", "url": urljoin(BASE, "dashboard/status-list")},

        {"name": "Reports",   "url": urljoin(BASE, "reports/scheduled")},

        {"name": "Alerts",    "url": urljoin(BASE, "alerts")},

        {"name": "Devices",   "url": urljoin(BASE, "devices")},

        {"name": "Alarms",    "url": urljoin(BASE, "alarms")},

        {"name": "Users",     "url": urljoin(BASE, "users/users-management")},

    ]

    # max_pages now limits how many sidebar sections get
    # visited, instead of limiting a URL queue.
    sections_to_run = SECTIONS[:max_pages] if max_pages else SECTIONS

    all_pages_data = []

    # ----------------------------------------
    # This callback is called ONCE per section by
    # crawl_dashboard_sections(), right after it has clicked
    # into that section and grabbed the rendered HTML.
    #
    # Everything inside here is IDENTICAL to what used to run
    # inside the old while-loop: BeautifulSoup parsing,
    # extract_elements(), and the printed summary. Only the
    # navigation that happens BEFORE this callback has changed.
    # ----------------------------------------
    def handle_section(page, name, section_url, html):

        if not html:

            print(f"No rendered HTML returned for {name}.")

            return

        print("Rendered HTML received.")

        # ------------------------------------
        # Parse HTML using BeautifulSoup.
        # (unchanged)
        # ------------------------------------
        soup = BeautifulSoup(

            html,

            "html.parser"

        )

        print(
            f"Parsing rendered HTML for {name}..."
        )

        # ------------------------------------
        # Extract buttons, inputs,
        # links and live widgets.
        # (unchanged - same function, same JSON schema)
        # ------------------------------------
        page_data = extract_elements(

            soup,

            section_url

        )

        all_pages_data.append(
            page_data
        )

        print("Saving page...")

        print(
            "\nExtraction Summary"
        )

        print(
            "-" * 40
        )

        print("Section :", name)

        print(
            "Buttons :",
            len(
                page_data.get(
                    "buttons",
                    []
                )
            )
        )

        print(
            "Inputs  :",
            len(
                page_data.get(
                    "inputs",
                    []
                )
            )
        )

        print(
            "Links   :",
            len(
                page_data.get(
                    "links",
                    []
                )
            )
        )

        print(
            "Widgets :",
            len(
                page_data.get(
                    "widgets",
                    []
                )
            )
        )

        print(
            "Total   :",
            page_data.get(
                "total_elements",
                0
            )
        )

    # ----------------------------------------
    # NEW: this callback is called ONCE for every safe
    # clickable element that gets explored INSIDE a sidebar
    # section (a dashboard card, a tab, a filter, pagination,
    # etc) - not just once per sidebar page.
    #
    # It reuses the exact same extract_elements() /
    # BeautifulSoup parsing as handle_section() above, so the
    # JSON schema never changes. The only new thing added to
    # each entry is which UI state it came from, so the JSON
    # stays easy to trace back to a specific screen.
    # ----------------------------------------
    def handle_element(
        page,
        section_name,
        section_url,
        element_text,
        element_selector,
        ui_state_id,
        html
    ):

        if not html:

            print(f"No rendered HTML returned for '{element_text}'.")

            return

        print("Rendered HTML received.")

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        print(
            f"Parsing rendered HTML for {ui_state_id}..."
        )

        page_data = extract_elements(
            soup,
            section_url
        )

        # Extra bookkeeping fields - added on top of the
        # existing schema, nothing existing is changed.
        page_data["ui_state"] = ui_state_id
        page_data["parent_section"] = section_name
        page_data["clicked_element"] = element_text
        page_data["clicked_selector"] = element_selector

        all_pages_data.append(
            page_data
        )

        print("Saving page...")

    # ----------------------------------------
    # This is the ONLY place a browser gets created for the
    # entire crawl. crawl_dashboard_sections() (in
    # playwright_check.py) opens one browser, loads auth.json
    # once, opens the dashboard once, clicks through every
    # other section, and closes the browser once at the end.
    # It calls handle_section() once per sidebar page, and
    # handle_element() once per clickable element explored
    # inside each page.
    # ----------------------------------------
    sections_visited_count = 0
    total_elements_explored = 0
    total_ui_states = 0

    try:

        (
            crawl_results,
            sections_visited_count,
            total_elements_explored,
            total_ui_states
        ) = crawl_dashboard_sections(
            sections_to_run,
            on_section_ready=handle_section,
            on_element_ready=handle_element
        )

    except Exception as e:

        print(
            "\nCrawl failed:"
        )

        print(
            "Reason:",
            e
        )

    # ----------------------------------------
    # Save extracted elements.
    # (unchanged - same file, same format)
    # ----------------------------------------
    print("\nSaving JSON report...")

    save_json(

        all_pages_data,

        OUTPUT_FILE

    )

    print("\n" + "=" * 60)
    print("Live Crawl Completed")
    print("=" * 60)

    print(
        f"Pages Crawled : {len(all_pages_data)}"
    )

    print(
        f"Output File   : {OUTPUT_FILE}"
    )

    # ----------------------------------------
    # Final summary requested by the requirements.
    # ----------------------------------------
    print("\nApplication crawl completed.")
    print(f"Total sidebar pages visited: {sections_visited_count}")
    print(f"Total clickable elements explored: {total_elements_explored}")
    print(f"Total UI states explored: {total_ui_states}")
    print("JSON saved successfully.")

    return all_pages_data

# ----------------------------------------
# Run Directly
# ----------------------------------------
if __name__ == "__main__":

    print("=" * 60)
    print("Playwright AI Automation - Week 3 Live App Crawl")
    print("=" * 60)
    print(f"Target URL : {URL}")
    print(f"Max Pages  : {MAX_PAGES}")
    print()

    main(
        url=URL,
        max_pages=MAX_PAGES
    )
