"""Result types returned by the rules and by pAIguard."""

from pydantic import BaseModel


class RuleResult(BaseModel):
    """The outcome of one rule for one image."""

    rule: str
    category: str
    score: float
    detected: bool
    needs_review: bool = False
    details: dict = {}


class InspectionResult(BaseModel):
    """The combined outcome of all rules for one image."""

    decision: str  # "allow", "review" or "block"
    results: list[RuleResult] = []

    @property
    def is_safe(self) -> bool:
        """True when no rule asked for a block or a review."""
        return self.decision == "allow"

    @property
    def violations(self) -> list[str]:
        """Categories of all rules that asked for a block or a review."""
        categories = []
        for result in self.results:
            if result.detected or result.needs_review:
                categories.append(result.category)
        return categories
