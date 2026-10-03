from .models import ScanResult
from .rules import (
    AuthBruteForceRule,
    PathTraversalRule,
    SecurityRule,
)

from . import logger


class SecurityScanner:
    def __init__(self, protected_paths = None, max_attempts: int = 5, window_seconds: int = 60, block_seconds: int = 300):
        self.rules: list[SecurityRule] = [
            PathTraversalRule(),
            AuthBruteForceRule(
                protected_paths=protected_paths or set(),
                max_attempts=max_attempts,
                window_seconds=window_seconds,
                block_seconds=block_seconds
            ),
        ]

    def scan(self, request) -> ScanResult:
        for rule in self.rules:
            if rule.check(request):
                return ScanResult(
                    blocked=True,
                    reason=type(rule).__name__,
                )

        return ScanResult(blocked=False)