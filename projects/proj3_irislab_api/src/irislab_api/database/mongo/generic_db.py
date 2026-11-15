"""Small synchronous MongoDB collection wrapper."""

import os
from collections.abc import Mapping
from typing          import Any

from bson     import ObjectId
from pydantic import BaseModel
from pymongo  import MongoClient


class MongoDB:
    """A small synchronous MongoDB collection wrapper."""

    def __init__(self, collection_name: str, client: MongoClient | None = None):
        """
        Constructor for the MongoDB class.
        
        :param self: The instance of the MongoDB class
        :param collection_name (str) The name of the MongoDB collection
        :param client (MongoClient | None) The MongoClient instance to use (optional)
        """
        self.client     = client
        self.database   = self.client[os.environ["MONGODB_DATABASE"]]
        self.collection = self.database[collection_name]

    def create_one(self, document: BaseModel | Mapping[str, Any]) -> ObjectId:
        """
        Create a single document in the MongoDB collection.

        :param self: The instance of the MongoDB class
        :param document (BaseModel | Mapping[str, Any]) The document to insert
        :return (ObjectId) The ObjectId of the inserted document
        """
        data = document.model_dump(by_alias=True) if isinstance(document, BaseModel) else dict(document)
        return self.collection.insert_one(data).inserted_id

    def get_one(self, query: Mapping[str, Any]) -> dict[str, Any] | None:
        """
        Get a single document from the MongoDB collection.

        :param self: The instance of the MongoDB class
        :param query (Mapping[str, Any]) The query to find the document
        :return (dict[str, Any] | None) The found document or None if not found
        """
        return self.collection.find_one(dict(query))

    def get_multiple(self, query: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Get multiple documents from the MongoDB collection.

        :param self: The instance of the MongoDB class
        :param query (Mapping[str, Any] | None) The query to find the documents (optional)
        :return (list[dict[str, Any]]) The list of found documents
        """
        return list(self.collection.find(dict(query or {})))

    def delete_one(self, query: Mapping[str, Any]) -> None:
        """
        Delete a single document from the MongoDB collection.

        :param self: The instance of the MongoDB class
        :param query (Mapping[str, Any]) The query to find the document to delete
        """
        self.collection.delete_one(dict(query))
