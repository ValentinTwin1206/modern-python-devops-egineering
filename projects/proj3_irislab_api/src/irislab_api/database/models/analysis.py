"""Pydantic schema for persisted analysis documents."""

from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from ...schemas.analysis import AnalysisResult
from . import MongoObjectId


class AnalysisDocument(BaseModel):
    """
    The AnalysisDocument class represents an analysis document in the MongoDB collection. 
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: MongoObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: MongoObjectId
    image_id: MongoObjectId
    result: AnalysisResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
