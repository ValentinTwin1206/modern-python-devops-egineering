from .exceptions import RequestBlocked
from .scanner import SecurityScanner


class PyGuardMiddleware:

    def __init__(self):
        self.scanner = SecurityScanner()

    def before_request(self, request):
        result = self.scanner.scan(request)

        if result.blocked:
            raise RequestBlocked(result.reason)

        return request