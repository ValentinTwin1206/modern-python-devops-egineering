"""The ``PaiGuard`` class runs pAIguard's configured rules and decides the outcome."""

import logging

from PIL import Image

from .results import InspectionResult, RuleResult
from .rules import PaiRule

logger = logging.getLogger("paiguard")


def decide(results: list[RuleResult]) -> str:
    """
    Turn the rule results into one decision.

    :param results (list[RuleResult]): The results of all rules
    :return (str): "block", "review" or "allow"
    """
    for result in results:
        if result.detected:
            return "block"

    for result in results:
        if result.needs_review:
            return "review"

    return "allow"


class PaiGuard:
    def __init__(self, rules: list[PaiRule] | None = None):
        self.rules = rules or []

    def inspect(self, image: Image.Image) -> InspectionResult:
        """
        Inspect the given image with all configured rules.

        The image must already be decoded. Validating and decoding uploads is
        the job of the calling application.

        :param image (Image.Image): The decoded image
        :return (InspectionResult): The decision and the result of each rule
        """
        if not isinstance(image, Image.Image):
            raise TypeError("PaiGuard.inspect() expects a PIL.Image.Image")

        # The models expect three color channels.
        if image.mode != "RGB":
            image = image.convert("RGB")

        results = []
        for rule in self.rules:
            result = rule.inspect(image)
            results.append(result)

        decision = decide(results)

        if decision != "allow":
            scores = {result.category: round(result.score, 3) for result in results}
            logger.warning("Image decision is '%s' with scores %s", decision, scores)

        return InspectionResult(decision=decision, results=results)
