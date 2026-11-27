"""The ``PaiGuard`` class runs pAIguard's configured rules and decides the outcome."""

import logging

from PIL import Image

from .results import InspectionResult, RuleResult
from .rules.base import PaiRule

logger = logging.getLogger("paiguard")


class PaiGuard:
    #
    # TODO: Implement a valid constructor "def __init__" for the PaiGuard class 
    # that is used by other projects as the public interface:
    #   - Set a "rules" input argument of type "list[PaiRule] | None" with a default of None.
    #   - Initialize a "self.rules" class property with "rules or []"

    @staticmethod
    def _decide(results: list[RuleResult]) -> str:
        """Turn rule results into one decision: block, review, or allow."""
        for result in results:
            if result.detected:
                return "block"

        for result in results:
            if result.needs_review:
                return "review"

        return "allow"

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

        decision = self._decide(results)

        if decision != "allow":
            scores = {result.category: round(result.score, 3) for result in results}
            logger.warning("Image decision is '%s' with scores %s", decision, scores)

        return InspectionResult(decision=decision, results=results)
