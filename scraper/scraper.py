
import requests
import json
from bs4 import BeautifulSoup
from playwright_check import check_page, get_rendered_html
from urllib.parse import urljoin
from datetime import datetime

URL = "https://ideabytes.com"
OUTPUT_FILE = "website_elements.json"


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
            timeout=10
        )

        response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")

    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        return None

    except requests.exceptions.HTTPError:
        print("HTTP Error:", response.status_code)
        return None

    except requests.exceptions.RequestException as e:
        print("Request Error:", e)
        return None


# ----------------------------------------
# Extract buttons, inputs and links
# ----------------------------------------
def extract_elements(soup, url):

    buttons = []

    # Normal button tags
    for button in soup.find_all("button"):

        # Escape single quotes in button text to prevent broken Playwright selectors
        text = button.get_text(strip=True).replace("'", "\\'")

        buttons.append({
            "text": button.get_text(strip=True) or "",
            "type": button.get("type", "button"),
            "id": button.get("id", ""),
            "class": " ".join(button.get("class", [])),
            "name": button.get("name", ""),
            # Use ID selector if available, otherwise fall back to text selector
            "selector": f"#{button.get('id')}" if button.get("id") else f"button:has-text('{text}')"
        })

    # Input buttons (type="submit" or type="button")
    for inp in soup.find_all("input"):

        if inp.get("type", "").lower() in ["submit", "button"]:

            buttons.append({
                "text": inp.get("value", ""),
                "type": inp.get("type", "button"),
                "id": inp.get("id", ""),
                "class": " ".join(inp.get("class", [])),
                "name": inp.get("name", ""),
                # Use ID selector if available, otherwise fall back to name attribute
                "selector": f"#{inp.get('id')}" if inp.get("id") else f"input[name='{inp.get('name', '')}']"
            })

    inputs = []

    # Skip input types that are already handled as buttons above
    SKIP_INPUT_TYPES = {"submit", "button"}

    for inp in soup.find_all("input"):

        input_type = inp.get("type", "text").lower()

        if input_type in SKIP_INPUT_TYPES:
            continue

        inputs.append({
            "type": input_type,
            "name": inp.get("name", ""),
            "id": inp.get("id", ""),
            "class": " ".join(inp.get("class", [])),
            "placeholder": inp.get("placeholder", ""),
            # Use ID selector if available, otherwise fall back to name attribute
            "selector": f"#{inp.get('id')}" if inp.get("id") else f"input[name='{inp.get('name', '')}']"
        })

    links = []

    # Track seen URLs to avoid adding duplicate links
    seen_links = set()

    for link in soup.find_all("a"):

        href = link.get("href", "")

        # Skip empty href
        if not href.strip():
            continue

        # Skip anchor-only links (e.g. href="#")
        if href == "#":
            continue

        # Resolve relative URLs to absolute using the base page URL
        full_url = urljoin(url, href)

        # Skip if this URL has already been added
        if full_url in seen_links:
            continue

        seen_links.add(full_url)

        lid = link.get("id", "")
        text = link.get_text(strip=True)

        links.append({
            "text": text or "",
            "href": full_url,
            "id": lid,
            "class": " ".join(link.get("class", [])),
            # Use ID selector if available,
            # then fall back to text selector,
            # finally fall back to href selector (may break if URL has special characters)
            "selector": f"#{lid}" if lid else f"a:has-text('{text}')" if text else f"a[href='{full_url}']"
        })

    # Warn if any element group came back empty
    if not buttons:
        print("No buttons found.")

    if not inputs:
        print("No inputs found.")

    if not links:
        print("No links found.")

    return {
        "url": url,
        "scraped_at": str(datetime.now()),
        "total_elements": len(buttons) + len(inputs) + len(links),
        "buttons": buttons,
        "inputs": inputs,
        "links": links
    }


# ----------------------------------------
# Save JSON
# ----------------------------------------
def save_json(data, filename):

    with open(filename, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False  # Preserves non-English characters in output
        )


# ----------------------------------------
# Main Program
# ----------------------------------------
def main(url=URL):

    print("Scraping:", url)

    # Basic Playwright page check before scraping
    check_page(url)

    # Download page with Requests
    soup = get_page(url)

    if soup is None:
        print("Scraping failed.")
        return None  # Return None so calling modules know scraping failed

    # Count total interactive elements found in static HTML
    total = len(soup.find_all("button")) + len(soup.find_all("input")) + len(soup.find_all("a"))

    # If very few elements found, page likely relies on JavaScript to render content
    # Threshold raised to 10 to avoid false negatives on simple static pages
    if total < 10:

        print("\nPossible JavaScript-heavy page detected.")

        html = get_rendered_html(url)

        if html:

            # Re-parse using the fully JS-rendered HTML from Playwright
            soup = BeautifulSoup(html, "html.parser")

            print("Scraper used: Playwright-rendered HTML")

        else:

            print("Playwright rendering failed. Using static HTML.")

    else:

        print("Scraper used: Requests + BeautifulSoup")

    try:

        data = extract_elements(soup, url)

        save_json(data, OUTPUT_FILE)

        print("\nButtons:", len(data["buttons"]))
        print("Inputs :", len(data["inputs"]))
        print("Links  :", len(data["links"]))

        print("\nSaved to", OUTPUT_FILE)

        # Return data so the pipeline can chain this into the next module
        return data

    except Exception as e:

        print("Error while extracting elements:", e)
        return None  # Return None on failure so callers can handle gracefully


if __name__ == "__main__":
    main()
