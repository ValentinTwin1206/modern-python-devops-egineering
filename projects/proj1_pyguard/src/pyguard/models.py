from pydantic import BaseModel


class Request(BaseModel):
    method: str
    path: str
    query: str = ""
    body: str = ""
    source: str = ""


class ScanResult(BaseModel):
    blocked: bool
    reason: str = ""