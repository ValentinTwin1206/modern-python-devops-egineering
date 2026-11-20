"""Analysis collection operations."""

from typing import Any

from bson    import ObjectId
from pymongo import MongoClient

from ..models.analysis import AnalysisDocument
from .generic_db       import MongoDB


class AnalysisDB(MongoDB):
    def __init__(self, client: MongoClient | None = None):
        super().__init__("analyses", client)

    def create_one(self, document: AnalysisDocument) -> ObjectId:
        return super().create_one(AnalysisDocument.model_validate(document))

    def get_one(self, query: dict[str, Any]) -> AnalysisDocument | None:
        document = super().get_one(query)
        return AnalysisDocument.model_validate(document) if document else None

    def get_multiple(self, query: dict[str, Any] | None = None) -> list[AnalysisDocument]:
        return [AnalysisDocument.model_validate(document) for document in super().get_multiple(query)]
