import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("pyguard")

from .middleware import PyGuardMiddleware
from .models     import Request, ScanResult
from .exceptions import RequestBlocked

__all__ = ["PyGuardMiddleware",
           "Request",
           "ScanResult",
           "RequestBlocked",
           ]