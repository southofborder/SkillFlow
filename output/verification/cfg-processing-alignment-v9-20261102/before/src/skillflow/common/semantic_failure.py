"""A validated model task failure, distinct from malformed output or transport."""
from __future__ import annotations

from copy import deepcopy


class SemanticFailure(ValueError):
    """Raised only after a stage validates its cannot_assess response and evidence.

    The reason is the model's declared limitation, not a proof that a task is
    impossible. Callers must not turn this into a successful empty finding list.
    """

    def __init__(self, failure: dict):
        self.failure = deepcopy(failure)
        self.reason = failure["reason"]
        super().__init__(self.reason)
