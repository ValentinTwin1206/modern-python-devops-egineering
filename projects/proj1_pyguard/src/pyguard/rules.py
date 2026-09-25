from abc import ABC, abstractmethod
import time
from collections import defaultdict, deque
from . import logger

class SecurityRule(ABC):
    @abstractmethod
    def check(self, request) -> bool:
        """Return True when the request should be blocked."""
        raise NotImplementedError

class PathTraversalRule(SecurityRule):
    PATTERNS = (
        "../",
        "..\\",
        "%2e%2e",
        "%252e",
    )

    def check(self, request) -> bool:
        text = f"{request.path}{request.query}".lower()

        return any(pattern in text for pattern in self.PATTERNS)


class AuthBruteForceRule(SecurityRule):
    def __init__(
        self,
        protected_paths: set[str],
        max_attempts: int = 5,
        window_seconds: int = 60,
        block_seconds: int = 300,
    ):
        self.protected_paths = protected_paths
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.block_seconds = block_seconds

        self.attempts = defaultdict(deque)
        self.blocked_until = {}

    def check(self, request) -> bool:
        """
        Check if the request should be blocked based on authentication brute force rules.

        :param request: The incoming request object.
        :type request: Request
        :return: True if the request should be blocked, False otherwise.
        :rtype: bool
        """

        # return False if the request is not for a protected path
        if (request.method, request.path) not in self.protected_paths:
            return False

        source = request.source

        if self.is_blocked(source):
            return True

        now: float = time.monotonic()
        attempts = self.attempts[source]

        # Remove attempts that are outside the time window
        while attempts and now - attempts[0] > self.window_seconds:
            attempts.popleft()

        attempts.append(now)

        # If the number of attempts exceeds the maximum allowed, block the source
        if len(attempts) >= self.max_attempts:
            logger.warning(
                "!!! Blocking source %s due to too many attempts: %d attempts in the last %d seconds",
                source,
                len(attempts),
                self.window_seconds,
            )
            self.blocked_until[source] = now + self.block_seconds
            return True

        return False


    def is_blocked(self, source: str) -> bool:
        """
        Check if the source is currently blocked.

        :param source: The source IP address.
        :type source: str
        :return: True if the source is blocked, False otherwise.
        :rtype: bool
        """
        blocked_until = self.blocked_until.get(source)

        if blocked_until is None:
            logger.info(
                "Source %s is not currently blocked",
                source,
            )
            return False

        if time.monotonic() >= blocked_until:
            logger.info(
                "Unblocking source %s after block period expired",
                source,
            )

            del self.blocked_until[source]
            return False

        logger.warning(
            "Source %s is currently blocked until %f",
            source,
            blocked_until,
        )
        
        return True