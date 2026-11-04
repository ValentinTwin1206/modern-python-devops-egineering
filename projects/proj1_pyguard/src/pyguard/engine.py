from .models import Request, ScanResult
from .rules import SecurityRule

class RequestBlocked(Exception):
    """Raised when a request is blocked."""

class PyGuard:

    # Allow access to the Request model via PyGuard.Request
    Request = Request

    def __init__(self, rules: list[SecurityRule] | None = None):
        self.rules = rules or []

    def scan(self, request: Request) -> ScanResult:
        """
        Scan the given request against the security rules.
        
        :param self:              The PyGuard instance
        :param request (Request): The request to be scanned
        :return (ScanResult):     The result of the scan
        """

        for rule in self.rules:
            if rule.check(request):
                return ScanResult(
                    blocked=True,
                    reason=type(rule).__name__
                )

        return ScanResult(blocked=False)


    def check(self, request: Request) -> Request:
        """
        Check the given request against the security rules and raise an exception if blocked.
        
        :param self:              The PyGuard instance
        :param request (Request): The request to be checked
        :return (Request):        The original request if not blocked
        """

        result = self.scan(request)

        if result.blocked:
            raise RequestBlocked(result.reason)

        return request
