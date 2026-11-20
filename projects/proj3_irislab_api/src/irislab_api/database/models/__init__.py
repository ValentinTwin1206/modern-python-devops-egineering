"""Validated MongoDB document models."""

from typing import Annotated

from bson import ObjectId
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema


def _validate_object_id(value: object) -> ObjectId:
    """
    Validate and convert a value to a MongoDB ObjectId.

    :param value (object) The value to validate and convert
    :return (ObjectId) The validated ObjectId
    """

    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    
    raise ValueError("Invalid MongoDB ObjectId")


# Annotated type for MongoDB ObjectId fields in Pydantic models.
MongoObjectId = Annotated[
    ObjectId,
    BeforeValidator(_validate_object_id),
    PlainSerializer(str, return_type=str, when_used="json"),
    WithJsonSchema({"type": "string", "format": "objectid"}),
]
