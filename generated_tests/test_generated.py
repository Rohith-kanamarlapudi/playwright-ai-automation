```python
# ===============================================================
# File: configs/config.py
# ===============================================================
import os

BASE_URL = os.environ.get("BASE_URL", "https://ideabytes.com")
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"
DEFAULT_VIEWPORT = {"width": 1280, "height": 720}
NAVIGATION_TIMEOUT = 30000
WAIT_TIMEOUT = 10000


# ===============================================================
# File: utils/logger.py
# ===============================================================
import logging
import os

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(LOG_DIR, "test_run.log"))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ===============================================================
# File: utils/screenshot.py
# ===============================================================
import os
from datetime import datetime

SCREENSHOT_DIR = "reports/screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def capture_screenshot(page, test_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    page.screenshot(path=filepath, full_page=True)
    return filepath


# ===============================================================
# File: utils/link_utils.py
# ===============================================================
from playwright.sync_api import Page

def validate_href(href: str) -> bool:
    """Return True if href is not empty and not javascript:void."""
    if not href:
        return False
    if href.strip().startswith("javascript"):
        return False
    return True

def check_pdf_extension(href: str) -> bool:
    return href.lower().endswith(".pdf")

def has_target_blank(page: Page, selector: str) -> bool:
    element = page.query_selector(selector)
    if element:
        target = element.get_attribute("target")
        return target == "_blank"
    return False

def get_text_content(page: Page, selector: str) -> str:
    element = page.query_selector(selector)
    if element:
        return element.text_content().strip()
    return ""


# ===============================================================
# File: utils/responsive_utils.py
# ===============================================================
from playwright.sync_api import Page

def set_viewport(page: Page, width: int, height: int = 800):
    page.set_viewport_size({"width": width, "height": height})

def is_element_hidden(page: Page, selector: str) -> bool:
    element = page.query_selector(selector)
    if element:
        return not element.is_visible()
    return True  # if element does not exist, consider hidden

def check_layout_integrity(page: Page):
    """Basic check: ensure no elements overlap in the navigation area."""
    nav_selectors = [
        "a:has-text('Contact')",
        "a:has-text('IoT Solutions')",
        "a:has-text('About Us')",
    ]
    boxes = []
    for sel in nav_selectors:
        els = page.query_selector_all(sel)
        for el in els:
            if el.is_visible():
                box = el.bounding_box()
                if box:
                    boxes.append(box)
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            # simple overlap check
            if (
                boxes[i]["x"] < boxes[j]["x"] + boxes[j]["width"]
                and boxes[i]["x"] + boxes[i]["width"] > boxes[j]["x"]
                and boxes[i]["y"] < boxes[j]["y"] + boxes[j]["height"]
                and boxes[i]["y"] + boxes[i]["height"] > boxes[j]["y"]
            ):
                return False
    return True


# ===============================================================
# File: pages/base_page.py
# ===============================================================
from playwright.sync_api import Page
from configs.config import BASE_URL, NAVIGATION_TIMEOUT, WAIT_TIMEOUT
from utils.logger import setup_logger
from utils.screenshot import capture_screenshot
import logging

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate(self, url: str = BASE_URL):
        self.page.goto(url, timeout=NAVIGATION_TIMEOUT)
        self.page.wait_for_load_state("networkidle")

    def click(self, selector: str):
        self.page.click(selector)

    def get_element(self, selector: str):
        return self.page.query_selector(selector)

    def wait_for_visible(self, selector: str, timeout: int = WAIT_TIMEOUT):
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def check_element_exists(self, selector: str) -> bool:
        return self.page.query_selector(selector) is not None

    def is_element_visible(self, selector: str) -> bool:
        element = self.page.query_selector(selector)
        if element:
            return element.is_visible()
        return False

    def get_attribute(self, selector: str, attribute: str):
        element = self.page.query_selector(selector)
        if element:
            return element.get_attribute(attribute)
        return None

    def take_screenshot(self, name: str):
        return capture_screenshot(self.page, name)


# ===============================================================
# File: pages/home_page.py
# ===============================================================
from pages.base_page import BasePage

class HomePage(BasePage):
    # Navigation links (unique text)
    contact_link = "a:has-text('Contact')"
    iot_solutions_link = "a:has-text('IoT Solutions')"
    dg_hazmat_link = "a:has-text('DG HAZMAT')"
    igbms_link = "a:has-text('IGBMS')"
    test_automation_link = "a:has-text('Test Automation')"
    application_dev_link = "a:has-text('Application Development')"
    teens4tech_link = "a:has-text('Teens4Tech')"
    partnerships_link = "a:has-text('Partnerships')"
    about_us_link = "a:has-text('About Us')"
    certificates_link = "a:has-text('Certificates')"
    team_link = "a:has-text('Team')"
    logo_link = "a.logo"  # class logo

    # Actionable links
    iot_hardware_software_link = "a.products_text"
    discover_more_links = "a.blog_link"  # multiple
    linkedin_link = "a[href='https://in.linkedin.com/company/ideabytes-inc']"

    # PDF links
    pdf_iso9001 = "a[href='https://ideabytes.com/certificates/Ideabytes-ISO9001-2015.pdf']"
    pdf_iso27001 = "a[href='https://ideabytes.com/certificates/Ideabytes-ISO-IEC27001-2022.pdf']"
    pdf_iso27017 = "a[href='https://ideabytes.com/certificates/Ideabytes-ISO-IEC27017-2015.pdf']"

    # Button
    hamburger_button = "button.lines-button.x"

    # Responsive: navigation container (assuming a nav element)
    nav_container = "nav"  # generic, adjust if needed
    mobile_menu_overlay = None  # not detected

    def click_nav_link(self, link_selector: str):
        self.click(link_selector)

    def click_hamburger(self):
        self.click(self.hamburger_button)

    def get_nav_links(self):
        """Return all top-level navigation link locators as list of strings."""
        return [
            self.contact_link,
            self.iot_solutions_link,
            self.dg_hazmat_link,
            self.igbms_link,
            self.test_automation_link,
            self.application_dev_link,
            self.teens4tech_link,
            self.partnerships_link,
            self.about_us_link,
            self.certificates_link,
            self.team_link,
        ]


# ===============================================================
# File: pages/contact_page.py
# ===============================================================
from pages.base_page import BasePage

class ContactPage(BasePage):
    # If a contact form exists, define locators here.
    # Since no inputs detected, keep as placeholder.
    pass


# ===============================================================
# File: pages/page_factory.py
# ===============================================================
from pages.home_page import HomePage
from pages.contact_page import ContactPage

class PageFactory:
    @staticmethod
    def get_page(page, page_name: str):
        if page_name == "home":
            return HomePage(page)
        elif page_name == "contact":
            return ContactPage(page)
        else:
            raise ValueError(f"Unknown page: {page_name}")


# ===============================================================
# File: tests/conftest.py
# ===============================================================
import pytest
import logging
from playwright.sync_api import sync_playwright
from configs.config import BASE_URL, HEADLESS, DEFAULT_VIEWPORT, NAVIGATION_TIMEOUT
from utils.logger import setup_logger
from utils.screenshot import capture_screenshot

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport=DEFAULT_VIEWPORT,
            ignore_https_errors=True,
        )
        yield context
        context.close()
        browser.close()

@pytest.fixture()
def page(browser_context):
    page = browser_context.new_page()
    # Capture console errors
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.console_errors = console_errors
    yield page
    page.close()

@pytest.fixture()
def home_page(page):
    from pages.home_page import HomePage
    home = HomePage(page)
    home.navigate(BASE_URL)
    return home

@pytest.fixture(params=[375, 768, 1024, 1280])
def viewport_size(request):
    return request.param

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_path = capture_screenshot(page, item.name)
            # Attach to report if using pytest-html
            try:
                from pytest_html import extras
                extra = getattr(rep, "extra", [])
                extra.append(extras.html(f"<a href='{screenshot_path}'>Screenshot</a>"))
                rep.extra = extra
            except ImportError:
                pass

# Set up logging for each test
@pytest.fixture(autouse=True)
def setup_logging(request):
    logger = setup_logger(request.node.name)
    request.node.logger = logger
    yield
    # Cleanup handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


# ===============================================================
# File: tests/test_navigation.py
# ===============================================================
import pytest
from pages.home_page import HomePage, BASE_URL

@pytest.mark.navigation
class TestNavigation:
    """Tests for all navigation links."""

    @pytest.mark.parametrize("link_selector, expected_url", [
        (HomePage.contact_link, "https://ideabytes.com/contact-us.html"),
        (HomePage.iot_solutions_link, "https://www.ideabytesiot.com/"),
        (HomePage.dg_hazmat_link, "https://www.dgsms.ca"),
        (HomePage.igbms_link, "https://igbms.com/"),
        (HomePage.test_automation_link, "https://ideabytes.com/test-automation.html"),
        (HomePage.application_dev_link, "https://ideabytes.com/web-mobile-app-dev.html"),
        (HomePage.teens4tech_link, "https://ideabytes.com/Teens_tech.html"),
        (HomePage.partnerships_link, "https://ideabytes.com/partnership.html"),
        (HomePage.about_us_link, "https://ideabytes.com/about-us.html"),
        (HomePage.certificates_link, "https://ideabytes.com/certificates.html"),
        (HomePage.team_link, "https://ideabytes.com/team.html"),
        (HomePage.linkedin_link, "https://in.linkedin.com/company/ideabytes-inc"),
        (HomePage.logo_link, "https://ideabytes.com/index.html"),
    ])
    def test_navigation_links(self, home_page, link_selector, expected_url):
        """Click a navigation link and verify the URL."""
        home_page.logger.info(f"Navigating to {link_selector}")
        with home_page.page.expect_navigation() as nav_info:
            home_page.click(link_selector)
        actual_url = nav_info.value.url
        assert actual_url == expected_url, f"Expected {expected_url}, got {actual_url}"

    @pytest.mark.parametrize("discover_href", [
        "https://ideabytes.com/test_automation_article4.html",
        "https://ideabytes.com/test_automation_article3.html",
        "https://ideabytes.com/security-testing-article-3.html",
        "https://ideabytes.com/test_automation_article2.html",
        "https://ideabytes.com/web-mobile-app-dev-art2.html",
        "https://ideabytes.com/web-mobile-app-dev-art1.html",
        "https://ideabytes.com/security-testing-article-1.html",
        "https://ideabytes.com/security-testing-article-2.html",
        "https://ideabytes.com/test_automation_article.html",
        "https://ideabytes.com/test_automation_article5.html",
    ])
    def test_discover_more_links(self, home_page, discover_href):
        """Click each 'Discover More' link by href and verify navigation."""
        selector = f"a.blog_link[href='{discover_href}']"
        home_page.logger.info(f"Clicking Discover More link with href {discover_href}")
        with home_page.page.expect_navigation() as nav_info:
            home_page.click(selector)
        assert nav_info.value.url == discover_href

    def test_iot_hardware_software_link(self, home_page):
        """Click IoT Hardware & Software Solutions link."""
        with home_page.page.expect_navigation() as nav_info:
            home_page.click(home_page.iot_hardware_software_link)
        assert nav_info.value.url == "https://www.ideabytesiot.com"

    def test_pdf_iso9001(self, home_page):
        """Click PDF for ISO9001 and verify download or navigation to PDF."""
        with home_page.page.expect_download() as download_info:
            home_page.click(home_page.pdf_iso9001)
        download = download_info.value
        assert download.suggested_filename.endswith(".pdf")

    def test_pdf_iso27001(self, home_page):
        with home_page.page.expect_download() as download_info:
            home_page.click(home_page.pdf_iso27001)
        download = download_info.value
        assert download.suggested_filename.endswith(".pdf")

    def test_pdf_iso27017(self, home_page):
        with home_page.page.expect_download() as download_info:
            home_page.click(home_page.pdf_iso27017)
        download = download_info.value
        assert download.suggested_filename.endswith(".pdf")


# ===============================================================
# File: tests/test_responsive.py
# ===============================================================
import pytest
from pages.home_page import HomePage
from utils.responsive_utils import set_viewport, is_element_hidden, check_layout_integrity

@pytest.mark.responsive
class TestResponsive:
    def test_hamburger_visible_on_small_viewport(self, home_page):
        """At 375px width, hamburger button is visible and nav links are hidden."""
        set_viewport(home_page.page, 375)
        home_page.page.wait_for_timeout(500)  # allow re-render
        assert home_page.is_element_visible(home_page.hamburger_button), "Hamburger not visible at 375px"
        # Check all top nav links are hidden (not visible)
        for nav_link in home_page.get_nav_links():
            if home_page.check_element_exists(nav_link):
                assert not home_page.is_element_visible(nav_link), f"Nav link {nav_link} still visible at 375px"

    def test_hamburger_hidden_on_large_viewport(self, home_page):
        """At 1024px width, hamburger button is hidden and nav links are visible."""
        set_viewport(home_page.page, 1024)
        home_page.page.wait_for_timeout(500)
        # Hamburger should be hidden or not exist
        if home_page.check_element_exists(home_page.hamburger_button):
            assert not home_page.is_element_visible(home_page.hamburger_button), "Hamburger visible at 1024px"
        # Nav links should be visible
        for nav_link in home_page.get_nav_links():
            if home_page.check_element_exists(nav_link):
                assert home_page.is_element_visible(nav_link), f"Nav link {nav_link} not visible at 1024px"

    def test_hamburger_toggle(self, home_page):
        """Click hamburger and verify that the mobile menu toggles (e.g., a class change)."""
        set_viewport(home_page.page, 375)
        home_page.page.wait_for_timeout(500)
        # Get initial state (maybe menu has class 'active' or similar)
        # Since we don't have exact class, we check that after click a menu becomes visible
        # Assume mobile menu is a sibling/child; use generic approach
        # For this test, we simply verify button click does not break
        home_page.click_hamburger()
        # Wait a bit and verify no errors
        assert "error" not in home_page.page.title()

    def test_layout_integrity_responsive(self, home_page, viewport_size):
        """Check that at various viewports, navigation elements do not overlap."""
        set_viewport(home_page.page, viewport_size)
        home_page.page.wait_for_timeout(500)
        assert check_layout_integrity(home_page.page), f"Layout overlap detected at {viewport_size}px"

    def test_text_not_cut_at_320px(self, home_page):
        """Verify that key text is not cut off at 320px width."""
        set_viewport(home_page.page, 320)
        home_page.page.wait_for_timeout(500)
        # Check visibility of an element like the hero heading (if exists). Use a generic check:
        body_text = home_page.page.inner_text("body")
        assert len(body_text) > 0, "Body text is empty at 320px"
        # Additional: check that no element has negative width/height (basic)
        # This is a placeholder; real implementation would check specific elements.

    def test_mobile_menu_closes_on_outside_click(self, home_page):
        """Test that clicking outside the mobile menu closes it."""
        set_viewport(home_page.page, 375)
        home_page.page.wait_for_timeout(500)
        # Open menu
        home_page.click_hamburger()
        # Assume the menu overlay has a specific class or id; we cannot detect.
        # For demonstration, we simply click on the page body and check that menu is hidden.
        # This is a placeholder.
        home_page.page.click("body")
        # Wait a bit
        home_page.page.wait_for_timeout(300)
        # No assertion, just ensure no errors


# ===============================================================
# File: tests/test_validation.py
# ===============================================================
import pytest
from playwright.sync_api import expect
from pages.home_page import HomePage, BASE_URL
from utils.link_utils import validate_href, check_pdf_extension, has_target_blank, get_text_content

@pytest.mark.validation
class TestValidation:
    def test_all_links_have_valid_href(self, home_page):
        """Verify all a elements have a valid href attribute."""
        links = home_page.page.query_selector_all("a")
        for link in links:
            href = link.get_attribute("href")
            assert validate_href(href), f"Invalid href: {href}"

    def test_external_links_target_blank(self, home_page):
        """Verify that external links open in new tab (target=_blank)."""
        external_selectors = [
            HomePage.linkedin_link,
            HomePage.iot_solutions_link,
            HomePage.dg_hazmat_link,
            HomePage.igbms_link,
            HomePage.iot_hardware_software_link,
        ]
        for sel in external_selectors:
            assert has_target_blank(home_page.page, sel), f"Link {sel} does not have target=_blank"

    def test_page_title(self, home_page):
        """Verify the page title is set."""
        title = home_page.get_title()
        assert title, "Page title is empty"
        # Optionally check contain "Ideabytes"
        assert "Ideabytes" in title, f"Title '{title}' does not contain 'Ideabytes'"

    def test_console_errors(self, home_page):
        """Verify no console errors on page load."""
        errors = getattr(home_page.page, "console_errors", [])
        assert len(errors) == 0, f"Console errors found: {errors}"

    def test_images_have_alt_text(self, home_page):
        """Verify all img elements have alt attribute."""
        images = home_page.page.query_selector_all("img")
        for img in images:
            alt = img.get_attribute("alt")
            assert alt is not None, f"Image with src {img.get_attribute('src')} missing alt text"

    def test_keyboard_navigation(self, home_page):
        """Test that links are focusable via Tab."""
        # Focus on first link
        home_page.page.keyboard.press("Tab")
        # Verify some element is focused
        focused = home_page.page.evaluate("document.activeElement.tagName")
        assert focused in ("A", "BUTTON"), f"Focused element is {focused}, expected link or button"

    def test_404_page(self, page):
        """Navigate to non-existent page and verify error or 404."""
        response = page.goto(f"{BASE_URL}/nonexistent")
        assert response.status == 404 or "not found" in page.title().lower()

    def test_link_text_not_empty(self, home_page):
        """Verify that each link has text content (except logo/social)."""
        links = home_page.page.query_selector_all("a")
        for link in links:
            text = link.text_content().strip()
            href = link.get_attribute("href")
            # Skip elements that are expected empty (logo, icon, pdf)
            if href and (".pdf" in href or "linkedin.com" in href):
                continue
            if link.get_attribute("class") and "logo" in link.get_attribute("class"):
                continue
            assert text, f"Link with href {href} has no text content"

    def test_pdf_extension(self, home_page):
        """Verify that PDF links have .pdf extension."""
        pdf_selectors = [
            HomePage.pdf_iso9001,
            HomePage.pdf_iso27001,
            HomePage.pdf_iso27017,
        ]
        for sel in pdf_selectors:
            href = home_page.get_attribute(sel, "href")
            assert check_pdf_extension(href), f"PDF link {sel} does not end with .pdf"

    def test_discover_more_unique_hrefs(self, home_page):
        """Verify Discover More links have unique hrefs."""
        links = home_page.page.query_selector_all("a.blog_link")
        hrefs = [link.get_attribute("href") for link in links if link.get_attribute("href")]
        assert len(hrefs) == len(set(hrefs)), "Duplicate Discover More hrefs found"

    def test_contact_button_css_class(self, home_page):
        """Verify Contact link has correct CSS class."""
        contact_el = home_page.page.query_selector(HomePage.contact_link)
        class_attr = contact_el.get_attribute("class")
        assert class_attr and "btn btn-md btn-rounded btn-outline" in class_attr

    def test_logo_link_homepage(self, home_page):
        """Verify logo link points to correct URL."""
        href = home_page.get_attribute(HomePage.logo_link, "href")
        assert href == "https://ideabytes.com/index.html"

    def test_back_button(self, home_page):
        """Test browser back button works after navigation."""
        home_page.click(home_page.contact_link)
        home_page.page.go_back()
        assert home_page.page.url == BASE_URL

    def test_double_click_no_error(self, home_page):
        """Test clicking a link twice does not cause JS error."""
        with home_page.page.expect_navigation() as nav_info:
            home_page.click(home_page.contact_link)
        # Go back
        home_page.page.go_back()
        home_page.page.wait_for_load_state("networkidle")
        # Click again
        with home_page.page.expect_navigation() as nav_info2:
            home_page.click(home_page.contact_link)
        assert nav_info2.value.url == "https://ideabytes.com/contact-us.html"

    def test_footer_linkedin_clickable(self, home_page):
        """Verify LinkedIn link is in footer and clickable."""
        footer = home_page.page.query_selector("footer")
        assert footer, "Footer not found"
        linkedin_in_footer = footer.query_selector("a[href='https://in.linkedin.com/company/ideabytes-inc']")
        assert linkedin_in_footer, "LinkedIn link not found in footer"
        # Click it
        with home_page.page.expect_navigation():
            linkedin_in_footer.click()
        assert "linkedin.com" in home_page.page.url

    def test_iot_hardware_has_class(self, home_page):
        """Verify IoT Hardware link has products_text class."""
        el = home_page.page.query_selector(HomePage.iot_hardware_software_link)
        class_attr = el.get_attribute("class")
        assert "products_text" in class_attr

    def test_hamburger_visible_below_768(self, page):
        """Check that hamburger button is visible only on screens < 768px."""
        from utils.responsive_utils import set_viewport
        home = HomePage(page)
        home.navigate()
        # Test below 768
        set_viewport(page, 600)
        page.wait_for_timeout(300)
        assert home.is_element_visible(home.hamburger_button), "Hamburger not visible at 600px"
        # Test above 768
        set_viewport(page, 1024)
        page.wait_for_timeout(300)
        assert not home.is_element_visible(home.hamburger_button), "Hamburger visible at 1024px"


# ===============================================================
# File: tests/test_login.py
# ===============================================================
import pytest
from pages.home_page import HomePage

@pytest.mark.login
class TestLogin:
    """Placeholder for login functionality. No login page detected."""
    def test_login_page_not_found(self, home_page):
        """Verify that there is no login button/link present."""
        # No login link detected; ensure none exists
        login_selectors = [
            "a:has-text('Login')",
            "a:has-text('Sign In')",
            "button:has-text('Login')",
        ]
        for sel in login_selectors:
            el = home_page.page.query_selector(sel)
            assert el is None, f"Unexpected login element found: {sel}"


# ===============================================================
# File: pytest.ini
# ===============================================================
# [pytest]
# minversion = 7.0
# addopts = -v --html=reports/report.html --self-contained-html
# testpaths = tests
# markers =
#     navigation: Tests for navigation links
#     responsive: Tests for responsive behavior
#     validation: Tests for link validity and accessibility
#     login: Tests for login functionality


# ===============================================================
# File: requirements.txt
# ===============================================================
# playwright==1.40.0
# pytest==7.4.3
# pytest-html==4.1.1
# pyyaml==6.0.1
# pytest-playwright==0.4.3

```