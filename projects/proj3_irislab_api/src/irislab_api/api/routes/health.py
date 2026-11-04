"""Liveness and readiness endpoints."""

from fastapi import APIRouter, HTTPException
from irislab.iris import model_path

router = APIRouter()


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready")
def ready() -> dict[str, str]:
    path = model_path()
    if not path.is_file() or path.stat().st_size == 0:
        raise HTTPException(status_code=503, detail="IrisLab model is unavailable")
    return {"status": "ready"}
