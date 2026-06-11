from docslug import slug_path, slugify, unique_slug


def test_slugify_normalizes_unicode_and_spacing() -> None:
    assert slugify("  Cafe au lait & Notes  ") == "cafe-au-lait-notes"


def test_slugify_returns_fallback_for_punctuation_only() -> None:
    assert slugify("!!!") == "item"


def test_unique_slug_adds_numeric_suffix() -> None:
    existing = {"release-notes", "release-notes-2"}
    assert unique_slug("Release Notes", existing) == "release-notes-3"


def test_slug_path_builds_nested_segments() -> None:
    assert slug_path("Guides", "API Reference") == "guides/api-reference"