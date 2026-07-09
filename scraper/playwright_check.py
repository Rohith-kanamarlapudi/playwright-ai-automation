from playwright.sync_api import sync_playwright
import os
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

AUTH_STATE = "auth.json"


def check_page(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            if os.path.exists(AUTH_STATE):
                context = browser.new_context(storage_state=AUTH_STATE)
            else:
                print("[WARNING] auth.json not found. Using anonymous session.")
                context = browser.new_context()

            page = context.new_page()

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            try:
                page.wait_for_selector(
                    "ib-iot-root",
                    timeout=30000
                )
            except Exception:
                pass

            page.wait_for_load_state("networkidle")

            if response and response.status < 400:
                print(f"Playwright Check: PASS (status {response.status})")
            else:
                print(
                    f"Playwright Check: FAIL "
                    f"(status {response.status if response else 'no response'})"
                )

            browser.close()

    except Exception as e:
        print(f"Playwright Check: FAIL — {e}")


def get_rendered_html(url):
    """
    Returns rendered HTML using an authenticated Playwright session.
    """
    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            if os.path.exists(AUTH_STATE):
                context = browser.new_context(
                    storage_state=AUTH_STATE
                )
            else:
                print("[WARNING] auth.json not found. Using anonymous session.")
                context = browser.new_context()

            page = context.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            try:
                page.wait_for_selector(
                    "ib-iot-root",
                    timeout=30000
                )
            except Exception:
                pass

            page.wait_for_load_state("networkidle")

            html = page.content()

            browser.close()

            return html

    except Exception as e:
        print(f"get_rendered_html failed for {url}: {e}")
        return None


def get_rendered_routes(url):
    """
    Discover routes after Angular has rendered using
    the authenticated Playwright session.
    """
    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            if os.path.exists(AUTH_STATE):
                context = browser.new_context(
                    storage_state=AUTH_STATE
                )
            else:
                context = browser.new_context()

            page = context.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            try:
                page.wait_for_selector(
                    "ib-iot-root",
                    timeout=30000
                )
            except Exception:
                pass

            page.wait_for_load_state("networkidle")

            routes = []

            anchors = page.locator("a")

            count = anchors.count()

            for i in range(count):

                anchor = anchors.nth(i)

                href = anchor.get_attribute("href")

                text = anchor.inner_text().strip()

                if not href:
                    continue

                routes.append({
                    "text": text,
                    "href": urljoin(url, href)
                })

            browser.close()

            return routes

    except Exception as e:
        print(f"get_rendered_routes failed: {e}")
        return []