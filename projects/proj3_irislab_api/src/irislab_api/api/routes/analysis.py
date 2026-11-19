"""Image analysis and reference color endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from irislab.analyze import REFERENCE_COLORS, EyeColorDetectionError

<<<<<<< HEAD
from ...schemas.analysis  import AnalysisHistoryItem, AnalysisResult, ReferenceColor
from ...services.analysis import AnalysisService, AnalysisStorageError, InvalidImageError, UploadTooLargeError, get_analysis_service
=======
from ...schemas.analysis import AnalysisResult, ReferenceColor
from ...services.analysis import (
    AnalysisService,
    ContentRejectedError,
    InvalidImageError,
    ModerationUnavailableError,
    UploadTooLargeError,
)
>>>>>>> main

router = APIRouter()


@router.get("/reference-colors", response_model=list[ReferenceColor])
def reference_colors() -> tuple:
    return REFERENCE_COLORS


@router.get("/analyses", response_model=list[AnalysisHistoryItem])
def analysis_history(
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    request: Request,
) -> list[AnalysisHistoryItem]:
    try:
        return service.get_user_analyses(request.state.jwt_claims["sub"])
    except AnalysisStorageError as error:
        raise HTTPException(status_code=503, detail="Analysis storage is unavailable") from error


@router.post("/analyses", response_model=AnalysisResult)
def analyze_image(
    image: Annotated[UploadFile, File(description="PNG or JPEG portrait")],
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    request: Request,
) -> AnalysisResult:
    try:
<<<<<<< HEAD
        # Analyze the image and handle potential errors
        try:
            return service.analyze_and_store(
                image.file,
                request.state.jwt_claims["sub"],
                image.filename,
                image.content_type,
            )
        except UploadTooLargeError as error:
            raise HTTPException(status_code=413, detail=str(error)) from error
        except InvalidImageError as error:
            raise HTTPException(status_code=415, detail=str(error)) from error
        except EyeColorDetectionError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except FileNotFoundError as error:
            raise HTTPException(status_code=503, detail="IrisLab model is unavailable") from error
        except AnalysisStorageError as error:
            raise HTTPException(status_code=503, detail="Analysis storage is unavailable") from error
    
=======
        return service.analyze(image.file)
    except UploadTooLargeError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except InvalidImageError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except ContentRejectedError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except ModerationUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except EyeColorDetectionError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail="IrisLab model is unavailable") from error
>>>>>>> main
    finally:
        image.file.close()
