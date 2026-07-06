"""Shared selector prioritisation and capping logic."""
import os

SELECTOR_CAP = int(os.getenv("SELECTOR_CAP", "15"))


def prioritise_selectors(selectors: list) -> list:
    """Sort: id-based (#id) first, then name-based, then text-based."""
    def score(s):
        sel = s.get("selector", "")
        if sel.startswith("#"):
            return 0   # most stable
        if sel.startswith("input[name") or sel.startswith("a[href"):
            return 1
        return 2       # text-based — least stable
    return sorted(selectors, key=score)


def cap_selectors(selectors: list, label: str) -> list:
    """Apply cap and log how many selectors were dropped."""
    total = len(selectors)
    capped = prioritise_selectors(selectors)[:SELECTOR_CAP]
    dropped = total - len(capped)
    if dropped > 0:
        print(
            f"[Selector Cap] {label}: using {len(capped)}/{total} "
            f"({dropped} dropped). Set SELECTOR_CAP env var to increase."
        )
    return capped