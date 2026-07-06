# agents/doc_sanitiser.py
"""
Sanitise uploaded design documents before injecting them into LLM prompts.
Removes instruction-injection patterns and enforces size limits.
"""
import re

MAX_DOC_CHARS = 8000  # prevent token overflow attacks

# Patterns that look like prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"forget\s+(all\s+)?previous",
    r"disregard\s+(all\s+)?previous",
    r"you\s+are\s+now",
    r"new\s+instructions?:",
    r"system\s*:",
    r"<\s*system\s*>",
    r"<\s*/?instructions?\s*>",
    r"import\s+os",
    r"import\s+subprocess",
    r"os\.system\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def sanitise_document(text: str) -> tuple[str, list[str]]:
    """
    Clean an uploaded design document before it enters an LLM prompt.

    Returns:
        (cleaned_text, warnings)  — warnings is a list of flagged issues.
    """
    warnings = []

    # 1. Enforce size limit
    if len(text) > MAX_DOC_CHARS:
        warnings.append(f"Document truncated from {len(text)} to {MAX_DOC_CHARS} chars.")
        text = text[:MAX_DOC_CHARS]

    # 2. Detect and strip injection patterns
    for pattern in _COMPILED:
        if pattern.search(text):
            warnings.append(f"Injection pattern removed: {pattern.pattern}")
            text = pattern.sub("[REMOVED]", text)

    # 3. Strip angle-bracket HTML/XML tags (not needed in design docs)
    text = re.sub(r"<[^>]{1,100}>", "", text)

    return text.strip(), warnings