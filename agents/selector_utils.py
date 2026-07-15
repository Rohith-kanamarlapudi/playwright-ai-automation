"""Shared selector prioritisation and capping logic."""

import os

try:
    from db.selector_memory import get_selector_score
except ImportError:
    get_selector_score = None

# Increase selector cap for the larger live IoT application
SELECTOR_CAP = int(os.getenv("SELECTOR_CAP", "25"))


def prioritise_selectors(selectors: list) -> list:
    """
    Prioritise the most stable selectors for Angular SPAs.

    Lower score = higher priority.

    Priority:
        data-testid / aria-label
        id
        name attributes
        semantic selectors
        buttons / inputs
        everything else

    Historical selector success is also considered.
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

        # Reject empty selectors
        if not sel:
            continue

        # Reject invalid selectors
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
        """
        Lower score = better selector.

        Combines selector quality with historical
        selector reliability stored in SQLite.
        """

        sel = str(s.get("selector", ""))

        sel_type = str(s.get("type", "")).lower()

        # ---------------------------------------------------
        # Base selector priority
        # ---------------------------------------------------

        if (
            sel.startswith("[data-testid")
            or sel.startswith("[aria-label")
        ):
            base = 0

        elif sel.startswith("#"):
            base = 1

        elif (
            sel.startswith("input[name")
            or sel.startswith("textarea[name")
            or sel.startswith("select[name")
            or sel.startswith("a[href")
        ):
            base = 2

        else:

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

            if any(
                keyword in sel.lower()
                for keyword in semantic_keywords
            ):
                base = 3

            elif sel_type in (
                "button",
                "input",
                "textarea",
                "select",
            ):
                base = 4

            else:
                base = 5

        # ---------------------------------------------------
        # Historical selector stability
        # ---------------------------------------------------

        if get_selector_score is None:
            return base

        try:

            memory_score = get_selector_score(sel)

            # 1.0 -> always passed
            # 0.5 -> unknown
            # 0.0 -> always failed

            memory_penalty = round(
                (1.0 - memory_score) * 3
            )

            return base + memory_penalty

        except Exception:
            return base

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