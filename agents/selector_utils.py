"""Shared selector prioritisation and capping logic."""

import os

# Increase selector cap for the larger live IoT application
SELECTOR_CAP = int(os.getenv("SELECTOR_CAP", "25"))


def prioritise_selectors(selectors: list) -> list:
    """
    Prioritise the most stable selectors for Angular SPAs.

    Priority:
    0 -> data-testid / aria-label
    1 -> id selectors
    2 -> input[name] / a[href]
    3 -> semantic widget classes
    4 -> buttons / inputs
    5 -> everything else

    Invalid selectors are discarded completely.
    """

    cleaned = []

    INVALID_PATTERNS = (
        "input[name='']",
        'input[name=""]',
        "input[id='']",
        'input[id=""]',
        "a[href='']",
        'a[href=""]',
        "button:has-text('')",
        'button:has-text("")',
        "a:has-text('')",
        'a:has-text("")',
        "#",
        ".",
    )

    for s in selectors:

        sel = str(s.get("selector", "")).strip()
        
        
        element_type = str(s.get("type", "")).lower()

        attributes = str(s.get("attributes", "")).lower()

        if "type=\"hidden\"" in attributes:
            continue

        if "type='hidden'" in attributes:
            continue

        if element_type == "hidden":
            continue

        # ---------------------------------------------
        # Reject empty selectors
        # ---------------------------------------------

        if not sel:
            continue

        # ---------------------------------------------
        # Reject invalid selectors
        # ---------------------------------------------

        if sel in INVALID_PATTERNS:
            continue

        if "has-text('')" in sel or 'has-text("")' in sel:
            continue

        if "input[name='']" in sel or 'input[name=""]' in sel:
            continue

        if "input[id='']" in sel or 'input[id=""]' in sel:
            continue

        if "a[href='']" in sel or 'a[href=""]' in sel:
            continue

        cleaned.append(s)

    def score(s):

        sel = str(s.get("selector", ""))
        sel_type = str(s.get("type", ""))

        # ---------------------------------------------
        # Highest priority
        # ---------------------------------------------

        if (
            sel.startswith("[data-testid")
            or sel.startswith("[aria-label")
        ):
            return 0

        # ---------------------------------------------
        # ID selectors
        # ---------------------------------------------

        if sel.startswith("#"):
            return 1

        # ---------------------------------------------
        # Stable attribute selectors
        # ---------------------------------------------

        if (
            sel.startswith("input[name")
            or sel.startswith("a[href")
        ):
            return 2

        # ---------------------------------------------
        # Semantic selectors
        # ---------------------------------------------

        semantic_keywords = (
            "widget",
            "gauge",
            "chart",
            "sensor",
            "metric",
            "dashboard",
            "card",
            "report",
            "alert",
            "alarm",
            "device",
            "table",
            "grid",
            "list",
            "menu",
            "navbar",
            "sidebar",
            "panel",
            "dialog",
            "modal",
        )

        if any(keyword in sel.lower() for keyword in semantic_keywords):
            return 3

        # ---------------------------------------------
        # Buttons / Inputs
        # ---------------------------------------------

        if sel_type in ("button", "input"):
            return 4

        return 5

    return sorted(cleaned, key=score)


def cap_selectors(selectors: list, label: str) -> list:
    """
    Apply selector cap and report dropped selectors.
    """

    selectors = prioritise_selectors(selectors)

    total = len(selectors)

    capped = selectors[:SELECTOR_CAP]

    dropped = total - len(capped)

    if dropped > 0:
        print(
            f"[Selector Cap] {label}: "
            f"using {len(capped)}/{total} "
            f"({dropped} dropped). "
            f"Increase SELECTOR_CAP to keep more."
        )

    return capped