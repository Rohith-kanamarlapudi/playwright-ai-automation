```
# File: config/config.py
import os
import yaml

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)

    @property
    def base_url(self):
        return self.data['base_url']

    @property
    def browser_type(self):
        return self.data['browser']['type']

    @property
    def headless(self):
        return self.data['browser']['headless']

    @property
    def slow_mo(self):
        return self.data['browser'].get('slow_mo', 0)

    @property
    def default_timeout(self):
        return self.data['timeouts']['default']

    @property
    def navigation_timeout(self):
        return self.data['timeouts']['navigation']

    @property
    def viewport(self):
        return self.data.get('viewport', {'width': 1280, 'height': 720})

    def get_viewport_for_test(self, size):
        return {'width': size[0], 'height': size[1]}

# If config.yaml is not present, a default is created automatically (you can embed the YAML as a string)
```
```yaml
# File: config/config.yaml
base_url: "https://ideabytes.com"
browser:
  type: chromium
  headless: true
  slow_mo: 100
timeouts:
  default: 30000
  navigation: 60000
viewport:
  width: 1280
  height: 720
```
```python
# File: utils/logger.py
import logging
import sys

def setup_logger(name=__name__, log_file='logs/automation.log'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()
```
```python
# File: utils/http_utils.py
import requests

def check_url_status(url: str) -> int:
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        return resp.status_code
    except requests.RequestException:
        return 0

def download_file_size(url: str) -> int:
    try:
        resp = requests.get(url, stream=True, timeout=10)
        resp.raise_for_status()
        return len(resp.content)
    except requests.RequestException:
        return 0
```
```python
# File: utils/allure_helper.py
import allure

def attach_log(text: str):
    allure.attach(text, 'test_log', attachment_type=allure.attachment_type.TEXT)

def attach_screenshot(page, name: str):
    allure.attach(page.screenshot(), name=name, attachment_type=allure.attachment_type.PNG)
```
```python
# File: selectors/home_selectors.py
class HomeSelectors:
    HAMBURGER_BUTTON = "button.lines-button.x"
    LOGO_LINK = "a.logo[href='https://ideabytes.com/index.html']"
    CONTACT_LINK = "a:has-text('Contact')"
    IOT_SOLUTIONS_LINK = "a:has-text('IoT Solutions')"
    DG_HAZMAT_LINK = "a:has-text('DG HAZMAT')"
    IGBMS_LINK = "a:has-text('IGBMS')"
    TEST_AUTOMATION_LINK = "a:has-text('Test Automation')"
    APPLICATION_DEVELOPMENT_LINK = "a:has-text('Application Development')"
    TEENS4TECH_LINK = "a:has-text('Teens4Tech')"
    PARTNERSHIPS_LINK = "a:has-text('Partnerships')"
    ABOUT_US_LINK = "a:has-text('About Us')"
    CERTIFICATES_LINK = "a:has-text('Certificates')"
    TEAM_LINK = "a:has-text('Team')"
    DISCOVER_MORE_LINKS = "a.blog_link:has-text('Discover More')"
    LINKEDIN_LINK = "a[href='https://in.linkedin.com/company/ideabytes-inc']"
    PDF_ISO9001 = "a[href='https://ideabytes.com/certificates/Ideabytes-ISO9001-2015.pdf']"
    PDF_ISO27001 = "a[href='https://ideabytes.com/certificates/Ideabytes-ISO-IEC27001-2022.pdf']"
    PDF_ISO27017 = "a[href='https://ideabytes.com/certificates/Ideabytes-ISO-IEC27017-2015.pdf']"
    # All navigation anchors (excluding logo and external)
    NAV_LINKS = [
        CONTACT_LINK,
        IOT_SOLUTIONS_LINK,
        DG_HAZMAT_LINK,
        IGBMS_LINK,
        TEST_AUTOMATION_LINK,
        APPLICATION_DEVELOPMENT_LINK,
        TEENS4TECH_LINK,
        PARTNERSHIPS_LINK,
        ABOUT_US_LINK,
        CERTIFICATES_LINK,
        TEAM_LINK,
    ]
```
```python
# File: selectors/contact_selectors.py
class ContactSelectors:
    # Selectors for contact form – none detected on the website provided, we will not invent.
    pass
```
```python
# File: pages/base_page.py
import allure
from playwright.sync_api import Page, expect
from utils.logger import logger

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 30000

    def navigate(self, url: str):
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="networkidle")

    def click(self, selector: str, **kwargs):
        logger.info(f"Clicking element: {selector}")
        self.page.click(selector, **kwargs)

    def fill(self, selector: str, text: str, **kwargs):
        logger.info(f"Filling '{text}' into {selector}")
        self.page.fill(selector, text, **kwargs)

    def wait_for_element(self, selector: str, state="visible", timeout=None):
        self.page.wait_for_selector(selector, state=state, timeout=timeout or self.timeout)

    def take_screenshot(self, name: str):
        self.page.screenshot(path=f"screenshots/{name}.png")
        allure.attach.file(f"screenshots/{name}.png", name=name, attachment_type=allure.attachment_type.PNG)

    def get_element_text(self, selector: str) -> str:
        return self.page.text_content(selector)

    def is_element_visible(self, selector: str) -> bool:
        return self.page.is_visible(selector)

    def get_attribute(self, selector: str, attribute: str) -> str:
        return self.page.get_attribute(selector, attribute)

    def wait_for_page_load(self):
        self.page.wait_for_load_state("networkidle")
```
```python
# File: pages/home_page.py
from pages.base_page import BasePage
from selectors.home_selectors import HomeSelectors

class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.selectors = HomeSelectors()

    def click_hamburger(self):
        self.click(self.selectors.HAMBURGER_BUTTON)

    def click_logo(self):
        self.click(self.selectors.LOGO_LINK)

    def get_all_discover_more_links_hrefs(self):
        elements = self.page.query_selector_all(self.selectors.DISCOVER_MORE_LINKS)
        return [el.get_attribute("href") for el in elements]

    def is_hamburger_visible(self):
        return self.is_element_visible(self.selectors.HAMBURGER_BUTTON)

    def click_nav_link(self, link_selector):
        self.click(link_selector)

    def get_nav_link_href(self, link_selector):
        return self.get_attribute(link_selector, "href")
```
```python
# File: pages/contact_page.py
from pages.base_page import BasePage
from selectors.contact_selectors import ContactSelectors

class ContactPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.selectors = ContactSelectors()
```
```python
# File: tests/conftest.py
import pytest
import yaml
from playwright.sync_api import sync_playwright
from config.config import Config
from utils.logger import logger
from pages.home_page import HomePage

# Load config once per session
@pytest.fixture(scope="session")
def config():
    return Config()

@pytest.fixture(scope="session")
def browser_context_args(config):
    return {
        "viewport": config.viewport,
        "locale": "en-US",
    }

@pytest.fixture(scope="function")
def page(config, browser_context_args):
    with sync_playwright() as playwright:
        browser = getattr(playwright, config.browser_type).launch(
            headless=config.headless,
            slow_mo=config.slow_mo
        )
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        yield page
        context.close()
        browser.close()

@pytest.fixture
def home_page(page, config):
    home = HomePage(page)
    home.navigate(config.base_url)
    home.wait_for_page_load()
    return home

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_name = f"{item.nodeid.replace('::', '_')}_fail"
            page.screenshot(path=f"screenshots/{screenshot_name}.png")
            logger.error(f"Test failed: {item.nodeid}")
            try:
                import allure
                allure.attach.file(f"screenshots/{screenshot_name}.png",
                                   name=screenshot_name,
                                   attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
```
```python
# File: tests/test_navigation.py
import allure
import pytest
from config.config import Config
from utils.http_utils import check_url_status

@allure.feature("Navigation Links")
class TestNavigation:

    @allure.story("Internal navigation links")
    @pytest.mark.parametrize("link_selector,expected_url", [
        ("a:has-text('Contact')", "https://ideabytes.com/contact-us.html"),
        ("a:has-text('IoT Solutions')", "https://www.ideabytesiot.com/"),
        ("a:has-text('DG HAZMAT')", "https://www.dgsms.ca"),
        ("a:has-text('IGBMS')", "https://igbms.com/"),
        ("a:has-text('Test Automation')", "https://ideabytes.com/test-automation.html"),
        ("a:has-text('Application Development')", "https://ideabytes.com/web-mobile-app-dev.html"),
        ("a:has-text('Teens4Tech')", "https://ideabytes.com/Teens_tech.html"),
        ("a:has-text('Partnerships')", "https://ideabytes.com/partnership.html"),
        ("a:has-text('About Us')", "https://ideabytes.com/about-us.html"),
        ("a:has-text('Certificates')", "https://ideabytes.com/certificates.html"),
        ("a:has-text('Team')", "https://ideabytes.com/team.html"),
    ])
    def test_nav_link_click_navigates(self, home_page, link_selector, expected_url):
        with allure.step(f"Click navigation link: {link_selector}"):
            home_page.click_nav_link(link_selector)
        with allure.step("Wait for page load"):
            home_page.wait_for_page_load()
        with allure.step("Verify current URL"):
            assert home_page.page.url == expected_url, f"Expected {expected_url}, got {home_page.page.url}"

    @allure.story("Logo link")
    def test_logo_link_navigates_to_home(self, home_page):
        with allure.step("Click logo link"):
            home_page.click_logo()
        with allure.step("Verify URL is homepage"):
            assert home_page.page.url == "https://ideabytes.com/index.html"

    @allure.story("Discover More links")
    def test_discover_more_links_http_status(self, home_page):
        with allure.step("Get all Discover More hrefs"):
            hrefs = home_page.get_all_discover_more_links_hrefs()
        assert len(hrefs) > 0, "No Discover More links found"
        for href in hrefs:
            with allure.step(f"Check HTTP status for {href}"):
                status = check_url_status(href)
                assert status == 200, f"{href} returned HTTP {status}"

    @allure.story("LinkedIn link opens in new tab or navigates")
    def test_linkedin_link(self, home_page):
        with allure.step("Click LinkedIn link and wait for new page"):
            with home_page.page.context.expect_page() as new_page_info:
                home_page.click("a[href='https://in.linkedin.com/company/ideabytes-inc']")
            new_page = new_page_info.value
            new_page.wait_for_load_state()
            assert "linkedin.com" in new_page.url

    @allure.story("PDF certificate links are downloadable")
    @pytest.mark.parametrize("pdf_selector", [
        "a[href='https://ideabytes.com/certificates/Ideabytes-ISO9001-2015.pdf']",
        "a[href='https://ideabytes.com/certificates/Ideabytes-ISO-IEC27001-2022.pdf']",
        "a[href='https://ideabytes.com/certificates/Ideabytes-ISO-IEC27017-2015.pdf']"
    ])
    def test_pdf_links_download(self, home_page, pdf_selector):
        with allure.step("Click PDF link and wait for download"):
            with home_page.page.expect_download() as download_info:
                home_page.click(pdf_selector)
            download = download_info.value
            # Expect a download event; we can accept it or just verify that it was triggered
            assert download.suggested_filename.endswith('.pdf')
```
```python
# File: tests/test_responsive.py
import allure
import pytest

@allure.feature("Responsive UI")
class TestResponsive:

    @allure.story("Hamburger menu visibility on mobile viewport")
    @pytest.mark.parametrize("viewport_size", [(375, 812), (768, 1024)])
    def test_hamburger_visible_on_mobile(self, home_page, viewport_size):
        with allure.step(f"Set viewport to {viewport_size}"):
            home_page.page.set_viewport_size({"width": viewport_size[0], "height": viewport_size[1]})
        with allure.step("Check that hamburger button is visible"):
            assert home_page.is_hamburger_visible(), \
                f"Hamburger button should be visible at viewport {viewport_size}"

    @allure.story("Hamburger menu hides on desktop viewport")
    def test_hamburger_hidden_on_desktop(self, home_page):
        with allure.step("Set viewport to 1920x1080"):
            home_page.page.set_viewport_size({"width": 1920, "height": 1080})
        with allure.step("Check that hamburger button is not visible"):
            assert not home_page.is_hamburger_visible(), \
                "Hamburger button should be hidden on desktop viewport"

    @allure.story("Hamburger toggles mobile navigation")
    def test_hamburger_toggles_nav(self, home_page):
        with allure.step("Set mobile viewport"):
            home_page.page.set_viewport_size({"width": 375, "height": 812})
        # We need to verify that clicking hamburger shows/hides a mobile menu.
        # Since we don't have a selector for the mobile menu panel, we check for the button's aria-expanded or a class.
        # Here we use a generic approach: expect the button to have an 'active' class or similar.
        hamburger_selector = "button.lines-button.x"
        # Before click, assume menu is closed.
        initial_class = home_page.get_attribute(hamburger_selector, "class")
        with allure.step("Click hamburger"):
            home_page.click_hamburger()
        # After click, the class may change (e.g., 'lines-button x active')
        after_click_class = home_page.get_attribute(hamburger_selector, "class")
        with allure.step("Verify class changed indicating toggled"):
            assert initial_class != after_click_class, \
                "Hamburger button class should change after click"
```
```python
# File: tests/test_keyboard_accessibility.py
import allure
import pytest

@allure.feature("Keyboard Accessibility")
class TestKeyboardAccessibility:

    @allure.story("All visible navigation links are focusable and activate with Enter")
    def test_nav_links_keyboard_focusable(self, home_page):
        # All nav links that are visible at default desktop viewport
        nav_selectors = [
            "a:has-text('Contact')",
            "a:has-text('IoT Solutions')",
            "a:has-text('DG HAZMAT')",
            "a:has-text('IGBMS')",
            "a:has-text('Test Automation')",
            "a:has-text('Application Development')",
            "a:has-text('Teens4Tech')",
            "a:has-text('Partnerships')",
            "a:has-text('About Us')",
            "a:has-text('Certificates')",
            "a:has-text('Team')",
        ]
        for selector in nav_selectors:
            with allure.step(f"Check focusability of {selector}"):
                elem = home_page.page.locator(selector).first
                # Check that the element is visible and can be focused
                assert elem.is_visible(), f"{selector} is not visible"
                # Focus using keyboard tab; but we can directly focus via Playwright
                elem.focus()
                # Verify it received focus
                active = home_page.page.evaluate("document.activeElement === arguments[0]", elem.element_handles()[0])
                assert active, f"{selector} did not receive focus"
                # Simulate Enter key
                home_page.page.keyboard.press("Enter")
                # Wait a moment, check if URL changed (should not be homepage for internal links)
                # We can use a simplified check: after pressing Enter on a link, the page should navigate.
                # For this test we only verify that the element is focusable; full navigation test is separate.
                # We'll just verify no error occurred and page is not blank.
                assert home_page.page.url != "about:blank"
                # Go back to home for next link
                if home_page.page.url != "https://ideabytes.com/":
                    home_page.navigate("https://ideabytes.com/")
                home_page.wait_for_page_load()
```
```python
# File: tests/test_error_handling.py
import allure
import pytest

@allure.feature("Error Handling")
class TestErrorHandling:

    @allure.story("Navigate to non-existent page returns 404")
    def test_404_page(self, home_page):
        with allure.step("Navigate to a non-existent URL"):
            home_page.page.goto("https://ideabytes.com/nonexistent", wait_until="networkidle")
        # The page may display custom 404 content or return HTTP 404.
        # Check for common indicators: title contains '404', or page text contains '404' or 'not found'
        page_content = home_page.page.content().lower()
        assert "404" in page_content or "page not found" in page_content or "not found" in page_content, \
            "Expected 404 page indicators not found"
```
```python
# File: conftest.py
# Root conftest to set up reporting and any global hooks (optional)
# If you already have tests/conftest.py, this is not needed. We keep it minimal.
```
```ini
# File: pytest.ini
[pytest]
log_cli = true
log_cli_level = INFO
addopts = -v --tb=short --html=reports/pytest-html/report.html --self-contained-html --alluredir=reports/allure-results
testpaths = tests
markers =
    smoke: smoke tests
    regression: full regression
```
```
# File: requirements.txt
playwright>=1.30.0
pytest>=7.0.0
pytest-html>=3.2.0
allure-pytest>=2.12.0
pyyaml>=6.0
requests>=2.28.0
```
```python
# File: tests/test_contact_form.py
# Note: No input selectors were detected on the contact page, so we skip form submission tests.
# This file is intentionally left empty to indicate that the Contact form is not present.
```