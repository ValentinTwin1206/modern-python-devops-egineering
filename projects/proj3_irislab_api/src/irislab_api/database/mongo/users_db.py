"""User collection operations."""

from typing import Any

from bson    import ObjectId
from pymongo import MongoClient

from ..models.users import UserDocument
from .generic_db    import MongoDB


class UsersDB(MongoDB):
    def __init__(self, client: MongoClient | None = None):
        super().__init__("users", client)

    def ensure_indexes(self) -> None:
        """
        Ensure that the necessary indexes exist on the users collection.

        :param self: The instance of the UsersDB class
        """
        self.collection.create_index("subject", unique=True)

    def get_one(self, query: dict[str, Any]) -> UserDocument | None:
        """
        Get a single user document from the users collection.

        :param self: The instance of the UsersDB class
        :param query (dict[str, Any]) The query to find the user document
        :return (UserDocument | None) The found user document or None if not found
        """
        document = super().get_one(query)
        return UserDocument.model_validate(document) if document else None

    def get_multiple(self, query: dict[str, Any] | None = None) -> list[UserDocument]:
        """
        Get multiple user documents from the users collection.

        :param self: The instance of the UsersDB class
        :param query (dict[str, Any] | None) The query to find the user documents (optional)
        :return (list[UserDocument]) The list of found user documents
        """
        return [UserDocument.model_validate(document) for document in super().get_multiple(query)]

    def get_or_create(self, subject: str) -> UserDocument:
        """
        Get or create a user document based on the subject.

        :param self: The instance of the UsersDB class
        :param subject (str) The subject of the user
        :return (UserDocument) The found or newly created user document
        """
        new_user = UserDocument(subject=subject)
        self.collection.update_one(
            {"subject": subject},
            {"$setOnInsert": new_user.model_dump(by_alias=True)},
            upsert=True,
        )
        document = self.collection.find_one({"subject": subject})
        return UserDocument.model_validate(document)

    def add_analysis_id(self, subject: str, analysis_id: ObjectId) -> None:
        """
        Add an analysis ID to the user's analyses list.

        :param self: The instance of the UsersDB class
        :param subject (str) The subject of the user
        :param analysis_id (ObjectId) The analysis ID to add
        """
        result = self.collection.update_one(
            {"subject": subject}, {"$addToSet": {"analyses": analysis_id}}
        )
        if result.matched_count != 1:
            raise RuntimeError("User document was not found")
