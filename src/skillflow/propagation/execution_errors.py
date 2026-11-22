"""Narrow abstract-operand failures, distinct from implementation invariants."""
from copy import deepcopy

from skillflow.propagation.data import DataConflictError


class OperandDomainError(DataConflictError):
    """A checked operand has an incompatible structural domain."""


class OperationExecutionError(DataConflictError):
    """A located domain failure with detached evidence from its failed attempt."""

    def __init__(self, error, *, position, input_data_ids, input_data, observed_operations):
        super().__init__(str(error))
        self.diagnostic = {
            "code": "operation_execution_error", **position,
            "reason": str(error), "error_type": type(error).__name__,
            "input_data_ids": sorted(input_data_ids),
            "observed_data": deepcopy(input_data),
            "observed_operations": deepcopy(observed_operations),
        }
