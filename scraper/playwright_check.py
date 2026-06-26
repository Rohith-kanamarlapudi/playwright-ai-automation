from playwright.sync_api import sync_playwright

def check_page(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(url, wait_until="networkidle", timeout=30000)

            print("Title:", page.title())
            print("Playwright Check: PASS")

            browser.close()

    except Exception as e:
        print("Playwright Check: FAIL")
        print(e)