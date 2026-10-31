"""Public JSON representations of IrisLab results."""

from pydantic import BaseModel, ConfigDict


class ReferenceColor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    eye_color: str
    rgb: tuple[int, int, int]


class AnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    eye_color: str
    eye_rgb: tuple[int, int, int]
    lab: tuple[float, float, float]
    hsv: tuple[float, float, float]
    chroma: float
    hue: float
    closest_profile: str
    profile_rgb: tuple[int, int, int]
    delta_e: float
    source: str
    confidence: float
    eyes_detected: int
