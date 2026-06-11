from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


def slugify(value: str, separator: str = "-") -> str:
    if not separator or separator.isspace():
        raise ValueError("separator must contain at least one non-whitespace character")

    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    cleaned = re.sub(r"[^a-z0-9\s_-]", "", ascii_text)
    parts = [part for part in re.split(r"[\s_-]+", cleaned.strip()) if part]
    if not parts:
        return "item"
    return separator.join(parts)


def unique_slug(value: str, existing: Iterable[str], separator: str = "-") -> str:
    taken = set(existing)
    base_slug = slugify(value, separator=separator)
    if base_slug not in taken:
        return base_slug

    suffix = 2
    candidate = f"{base_slug}{separator}{suffix}"
    while candidate in taken:
        suffix += 1
        candidate = f"{base_slug}{separator}{suffix}"
    return candidate


def slug_path(*parts: str, separator: str = "-") -> str:
    slugs = [slugify(part, separator=separator) for part in parts if part.strip()]
    if not slugs:
        raise ValueError("slug_path requires at least one non-empty part")
    return "/".join(slugs)