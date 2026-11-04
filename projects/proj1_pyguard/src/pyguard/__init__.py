import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("pyguard")

# must be imported after logger is configured because rules.py uses logger
from .engine import PyGuard, RequestBlocked

# Define the public API of the package
__all__ = ["PyGuard", "RequestBlocked"]