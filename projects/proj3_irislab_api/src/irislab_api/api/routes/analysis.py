"""Image analysis and reference color endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from irislab.analyze import REFERENCE_COLORS, EyeColorDetectionError

from ...schemas.analysis import AnalysisResult, ReferenceColor
from ...services.analysis import AnalysisService, InvalidImageError, UploadTooLargeError

router = APIRouter()


@router.get("/reference-colors", response_model=list[ReferenceColor])
def reference_colors() -> tuple:
    return REFERENCE_COLORS


@router.post("/analyses", response_model=AnalysisResult)
def analyze_image(
    image: Annotated[UploadFile, File(description="PNG or JPEG portrait")],
    service: Annotated[AnalysisService, Depends()],
) -> AnalysisResult:
    try:
        return service.analyze(image.file)
    except UploadTooLargeError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except InvalidImageError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except EyeColorDetectionError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail="IrisLab model is unavailable") from error
    finally:
        image.file.close()
