"""Base classes shared by pAIguard's moderation rules."""

from abc import ABC, abstractmethod

from PIL import Image

from ..results import RuleResult


class PaiRule(ABC):
    """Abstract base class for all pAIguard rules."""

    @abstractmethod
    def inspect(self, image: Image.Image) -> RuleResult:
        """Inspect the image and return the result of this rule."""
        raise NotImplementedError


class PaiDetectionRule(PaiRule):
    """
    Shared behavior of the model-based rules.

    A score at or above `threshold` marks the image as detected (block).
    A score at or above `review_threshold` marks it for review.
    """


    @property
    @abstractmethod
    def category(self) -> str:
        """Return the stable category name used in results and violations."""
        raise NotImplementedError

    def __init__(
        self,
        threshold: float,
        review_threshold: float | None = None,
        model=None,
    ):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")

        if review_threshold is not None and review_threshold > threshold:
            raise ValueError("review_threshold must not be above threshold")

        self.threshold = threshold
        self.review_threshold = review_threshold
        self.model = model or self.create_default_model()

    @abstractmethod
    def create_default_model(self):
        """Return the model used when the caller does not pass one."""
        raise NotImplementedError

    def inspect(self, image: Image.Image) -> RuleResult:
        score = self.model.score(image)

        detected = score >= self.threshold

        needs_review = False
        if not detected and self.review_threshold is not None:
            needs_review = score >= self.review_threshold

        return RuleResult(
            rule=type(self).__name__,
            category=self.category,
            score=score,
            detected=detected,
            needs_review=needs_review,
            details={
                "threshold": self.threshold,
                "review_threshold": self.review_threshold,
                "model": type(self.model).__name__,
            },
        )
