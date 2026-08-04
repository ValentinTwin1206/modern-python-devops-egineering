PATTERNS = (
    "../",
    "..\\",
    "%2e%2e",
    "%252e",
)


def has_path_traversal(request) -> bool:
    text = f"{request.path}{request.query}".lower()
    return any(p in text for p in PATTERNS)