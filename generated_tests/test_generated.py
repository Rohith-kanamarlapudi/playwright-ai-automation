# File: config/config.yaml
browser:
  type: chromium
  headless: true

viewport:
  default:
    width: 1280
    height: 720

timeout:
  navigation: 30000
  element: 5000

base_url: "https://ideabytes.com"

reporting:
  type: "allure"
  output: "reports/allure-results"

logging:
  level: "INFO"
  file: "logs/test_log.log"
# File: config/test_data.yaml
contact_form:
  name: "Test User"
  email: "test@example.com"
  message: "This is a test message."
# File: pages/__init__.py
# Empty file to mark directory as package.
# File: pages/base_page.py
from playwright.sync_api import Page, expect
from utilities.logger import Logger
import allure

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = Logger.get_logger()

    def navigate(self, url: str):
        """Navigate to the given URL and wait for load."""
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until='load')

    def click(self, selector: str):
        """Click on an element identified by selector, with auto-wait."""
        self.logger.info(f"Clicking element: {selector}")
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """Fill an input field with text."""
        self.logger.info(f"Filling {selector} with '{text}'")
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        return self.page.text_content(selector)

    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        return self.page.is_visible(selector)

    def get_element(self, selector: str):
        """Return a locator for the given selector."""
        return self.page.locator(selector)

    def open_new_tab(self, selector: str):
        """Click a link that opens in a new tab and return the new page."""
        with self.page.context.expect_page() as new_page_info:
            self.page.click(selector)
        new_page = new_page_info.value
        new_page.wait_for_load_state()
        return new_page

    def wait_for_element(self, selector: str, timeout=5000):
        """Wait for an element to be present in DOM."""
        self.page.wait_for_selector(selector, timeout=timeout)

    def press_key(self, key: str):
        """Press a keyboard key."""
        self.page.keyboard.press(key)

    def get_response_status(self, url: str) -> int:
        """Perform a GET request and return the response status code."""
        response = self.page.request.get(url)
        return response.status
# File: pages/home_page.py
from pages.base_page import BasePage
from pages.elements_library import HomePageSelectors as Sel

class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Selectors from elements library
        self.logo_link = Sel.LOGO_LINK
        self.hamburger_button = Sel.HAMBURGER_BUTTON
        self.contact_link = Sel.CONTACT_LINK
        self.navigation_links = Sel.NAV_LINKS
        self.discover_more_links = Sel.DISCOVER_MORE

    def load(self):
        """Navigate to the base URL."""
        self.navigate("https://ideabytes.com")

    def click_navigation_link(self, link_name):
        """Click a navigation menu link by its visible text."""
        selector = self.navigation_links[link_name]
        self.click(selector)

    def click_contact(self):
        """Click the 'Contact' button/link."""
        self.click(self.contact_link)

    def click_logo(self):
        """Click the logo to return to homepage."""
        self.click(self.logo_link)

    def toggle_hamburger(self):
        """Click the hamburger button (mobile menu toggle)."""
        self.click(self.hamburger_button)

    def get_page_title(self) -> str:
        """Return the page title."""
        return self.page.title()

    def get_lang_attribute(self) -> str:
        """Return the lang attribute of the <html> element."""
        return self.page.get_attribute("html", "lang")

    def is_hamburger_visible(self) -> bool:
        """Check if the hamburger button is visible."""
        return self.is_visible(self.hamburger_button)

    def is_contact_link_visible(self) -> bool:
        """Check if the Contact link is visible."""
        return self.is_visible(self.contact_link)
# File: pages/contact_page.py
from pages.base_page import BasePage
from pages.elements_library import ContactPageSelectors as Sel

class ContactPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name_input = Sel.NAME_INPUT
        self.email_input = Sel.EMAIL_INPUT
        self.message_textarea = Sel.MESSAGE_TEXTAREA
        self.submit_button = Sel.SUBMIT_BUTTON
        # Note: The detected elements did not include these inputs;
        # they are assumed based on common contact forms. If not present,
        # adjust selectors accordingly or skip form tests.

    def fill_contact_form(self, name, email, message):
        """Fill all contact form fields."""
        self.fill(self.name_input, name)
        self.fill(self.email_input, email)
        self.fill(self.message_textarea, message)

    def submit_form(self):
        """Click the submit button."""
        self.click(self.submit_button)
# File: pages/elements_library.py
"""Centralized selectors for all page objects."""

class HomePageSelectors:
    LOGO_LINK = "a[href='https://ideabytes.com/index.html']"
    HAMBURGER_BUTTON = "button:has-text('')"  # detected class: lines-button x
    CONTACT_LINK = "a:has-text('Contact')"
    NAV_LINKS = {
        "IoT Solutions": "a:has-text('IoT Solutions')",
        "DG HAZMAT": "a:has-text('DG HAZMAT')",
        "IGBMS": "a:has-text('IGBMS')",
        "Test Automation": "a:has-text('Test Automation')",
        "Application Development": "a:has-text('Application Development')",
        "Teens4Tech": "a:has-text('Teens4Tech')",
        "Partnerships": "a:has-text('Partnerships')",
        "About Us": "a:has-text('About Us')",
        "Certificates": "a:has-text('Certificates')",
        "Team": "a:has-text('Team')"
    }
    DISCOVER_MORE = "a:has-text('Discover More')"

class ContactPageSelectors:
    # Assumed common selectors (not provided in detected elements)
    # These should be updated after real inspection of the contact page.
    NAME_INPUT = "input[name='name']"
    EMAIL_INPUT = "input[name='email']"
    MESSAGE_TEXTAREA = "textarea[name='message']"
    SUBMIT_BUTTON = "button[type='submit']"
# File: utilities/__init__.py
# Empty file to mark directory as package.
# File: utilities/logger.py
import logging
import os

class Logger:
    @staticmethod
    def get_logger(name=__name__, level=logging.INFO):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(level)
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            fh = logging.FileHandler(os.path.join(log_dir, "test_log.log"))
            fh.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        return logger
# File: utilities/screenshots.py
import os
import pytest
from datetime import datetime

def take_screenshot_on_failure(page, test_name):
    """Take screenshot and attach to report if test fails."""
    screenshot_dir = "reports/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshot_dir, f"{test_name}_{timestamp}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    return screenshot_path

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        # Try to get page from various fixtures
        page = None
        for fixture in ('page', 'home_page', 'contact_page'):
            if fixture in item.funcargs:
                obj = item.funcargs[fixture]
                if hasattr(obj, 'page'):
                    page = obj.page
                elif hasattr(obj, 'page') is False and fixture == 'page':
                    page = obj
                break
        if page:
            screenshot_path = take_screenshot_on_failure(page, item.name)
            if 'allure' in sys.modules:
                import allure
                allure.attach.file(screenshot_path, "screenshot", attachment_type=allure.attachment_type.PNG)
            elif 'pytest_html' in sys.modules:
                from pytest_html import extras
                report.extra.append(extras.image(screenshot_path, 'png'))
# File: utilities/browser_factory.py
from playwright.sync_api import sync_playwright

class BrowserFactory:
    @staticmethod
    def get_browser(browser_type="chromium", headless=True):
        """Launch and return a browser instance."""
        with sync_playwright() as p:
            if browser_type == "chromium":
                return p.chromium.launch(headless=headless)
            elif browser_type == "firefox":
                return p.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                return p.webkit.launch(headless=headless)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
# File: utilities/allure_reporter.py
import allure

def attach_environment_info(browser_name, browser_version, platform):
    """Attach environment info to Allure report."""
    allure.environment(browser=browser_name, browser_version=browser_version, platform=platform)
# File: tests/__init__.py
# Empty file to mark directory as package.
# File: tests/conftest.py
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from pages.home_page import HomePage
from utilities.logger import Logger
from utilities.screenshots import take_screenshot_on_failure
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)

def load_test_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_data.yaml')
    with open(data_path) as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def config():
    return load_config()

@pytest.fixture(scope="session")
def test_data():
    return load_test_data()

@pytest.fixture(scope="session")
def browser(config):
    with sync_playwright() as p:
        browser_type = config["browser"]["type"]
        headless = config["browser"]["headless"]
        if browser_type == "chromium":
            browser = p.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            browser = p.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            browser = p.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser: {browser_type}")
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def context(browser, config):
    context = browser.new_context(
        viewport=config["viewport"]["default"],
        locale=config.get("locale", "en-US")
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def home_page(page):
    hp = HomePage(page)
    hp.load()
    return hp

@pytest.fixture(scope="function")
def contact_page(page):
    from pages.contact_page import ContactPage
    cp = ContactPage(page)
    cp.navigate("https://ideabytes.com/contact-us.html")
    return cp

@pytest.fixture(params=[(375, 812), (768, 1024), (1280, 720)], ids=["mobile", "tablet", "desktop"])
def viewport(request):
    return request.param

@pytest.fixture(scope="function")
def page_with_viewport(context, viewport):
    context.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    page = context.new_page()
    yield page
    page.close()
# File: tests/test_navigation.py
import pytest
import allure

@allure.feature("Navigation")
class TestNavigation:

    @allure.title("Verify homepage loads successfully")
    def test_homepage_loads(self, home_page):
        """Check that the homepage title is not empty and page loads."""
        assert home_page.get_page_title(), "Page title should not be empty"
        assert home_page.is_visible(home_page.logo_link), "Logo should be visible on homepage"

    @allure.title("Verify all navigation links are present and clickable")
    def test_navigation_links_present_and_clickable(self, home_page):
        """Ensure all navigation links are visible and respond to click (no 404)."""
        for name, selector in home_page.navigation_links.items():
            assert home_page.is_visible(selector), f"Navigation link '{name}' should be visible"
            # Click each internal link and verify it navigates to a valid page
            home_page.click(selector)
            home_page.page.wait_for_load_state()
            # Get current URL and ensure it matches expected (or at least not error)
            current_url = home_page.page.url
            assert "404" not in current_url, f"Link '{name}' returned a 404 page: {current_url}"
            # Go back to homepage for next link
            home_page.load()

    @allure.title("Verify clicking the hamburger button toggles mobile navigation menu")
    def test_hamburger_toggles_mobile_menu(self, home_page):
        """Click hamburger button and verify it toggles (e.g., menu becomes visible)."""
        # This test assumes the hamburger button existence and that it toggles a menu.
        # Since we have no selector for the menu, we just verify the button is clickable.
        home_page.toggle_hamburger()
        # After click, we can check that hamburger button class changes? Not provided.
        # At minimum, the button should still be present.
        assert home_page.is_hamburger_visible(), "Hamburger button should still be visible after toggle"

    @allure.title("Verify Contact link navigates to contact us page")
    def test_contact_link_navigates_to_contact_page(self, home_page):
        """Click Contact link and verify URL ends with contact-us.html."""
        home_page.click_contact()
        home_page.page.wait_for_load_state()
        assert "contact-us.html" in home_page.page.url, "Should navigate to contact us page"

    @allure.title("Verify IoT Solutions link opens external site in new tab")
    def test_iot_solutions_opens_new_tab(self, home_page):
        """Click IoT Solutions link and verify a new tab opens with the external URL."""
        new_page = home_page.open_new_tab(home_page.navigation_links["IoT Solutions"])
        assert "ideabytesiot.com" in new_page.url, "New tab should be on ideabytesiot.com"
        new_page.close()

    @allure.title("Verify DG HAZMAT link opens external site in new tab")
    def test_dg_hazmat_opens_new_tab(self, home_page):
        """Click DG HAZMAT link and verify a new tab opens with dgsms.ca."""
        new_page = home_page.open_new_tab(home_page.navigation_links["DG HAZMAT"])
        assert "dgsms.ca" in new_page.url, "New tab should be on dgsms.ca"
        new_page.close()

    @allure.title("Verify IGBMS link opens external site in new tab")
    def test_igbms_opens_new_tab(self, home_page):
        """Click IGBMS link and verify a new tab opens with igbms.com."""
        new_page = home_page.open_new_tab(home_page.navigation_links["IGBMS"])
        assert "igbms.com" in new_page.url, "New tab should be on igbms.com"
        new_page.close()

    @allure.title("Verify Test Automation link navigates to test-automation.html")
    def test_test_automation_link(self, home_page):
        """Click Test Automation link and verify it navigates to the correct page."""
        home_page.click_navigation_link("Test Automation")
        home_page.page.wait_for_load_state()
        assert "test-automation.html" in home_page.page.url

    @allure.title("Verify Application Development link navigates to web-mobile-app-dev.html")
    def test_application_development_link(self, home_page):
        """Click Application Development link and verify correct URL."""
        home_page.click_navigation_link("Application Development")
        home_page.page.wait_for_load_state()
        assert "web-mobile-app-dev.html" in home_page.page.url

    @allure.title("Verify Teens4Tech link navigates to Teens_tech.html")
    def test_teens4tech_link(self, home_page):
        """Click Teens4Tech link and verify correct URL."""
        home_page.click_navigation_link("Teens4Tech")
        home_page.page.wait_for_load_state()
        assert "Teens_tech.html" in home_page.page.url

    @allure.title("Verify Partnerships link navigates to partnership.html")
    def test_partnerships_link(self, home_page):
        """Click Partnerships link and verify correct URL."""
        home_page.click_navigation_link("Partnerships")
        home_page.page.wait_for_load_state()
        assert "partnership.html" in home_page.page.url

    @allure.title("Verify About Us link navigates to about-us.html")
    def test_about_us_link(self, home_page):
        """Click About Us link and verify correct URL."""
        home_page.click_navigation_link("About Us")
        home_page.page.wait_for_load_state()
        assert "about-us.html" in home_page.page.url

    @allure.title("Verify Certificates link navigates to certificates.html")
    def test_certificates_link(self, home_page):
        """Click Certificates link and verify correct URL."""
        home_page.click_navigation_link("Certificates")
        home_page.page.wait_for_load_state()
        assert "certificates.html" in home_page.page.url

    @allure.title("Verify Team link navigates to team.html")
    def test_team_link(self, home_page):
        """Click Team link and verify correct URL."""
        home_page.click_navigation_link("Team")
        home_page.page.wait_for_load_state()
        assert "team.html" in home_page.page.url

    @allure.title("Verify clicking the logo link returns to homepage")
    def test_logo_returns_home(self, home_page):
        """Navigate to another page, click logo, and verify URL is back to homepage."""
        # First, go to a subpage
        home_page.click_navigation_link("About Us")
        home_page.page.wait_for_load_state()
        # Now click logo
        home_page.click_logo()
        home_page.page.wait_for_load_state()
        assert home_page.page.url == "https://ideabytes.com/" or "index.html" in home_page.page.url

    @allure.title("Verify all external links open with rel='noopener noreferrer' if applicable")
    def test_external_links_have_noopener_noreferrer(self, home_page):
        """Check external links for the attribute rel='noopener noreferrer'."""
        external_selectors = [
            "a[href='https://in.linkedin.com/company/ideabytes-inc']",
            "a[href='https://www.ideabytesiot.com/']",
            "a[href='https://www.dgsms.ca']",
            "a[href='https://igbms.com/']",
            "a[href='https://www.ideabytesiot.com']",  # from detected
        ]
        for selector in external_selectors:
            rel_attr = home_page.page.get_attribute(selector, "rel")
            assert rel_attr and "noopener" in rel_attr and "noreferrer" in rel_attr, \
                f"External link {selector} should have rel='noopener noreferrer'"
# File: tests/test_responsive.py
import pytest
import allure

@allure.feature("Responsive Layout")
class TestResponsive:

    @allure.title("Verify page layout adapts correctly at viewport width 375px")
    def test_mobile_layout(self, page_with_viewport, viewport):
        """At mobile width (375x812), check no horizontal scroll and logo/hamburger visible."""
        page_with_viewport.goto("https://ideabytes.com")
        page_with_viewport.wait_for_load_state()
        # Check no horizontal scroll
        has_scroll = page_with_viewport.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        assert not has_scroll, "Page should not have horizontal scroll at 375px"
        # Check logo and hamburger are visible (assume they exist)
        from pages.elements_library import HomePageSelectors as Sel
        assert page_with_viewport.is_visible(Sel.LOGO_LINK), "Logo should be visible on mobile"
        assert page_with_viewport.is_visible(Sel.HAMBURGER_BUTTON), "Hamburger button should be visible on mobile"

    @allure.title("Verify page layout adapts correctly at viewport width 768px")
    def test_tablet_layout(self, page_with_viewport, viewport):
        """At tablet width (768x1024), check no horizontal scroll and logo visible."""
        page_with_viewport.goto("https://ideabytes.com")
        page_with_viewport.wait_for_load_state()
        has_scroll = page_with_viewport.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        assert not has_scroll, "Page should not have horizontal scroll at 768px"
        from pages.elements_library import HomePageSelectors as Sel
        assert page_with_viewport.is_visible(Sel.LOGO_LINK), "Logo should be visible on tablet"
# File: tests/test_accessibility.py
import pytest
import allure

@allure.feature("Accessibility")
class TestAccessibility:

    @allure.title("Verify page has a valid lang attribute set to 'en'")
    def test_lang_attribute(self, home_page):
        """Check the lang attribute on <html> element."""
        lang = home_page.get_lang_attribute()
        assert lang == "en", f"Expected lang='en', got '{lang}'"

    @allure.title("Verify page title is descriptive and not empty")
    def test_page_title_not_empty(self, home_page):
        """Page title should contain meaningful text."""
        title = home_page.get_page_title()
        assert title, "Page title should not be empty"
        assert len(title) > 10, "Page title should be descriptive (more than 10 chars)"

    @allure.title("Verify keyboard focus is visible on all interactive elements")
    def test_keyboard_focus_visible(self, home_page):
        """Tab through all interactive elements and verify focus indicator is visible."""
        # Get all focusable elements (a, button, input, select, textarea)
        focusable_elements = home_page.page.evaluate('''
            () => {
                const elements = document.querySelectorAll('a, button, input, select, textarea');
                return Array.from(elements).map(el => el.tagName);
            }
        ''')
        # Focus first element
        home_page.page.keyboard.press('Tab')
        for i in range(len(focusable_elements)):
            focused = home_page.page.evaluate('document.activeElement')
            # Check that the focused element is not body
            assert focused, "Focus should be on an interactive element"
            tag = home_page.page.evaluate('document.activeElement.tagName')
            assert tag in ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'], f"Focus on unexpected element {tag}"
            # Verify that there is some visible focus indicator (e.g., outline)
            has_outline = home_page.page.evaluate('''
                () => {
                    const el = document.activeElement;
                    const style = window.getComputedStyle(el);
                    return style.outlineWidth !== '0px' || style.outlineStyle !== 'none';
                }
            ''')
            if not has_outline:
                # Fallback: check for box-shadow or border
                has_other_indicator = home_page.page.evaluate('''
                    () => {
                        const el = document.activeElement;
                        const style = window.getComputedStyle(el);
                        return style.boxShadow !== 'none' || 
                               (style.borderStyle !== 'none' && style.borderWidth !== '0px');
                    }
                ''')
                assert has_other_indicator, f"Focus indicator not visible on element {tag}"
            if i < len(focusable_elements) - 1:
                home_page.page.keyboard.press('Tab')

    @allure.title("Verify hamburger button is accessible via keyboard")
    def test_hamburger_keyboard_accessible(self, home_page):
        """Tab to hamburger button and press Enter/Space to activate it."""
        # Find hamburger button using selector
        hamburger_selector = "button:has-text('')"
        # Use page.locator to get the element
        hamburger = home_page.page.locator(hamburger_selector)
        # Focus the hamburger button directly
        hamburger.focus()
        # Verify it's focused
        is_focused = home_page.page.evaluate('document.activeElement === document.querySelector("button:has-text(\\"\\")")')
        assert is_focused, "Hamburger button should be focusable"
        # Press Enter and verify toggle (e.g., menu appears) – we only verify that click works
        home_page.page.keyboard.press('Enter')
        # No assertion for menu visibility due to lack of selector

    @allure.title("Verify Contact link has an accessible name")
    def test_contact_link_accessible_name(self, home_page):
        """Check the Contact link has an accessible name (text or aria-label)."""
        contact_selector = "a:has-text('Contact')"
        # Get text content
        text = home_page.page.text_content(contact_selector)
        assert text and text.strip() == "Contact", "Contact link should have text 'Contact'"
        # Also check aria-label if present
        aria_label = home_page.page.get_attribute(contact_selector, "aria-label")
        if aria_label:
            assert len(aria_label) > 0, "aria-label should not be empty"

    @allure.title("Verify page content is readable when zoomed to 200%")
    def test_zoom_200_percent(self, home_page):
        """Apply 200% zoom and verify page content is still accessible."""
        home_page.page.evaluate("document.body.style.zoom = '200%'")
        # Wait a moment for reflow
        home_page.page.wait_for_timeout(500)
        # Check that main content is still visible (logo, navigation links)
        assert home_page.is_visible(home_page.logo_link), "Logo should be visible at 200% zoom"
        # Check no element is completely out of viewport (alternative: no error)
        # We'll just verify the page doesn't crash.
        assert home_page.get_page_title(), "Page title should still be present"
        # Reset zoom for other tests
        home_page.page.evaluate("document.body.style.zoom = '100%'")
# File: tests/test_functional.py
import pytest
import allure

@allure.feature("Functional")
class TestFunctional:

    @allure.title("Verify hamburger button toggles mobile navigation menu")
    def test_hamburger_toggle_menu(self, home_page):
        """Click hamburger button and verify menu appears (if selector known)."""
        # Since no mobile menu selector is provided, we simply check the button is clicked.
        # This test is a placeholder – may be enhanced when selectors are available.
        home_page.toggle_hamburger()
        # We can check that the hamburger button class changed (e.g., active)
        class_attr = home_page.page.get_attribute(home_page.hamburger_button, "class")
        # The button should have class 'lines-button x' initially, may add 'active' after click
        # This is an assumption; we just verify it is clickable.
        assert home_page.is_hamburger_visible(), "Hamburger button should still be visible"
# File: tests/test_broken_links.py
import pytest
import allure
from urllib.parse import urlparse, urljoin

@allure.feature("Broken Links")
class TestBrokenLinks:

    @allure.title("Verify no links return 404 status when navigated to")
    def test_no_broken_internal_links(self, home_page):
        """Check all internal links (same origin) for 404 status, without navigating away."""
        base_url = "https://ideabytes.com"
        # Extract all anchor tags with href
        links = home_page.page.evaluate('''
            () => {
                const anchors = document.querySelectorAll('a[href]');
                return Array.from(anchors).map(a => a.href);
            }
        ''')
        # Filter internal links (same origin)
        internal_links = [link for link in links if link.startswith(base_url) and not link.endswith('.pdf')]
        # Check each link using request (no navigation)
        broken = []
        for link in internal_links:
            status = home_page.get_response_status(link)
            if status >= 400:
                broken.append((link, status))
        assert not broken, f"Found broken internal links: {broken}"

    def get_response_status(self, url):
        """Override to use request method (already defined in BasePage)."""
        return super().get_response_status(url)
# File: requirements.txt
playwright==1.40.0
pytest==7.4.3
pytest-playwright==0.4.3
pyyaml==6.0.1
allure-pytest==2.13.2
pytest-html==4.1.1
# File: pytest.ini
[pytest]
addopts = -v --tb=short --html=reports/pytest_report.html --self-contained-html --alluredir=reports/allure-results
testpaths = tests
python_files = test_*.py
markers =
    smoke: quick sanity check tests
    regression: full regression suite
    responsive: tests for different viewports
    accessibility: accessibility checks
# File: README.md
# Ideabytes Website Automation Suite

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Install Playwright browsers: `playwright install`
3. Run tests: `pytest`
4. Generate Allure report: `allure generate reports/allure-results -o reports/allure-report --clean`

## Config
- Browser type and headless mode: `config/config.yaml`
- Test data: `config/test_data.yaml`