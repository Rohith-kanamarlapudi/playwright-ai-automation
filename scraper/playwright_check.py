from playwright.sync_api import sync_playwright


def check_page(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(url, timeout=10000)
            browser.close()

            if response and response.status < 400:
                print(f"Playwright Check: PASS (status {response.status})")
            else:
                print(f"Playwright Check: FAIL (status {response.status if response else 'no response'})")

    except Exception as e:
        print(f"Playwright Check: FAIL — {e}")


def get_rendered_html(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=10000)
            html = page.content()
            browser.close()
            return html

    except Exception as e:
        print(f"get_rendered_html failed for {url}: {e}")
        return None