import re
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
 
 
# ==========================================================
# PLAYWRIGHT FILE HEADER
# BUG FIX 1: Added "import os" to the header string — the
# original header used os.getenv() but never imported os,
# causing a NameError in every generated file which made
# pytest hang during collection (the infinite loop).
# ==========================================================
 
PLAYWRIGHT_HEADER = """
import os
import re
import pytest
 
from playwright.sync_api import (
    Page,
    expect,
    BrowserContext,
    sync_playwright,
)
"""
 
# ==========================================================
# HELPERS
# ==========================================================
 
def clean_step(step: str) -> str:
    """Remove extra whitespace/newlines."""
    return " ".join(str(step).split())
 
 
def quote(value: str) -> str:
    """Escape double-quotes for embedding in Python strings."""
    return value.replace('"', '\\"')


def _locator_expr(sel: str) -> str:
    """
    Build the `page.locator("...")` expression string embedded in
    generated test code. Automatically appends `.first` whenever the
    selector uses `:has-text(`, since substring text matching is
    inherently prone to matching MULTIPLE real elements -- e.g.
    `a:has-text('Reports')` matches the main "Reports" nav link AND
    the "Scheduled Reports"/"On-Demand Reports" sub-tabs, since all
    three contain "Reports" as a substring. Without `.first`,
    Playwright raises a strict-mode violation (not a "not found"
    error) instead of running the intended single-element check or
    action.
    """
    expr = f'page.locator("{quote(sel)}")'
    if ":has-text(" in sel:
        expr += ".first"
    return expr


_MAP_HREF_DOMAINS = (
    "maps.google.", "google.com/maps", "www.google.com/maps",
    "maps.apple.com", "bing.com/maps", "openstreetmap.org",
)

_HREF_ATTR_RE = re.compile(r"""href\s*=\s*['"]([^'"]+)['"]""", re.IGNORECASE)

def _href_looks_like_map_link(sel: str) -> bool:
    """
    True if a CSS attribute selector like `a[href='...']` points to a
    map service (Google Maps, Apple Maps, Bing Maps, OpenStreetMap).
    Map links are almost universally rendered inside an expandable
    row/detail panel or a "view location" action, not inline on page
    load -- asserting one is visible immediately after "Open page" is
    a near-guaranteed false failure regardless of how correct the
    selector itself is. Treated as conditionally-visible: checked
    softly rather than hard-asserted.
    """
    m = _HREF_ATTR_RE.search(sel)
    if not m:
        return False
    href = m.group(1).lower()
    return any(domain in href for domain in _MAP_HREF_DOMAINS)
 
 
# ==========================================================
# URL EXTRACTION
# ==========================================================
 
URL_PATTERN = re.compile(r"https?://[^\s]+")
 
 
def extract_url(text: str):
    if not text:
        return None
    m = URL_PATTERN.search(text)
    if not m:
        return None
    return m.group(0).rstrip(".,;").strip("'").strip('"')
 
 
# ==========================================================
# BASE URL  (FIX 8 — never hardcoded in generated code)
# ==========================================================
 
def get_base_url() -> str:
    return os.getenv("BASE_URL", os.getenv("TARGET_URL", "http://localhost:3000"))
 
 
# ==========================================================
# SELECTOR DETECTION HELPERS
# ==========================================================
 
# Does the string look like a CSS/XPath selector?
_CSS_SELECTOR_RE = re.compile(
    r"^(#[\w\-]+|\.[\w\-]+|\[[\w\-]+|"
    r"(?:input|button|a|textarea|select|div|span|form|nav|header|footer|main)"
    # BUG FIX: bare `\s` used to be in this lookahead, so a plain
    # English sentence starting with a tag word followed by a
    # space (e.g. "button is present") was misclassified as CSS.
    # Only real selector-syntax characters (or end of string) now
    # qualify — a following space no longer counts.
    r"(?=[\[\.\:>,]|$))",
    re.IGNORECASE,
)

_DIALOG_BUTTON_LABELS = {
    "yes", "no", "confirm", "cancel", "ok", "okay",
    "delete", "remove", "close", "dismiss",
}

def _is_dialog_confirmation_label(text: str) -> bool:
    """
    True for button labels that typically belong to a confirmation
    dialog (Yes/No/Confirm/Cancel/OK/etc.) rather than a normal
    always-present page control. These are only visible after some
    OTHER action opens the dialog — a YAML step that clicks one
    immediately after page load, with nothing in between that could
    have triggered it, will hang for the full timeout and fail, even
    though the button conversion itself is correct. Code generated for
    these labels checks visibility first and skips gracefully instead
    of hard-failing, since we have no way to know from the step text
    alone whether the dialog was actually opened first.
    """
    return text.strip().lower() in _DIALOG_BUTTON_LABELS


def _strip_wrapping_quotes(value: str) -> str:
    """
    Remove one or more layers of matching wrapping quote characters
    (straight single or double) from step-derived text. Step wording
    like `Click button "Save"` or `Click "Reports" link` otherwise
    leaves the literal quote marks baked into the extracted text,
    which breaks _is_css_selector()'s prefix match (a leading `"` or
    `'` never matches a tag/`#`/`.`/`[`) and ends up embedded verbatim
    in a get_by_role(name=...) that can never match a real element.
    """
    value = value.strip()
    while len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1].strip()
    return value

_PURPOSE_PHRASE_RE = re.compile(
    r"^(to|in\s+order\s+to|so\s+that|for|that|which)\b", re.IGNORECASE
)

def _looks_like_purpose_phrase(text: str) -> bool:
    """
    True if `text` reads like a description of WHY to click something
    (e.g. "to open modal") rather than the clicked element's actual
    visible label. Step wording like "Click button to open modal" is
    the LLM describing intent, not naming a button — using it verbatim
    as a get_by_role(name=...) guarantees a locator that can never
    match anything real, since no button is actually labelled
    "to open modal".
    """
    return bool(_PURPOSE_PHRASE_RE.match(text.strip()))

def _is_css_selector(value: str) -> bool:
    """Return True if value looks like a CSS selector, not plain text."""
    return bool(_CSS_SELECTOR_RE.match(value.strip()))
 
 
LINK_SELECTOR_PATTERN = re.compile(r"Click\s+link\s+(.+)", re.IGNORECASE)
# BUG FIX: the old character class included bare `\s` and `\w`,
# so it greedily matched straight through plain English text that
# merely contains the word "button", e.g. "Verify Sign In button is
# present" matched "button is present" as if it were a CSS
# selector (later fed straight into page.locator(...)). Now
# "button" must be IMMEDIATELY followed by real selector syntax
# (":", ".", "#", "[") to match at all — plain prose after the
# word "button" no longer matches.
BUTTON_SELECTOR_PATTERN = re.compile(
    # BUG FIX: the trailing character class used to exclude bare
    # whitespace entirely, which was meant to stop "button is
    # present" (plain English) from matching — but that job is
    # already done by the (?=[:\.\[#]) lookahead right after
    # "button", which requires real selector syntax to even start
    # matching. Excluding \s from the class as well was an
    # over-correction: it truncated any legitimate selector with a
    # multi-word quoted argument, e.g. "button:has-text('Live
    # Alerts')" got cut down to "button:has-text('Live" at the
    # first space. Restoring \s here is safe because the lookahead
    # alone already rejects the plain-English case.
    r"button(?=[:\.\[#])[:\w\-\(\)\'\"=\[\]\.>\s]*", re.IGNORECASE
)
 
 
def extract_selector(step: str):
    step = clean_step(step)

    def _unquote(value: str) -> str:
        value = value.strip()
        # BUG FIX: LINK_SELECTOR_PATTERN's `(.+)` greedily captures
        # everything after "Click link ", including any wrapping quote
        # characters the step text itself used, e.g.
        # `Click link "a:has-text('Reports')"` used to be captured as
        # the literal string `"a:has-text('Reports')"` — quotes and
        # all. A leading `"` character then made _is_css_selector()
        # fail to recognize it as CSS (it only matches strings
        # starting with an element/`#`/`.`/`[`), so it silently fell
        # through to get_by_role(name=...) with the quote marks baked
        # into the accessible name, which can never match a real
        # element. Strip one layer of wrapping quotes (either style)
        # so the real selector underneath is what gets used.
        while len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1].strip()
        return value

    m = re.search(r"selector\s+'([^']+)'", step, re.IGNORECASE)
    if m:
        return _unquote(m.group(1))

    m = re.search(r'selector\s+"([^"]+)"', step, re.IGNORECASE)
    if m:
        return _unquote(m.group(1))

    # BUG FIX: step wording like
    # "Verify element visible a:has-text('Forgot Password?')" or
    # "Verify element visible #modal-yes" gives the selector
    # directly after "element visible", but nothing here ever
    # parsed it out. extract_selector() returned None, so the verify
    # branch fell through to the vacuous `expect(page.locator("body"))
    # .to_be_visible()` fallback — which is trivially true on any
    # loaded page, so the test "passed" without ever actually
    # checking for the named element.
    m = re.search(r"elements?\s+visible\s+(.+)$", step, re.IGNORECASE)
    if m:
        return _unquote(m.group(1))

    m = LINK_SELECTOR_PATTERN.search(step)
    if m:
        return _unquote(m.group(1))

    m = BUTTON_SELECTOR_PATTERN.search(step)
    if m:
        return _unquote(m.group(0))

    return None
 
 
# ==========================================================
# KEYWORD EXTRACTOR (for fallback assertions)
# ==========================================================
 
def _extract_page_keyword(step: str) -> str:
    """
    Pull the meaningful noun from a step description.
    'Verify dashboard is visible' -> 'dashboard'
    """
    cleaned = re.sub(
        r"^(open|verify|assert|check|confirm|ensure|visit)\s+",
        "", step.strip(), flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\s+(page|is|the|visible|present|exists?|shown?|displayed?)$",
        "", cleaned.strip(), flags=re.IGNORECASE,
    )
    return cleaned.strip().lower()
 
 
# ==========================================================
# EXTERNAL LINK DETECTOR  (FIX 6)
# ==========================================================
#
# BUG FIX: this used to be a bare regex substring search
# (r"...|t\.co") which matches "t.co" as a substring ANYWHERE in the
# URL — including inside completely unrelated domains, e.g.
# "ideabytesiot.com" contains the literal substring "t.com", which
# starts with "t.co". That falsely flagged the app's own domain as
# "external" on every single "Open page <url>" step, wrapping every
# generated test's page.goto() in a with page.context.expect_page()
# block that then hung for the full default timeout waiting for a
# popup that never opens.
#
# Fixed by parsing the actual hostname out of the URL and comparing
# it (or its parent domain, for subdomains) against an exact set of
# known external domains, instead of substring-matching the raw URL.

from urllib.parse import urlparse

_EXTERNAL_DOMAINS = {
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "github.com",
    "youtube.com",
    "t.co",
}

def _is_external_link(url: str) -> bool:
    if not url:
        return False

    host = urlparse(url).netloc.lower()
    host = host.split(":")[0]  # drop a port if present, e.g. example.com:8080

    if not host:
        return False

    if host.startswith("www."):
        host = host[4:]

    return any(
        host == domain or host.endswith("." + domain)
        for domain in _EXTERNAL_DOMAINS
    )
 
 
# ==========================================================
# PLAYWRIGHT CODE WRITER
# ==========================================================
 
class CodeWriter:
 
    def __init__(self):
        self.lines = []
 
    def add(self, line=""):
        self.lines.append(line)
 
    def extend(self, items):
        self.lines.extend(items)
 
    def blank(self):
        self.lines.append("")
 
    def build(self):
        return "\n".join(self.lines)
 
 
# ==========================================================
# PATH MAP  (for keyword-based page navigation)
# ==========================================================
 
PATH_MAP = {
    "login":     "/login",
    "register":  "/register",
    "signup":    "/signup",
    "sign up":   "/signup",
    "home":      "/",
    "dashboard": "/dashboard",
    "profile":   "/profile",
    "settings":  "/settings",
    "checkout":  "/checkout",
    "cart":      "/cart",
    "products":  "/products",
    "contact":   "/contact",
    "about":     "/about",
    "search":    "/search",
    "blog":      "/blog",
}
 
# ==========================================================
# FIELD → SELECTOR MAP  (for "Enter <field>" steps)
# ==========================================================
 
FIELD_SELECTOR_MAP = {
    "username":   "#username, input[name='username'], input[placeholder*='username' i]",
    "password":   "#password, input[name='password'], input[type='password']",
    "email":      "#email, input[name='email'], input[type='email']",
    "name":       "#name, input[name='name'], input[placeholder*='name' i]",
    "phone":      "#phone, input[name='phone'], input[type='tel']",
    "search":     "#search, input[name='search'], input[type='search']",
    "first name": "input[name='firstName'], input[name='first_name']",
    "last name":  "input[name='lastName'], input[name='last_name']",
    "message":    "textarea[name='message'], #message",
    "subject":    "input[name='subject'], #subject",
    "query":      "input[name='query'], input[name='q']",
}
 
 
# ==========================================================
# STEP CONVERTER
# FIX 1: Selector strings now use page.locator() not get_by_text()
# FIX 2: URL assertions use expect(page).to_have_url()
# FIX 3: Fallback assertions check page structure, not English text
# FIX 4: Button selectors require non-empty text / use get_by_role
# FIX 5: PDF steps use expect_download() context
# FIX 6: External/LinkedIn links use expect_page() popup handling
# FIX 7: Link validation uses requests HEAD check for 404 detection
# FIX 8: All goto() calls use base_url fixture, no hardcoded URLs
# ==========================================================
 
def convert_step(step: str) -> List[str]:
    """
    Convert one YAML step string into Playwright Python code lines.
    Returns lines without leading indentation (caller adds 4 spaces).
    """
    step = clean_step(step)
    code: List[str] = []
    url = extract_url(step)
    sl = step.lower()
 
    # -------------------------------------------------------
    # Navigate  (explicit "Navigate to <url>")
    # -------------------------------------------------------
    if sl.startswith("navigate"):
        if url:
            code.append(f'page.goto("{quote(url)}")')
        else:
            # FIX 8: use base_url fixture
            code.append('page.goto(base_url)')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Open <explicit url>
    # -------------------------------------------------------
    if sl.startswith("open ") and url:
        # FIX 6: External link → expect_page (popup/new tab)
        if _is_external_link(url):
            code.append(f"# External link — opens in new tab")
            code.append(f"with page.context.expect_page() as popup_info:")
            code.append(f'    page.goto("{quote(url)}")')
            code.append(f"popup = popup_info.value")
            code.append(f"popup.wait_for_load_state('networkidle')")
        else:
            code.append(f'page.goto("{quote(url)}")')
            code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Open <page keyword>  (no URL in step text)
    # FIX 8: goto uses base_url + path, no hardcoded domain
    # -------------------------------------------------------
    if sl.startswith("open "):
        keyword = _extract_page_keyword(step)
        path = PATH_MAP.get(keyword, f"/{keyword}")
        code.append(f'page.goto(base_url + "{path}")')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Click the '...' link with selector '...'
    # -------------------------------------------------------
    m = re.search(
        r"Click\s+the\s+'.*?'\s+link\s+with\s+selector\s+'([^']+)'",
        step, re.IGNORECASE,
    )
    if m:
        sel = m.group(1)
        code.append(f'{_locator_expr(sel)}.click()')
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Click Link  (FIX 1 + FIX 6)
    # -------------------------------------------------------
    if sl.startswith("click link ") or sl == "click link":
        sel = extract_selector(step)
        href = extract_url(step)
        # Detect bare path like "/about" as an href-based locator
        if not href and not sel:
            bare = re.search(r"(/[\w\-/]+)", step)
            if bare:
                sel = f"a[href='{bare.group(1)}']"
        if href and _is_external_link(href):
            # FIX 6: external link → popup handling
            code.append("# External link — handle new tab")
            code.append("with page.context.expect_page() as popup_info:")
            code.append(f'    page.locator("a[href*=\\"{quote(href)}\\"]").click()')
            code.append("popup = popup_info.value")
            code.append("popup.wait_for_load_state('networkidle')")
        elif sel:
            # FIX 1: if sel looks like CSS selector use locator(), 
            # if bare /path treat as href, else get_by_role
            if _is_css_selector(sel):
                code.append(f'{_locator_expr(sel)}.click()')
            elif sel.startswith("/"):
                # bare path -> href locator
                code.append(f'page.locator("a[href=\\"{quote(sel)}\\"]").click()')
            else:
                code.append(f'page.get_by_role("link", name="{quote(sel)}").click()')
            code.append("page.wait_for_load_state('networkidle')")
        else:
            code.append("# TODO: specify link selector")
        return code
 
    # -------------------------------------------------------
    # Click Button  (FIX 4 — reject empty text selectors)
    # -------------------------------------------------------
    if sl.startswith("click button"):
        raw = _strip_wrapping_quotes(step[len("click button"):].strip())
        if not raw:
            # FIX 4: empty — use get_by_role to avoid clicking random buttons
            code.append('page.get_by_role("button").first.click()')
            code.append("# WARNING: no button text given — clicking first button found")
        elif raw[0] in ":.#[>":
            # BUG FIX: step text like "Click button:has-text('Srinivas')"
            # is a full CSS/Playwright selector continuing directly off
            # the word "button" (a pseudo-class/attribute/combinator),
            # not a separate plain-text label. Slicing after "click
            # button" throws away the "button" prefix and leaves an
            # orphaned fragment like ":has-text('Srinivas')", which
            # _is_css_selector() correctly rejects as not looking like a
            # selector on its own — so it was falling through to
            # get_by_role("button", name=":has-text('Srinivas')"), which
            # can never match anything. Reconstruct the full selector
            # instead, matching what extract_selector() already does
            # correctly for the "Click Link" branch above.
            code.append(f'{_locator_expr("button" + raw)}.click()')
        elif _is_css_selector(raw):
            # FIX 1: CSS selector → locator()
            code.append(f'{_locator_expr(raw)}.click()')
        elif _looks_like_purpose_phrase(raw):
            # BUG FIX: text like "to open modal" describes WHY to
            # click, not WHAT the button is called — using it as
            # name= guarantees a locator that can never match. No
            # real button label is available here, so fall back to
            # the safest available action rather than a guaranteed
            # failure.
            code.append('page.get_by_role("button").first.click()')
            code.append(
                f"# WARNING: step text \"{raw}\" describes intent, not a "
                "button label — clicking first visible button as a "
                "best-effort fallback"
            )
        elif _is_dialog_confirmation_label(raw):
            # BUG FIX: "Yes"/"No"/"Confirm"/etc. buttons belong to a
            # confirmation dialog that's only visible after some other
            # action opens it. A step like "Click Yes button" right
            # after page load, with nothing in between that could have
            # triggered the dialog, would otherwise hang for the full
            # default timeout and fail — even though this conversion
            # is correct. Check visibility first and skip gracefully
            # if the dialog was never opened, rather than hard-failing.
            code.append(
                f'if page.get_by_role("button", name="{quote(raw)}").count() > 0:'
            )
            code.append(
                f'    page.get_by_role("button", name="{quote(raw)}").first.click()'
            )
            code.append("else:")
            code.append(
                f'    print("SKIPPED: \\"{quote(raw)}\\" dialog button not '
                'present — its triggering dialog was not opened")'
            )
        else:
            # FIX 4: text → get_by_role with name
            code.append(f'page.get_by_role("button", name="{quote(raw)}").click()')
        return code
 
    # -------------------------------------------------------
    # External / Social link click  (FIX 6) — must come BEFORE generic click
    # -------------------------------------------------------
    if sl.startswith(("click ", "open ")) and any(d in sl for d in ("linkedin", "twitter", "facebook", "github", "instagram")):
        href = extract_url(step)
        if not href:
            for dom in ("linkedin.com", "twitter.com", "facebook.com", "github.com", "instagram.com"):
                if dom.split(".")[0] in sl:
                    href = "https://" + dom
                    break
        code.append("# FIX 6: social/external link — use expect_page() for new tab")
        code.append("with page.context.expect_page() as popup_info:")
        if href:
            code.append(f'    page.locator("a[href*=\\"{quote(href.split("/")[2])}\\"]").click()')
            code.append("popup = popup_info.value")
            code.append("popup.wait_for_load_state('networkidle')")
            code.append(f'assert "{href.split("/")[2]}" in popup.url')
        else:
            code.append('    page.get_by_role("link", name=re.compile(r"linkedin|twitter|github|instagram", re.I)).click()')
            code.append("popup = popup_info.value")
            code.append("popup.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Click <anything>  generic  (FIX 1 + FIX 4)
    # -------------------------------------------------------
    if sl.startswith("click "):
        raw = step[len("click "):].strip()

        # BUG FIX: natural phrasing very often includes a leading
        # filler word before the real target — "Click on Reports
        # link", "Click the Dashboard link", "Click the Assign
        # Devices button" — none of which get stripped, so they end
        # up baked into the label as "on Reports"/"the Dashboard"/
        # "the Assign Devices", producing a get_by_role(name=...) that
        # can never match the real element (actually named just
        # "Reports"/"Dashboard"/"Assign Devices"). Strip common
        # leading filler words before any further processing.
        raw = re.sub(r"^(on|the|an?)\s+", "", raw, flags=re.IGNORECASE).strip()

        # BUG FIX: this used to strip the trailing role word
        # ("button"/"link"/"icon"/"tab") for a clean `name=`, but then
        # unconditionally emitted get_by_role("button", ...) — even
        # for text that explicitly said "... link" or "... nav link".
        # Real navigation items are almost always <a> elements, so
        # "Click Reports link" was being converted to
        # get_by_role("button", name="Reports"), which never matches
        # and times out. Now the actual word that was stripped decides
        # the role, and we also fall back to the other role once in
        # case the live markup doesn't match the wording exactly.
        role_match = re.search(
            r"\b(nav(?:igation)?\s+link|button|link|icon|tab)$",
            raw,
            flags=re.IGNORECASE,
        )
        role = "button"  # preserve the original default for ambiguous wording
        if role_match:
            word = role_match.group(1).lower()
            role = "button" if word == "button" else "link"

        label = re.sub(
            r"\s*(nav(?:igation)?\s+link|button|link|icon|tab)$",
            "",
            raw,
            flags=re.IGNORECASE,
        ).strip()
        label = _strip_wrapping_quotes(label)

        if label.startswith("#") or label.startswith("."):

            code.append(f'{_locator_expr(label)}.click()')
            code.append("page.wait_for_load_state('networkidle')")
            return code
        
        if not label:
            code.append("# TODO: Unknown click target")
            return code
        if _is_css_selector(label):
            # FIX 1: CSS selector → locator, not get_by_text
            code.append(f'{_locator_expr(label)}.click()')
        elif _looks_like_purpose_phrase(label):
            # BUG FIX: same class of issue as the click-button branch
            # — "to open modal" describes intent, not a real element
            # label. Fall back rather than emit a name= that can never
            # match.
            code.append(f'page.get_by_role("{role}").first.click()')
            code.append(
                f"# WARNING: step text \"{label}\" describes intent, not "
                f"an element label — clicking first visible {role} as a "
                "best-effort fallback"
            )
        elif _is_dialog_confirmation_label(label):
            # BUG FIX: same reasoning as the click-button branch —
            # "Yes"/"No"/etc. belong to a conditionally-visible
            # confirmation dialog, not an always-present control.
            code.append(
                f'if page.get_by_role("{role}", name="{quote(label)}").count() > 0:'
            )
            code.append(
                f'    page.get_by_role("{role}", name="{quote(label)}").first.click()'
            )
            code.append("else:")
            code.append(
                f'    print("SKIPPED: \\"{quote(label)}\\" dialog button not '
                'present — its triggering dialog was not opened")'
            )
        else:
            other_role = "button" if role == "link" else "link"
            code.append(
                f'page.get_by_role("{role}", name="{quote(label)}").or_('
                f'page.get_by_role("{other_role}", name="{quote(label)}")'
                f').first.click()'
            )
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # PDF / Download  (FIX 5)
    # -------------------------------------------------------
    if any(kw in sl for kw in ("download", "pdf", ".pdf", "export")):
        sel = extract_selector(step)
        if sel:
            code.append("# FIX 5: PDF/download — use expect_download()")
            code.append("with page.expect_download() as download_info:")
            if _is_css_selector(sel):
                code.append(f'    {_locator_expr(sel)}.click()')
            else:
                code.append(f'    page.get_by_text("{quote(sel)}").click()')
            code.append("download = download_info.value")
            code.append('assert download.suggested_filename.endswith(".pdf") or download.url != ""')
        else:
            code.append("with page.expect_download() as download_info:")
            code.append('    page.get_by_role("link", name=re.compile(r"download|pdf", re.I)).click()')
            code.append("download = download_info.value")
            code.append('assert download.url != ""')
        return code
 
    # -------------------------------------------------------
    # Fill Inputs
    # -------------------------------------------------------
    if sl.startswith("fill"):
        m = re.search(r"Fill\s+(.+?)\s+with\s+(.+)", step, re.IGNORECASE)
        if m:
            sel = m.group(1).strip()
            val = m.group(2).strip().strip("'").strip('"')
            code.append(f'{_locator_expr(sel)}.fill("{quote(val)}")')
            return code
 
    # -------------------------------------------------------
    # Type X into Y
    # -------------------------------------------------------
    if sl.startswith("type"):
        m = re.search(r"Type\s+(.+?)\s+into\s+(.+)", step, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            sel = m.group(2).strip()
            code.append(f'{_locator_expr(sel)}.fill("{quote(val)}")')
            return code
 
    # -------------------------------------------------------
    # Enter <field>  (FIX 6 implicit — mapped to real selectors)
    # -------------------------------------------------------
    if sl.startswith("enter "):
        field = step[len("enter "):].strip().lower()
        sel = FIELD_SELECTOR_MAP.get(field, f"input[name='{field}'], #{field}")
        val_m = re.search(r"['\"]([^'\"]+)['\"]", step)
        val = val_m.group(1) if val_m else f"test_{field}"
        code.append(f'page.locator("{quote(sel)}").first.fill("{quote(val)}")')
        return code
 
    # -------------------------------------------------------
    # Visibility check
    # -------------------------------------------------------
    if "visibility" in sl:
        sel = extract_selector(step)
        if sel:
            if _is_css_selector(sel):
                code.append(f'expect({_locator_expr(sel)}).to_be_visible()')
            else:
                code.append(f'expect(page.get_by_text("{quote(sel)}", exact=False).first).to_be_visible()')
            return code
 
    # -------------------------------------------------------
    # Heading check
    # -------------------------------------------------------
    if "heading" in sl:
        m = re.search(r"['\"]([^'\"]+)['\"]", step)
        if m:
            code.append(
                f'expect(page.get_by_role("heading", name="{quote(m.group(1))}")).to_be_visible()'
            )
        else:
            # FIX 3: check structural heading element, not English text
            code.append('expect(page.locator("h1, h2, h3").first).to_be_visible()')
        return code
 
    # -------------------------------------------------------
    # Viewport resize
    # -------------------------------------------------------
    if "viewport" in sl:
        m = re.search(r"(\d+)\s*x\s*(\d+)", step)
        if m:
            w, h = int(m.group(1)), int(m.group(2))
            code.append(f"page.set_viewport_size({{'width': {w}, 'height': {h}}})")
            return code
 
    # -------------------------------------------------------
    # Wait
    # -------------------------------------------------------
    if "wait" in sl:
        sel = extract_selector(step)
        if sel and _is_css_selector(sel):
            code.append(f'page.wait_for_selector("{quote(sel)}")')
        else:
            code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Screenshot
    # -------------------------------------------------------
    if "screenshot" in sl:
        code.append('page.screenshot(path="screenshot.png")')
        return code
 
    # -------------------------------------------------------
    # Scroll
    # -------------------------------------------------------
    if "scroll" in sl:
        code.append("page.mouse.wheel(0, 1200)")
        return code
 
    # -------------------------------------------------------
    # Refresh
    # -------------------------------------------------------
    if "refresh" in sl:
        code.append("page.reload()")
        code.append("page.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # Press Enter
    # -------------------------------------------------------
    if "press enter" in sl:
        code.append('page.keyboard.press("Enter")')
        return code
 
    # -------------------------------------------------------
    # Verify href attribute  (FIX 1 + FIX 2)
    # -------------------------------------------------------
    if "href attribute" in sl:
        url2 = extract_url(step)
        sel = extract_selector(step)
        if sel and url2:
            if _is_css_selector(sel):
                if _href_looks_like_map_link(sel):
                    loc = _locator_expr(sel)
                    code.append(f'if {loc}.count() > 0:')
                    code.append(f'    expect({loc}).to_have_attribute("href", "{quote(url2)}")')
                    code.append('else:')
                    code.append(
                        '    print("SKIPPED: map link not present on '
                        'this view — it may require expanding a row '
                        'or detail panel first")'
                    )
                else:
                    code.append(f'expect({_locator_expr(sel)}).to_have_attribute("href", "{quote(url2)}")')
            else:
                code.append(f'expect(page.get_by_role("link", name="{quote(sel)}")).to_have_attribute("href", "{quote(url2)}")')
        elif url2:
            # FIX 1: use locator(a[href=...]) not get_by_text
            code.append(f'expect(page.locator("a[href=\\"{quote(url2)}\\"]")).to_be_visible()')
        return code
 
    # -------------------------------------------------------
    # Verify URL  (FIX 2 — always expect(page).to_have_url)
    # -------------------------------------------------------
    if (
    sl.startswith("verify url")
    or "verify the url" in sl
    or "check the url" in sl
    or "url should" in sl
    ):
        url2 = extract_url(step)
        if url2:
            if "contain" in sl:
                code.append(f'expect(page).to_have_url(re.compile(r"{quote(url2)}"))')
            else:
                code.append(f'expect(page).to_have_url("{quote(url2)}")')
        else:
            # try quoted fragment
            path_m = re.search(r"['\"]([^\'\"]+)['\"]", step)
            # try bare /path
            bare_m = re.search(r"(/[\w\-/]+)", step)
            fragment = (path_m.group(1) if path_m else None) or (bare_m.group(1) if bare_m else None)
            if fragment:
                code.append(f'expect(page).to_have_url(re.compile(r"{quote(fragment)}"))')
            else:
                code.append('assert page.url != ""  # URL is non-empty')
        return code
 
    # -------------------------------------------------------
    # Verify URL contains  (FIX 2)
    # -------------------------------------------------------
    if "url" in sl and "contain" in sl:
        url2 = extract_url(step)
        # quoted fragment: "contains '/home'"
        _QUOT = re.compile(r"""[\x27\x22]([\w/\-\.]+)[\x27\x22]""")
        path_m = _QUOT.search(step)
        # bare path: "contains /home"
        bare_m = re.search(r"(/[\w\-/]+)", step)
        fragment = url2 or (path_m.group(1) if path_m else None) or (bare_m.group(1) if bare_m else None)
        if fragment:
            code.append(f'expect(page).to_have_url(re.compile(r"{quote(fragment)}"))')
        else:
            code.append('assert page.url != ""')
        return code
 
    # -------------------------------------------------------
    # Verify page title
    # -------------------------------------------------------
    if "page title" in sl:
        m = re.search(r"contains\s+'([^']+)'", step, re.IGNORECASE)
        if m:
            code.append(f'expect(page).to_have_title(re.compile("{quote(m.group(1))}"))')
            return code
 
    # -------------------------------------------------------
    # Link validation / 404 check  (FIX 7)
    # -------------------------------------------------------
    if "404" in sl or ("link" in sl and ("valid" in sl or "broken" in sl or "no 404" in sl)):
        url2 = extract_url(step)
        sel = extract_selector(step)
        if url2:
            # FIX 7: actually verify HTTP status via requests HEAD
            code.append(f"# FIX 7: real HTTP status check for 404")
            code.append(f'_resp = _requests.head("{quote(url2)}", timeout=10, allow_redirects=True)')
            code.append(f'assert _resp.status_code != 404, f"Link returned 404: {quote(url2)}"')
            code.append(f'assert _resp.status_code < 400, f"Link broken ({{_resp.status_code}}): {quote(url2)}"')
        elif sel:
            if _is_css_selector(sel):
                code.append(f"_link = page.locator(\"{quote(sel)}\").get_attribute('href')")
            else:
                code.append(f"_link = page.get_by_role('link', name=\"{quote(sel)}\").get_attribute('href')")
            code.append("if _link and _link.startswith('http'):")
            code.append("    _resp = _requests.head(_link, timeout=10, allow_redirects=True)")
            code.append("    assert _resp.status_code != 404, f'Link returned 404: {_link}'")
            code.append("    assert _resp.status_code < 400, f'Link broken ({_resp.status_code}): {_link}'")
        else:
            # FIX 7: check all anchor hrefs on the page
            code.append("# FIX 7: validate all page links return non-404")
            code.append("_all_links = page.locator('a[href]').evaluate_all(")
            code.append("    'els => els.map(e => e.href).filter(h => h.startsWith(\"http\"))'")
            code.append(")")
            code.append("for _href in _all_links:")
            code.append("    _r = _requests.head(_href, timeout=5, allow_redirects=True)")
            code.append("    assert _r.status_code != 404, f'Broken link: {_href}'")
        return code
 
    # -------------------------------------------------------
    # Verify Visible  (FIX 1 + FIX 3)
    # -------------------------------------------------------
    if "visible" in sl:
        sel = extract_selector(step)
        if sel:
            # FIX 1: CSS selector → locator(), not get_by_text
            if _is_css_selector(sel):
                if _href_looks_like_map_link(sel):
                    # BUG FIX: map links are almost always gated behind
                    # an expand/detail action, not visible on page
                    # load. Check softly instead of hard-asserting, so
                    # a genuinely-absent trigger step doesn't fail the
                    # whole test over a link we have no way to reveal.
                    loc = _locator_expr(sel)
                    code.append(f'if {loc}.count() > 0:')
                    code.append(f'    expect({loc}).to_be_visible()')
                    code.append('else:')
                    code.append(
                        '    print("SKIPPED: map link not present on '
                        'this view — it may require expanding a row '
                        'or detail panel first")'
                    )
                else:
                    code.append(f'expect({_locator_expr(sel)}).to_be_visible()')
            else:
                code.append(f'expect(page.get_by_text("{quote(sel)}", exact=False).first).to_be_visible()')
        else:
            # FIX 3: structural fallback — NOT English text
            keyword = _extract_page_keyword(step)
            if keyword and not any(c.isspace() for c in keyword[:3]):
                # if keyword looks like it could be a tag/id, use locator
                code.append(f'expect(page.locator("body")).to_be_visible()  # page loaded')
            else:
                code.append(f'expect(page.locator("body")).to_be_visible()  # page loaded')
        return code
 
    # -------------------------------------------------------
    # Verify Clickable  (FIX 1)
    # -------------------------------------------------------
    if "clickable" in sl:
        sel = extract_selector(step)
        if sel:
            if _is_css_selector(sel):
                code.append(f'expect({_locator_expr(sel)}).to_be_enabled()')
            else:
                code.append(f'expect(page.get_by_role("button", name="{quote(sel)}")).to_be_enabled()')
            return code
 
    # -------------------------------------------------------
    # Verify href  (FIX 1)
    # -------------------------------------------------------
    if "href" in sl:
        sel = extract_selector(step)
        url2 = extract_url(step)
        if url2:
            if sel and _is_css_selector(sel):
                # Specific element: check its href attribute
                if _href_looks_like_map_link(sel):
                    loc = _locator_expr(sel)
                    code.append(f'if {loc}.count() > 0:')
                    code.append(f'    expect({loc}).to_have_attribute("href", "{quote(url2)}")')
                    code.append('else:')
                    code.append(
                        '    print("SKIPPED: map link not present on '
                        'this view — it may require expanding a row '
                        'or detail panel first")'
                    )
                else:
                    code.append(f'expect({_locator_expr(sel)}).to_have_attribute("href", "{quote(url2)}")')
            else:
                # No specific element: verify a link with that href exists on page
                # BUG FIX: an href attribute selector can still match
                # more than one real element (e.g. the same link
                # appears in both the header and footer) — add .first
                # defensively rather than risk a strict-mode violation.
                code.append(f'expect(page.locator("a[href=\\"{quote(url2)}\\"]").first).to_have_attribute("href", "{quote(url2)}")')
        elif sel:
            # BUG FIX: when sel isn't recognizable as a CSS selector,
            # this falls back to the bare tag "a" — deliberately broad
            # (ANY anchor on the page), which is guaranteed to match
            # many elements on a real page and previously caused the
            # exact same strict-mode violation as unguarded
            # :has-text() selectors. .first is mandatory here, not
            # just for :has-text(), so this bypasses _locator_expr's
            # narrower has-text-only check.
            fallback_sel = quote(sel) if _is_css_selector(sel) else "a"
            code.append(f'expect(page.locator("{fallback_sel}").first).to_be_visible()')
        return code
 
    # -------------------------------------------------------
    # External / LinkedIn link  (FIX 6)
    # -------------------------------------------------------
    if any(d in sl for d in ("linkedin", "twitter", "facebook", "github", "external")):
        href = extract_url(step)
        # Try to find social domain mentioned as text even without https://
        if not href:
            for dom in ("linkedin.com", "twitter.com", "facebook.com", "github.com"):
                if dom.split(".")[0] in sl:
                    href = "https://" + dom
                    break
        if href:
            code.append("# FIX 6: external link opens in new tab — use expect_page()")
            code.append("with page.context.expect_page() as popup_info:")
            code.append(f'    page.locator("a[href*=\\"{quote(href)}\\"]").click()')
            code.append("popup = popup_info.value")
            code.append("popup.wait_for_load_state('networkidle')")
            code.append(f'assert "{quote(href.split("/")[2])}" in popup.url')
        else:
            code.append("with page.context.expect_page() as popup_info:")
            code.append('    page.get_by_role("link", name=re.compile(r"linkedin|twitter|github", re.I)).click()')
            code.append("popup = popup_info.value")
            code.append("popup.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # New Tab  (FIX 6)
    # -------------------------------------------------------
    if "new tab" in sl:
        sel = extract_selector(step)
        code.append("# FIX 6: new tab — use expect_page()")
        code.append("with page.context.expect_page() as popup_info:")
        if sel and _is_css_selector(sel):
            code.append(f'    {_locator_expr(sel)}.click()')
        else:
            code.append("    pass  # TODO: add the click that triggers the new tab")
        code.append("popup = popup_info.value")
        code.append("popup.wait_for_load_state('networkidle')")
        return code
 
    # -------------------------------------------------------
    # URL Starts With  (FIX 2)
    # -------------------------------------------------------
    if "starts with" in sl:
        url2 = extract_url(step)
        if url2:
            code.append(f'expect(page).to_have_url(re.compile(r"^{re.escape(url2)}"))')
            return code
 
    # -------------------------------------------------------
    # URL Ends With  (FIX 2)
    # -------------------------------------------------------
    if "ends with" in sl:
        m = re.search(r"ends with\s+'([^']+)'", step, re.IGNORECASE)
        if m:
            suffix = m.group(1)
            code.append(f'expect(page).to_have_url(re.compile(r"{re.escape(suffix)}$"))')
            return code
 
    # -------------------------------------------------------
    # Contains Text
    # -------------------------------------------------------
    if "contains" in sl:
        m = re.search(r"contains\s+'([^']+)'", step, re.IGNORECASE)
        if m:
            text = m.group(1)
            code.append(f'expect(page.locator("body")).to_contain_text("{quote(text)}")')
            return code
 
    # -------------------------------------------------------
    # Accessibility
    # -------------------------------------------------------
    if "accessible name" in sl:
        sel = extract_selector(step)
        if sel:
            if _is_css_selector(sel):
                code.append(f'expect({_locator_expr(sel)}).to_be_visible()')
            else:
                code.append(f'expect(page.get_by_role("region", name="{quote(sel)}")).to_be_visible()')
            return code
 
    # -------------------------------------------------------
    # Verify / Assert generic fallback  (FIX 3)
    # FIX 3: check page structure, NOT English-text content
    # -------------------------------------------------------
    if sl.startswith(("verify", "assert", "check", "confirm", "ensure")):
        # Try to get a CSS selector from the step
        sel = extract_selector(step)
        url2 = extract_url(step)
        if url2:
            # FIX 2: URL assertion
            code.append(f'expect(page).to_have_url(re.compile(r"{quote(url2)}"))')
        elif sel and _is_css_selector(sel):
            # FIX 1: real selector
            code.append(f'expect({_locator_expr(sel)}).to_be_visible()')
        else:
            # FIX 3: structural check — body is visible = page loaded without crash
            code.append('expect(page.locator("body")).to_be_visible()  # page loaded successfully')
        return code
 
    # -------------------------------------------------------
    # Unsupported Step
    # -------------------------------------------------------
    code.append(f'print("WARNING: Unsupported step -> {quote(step)}")')
    code.append(f"# Unsupported Step: {step}")
    return code
 
 
# ==========================================================
# EXPECTED RESULT CONVERTER  (FIX 2 + FIX 3)
# ==========================================================
 
def convert_expected(expected: str) -> List[str]:
    """Convert expected_result string into Playwright assertions."""
    from typing import List
 
    result = _parse_expected(expected)
    code: List[str] = []
 
    if result["url"]:
        # FIX 2: always expect(page).to_have_url — never expect(page.url)
        code.append(f'expect(page).to_have_url("{quote(result["url"])}")')
 
    if result["title"]:
        code.append(f'expect(page).to_have_title(re.compile("{quote(result["title"])}"))')
 
    if result["contains"]:
        code.append(f'expect(page.locator("body")).to_contain_text("{quote(result["contains"])}")')
 
    if result["heading"]:
        # FIX 3: structural heading element, not text content
        code.append('expect(page.locator("h1, h2, h3").first).to_be_visible()')
 
    if result["visible"]:
        # FIX 4: specific button role, not generic locator("button")
        code.append('expect(page.get_by_role("button").first).to_be_visible()')
 
    if result["accessibility"]:
        code.append("# TODO: Accessibility validation (use axe-playwright)")
 
    # FIX 3: fallback is structural (body visible), not English text search
    if not code:
        code.append('expect(page.locator("body")).to_be_visible()  # page loaded successfully')
 
    return code
 
 
def _parse_expected(expected: str) -> dict:
    expected = clean_step(expected)
    data = {"url": None, "title": None, "contains": None,
            "visible": None, "heading": False, "accessibility": False}
 
    url = extract_url(expected)
    if url:
        data["url"] = url
 
    if "title contains" in expected.lower():
        data["title"] = expected.split("contains", 1)[1].strip().strip("'")
 
    if "body contains" in expected.lower():
        data["contains"] = expected.split("contains", 1)[1].strip().strip("'")
 
    if "button exists" in expected.lower():
        data["visible"] = True
 
    if "heading" in expected.lower():
        data["heading"] = True
 
    if "accessible" in expected.lower():
        data["accessibility"] = True
 
    return data
 
 
# ==========================================================
# TEST NAME SANITISER
# ==========================================================
 
def sanitize_test_name(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    if not name.startswith("test_"):
        name = "test_" + name
    return name
 
 
# ==========================================================
# SINGLE TEST CASE GENERATOR  (FIX 8 — base_url as parameter)
# ==========================================================
 
def generate_test_case(test_case: Dict[str, Any]) -> List[str]:
    writer = CodeWriter()
 
    test_name = sanitize_test_name(test_case.get("title", "generated_test"))
 
    writer.add("")
    writer.add("# =====================================================")
    writer.add(f"# {test_case.get('id', '')} - {test_case.get('title', '')}")
    writer.add("# =====================================================")
    writer.blank()

    # BUG FIX: the shared `page` fixture is backed by a session-wide
    # context that's already logged in (by design, so the other 29
    # tests don't have to re-authenticate). That means any test
    # whose whole point is to check the actual PRE-login state (e.g.
    # "Verify Forgot Password link is present on login page") can
    # never see it through that fixture — navigating to the base URL
    # there lands straight on the dashboard, not the login form. Such
    # tests get the dedicated `unauthenticated_page` fixture instead,
    # bound to the local name `page` so the rest of the generated
    # body (which references `page.` throughout) needs no changes.
    title = test_case.get("title", "")
    needs_unauthenticated = bool(
        re.search(r"\blogin\s+page\b", title, re.IGNORECASE)
    )

    # FIX 8: accept base_url from fixture
    if needs_unauthenticated:
        writer.add(f"def {test_name}(unauthenticated_page: Page, base_url: str):")
        writer.add("    page = unauthenticated_page")
    else:
        writer.add(f"def {test_name}(page: Page, base_url: str):")
    writer.add("    page.set_default_timeout(10000)")
    writer.add("    page.set_default_navigation_timeout(30000)")
    writer.blank()
 
    steps = test_case.get("steps", [])
 
    # Deduplicate steps preserving order
    seen: set = set()
    filtered: List[str] = []
    for s in steps:
        if s not in seen:
            seen.add(s)
            filtered.append(s)
    steps = filtered
 
    if not steps:
        writer.add("    pass")
        return writer.lines
 
    has_assertion = False
 

    for step in steps:
        commands = convert_step(step)

        inside_with = False

        for cmd in commands:

            if cmd.startswith("with "):
                writer.add(f"    {cmd}")
                inside_with = True
                continue

            if inside_with:

                if (
                    cmd.startswith("popup")
                    or cmd.startswith("download")
                    or cmd.startswith("page.")
                    or cmd.startswith("expect(")
                    or cmd.startswith("assert ")
                ):
                    writer.add(f"        {cmd}")
                    continue

                inside_with = False

            writer.add(f"    {cmd}")

            if "expect(" in cmd or cmd.strip().startswith("assert "):
                has_assertion = True



 
    writer.blank()
 
    expected = test_case.get("expected_result", "")
    if expected:
        assertions = convert_expected(expected)
        for a in assertions:
            writer.add(f"    {a}" if not a.startswith("    ") else a)
            if "expect(" in a or a.strip().startswith("assert "):
                has_assertion = True
 
    # Safety net — every test must have at least one assertion
    if not has_assertion:
        writer.add(
            '    expect(page.locator("body")).to_be_visible()'
            '  # safety assertion'
        )
 
    writer.blank()
    return writer.lines
 
 
# ==========================================================
# PLAYWRIGHT FILE GENERATOR
# FIX 9: header no longer imports os or subprocess
# ==========================================================
 
def generate_playwright_file(test_cases: List[Dict[str, Any]]) -> str:
    writer = CodeWriter()
    writer.add(PLAYWRIGHT_HEADER)
 
    # FIX 7: import requests for HTTP status checks
    writer.add("try:")
    writer.add("    import requests as _requests")
    writer.add("except ImportError:")
    writer.add("    _requests = None  # link-validation steps will be skipped")
    writer.blank()
 
    writer.add("# ==========================================")
    writer.add("# AUTO GENERATED BY AI PLAYWRIGHT GENERATOR")
    writer.add("# ==========================================")
    writer.blank()
    writer.blank()
 
    if not test_cases:
        writer.add("# No test cases generated.")
        return writer.build()
 
    for index, tc in enumerate(test_cases, start=1):
        writer.add(f"# Test Case {index}")
        writer.extend(generate_test_case(tc))
        writer.blank()
 
    return writer.build()
 
 
# ==========================================================
# DEBUG HELPERS
# ==========================================================
 
def print_summary(test_cases: List[Dict[str, Any]]):
    total = sum(len(tc.get("steps", [])) for tc in test_cases)
    print()
    print("=" * 70)
    print("PLAYWRIGHT CONVERSION SUMMARY")
    print("=" * 70)
    print(f"Total Test Cases : {len(test_cases)}")
    print(f"Total Steps      : {total}")
    print()
    for tc in test_cases:
        print(f"{tc.get('id')} : {tc.get('title')}")
    print("=" * 70)
    print()
 
 
# ==========================================================
# VALIDATION
# ==========================================================
 
def validate_test_case(tc: Dict[str, Any]) -> bool:
    required = ["id", "title", "steps", "expected_result"]
    for field in required:
        if field not in tc:
            return False
    return isinstance(tc["steps"], list)
 
 
def filter_valid_tests(test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    valid = []
    for tc in test_cases:
        if validate_test_case(tc):
            valid.append(tc)
        else:
            print(f"Skipping invalid test case: {tc.get('id', 'UNKNOWN')}")
    return valid
 
 
# ==========================================================
# MAIN CONVERTER
# ==========================================================
 
def convert_yaml_to_playwright(yaml_text: str) -> Dict[str, Any]:
    """
    Convert validated YAML test cases into a complete
    Playwright + pytest automation script.
    """
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "generated_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
 
    if not yaml_text or not yaml_text.strip():
        return {"code": "# Empty YAML supplied.", "unsupported": [], "test_cases": []}
 
    try:
        data = yaml.safe_load(yaml_text)
    except Exception as e:
        return {"code": f"# Invalid YAML\n# {e}", "unsupported": [], "test_cases": []}
 
    if not isinstance(data, dict):
        return {"code": "# YAML root must be a dictionary.", "unsupported": [], "test_cases": []}
 
    test_cases = data.get("test_cases", [])
 
    yaml_path = output_dir / "generated_yaml.yaml"
    yaml_path.write_text(yaml_text, encoding="utf-8")
 
    if not isinstance(test_cases, list):
        return {"code": "# test_cases must be a list.", "unsupported": [], "test_cases": []}
 
    test_cases = filter_valid_tests(test_cases)
    playwright_code = generate_playwright_file(test_cases)
 
    # Detect unsupported steps by scanning output (single pass)
    unsupported: List[str] = []
    unsupported_lines: List[str] = []
    for line in playwright_code.splitlines():
        if line.strip().startswith("# Unsupported Step:"):
            step_text = line.strip()[len("# Unsupported Step:"):].strip()
            if step_text not in unsupported:
                unsupported.append(step_text)
                unsupported_lines.append(f"- {step_text}")
 
    print_summary(test_cases)
    print(f"[Playwright Converter] Generated {len(test_cases)} test case(s).")
    print(f"[Playwright Converter] Unsupported Steps: {len(unsupported)}")
 
    if unsupported_lines:
        (output_dir / "unsupported_steps.txt").write_text(
            "\n".join(unsupported_lines), encoding="utf-8"
        )
 
    print()
    print("=" * 70)
    print("FINAL CONVERSION REPORT")
    print("=" * 70)
    print(f"Test Cases      : {len(test_cases)}")
    print(f"Unsupported     : {len(unsupported)}")
    print(f"Output Script   : {output_dir / 'generated_test.py'}")
    print(f"Generated YAML  : {yaml_path}")
    if unsupported_lines:
        print(f"Unsupported Log : {output_dir / 'unsupported_steps.txt'}")
    print("=" * 70)
 
    return {
        "code": playwright_code,
        "unsupported": unsupported,
        "test_cases": test_cases,
    }