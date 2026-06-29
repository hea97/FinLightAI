from __future__ import annotations

import re


RELEVANCE_TERMS = (
    "AI",
    "artificial intelligence",
    "semiconductor",
    "chip",
    "export control",
    "NVIDIA",
    "AMD",
    "Samsung",
    "SK Hynix",
)


def contains_term(text: str, term: str) -> bool:
    """Match a keyword as a token or phrase, never as an arbitrary substring."""
    normalized_term = " ".join(term.lower().split())
    escaped = re.escape(normalized_term).replace(r"\ ", r"\s+")
    pattern = rf"(?<![\w]){escaped}(?![\w])"
    return re.search(pattern, text.lower(), flags=re.UNICODE) is not None


def matched_relevance_terms(text: str) -> list[str]:
    return [term for term in RELEVANCE_TERMS if contains_term(text, term)]


def relevance_score(text: str) -> int:
    return len(matched_relevance_terms(text))
