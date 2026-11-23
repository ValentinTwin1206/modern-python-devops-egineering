"""Public user management schemas."""

from pydantic import BaseModel, SecretStr


class UserCreate(BaseModel):
    username: str
    password: SecretStr


class UserSummary(BaseModel):
    id: str
    username: str
    enabled: bool
    roles: list[str]


class UserReference(BaseModel):
    id: str
    username: str
