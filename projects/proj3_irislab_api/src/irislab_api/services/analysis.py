"""Validate uploads and adapt IrisLab's path-based API."""

import base64
import logging
from io       import BytesIO
from pathlib  import Path
from tempfile import TemporaryDirectory
from time     import perf_counter
from typing   import BinaryIO

from bson         import ObjectId
from fastapi      import Request
from gridfs       import GridFSBucket
from irislab      import analyze
from irislab.iris import model_path
from PIL          import Image, UnidentifiedImageError

from ..database.models.analysis   import AnalysisDocument
from ..database.mongo.analysis_db import AnalysisDB
from ..database.mongo.users_db    import UsersDB
from ..schemas.analysis           import AnalysisHistoryItem, AnalysisResult

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
logger = logging.getLogger("iris-lab")


class InvalidImageError(ValueError):
    """The upload is not a supported image."""


class UploadTooLargeError(ValueError):
    """The upload exceeds the size limit."""


class AnalysisStorageError(RuntimeError):
    """The analysis result could not be persisted."""


class AnalysisService:
    def __init__(
        self,
        gridfs: GridFSBucket,
        users_db: UsersDB,
        analysis_db: AnalysisDB,
    ):
        self.gridfs = gridfs
        self.users_db = users_db
        self.analysis_db = analysis_db

    def analyze(self, upload: BinaryIO) -> AnalysisResult:
        data = upload.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise UploadTooLargeError("Image exceeds the 10 MiB upload limit")

        try:
            with Image.open(BytesIO(data)) as image:
                if image.format not in {"PNG", "JPEG"}:
                    raise InvalidImageError("Only PNG and JPEG images are supported")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise InvalidImageError("Image exceeds the 20 megapixel limit")
                suffix = ".png" if image.format == "PNG" else ".jpg"
                image.verify()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
            raise InvalidImageError("Invalid PNG or JPEG image") from error

        path = model_path()
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError("IrisLab model is unavailable")
        with TemporaryDirectory(prefix="irislab-") as directory:
            path = Path(directory) / f"upload{suffix}"
            path.write_bytes(data)
            return AnalysisResult.model_validate(analyze(path, device="cpu"))

    def analyze_and_store(
        self,
        upload: BinaryIO,
        subject: str,
        filename: str | None,
        content_type: str | None,
    ) -> AnalysisResult:
        """
        Analyze an uploaded image and store the result in the database.
        
        :param self: Description
        :param upload (BinaryIO) The uploaded image file
        :param subject (str) The subject identifier
        :param filename (str | None) The name of the uploaded file
        :param content_type (str | None) The MIME type of the uploaded file
        :return (AnalysisResult) The result of the analysis
        """

        started_at = perf_counter()
        logger.info("Image analysis started (content_type=%s)", content_type)
        try:
            result = self.analyze(upload)
        except Exception:
            logger.exception(
                "Image analysis failed (content_type=%s, elapsed_ms=%.1f)",
                content_type,
                (perf_counter() - started_at) * 1000,
            )
            raise

        logger.info(
            "Image analysis completed (elapsed_ms=%.1f)",
            (perf_counter() - started_at) * 1000,
        )

        file_id: ObjectId | None = None
        analysis_id: ObjectId | None = None
        user_id: ObjectId | None = None
        persistence_started_at = perf_counter()

        # Persist the analysis result and handle potential errors
        try:

            # Get or create the user document and store the analysis result
            user = self.users_db.get_or_create(subject)
            user_id = user.id
            logger.info("Resolved analysis owner (user_id=%s)", user_id)
            
            # Store the uploaded image in GridFS and create an analysis document
            upload.seek(0)
            file_id = self.gridfs.upload_from_stream(
                filename or "upload",
                upload,
                metadata={"content_type": content_type, "user_id": user.id},
            )
            logger.info("Stored analysis image in GridFS (file_id=%s)", file_id)

            # Create an analysis document and store it in the database
            document    = AnalysisDocument(user_id=user.id, image_id=file_id, result=result)
            analysis_id = self.analysis_db.create_one(document)
            logger.info(
                "Created analysis document (analysis_id=%s, user_id=%s)",
                analysis_id,
                user_id,
            )
            
            # Add the analysis ID to the user's document
            self.users_db.add_analysis_id(subject, analysis_id)
            logger.info(
                "Linked analysis to user (analysis_id=%s, user_id=%s, persistence_ms=%.1f)",
                analysis_id,
                user_id,
                (perf_counter() - persistence_started_at) * 1000,
            )

        except Exception as error:
            # Clean up any partially persisted data and log the error
            if analysis_id is not None:
                try:
                    self.analysis_db.delete_one({"_id": analysis_id})
                except Exception:
                    logger.exception("Failed to clean up analysis %s", analysis_id)

            # Clean up the uploaded file in GridFS if it was created
            if file_id is not None:
                try:
                    self.gridfs.delete(file_id)
                except Exception:
                    logger.exception("Failed to clean up GridFS file %s", file_id)
            logger.exception(
                "Failed to persist image analysis (user_id=%s, file_id=%s, analysis_id=%s, persistence_ms=%.1f)",
                user_id,
                file_id,
                analysis_id,
                (perf_counter() - persistence_started_at) * 1000,
            )
            raise AnalysisStorageError("Analysis storage is unavailable") from error
        
        return result

    def get_user_analyses(self, subject: str) -> list[AnalysisHistoryItem]:
        """
        Get the analysis history for a user.

        :param self: The analysis service instance
        :param subject (str) The subject identifier of the user
        :return (list[AnalysisHistoryItem]) A list of analysis history items for the user
        """
        try:
            # Retrieve the user document based on the subject
            user = self.users_db.get_one({"subject": subject})
            if user is None:
                return []

            history = []
            # Iterate through the user's analyses
            for analysis_id in user.analyses:
                document = self.analysis_db.get_one({"_id": analysis_id})
                if document is None:
                    continue
                # Retrieve the associated image from GridFS
                with self.gridfs.open_download_stream(document.image_id) as image:
                    metadata = image.metadata or {}
                    history.append(
                        AnalysisHistoryItem(
                            id=str(document.id),
                            result=document.result,
                            image_base64=base64.b64encode(image.read()).decode("ascii"),
                            filename=image.filename,
                            content_type=metadata.get("content_type"),
                            created_at=document.created_at,
                        )
                    )
            return history
        except Exception as error:
            logger.exception("Failed to retrieve analysis history")
            raise AnalysisStorageError("Analysis storage is unavailable") from error


def get_analysis_service(request: Request) -> AnalysisService:
    """Build the request's analysis service from lifespan-managed resources."""
    return AnalysisService(
        request.app.state.gridfs,
        request.app.state.users_db,
        request.app.state.analysis_db,
    )
