from dataclasses import dataclass


@dataclass
class Request:
    method: str
    path: str
    query: str = ""
    body: str = ""


@dataclass
class ScanResult:
    blocked: bool
    reason: str = ""