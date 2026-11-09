"""Narrow delivery failures, distinct from invalid analysis or saved artifacts.

Clients may raise these only for a known request rejection or a confirmed-ended
request without a complete answer. Unknown process state and integrity errors
must retain their own failure types.
"""


class ModelRequestFailure(ValueError):
    """A model request ended or was rejected without a usable complete answer."""


class InputTooLarge(ModelRequestFailure):
    """The complete delivery exceeds the known interface character limit."""
