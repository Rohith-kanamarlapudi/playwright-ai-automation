"""Shared selector prioritisation and capping logic."""

import os

# Increase selector cap for the larger live IoT application
SELECTOR_CAP = int(os.getenv("SELECTOR_CAP", "30"))


def prioritise_selectors(selectors: list) -> list:
    """
    Prioritise the most stable selectors for Angular SPAs.

    Priority:
    0 -> data-testid / aria-label
    1 -> id selectors
    2 -> input[name] / a[href]
    3 -> semantic widget classes
    4 -> everything else
    """

    def score(s):

        sel = str(s.get("selector", ""))
        sel_type = str(s.get("type", ""))

        # -------------------------------------------------
        # Most stable selectors
        # -------------------------------------------------

        if (
            sel.startswith("[data-testid")
            or sel.startswith("[aria-label")
        ):
            return 0

        # -------------------------------------------------
        # ID selectors
        # -------------------------------------------------

        if sel.startswith("#"):
            return 1

        # -------------------------------------------------
        # Name / href selectors
        # -------------------------------------------------

        if (
            sel.startswith("input[name")
            or sel.startswith("a[href")
        ):
            return 2

        # -------------------------------------------------
        # Semantic Angular / IoT widgets
        # -------------------------------------------------

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
        )

        if any(keyword in sel.lower() for keyword in semantic_keywords):
            return 3

        # -------------------------------------------------
        # Prefer buttons/inputs slightly over generic text
        # -------------------------------------------------

        if sel_type in ("button", "input"):
            return 4

        # -------------------------------------------------
        # Least stable
        # -------------------------------------------------

        return 5

    return sorted(selectors, key=score)


def cap_selectors(selectors: list, label: str) -> list:
    """
    Apply selector cap and report dropped selectors.
    """

    total = len(selectors)

    capped = prioritise_selectors(selectors)[:SELECTOR_CAP]

    dropped = total - len(capped)

    if dropped > 0:

        print(
            f"[Selector Cap] {label}: "
            f"using {len(capped)}/{total} "
            f"({dropped} dropped). "
            f"Increase SELECTOR_CAP to keep more."
        )

    return capped