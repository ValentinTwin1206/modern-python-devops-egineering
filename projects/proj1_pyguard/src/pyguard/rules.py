import time

from abc          import ABC, abstractmethod
from collections  import defaultdict, deque
from urllib.parse import unquote

from . import logger

class SecurityRule(ABC):
    """Abstract base class for security rules."""
    @abstractmethod
    def check(self, request) -> bool:
        """Return True when the request should be blocked."""
        raise NotImplementedError


class PathTraversal(SecurityRule):
    """Security rule to detect path traversal attacks."""

    def check(self, request) -> bool:
        """
        Check if the request contains a path traversal attempt.
        """

        if request.status_code is not None:
            return False

        text = f"{request.path} {request.query} {request.body}".lower()

        # Decode nested URL encoding (maximum 5 iterations)
        for _ in range(5):
            decoded = unquote(text)
            if decoded == text:
                break
            text = decoded

        # Normalize Windows path separators
        text = text.replace("\\", "/")

        # Detect directory traversal
        return ".." in text.split("/")


class BruteForce(SecurityRule):
    """Block sources that exceed a failed-authentication limit."""

    def __init__(
        self,
        paths: list[str],
        max_attempts: int = 5,
        window: int = 60,
        block_duration: int = 300,
    ):
        self.paths          = set(paths)
        self.max_attempts   = max_attempts
        self.window_seconds = window
        self.block_seconds  = block_duration

        self.last_cleanup     = time.monotonic()
        self.cleanup_interval = 60
        self.attempts         = defaultdict(deque)
        self.blocked_until    = {}


    def _cleanup(self, now: float) -> None:
        """Remove expired attempts and blocked sources."""

        # Clean up expired attempts
        for source, attempts in list(self.attempts.items()):
            while attempts and now - attempts[0] > self.window_seconds:
                attempts.popleft()

            if not attempts:
                del self.attempts[source]

        # Clean up expired blocks
        for source, blocked_until in list(self.blocked_until.items()):
            if now >= blocked_until:
                del self.blocked_until[source]

        self.last_cleanup = now


    def check(self, request) -> bool:
        """
        Track 401/403 responses and block the source's next request at the limit.

        :param request (Request): The incoming request object.
        :return (bool): True if the request should be blocked, False otherwise.
        """

        if request.path not in self.paths:
            return False

        # Get the current time in seconds since an unspecified starting point and 
        # perform cleanup if necessary
        now = time.monotonic()
        if now - self.last_cleanup >= self.cleanup_interval:
            self._cleanup(now)

        source = request.source

        if request.status_code is not None:
            # If the response is not a failed-authentication response (401 or 403), 
            # do not track it.
            if request.status_code not in {401, 403}:
                return False

            # If the request is a failed-authentication response, track the attempt 
            # and check if the source should be blocked.
            attempts = self.attempts[source]
            while attempts and now - attempts[0] > self.window_seconds:
                attempts.popleft()
            attempts.append(now)

            # If the number of failed attempts exceeds the maximum allowed, block the 
            # source for the specified duration.
            if len(attempts) >= self.max_attempts:
                logger.warning(
                    "Blocking source %s after %d failed-auth responses in %d seconds",
                    source,
                    len(attempts),
                    self.window_seconds,
                )
                self.blocked_until[source] = now + self.block_seconds
            return False

        if self.is_blocked(source):
            return True

        attempts = self.attempts[source]
        while attempts and now - attempts[0] > self.window_seconds:
            attempts.popleft()

        return False


    def is_blocked(self, source: str) -> bool:
        """
        Check if the source is currently blocked.

        :param source (str): The source IP address.
        :return (bool): True if the source is blocked, False otherwise.
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