"""NSFW moderation rules."""

# TODO: Implement `PaiNsfwDetection` as a `PaiDetectionRule` subclass:
#   - Import `PaiDetectionRule` from `.base` and `FalconsaiNsfwModel` from
#     `..models`.
#   - Add a class docstring describing NSFW / explicit-content detection.
#   - Implement the abstract `category` property to return `"nsfw"`.
#   - Define `__init__(self, threshold: float = 0.80, review_threshold=None,
#     model=None)` and pass these arguments to `super().__init__` in order.
#   - Implement `create_default_model(self)` to return `FalconsaiNsfwModel()`;
#     this model is used when the caller does not provide a custom model.
