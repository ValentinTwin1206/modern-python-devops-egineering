"""Violence moderation rules."""

from ..models import SiglipViolenceModel
from .base import PaiDetectionRule


class PaiViolenceDetection(PaiDetectionRule):
    """Rule to detect violent content."""

    category = "violence"

    def __init__(self, threshold: float = 0.85, review_threshold=None, model=None):
        super().__init__(threshold, review_threshold, model)

    def create_default_model(self):
        return SiglipViolenceModel()
