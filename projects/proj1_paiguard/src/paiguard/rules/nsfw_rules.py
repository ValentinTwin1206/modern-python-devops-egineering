"""NSFW moderation rules."""

from ..models import FalconsaiNsfwModel
from .base import PaiDetectionRule


class PaiNsfwDetection(PaiDetectionRule):
    """Rule to detect NSFW / explicit content."""

    category = "nsfw"

    def __init__(self, threshold: float = 0.80, review_threshold=None, model=None):
        super().__init__(threshold, review_threshold, model)

    def create_default_model(self):
        return FalconsaiNsfwModel()
