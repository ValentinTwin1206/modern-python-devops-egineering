from .exceptions import RequestBlocked
from .scanner import SecurityScanner


class PyGuardMiddleware:

    def __init__(self, protected_paths=None):
        self.scanner = SecurityScanner(
            protected_paths=protected_paths,
        )

    def before_request(self, request):
        result = self.scanner.scan(request)

        if result.blocked:
            raise RequestBlocked(result.reason)

        return request