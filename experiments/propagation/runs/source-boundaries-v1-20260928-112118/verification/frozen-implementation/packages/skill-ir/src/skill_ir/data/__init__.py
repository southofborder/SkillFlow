"""Unified data descriptions, with no model calls or propagation runtime."""

from .models import (
    Annotations, Content, Data, DataPart, Dependency, FieldUpdatesContent, KnownPartsContent,
    LiteralContent, OpaqueContent, Origin, Path, PathStep, WholeExceptContent,
)
from .registry import (
    SCHEMA_VERSION, DataConflictError, DataReferenceError, DataRegistry,
    DataRegistryError, export_identity_index, restore_registry, validate_data_records,
)

__all__ = [
    "Annotations", "Content", "Data", "DataPart", "Dependency", "FieldUpdatesContent", "KnownPartsContent",
    "LiteralContent", "OpaqueContent", "Origin", "Path", "PathStep", "WholeExceptContent",
    "SCHEMA_VERSION", "DataConflictError", "DataReferenceError", "DataRegistry", "DataRegistryError",
    "export_identity_index", "restore_registry", "validate_data_records",
]
