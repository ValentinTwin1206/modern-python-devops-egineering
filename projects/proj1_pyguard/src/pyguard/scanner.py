from .models import ScanResult
from .rules import has_path_traversal


class SecurityScanner:

    def scan(self, request) -> ScanResult:
        if has_path_traversal(request):
            return ScanResult(
                blocked=True,
                reason="Path traversal detected",
            )

        return ScanResult(blocked=False)