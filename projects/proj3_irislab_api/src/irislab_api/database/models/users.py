"""Pydantic schema for user documents."""

from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from . import MongoObjectId


class UserDocument(BaseModel):
    """
    The UserDocument class represents a user document in the MongoDB collection. 
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: MongoObjectId = Field(default_factory=ObjectId, alias="_id")
    subject: str
    analyses: list[MongoObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
