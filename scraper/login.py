from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()


def login_and_save_state():
    with sync_playwright() as p:
        print("[INFO] Launching browser...")

        browser = p.chromium.launch(headless=True)

        context = browser.new_context()

        page = context.new_page()

        print("[INFO] Opening login page...")
        page.goto(os.getenv("TARGET_URL"), wait_until="networkidle")

        print("[INFO] Filling email...")
        page.fill("#username", os.getenv("EMAIL"))

        print("[INFO] Filling password...")
        page.fill("#password", os.getenv("PASSWORD"))

        print("[INFO] Clicking Sign In...")
        page.click("#kc-login")

        print("[INFO] Waiting for Angular dashboard...")
        page.wait_for_selector("ib-iot-root", timeout=30000)

        page.wait_for_load_state("networkidle")

        print("[INFO] Saving authentication state...")
        context.storage_state(path="auth.json")

        browser.close()

        print("[SUCCESS] Authentication saved to auth.json")


if __name__ == "__main__":
    login_and_save_state()