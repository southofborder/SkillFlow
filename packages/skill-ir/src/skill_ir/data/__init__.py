"""Unified data descriptions, with no model calls or propagation runtime."""

from .models import (
    Annotations, Content, Data, DataPart, Dependency, ElementStep, FieldUpdatesContent, KnownPartsContent,
    LiteralContent, OpaqueContent, Origin, Path, PathStep, SubsetViewContent, WholeExceptContent,
)
from .registry import (
    SCHEMA_VERSION, DataConflictError, DataReferenceError, DataRegistry,
    DataRegistryError, export_identity_index, restore_registry, validate_data_records, validate_element_membership,
    is_definitely_empty_collection,
)

__all__ = [
    "Annotations", "Content", "Data", "DataPart", "Dependency", "ElementStep", "FieldUpdatesContent", "KnownPartsContent",
    "LiteralContent", "OpaqueContent", "Origin", "Path", "PathStep", "SubsetViewContent", "WholeExceptContent",
    "SCHEMA_VERSION", "DataConflictError", "DataReferenceError", "DataRegistry", "DataRegistryError",
    "export_identity_index", "restore_registry", "validate_data_records", "validate_element_membership",
    "is_definitely_empty_collection",
]
