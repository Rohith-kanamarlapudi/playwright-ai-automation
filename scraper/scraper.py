from wsgiref import headers

import requests
import json
from bs4 import BeautifulSoup
try:
    from scraper.playwright_check import (
        check_page,
        get_rendered_html,


    )
except ModuleNotFoundError:
    from playwright_check import (
        check_page,
        get_rendered_html,


    )
from urllib.parse import urljoin, urlparse
from datetime import datetime
from pathlib import Path

# ----------------------------------------
# Configuration
# ----------------------------------------

import os
from dotenv import load_dotenv

load_dotenv()

# Week 3 Live Application Configuration
URL = os.getenv(
    "TARGET_URL",
    "https://live.ideabytesiot.com/demolive"
)

MAX_PAGES = int(
    os.getenv("MAX_PAGES", "10")
)

OUTPUT_FILE = "reports/website_elements.json"


# ----------------------------------------
# Download page using Requests
# ----------------------------------------
def get_page(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser"
        )

    except requests.exceptions.Timeout:

        print("Error: Request timed out.")
        return None

    except requests.exceptions.HTTPError:

        print(
            "HTTP Error:",
            response.status_code
        )
        return None

    except requests.exceptions.RequestException as e:

        print("Request Error:", e)
        return None


# ----------------------------------------
# Find Internal Links
# ----------------------------------------
def get_internal_links(soup, base_url):

    internal_links = set()

    base_domain = urlparse(base_url).netloc

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

        if href.startswith("#"):
            continue

        if href.startswith("mailto:"):
            continue

        if href.startswith("tel:"):
            continue

        full_url = urljoin(base_url, href)

        parsed = urlparse(full_url)

        if parsed.netloc == base_domain:

            cleaned_url = (
                parsed.scheme
                + "://"
                + parsed.netloc
                + parsed.path
            )

            internal_links.add(cleaned_url)

    return internal_links


# ----------------------------------------
# Extract Elements
# ----------------------------------------
def extract_elements(soup, url):

    buttons = []

    for button in soup.find_all("button"):

        text = button.get_text(
            strip=True
        ).replace("'", "\\'")
        
        if not text and not button.get("id"):
            continue

        buttons.append({

            "text":
            button.get_text(
                strip=True
            ) or "",

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

            "selector":
            (
                f"#{button.get('id')}"
                if button.get("id")
                else f"button:has-text('{text}')"
            )
        })

    # Input buttons
    for inp in soup.find_all("input"):

        if inp.get(
            "type",
            ""
        ).lower() in [
            "submit",
            "button"
        ]:

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
                (
                    f"#{inp.get('id')}"
                    if inp.get("id")
                    else f"input[name='{inp.get('name', '')}']"
                )
            })

    # Inputs
    # Inputs
    inputs = []

    SKIP_INPUT_TYPES = {
        "submit",
        "button",
        "hidden",
        "file",
        "image",
        "reset",
    }

    for inp in soup.find_all("input"):

        input_type = inp.get(
            "type",
            "text"
        ).lower()

        # Skip non-interactable inputs
        if input_type in SKIP_INPUT_TYPES:
            continue

        # Skip disabled inputs
        if inp.has_attr("disabled"):
            continue

        # Skip readonly inputs
        if inp.has_attr("readonly"):
            continue

        # Skip CSS-hidden inputs
        style = inp.get("style", "").lower()

        if "display:none" in style:
            continue

        if "visibility:hidden" in style:
            continue

        selector = (
            f"#{inp.get('id')}"
            if inp.get("id")
            else f"input[name='{inp.get('name', '')}']"
        )

        # Skip empty selectors
        if selector in (
            "input[name='']",
            'input[name=""]',
        ):
            continue

        inputs.append({

            "type": input_type,

            "name": inp.get(
                "name",
                ""
            ),

            "id": inp.get(
                "id",
                ""
            ),

            "class": " ".join(
                inp.get(
                    "class",
                    []
                )
            ),

            "placeholder": inp.get(
                "placeholder",
                ""
            ),

            "selector": selector,
        })
    # Links
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

        full_url = urljoin(url, href)

        if full_url in seen_links:
            continue

        seen_links.add(full_url)

        text = link.get_text(strip=True)
        if text == "":
            continue

        lid = link.get("id", "")

        # Skip completely empty links
        if not text and not lid and not href:
            continue

        links.append({

            "text": text or "",

            "href": full_url,

            "id": lid,

            "class": " ".join(
                link.get(
                    "class",
                    []
                )
            ),

            "selector": (
                f"#{lid}"
                if lid
                else f"a:has-text('{text}')"
                if text
                else f"a[href='{full_url}']"
            )
        })
    return {

        "url":
        url,

        "scraped_at":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "total_elements":
        len(buttons)
        + len(inputs)
        + len(links),

        "buttons":
        buttons,

        "inputs":
        inputs,

        "links":
        links
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
    url = url or os.getenv("TARGET_URL", URL)
    max_pages = max_pages or int(os.getenv("MAX_PAGES", "10"))

    print("=" * 50)
    print("Starting Crawl")
    print("=" * 50)

    if not url.startswith(
        ("http://", "https://")
    ):
        print("Invalid URL")
        return []

    visited = set()

    to_visit = [url]
    BASE = "https://live.ideabytesiot.com/demolive/"
    KNOWN_ROUTES = [
        "dashboard/status-list",
        "reports/scheduled",
        "alerts",
        "devices",
        "alarms",
        "users/users-management",
    ]

    for route in KNOWN_ROUTES:
        to_visit.append(urljoin(BASE, route))

    all_pages_data = []

    while (
        to_visit
        and len(visited) < max_pages
    ):

        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        visited.add(
            current_url
        )

        print(
            f"\n[{len(visited)}/{max_pages}] "
            f"Scraping: {current_url}"
        )

        try:

            #check_page(
            #    current_url
            #)

            html = get_rendered_html(current_url)

            if not html:
                continue

            soup = BeautifulSoup(
                html,
                "html.parser"
            )


            print("Using Playwright rendered HTML")

            page_data = extract_elements(
                soup,
                current_url
            )

            all_pages_data.append(
                page_data
            )

            print(
                "Buttons:",
                len(
                    page_data["buttons"]
                )
            )

            print(
                "Inputs:",
                len(
                    page_data["inputs"]
                )
            )

            print(
                "Links:",
                len(
                    page_data["links"]
                )
            )

            internal_links = get_internal_links(
                soup,
                current_url
            )
            

            for link in sorted(internal_links):

                if (
                    link not in visited
                    and link not in to_visit
                ):
                    print(f"[DISCOVERED] {link}")
                    to_visit.append(link)

        except Exception as e:

            print(
                f"Failed to scrape {current_url}"
            )

            print(e)

    save_json(
        all_pages_data,
        OUTPUT_FILE
    )

    print("\nCrawl Complete")
    print(
        "Pages Crawled:",
        len(all_pages_data)
    )

    print(
        "Saved:",
        OUTPUT_FILE
    )

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