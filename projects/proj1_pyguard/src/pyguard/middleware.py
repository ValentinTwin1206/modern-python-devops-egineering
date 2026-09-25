from .exceptions import RequestBlocked
from .scanner import SecurityScanner
from . import logger

class PyGuardMiddleware:

    def __init__(self, protected_paths=None):
        
        logger.info("Initializing PyGuardMiddleware with protected paths: %s", protected_paths)

        self.scanner = SecurityScanner(
            protected_paths=protected_paths,
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