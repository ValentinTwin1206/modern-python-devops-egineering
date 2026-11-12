from collections.abc import Awaitable, Callable
from typing import Any

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


    def check(
        self,
        request: Request,
        handler: Callable[[], Awaitable[Any]] | None = None,
    ) -> Request | Awaitable[Any]:
        """
        Check the given request against the security rules and raise an exception if blocked.
        
        :param self:              The PyGuard instance
        :param request (Request): The request to be checked
        :return (Request):        The original request if not blocked
        """

        result = self.scan(request)
        if result.blocked:
            raise RequestBlocked(result.reason)
        if handler is not None:
            return self._check_handler(request, handler)
        return request

    async def _check_handler(
        self,
        request: Request,
        handler: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        Check the given request using the provided handler and update the request status.

        :param self: The PyGuard instance
        :param request (Request): The request to be checked
        :param handler (Callable[[], Awaitable[Any]]): The handler to process the request
        :return (Any): The response from the handler
        """
        response = await handler()
        request.status_code = response.status_code
        self.scan(request)
        return response

