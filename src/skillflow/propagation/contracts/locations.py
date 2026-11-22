"""Explicit address uncertainty, independent of value-content uncertainty.

Names identify sources. They are not a second language for declaring aliases.
The current profile identity owns this policy; old prefixed declarations need
an explicit policy before they can be accepted under that identity.
"""
from typing import Literal

from pydantic import model_serializer, model_validator

from skillflow.propagation.contracts.values import StrictSpec, Text


AddressKind = Literal["identified", "unidentified"]


class AddressPolicy(StrictSpec):
    address_kind: AddressKind = "identified"
    address_reason: Text | None = None

    @model_validator(mode="before")
    @classmethod
    def explicit_legacy_address_policy(cls, value):
        if (isinstance(value, dict) and isinstance(value.get("name"), str)
                and value["name"].startswith("symbolic:") and "address_kind" not in value):
            raise ValueError("A symbolic: location name requires explicit address_kind: identified for a known source with unknown content, or unidentified for an unknown address with a specific address_reason and source evidence")
        return value

    @model_validator(mode="after")
    def explained_address_uncertainty(self):
        if self.address_kind == "unidentified" and self.address_reason is None:
            raise ValueError("An unidentified address requires a specific address_reason explaining which address relation is unknown; unknown content alone is insufficient")
        if self.address_kind == "identified" and self.address_reason is not None:
            raise ValueError("address_reason describes unidentified-address uncertainty; identified locations omit it")
        return self

    @model_serializer(mode="wrap")
    def omit_default_address_policy(self, handler):
        result = handler(self)
        if self.address_kind == "identified" and not result.get("name", "").startswith("symbolic:"):
            result.pop("address_kind", None)
        if self.address_reason is None:
            result.pop("address_reason", None)
        return result


def address_is_unknown(location) -> bool:
    """Use a checked declaration's explicit policy, never its name's spelling."""
    if hasattr(location, "address_kind"):
        return location.address_kind == "unidentified"
    if hasattr(location, "model_dump"):
        location = location.model_dump(mode="json")
    kind = location.get("address_kind", "identified")
    if kind not in {"identified", "unidentified"}:
        raise ValueError("Unsupported location address_kind")
    if location.get("name", "").startswith("symbolic:") and "address_kind" not in location:
        raise ValueError("Ambiguous legacy location requires explicit address_kind")
    return kind == "unidentified"


def locations_may_alias(left, right) -> bool:
    """An unidentified address may overlap any declared address of its kind."""
    left = left.model_dump(mode="json") if hasattr(left, "model_dump") else left
    right = right.model_dump(mode="json") if hasattr(right, "model_dump") else right
    return left["kind"] == right["kind"] and (
        left["name"] == right["name"] or address_is_unknown(left) or address_is_unknown(right))


def require_address_source_evidence(location, evidences) -> None:
    """Check provenance shape only; review still checks the stated relation."""
    if not address_is_unknown(location):
        return
    if not any((getattr(item, "file", None) if not isinstance(item, dict) else item.get("file"))
               for item in evidences):
        raise ValueError("An unidentified address requires physical source evidence for address uncertainty; a runtime rule alone does not establish an unknown address")
