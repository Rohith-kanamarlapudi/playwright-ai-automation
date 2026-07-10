from playwright.sync_api import sync_playwright
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------
# CHANGED: auth.json now resolves to an absolute path instead of
# the cwd-relative "auth.json" the original code used.
#
# Why this matters: playwright_check.py already computes
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     AUTH_STATE = BASE_DIR / "auth.json"
# which is an ABSOLUTE path anchored to the project root, no
# matter where `python scraper.py` is run from. The old
# login.py instead wrote to whatever the current working
# directory happened to be when `python login.py` was run
# (context.storage_state(path="auth.json")). If those two
# working directories ever differed, playwright_check.py would
# report "auth.json not found" even right after a successful
# login - which is exactly the kind of manual, confusing cleanup
# the single-command workflow requirement asks us to eliminate.
#
# login.py lives in the SAME folder as playwright_check.py
# (both inside the `scraper/` package), so it needs the exact
# same ".parent.parent" (two levels up, to the project root) -
# NOT just ".parent" - to land on the identical auth.json.
# Using only one ".parent" here was the actual bug: login.py
# was saving to <project_root>/scraper/auth.json while
# playwright_check.py kept looking for <project_root>/auth.json,
# so every run "succeeded" at login but still reported the file
# as missing right afterwards.
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_STATE = BASE_DIR / "auth.json"


# ----------------------------------------------------------
# NEW: the actual login steps, factored out of
# login_and_save_state() so they can run inside a `browser`
# that already exists.
#
# Why: scraper.py's single-command workflow (see
# playwright_check.py's ensure_authenticated()) needs to be able
# to trigger a login automatically, mid-crawl, without opening a
# SECOND Chromium instance on top of the one the crawler already
# has open. Splitting the steps into perform_login(browser) lets
# both callers share one browser:
#   - `python login.py` on its own -> login_and_save_state() below
#     opens its own browser, calls perform_login(browser), closes it.
#   - the crawler -> passes its own already-open `browser` straight
#     into perform_login(browser), no extra browser launch.
#
# Every individual step (goto, fill email, fill password, click
# Sign In, wait for the Angular dashboard, save storage_state) is
# unchanged from the original login_and_save_state() - only where
# the browser comes from has changed.
# ----------------------------------------------------------
def perform_login(browser):
    """
    Logs in inside a fresh context on the given (already open)
    `browser`, then overwrites auth.json with the new session.
    Returns nothing - callers that need a working context/page
    afterwards should open a NEW context from auth.json themselves
    (this keeps "log in" and "use the session" as separate, simple
    steps, same as the rest of the project's style).
    """

    context = browser.new_context()

    page = context.new_page()

    print("[INFO] Opening login page...")
    page.goto(os.getenv("TARGET_URL"), wait_until="domcontentloaded")

    print("[INFO] Filling email...")
    page.fill("#username", os.getenv("EMAIL"))

    print("[INFO] Filling password...")
    page.fill("#password", os.getenv("PASSWORD"))

    print("[INFO] Clicking Sign In...")
    page.click("#kc-login")

    print("[INFO] Waiting for Angular dashboard...")
    page.wait_for_selector("ib-iot-root", timeout=30000)

    page.wait_for_load_state("domcontentloaded")

    print("[INFO] Saving authentication state...")
    context.storage_state(path=str(AUTH_STATE))

    context.close()

    print(f"[SUCCESS] Authentication saved to {AUTH_STATE}")


# ----------------------------------------------------------
# Standalone entry point - unchanged behavior from the original
# file. `python login.py` still opens its own browser, logs in,
# saves auth.json, and closes the browser. It now just delegates
# the actual steps to perform_login(browser) above instead of
# duplicating them.
# ----------------------------------------------------------
def login_and_save_state():
    with sync_playwright() as p:
        print("[INFO] Launching browser...")

        browser = p.chromium.launch(headless=False)

        perform_login(browser)

        browser.close()


if __name__ == "__main__":
    login_and_save_state()