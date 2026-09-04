from .models import ScanResult
from .rules import (
    AuthBruteForceRule,
    PathTraversalRule,
    SecurityRule,
)


class SecurityScanner:
    def __init__(self, protected_paths=None):
        self.rules: list[SecurityRule] = [
            PathTraversalRule(),
            AuthBruteForceRule(
                protected_paths=protected_paths or set(),
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