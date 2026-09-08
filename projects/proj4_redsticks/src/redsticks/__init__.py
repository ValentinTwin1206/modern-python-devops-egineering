"""redsticks: lipstick shade suggestions from eye-color images."""

from .suggest import SuggestionResult, UnsupportedImageError, suggest

__all__ = ["SuggestionResult", "UnsupportedImageError", "suggest"]
