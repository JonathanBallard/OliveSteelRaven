
# `recipes` app utils.py

import re

_whitespace_re = re.compile(r"\s+")

def normalize_name(raw: str) -> str:
    """
    Canonicalize user-entered names (ingredients, tags, etc.)
    by collapsing whitespace and normalizing case.

    Examples:
        "  Meal   Prep " -> "meal prep"
        "Onion POWDER"   -> "onion powder"
    """
    if not raw:
        return ""
    return _whitespace_re.sub(" ", raw.strip()).lower()