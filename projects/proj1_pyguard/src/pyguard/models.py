from pydantic import BaseModel


class Request(BaseModel):
    method: str
    path: str
    query: str  = ""
    body: str   = ""
    source: str = ""
    status_code: int | None = None


class ScanResult(BaseModel):
    blocked: bool
    reason: str = ""