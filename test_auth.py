from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        storage_state="auth.json"
    )

    page = context.new_page()

    page.goto(
        "https://live.ideabytesiot.com/demolive/dashboard/status-list"
    )

    page.wait_for_timeout(5000)

    print(page.url)

    browser.close()