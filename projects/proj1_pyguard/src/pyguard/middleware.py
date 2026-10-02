from .exceptions import RequestBlocked
from .scanner import SecurityScanner
from . import logger

class PyGuardMiddleware:

    def __init__(self, protected_paths=None, brute_force_config: dict = {}):
        
        logger.info("Initializing PyGuardMiddleware with protected paths: %s", protected_paths)

        self.scanner = SecurityScanner(
            protected_paths=protected_paths,
            max_attempts = brute_force_config.get("max_attempts", 5),
            window_seconds = brute_force_config.get("window_seconds", 60),
            block_seconds= brute_force_config.get("block_seconds", 300),
        )
        logger.info("PyGuardMiddleware initialized successfully")

    def before_request(self, request):

        logger.info( 
            "Scanning request: %s %s from %s", 
            request.method, 
            request.path, 
            request.source
        )
        
        result = self.scanner.scan(request)

        if result.blocked:
            raise RequestBlocked(result.reason)

        return request