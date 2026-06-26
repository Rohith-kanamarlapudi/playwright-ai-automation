import requests
import json
from bs4 import BeautifulSoup
from scraper.playwright_check import check_page
from urllib.parse import urljoin
from datetime import datetime

URL = "https://ideabytes.com"
OUTPUT_FILE = "website_elements.json"

# Download page and create BeautifulSoup object
def get_page(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


# Extract buttons, inputs and links
def extract_elements(soup, url):

    buttons = []

    # Normal button tags
    for button in soup.find_all("button"):
        buttons.append({
            "text": button.get_text(strip=True) or "",
            "type": button.get("type", "button"),
            "id": button.get("id", ""),
            "class": " ".join(button.get("class", [])),
            "name": button.get("name", ""),
            "selector": f"#{button.get('id')}" if button.get("id") else f"button:has-text('{button.get_text(strip=True)}')"
        })

    # Input buttons (submit/button)
    for inp in soup.find_all("input"):

        if inp.get("type", "").lower() in ["submit", "button"]:
            buttons.append({
                "text": inp.get("value", ""),
                "type": inp.get("type", "button"),
                "id": inp.get("id", ""),
                "class": " ".join(inp.get("class", [])),
                "name": inp.get("name", ""),
                "selector": f"#{inp.get('id')}" if inp.get("id") else f"input[name='{inp.get('name', '')}']"
            })

    inputs = []

    # Skip input types already treated as buttons
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
            "selector": f"#{inp.get('id')}" if inp.get("id") else f"input[name='{inp.get('name', '')}']"
        })

    links = []

    for link in soup.find_all("a"):

        href = link.get("href", "")

        links.append({
            "text": link.get_text(strip=True) or "",
            "href": urljoin(url, href),
            "id": link.get("id", ""),
            "class": " ".join(link.get("class", [])),
            "selector": f"#{link.get('id')}" if link.get("id") else f"a[href='{urljoin(url, href)}']"
        })
    links = [
        link for link in links
        if link["text"] and not link["href"].endswith("#")
    ] 

    return {
        "url": url,
        "scraped_at": str(datetime.now()),
        "total_elements": len(buttons) + len(inputs) + len(links),
        "buttons": buttons,
        "inputs": inputs,
        "links": links
    }


# Save data to JSON file
def save_json(data, filename):

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def main(url=URL):

    print("Scraping:", url)
    check_page(url)

    try:

        soup = get_page(url)

        data = extract_elements(soup, url)

        save_json(data, OUTPUT_FILE)

        print("Buttons:", len(data["buttons"]))
        print("Inputs :", len(data["inputs"]))
        print("Links  :", len(data["links"]))

        print("Saved to", OUTPUT_FILE)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()

