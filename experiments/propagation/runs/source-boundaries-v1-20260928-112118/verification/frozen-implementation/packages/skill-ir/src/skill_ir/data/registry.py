"""Identity and description updates; no execution or propagation semantics.

All mutations are transactional and every public record is detached from the
registry.  A caller supplies the meaning of a processing result, never an opcode
for this module to interpret.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field, TypeAdapter, model_validator

from .models import (
    Annotations, Content, Data, DataPart, FieldUpdatesContent, KnownPartsContent, LiteralContent,
    OpaqueContent, Origin, Path, StrictRecord, Text, WholeExceptContent, path_key,
)

SCHEMA_VERSION = "skillflow-data-v3"
_TEXT = TypeAdapter(Text)
_PATH = TypeAdapter(Path)


class DataRegistryError(ValueError):
    """The supplied descriptions violate the registry's structural contract."""


class DataConflictError(DataRegistryError):
    """An update would overwrite a different identity or established fact."""


class DataReferenceError(DataRegistryError):
    """A data reference or requested part is missing or excluded."""


class _MissingPart(DataReferenceError):
    """No registered identity is known, without asserting absence."""


class _ExcludedPart(DataReferenceError):
    """An explicit exclusion prevents returning the unfiltered data."""


class _ClosedPart(DataReferenceError):
    """The request conflicts with a literal or a closed composition."""


def _list_only(value: object) -> object:
    if type(value) is not list:
        raise ValueError("expected a list")
    return value


class _Identity(StrictRecord):
    kind: Literal["source", "result", "part"]
    key: Text | None = None
    parent_id: Text | None = None
    path: Path | None = None

    @model_validator(mode="after")
    def consistent_identity(self) -> "_Identity":
        if self.kind == "part":
            if self.key is not None or self.parent_id is None or self.path is None:
                raise ValueError("part identity requires only parent_id and path")
        elif self.key is None or self.parent_id is not None or self.path is not None:
            raise ValueError("source/result identity requires only key")
        return self


class _Entry(StrictRecord):
    identity: _Identity
    data: Data


class _Snapshot(StrictRecord):
    schema_version: Literal["skillflow-data-v3"]
    namespace: Text
    records: Annotated[list[_Entry], BeforeValidator(_list_only)]


class _IdentityIndex(StrictRecord):
    schema_version: Literal["skillflow-data-v3"]
    namespace: Text
    identities: dict[Text, _Identity]


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _equal(left: object, right: object) -> bool:
    # Python equality collapses True/1 and 1/1.0; JSON identity must not.
    return _canonical(left) == _canonical(right)


def _union(left: list[str], right: list[str]) -> list[str]:
    return list(dict.fromkeys([*left, *right]))


def _prefix(left: list[str | int], right: list[str | int]) -> bool:
    return len(left) <= len(right) and left == right[:len(left)]


def _annotations_merge(old: Annotations, new: Annotations) -> Annotations:
    if old.description is not None and new.description not in (None, old.description):
        raise DataConflictError("description conflicts; refinement cannot overwrite it")
    return Annotations(
        description=old.description if old.description is not None else new.description,
        sensitivity=_union(old.sensitivity, new.sensitivity),
        evidences=_union(old.evidences, new.evidences),
    )


def _parts_merge(old: Content, incoming: KnownPartsContent) -> KnownPartsContent:
    if isinstance(old, OpaqueContent):
        return incoming.model_copy(deep=True)
    if not isinstance(old, KnownPartsContent):
        raise DataConflictError("only opaque/known_parts content accepts part refinement")
    merged = {path_key(item.path): item for item in old.parts}
    for item in incoming.parts:
        key = path_key(item.path)
        existing = merged.get(key)
        if existing is not None and existing.data != item.data:
            raise DataConflictError(f"part {item.path!r} already refers to different data")
        if existing is None and old.parts_complete:
            raise DataConflictError("cannot add a part to a complete composition")
        merged[key] = item
    return KnownPartsContent(
        parts=list(merged.values()),
        parts_complete=old.parts_complete or incoming.parts_complete,
    )


def _content_merge(old: Content, new: Content) -> Content:
    if isinstance(new, OpaqueContent):
        # Re-registering an initially opaque source must not erase refinements.
        return old
    if isinstance(new, KnownPartsContent):
        if isinstance(old, KnownPartsContent) and new.parts_complete:
            declared = {path_key(item.path): item.data for item in new.parts}
            if any(declared.get(path_key(item.path)) != item.data for item in old.parts):
                raise DataConflictError("complete replacement omits previously known parts")
        return _parts_merge(old, new)
    if _equal(old.model_dump(mode="python"), new.model_dump(mode="python")):
        return old
    raise DataConflictError("content changed; register a new processing result instead")


class DataRegistry:
    """One namespace of Data identities and additive description refinements.

    ``key`` is a stable acquisition/output position supplied by the caller.  The
    namespace and identity, not the contents, determine a SHA-256 data ID.  This
    is not an allocation-site propagation engine or a loop solver.
    """

    def __init__(self, namespace: str):
        self._namespace = _TEXT.validate_python(namespace, strict=True)
        self._records: dict[str, _Entry] = {}
        self._revision = 0

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def revision(self) -> int:
        """Local descriptor-change counter, excluding pure record additions.

        The counter starts at zero on import; it is an invalidation aid, not a
        stored identity or an analysis iteration number. Adding a part changes
        its existing parent's description and therefore advances the counter.
        """
        return self._revision

    def __len__(self) -> int:
        return len(self._records)

    def _id(self, identity: _Identity) -> str:
        payload = [SCHEMA_VERSION, self._namespace, identity.model_dump(mode="python")]
        return "data_" + hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()

    def _entry(self, data_id: str) -> _Entry:
        _TEXT.validate_python(data_id, strict=True)
        try:
            return self._records[data_id]
        except KeyError as exc:
            raise DataReferenceError(f"unknown data ID: {data_id}") from exc

    def get(self, data_id: str) -> Data:
        """Return a detached description; mutating it cannot edit the registry."""
        return self._entry(data_id).data.model_copy(deep=True)

    def _commit(self, updates: dict[str, _Entry]) -> None:
        records = {**self._records, **updates}
        self._validate_records(records)
        if any(
            key in self._records and not _equal(
                self._records[key].data.model_dump(mode="python"),
                entry.data.model_dump(mode="python"),
            )
            for key, entry in updates.items()
        ):
            self._revision += 1
        self._records = records

    def _register(self, identity: _Identity, data: Data) -> Data:
        # Round-trip through strict models even for forged model_copy instances.
        incoming = _Entry.model_validate({"identity": identity, "data": data})
        data = incoming.data
        old = self._records.get(data.id)
        if old is not None:
            if old.identity != identity:
                raise DataConflictError("data ID collision between different identities")
            if not _equal(old.data.origin.model_dump(mode="python"),
                          data.origin.model_dump(mode="python")):
                raise DataConflictError("identity already has a different origin or input relation")
            data = Data(
                id=data.id, content=_content_merge(old.data.content, data.content),
                origin=old.data.origin, annotations=_annotations_merge(old.data.annotations, data.annotations),
            )
        self._commit({data.id: _Entry(identity=identity, data=data)})
        return self.get(data.id)

    def register_source(
        self, key: str, *, acquired_from: str, at: str | None = None,
        content: Content | None = None, annotations: Annotations | None = None,
    ) -> Data:
        identity = _Identity(kind="source", key=key)
        return self._register(identity, Data(
            id=self._id(identity), content=content if content is not None else OpaqueContent(),
            origin=Origin(at=at, acquired_from=acquired_from),
            annotations=annotations if annotations is not None else Annotations(),
        ))

    def create_result(
        self, key: str, *, content: Content, origin: Origin,
        annotations: Annotations | None = None,
    ) -> Data:
        identity = _Identity(kind="result", key=key)
        return self._register(identity, Data(
            id=self._id(identity), content=content, origin=origin,
            annotations=annotations if annotations is not None else Annotations(),
        ))

    def refine(
        self, data_id: str, *, parts: list[DataPart] | None = None,
        parts_complete: bool | None = None, annotations: Annotations | None = None,
    ) -> Data:
        """Add descriptions without changing identity, origin, or content extent."""
        old = self._entry(data_id)
        content = old.data.content
        if parts is not None or parts_complete is not None:
            if parts_complete is not None and type(parts_complete) is not bool:
                raise DataRegistryError("parts_complete must be a boolean")
            if isinstance(content, KnownPartsContent) and content.parts_complete and parts_complete is False:
                raise DataConflictError("cannot reopen a complete composition")
            incoming = KnownPartsContent(
                parts=parts if parts is not None else [], parts_complete=parts_complete is True,
            )
            content = _parts_merge(content, incoming)
        merged_annotations = old.data.annotations
        if annotations is not None:
            annotations = Annotations.model_validate(annotations)
            merged_annotations = _annotations_merge(merged_annotations, annotations)
        data = Data(id=data_id, content=content, origin=old.data.origin, annotations=merged_annotations)
        self._commit({data_id: _Entry(identity=old.identity, data=data)})
        return self.get(data_id)

    def _part_identity(self, parent_id: str, path: Path) -> _Identity:
        # Equivalent walks through registered *parts* share the root/path key.
        # A composed output referencing a source is not flattened into that
        # source merely because the source also appears in its contents.
        seen: set[str] = set()
        while True:
            parent = self._entry(parent_id).data
            if parent_id in seen:
                raise DataConflictError("cyclic part origins")
            seen.add(parent_id)
            if parent.origin.part_of is None:
                break
            path = [*parent.origin.path, *path]
            parent_id = parent.origin.part_of
        return _Identity(kind="part", parent_id=parent_id, path=path)

    def register_part(
        self, parent_id: str, path: Path, *, content: Content | None = None,
        annotations: Annotations | None = None,
    ) -> Data:
        path = _PATH.validate_python(path, strict=True)
        parent = self._entry(parent_id).data
        # Exclusions must be checked before consulting a potentially shared ID.
        try:
            existing_id = self._locate(self._records, parent_id, path, set())
        except _ClosedPart as exc:
            raise DataConflictError(str(exc)) from exc
        except _MissingPart:
            if isinstance(parent.content, (WholeExceptContent, FieldUpdatesContent, LiteralContent)):
                raise
            existing_id = None
        if existing_id is not None:
            old = self._entry(existing_id)
            return self._register(old.identity, Data(
                id=existing_id, content=content if content is not None else OpaqueContent(),
                origin=old.data.origin, annotations=annotations if annotations is not None else Annotations(),
            ))
        if not isinstance(parent.content, (OpaqueContent, KnownPartsContent)):
            raise DataConflictError("this content form cannot be refined into parts")
        if isinstance(parent.content, KnownPartsContent):
            # An existing enclosing part owns refinements below that position.
            prefixes = [p for p in parent.content.parts if len(p.path) < len(path) and _prefix(p.path, path)]
            if prefixes:
                prefix = max(prefixes, key=lambda p: len(p.path))
                return self.register_part(
                    prefix.data, path[len(prefix.path):], content=content,
                    annotations=annotations,
                )
        identity = self._part_identity(parent_id, path)
        data_id = self._id(identity)
        if data_id in self._records:
            raise DataConflictError("part identity exists without a consistent composition reference")
        part = Data(
            id=data_id, content=content if content is not None else OpaqueContent(),
            origin=Origin(part_of=identity.parent_id, path=identity.path),
            annotations=annotations if annotations is not None else Annotations(),
        )
        parent_content = _parts_merge(parent.content, KnownPartsContent(parts=[DataPart(path=path, data=data_id)]))
        updated_parent = Data(
            id=parent_id, content=parent_content, origin=parent.origin, annotations=parent.annotations,
        )
        self._commit({
            data_id: _Entry(identity=identity, data=part),
            parent_id: _Entry(identity=self._entry(parent_id).identity, data=updated_parent),
        })
        return self.get(data_id)

    @staticmethod
    def _locate(records: dict[str, _Entry], data_id: str, path: Path, seen: set[tuple]) -> str:
        return DataRegistry._locate_data({key: entry.data for key, entry in records.items()}, data_id, path, seen)

    @staticmethod
    def _locate_data(records: dict[str, Data], data_id: str, path: Path, seen: set[tuple]) -> str:
        marker = (data_id, path_key(path))
        if marker in seen:
            raise _MissingPart("part has no explicit composition reference")
        seen = {*seen, marker}
        try:
            data = records[data_id]
        except KeyError as exc:
            raise DataReferenceError(f"unknown data ID: {data_id}") from exc
        content = data.content
        if isinstance(content, FieldUpdatesContent):
            for update in content.updates:
                if _prefix(update.path, path):
                    suffix = path[len(update.path):]
                    return update.data if not suffix else DataRegistry._locate_data(records, update.data, suffix, seen)
                if _prefix(path, update.path):
                    raise _ExcludedPart("requested ancestor is partially updated; resolve its updated view explicitly")
            return DataRegistry._locate_data(records, content.base, path, seen)
        if isinstance(content, WholeExceptContent):
            for excluded in content.excluded_parts:
                if _prefix(excluded, path):
                    raise _ExcludedPart(f"requested part {path!r} is explicitly excluded")
                if _prefix(path, excluded):
                    raise _ExcludedPart("requested ancestor is partially excluded; define its filtered result explicitly")
            return DataRegistry._locate_data(records, content.base, path, seen)
        if isinstance(content, LiteralContent):
            raise _ClosedPart("literal contents do not declare separate part identities")
        if isinstance(content, KnownPartsContent):
            for part in content.parts:
                if part.path == path:
                    return part.data
            prefixes = [p for p in content.parts if len(p.path) < len(path) and _prefix(p.path, path)]
            if prefixes:
                prefix = max(prefixes, key=lambda p: len(p.path))
                return DataRegistry._locate_data(records, prefix.data, path[len(prefix.path):], seen)
            if content.parts_complete:
                raise _ClosedPart("part is not present in the complete composition")
        if data.origin.part_of is not None:
            return DataRegistry._locate_data(records, data.origin.part_of, [*data.origin.path, *path], seen)
        raise _MissingPart(f"part {path!r} is not explicitly registered; unknown does not mean absent")

    def get_part(self, data_id: str, path: Path) -> Data:
        """Resolve a registered, unexcluded part without interpreting operations.

        This is a structural lookup, not a statement that the part exists in
        every execution.  A partially filtered ancestor is never returned as
        its unfiltered base.
        """
        self._entry(data_id)
        path = _PATH.validate_python(path, strict=True)
        return self.get(self._locate(self._records, data_id, path, set()))

    def resolve_part(self, data_id: str, path: Path) -> Data:
        """Resolve a typed path, registering stable structural views as needed.

        Unknown parts refine their original base. Literal children and partial
        exclusion/overlay ancestors get explicit result views; they never
        expose an unfiltered ancestor. This interprets only the five content
        forms, not an opcode, a script, or a user-defined function. A failed
        resolution rolls back every intermediate refinement and its revision.
        """
        self._entry(data_id)
        path = _PATH.validate_python(path, strict=True)
        before, revision = self._records, self._revision
        try:
            return self._resolve_part(data_id, path, set())
        except Exception:
            self._records, self._revision = before, revision
            raise

    def _part_view(self, data_id: str, path: Path, content: Content) -> Data:
        source = self._entry(data_id).data
        key = "data-resolved-part:" + _canonical([data_id, path])
        return self.create_result(
            key, content=content,
            origin=Origin(
                at=source.origin.at or f"data:{data_id}/content",
                inputs=[data_id],
            ),
        )

    def _resolve_part(self, data_id: str, path: Path, seen: set[tuple]) -> Data:
        marker = (data_id, path_key(path))
        if marker in seen:
            raise DataReferenceError("cyclic path resolution")
        seen = {*seen, marker}
        data = self._entry(data_id).data
        content = data.content
        if isinstance(content, FieldUpdatesContent):
            for update in content.updates:
                if _prefix(update.path, path):
                    suffix = path[len(update.path):]
                    return self.get(update.data) if not suffix else self._resolve_part(update.data, suffix, seen)
            descendants = [
                DataPart(path=update.path[len(path):], data=update.data)
                for update in content.updates if _prefix(path, update.path)
            ]
            if descendants:
                try:
                    base = self._resolve_part(content.base, path, seen)
                except (_ClosedPart, _ExcludedPart):
                    # The overlay explicitly introduces these children where
                    # the base has no such ancestor. No old remainder exists.
                    return self._part_view(data_id, path, KnownPartsContent(
                        parts=descendants, parts_complete=True,
                    ))
                return self._part_view(data_id, path, FieldUpdatesContent(
                    base=base.id, updates=descendants,
                ))
            return self._resolve_part(content.base, path, seen)
        if isinstance(content, WholeExceptContent):
            if any(_prefix(excluded, path) for excluded in content.excluded_parts):
                raise _ExcludedPart(f"requested part {path!r} is explicitly excluded")
            relative = [
                excluded[len(path):] for excluded in content.excluded_parts
                if _prefix(path, excluded)
            ]
            base = self._resolve_part(content.base, path, seen)
            if relative:
                return self._part_view(data_id, path, WholeExceptContent(
                    base=base.id, excluded_parts=relative,
                ))
            return base
        if isinstance(content, LiteralContent):
            value = content.value
            for step in path:
                if type(value) is dict and type(step) is str and step in value:
                    value = value[step]
                elif type(value) is list and type(step) is int and step < len(value):
                    value = value[step]
                else:
                    raise _ClosedPart(f"literal has no part at typed path {path!r}")
            return self._part_view(data_id, path, LiteralContent(value=deepcopy(value)))
        if isinstance(content, KnownPartsContent):
            for part in content.parts:
                if part.path == path:
                    return self.get(part.data)
            prefixes = [part for part in content.parts if _prefix(part.path, path)]
            if prefixes:
                prefix = max(prefixes, key=lambda part: len(part.path))
                return self._resolve_part(prefix.data, path[len(prefix.path):], seen)
            descendants = [
                DataPart(path=part.path[len(path):], data=part.data)
                for part in content.parts if _prefix(path, part.path)
            ]
            if content.parts_complete:
                if descendants:
                    return self._part_view(data_id, path, KnownPartsContent(
                        parts=descendants, parts_complete=True,
                    ))
                raise _ClosedPart(f"part {path!r} is absent from complete composition")
        # Existing canonical part identities may be discoverable via their
        # enclosing whole. register_part preserves these aliases and refines
        # the original source, never a filtered/overlaid view.
        return self.register_part(data_id, path)

    def _validate_records(self, records: dict[str, _Entry]) -> None:
        for data_id, entry in records.items():
            data, identity = entry.data, entry.identity
            if data.id != data_id or data_id != self._id(identity):
                raise DataConflictError("data ID does not match namespace and identity key")
            origin, content = data.origin, data.content
            if identity.kind == "source":
                if origin.acquired_from is None or origin.part_of is not None:
                    raise DataConflictError("source identity requires an acquisition origin")
            elif identity.kind == "result":
                if origin.at is None or origin.part_of is not None:
                    raise DataConflictError("result identity requires an operation location")
            elif origin.part_of != identity.parent_id or origin.path != identity.path:
                raise DataConflictError("part identity disagrees with its origin")
        self._validate_data_values({key: entry.data for key, entry in records.items()})

    @staticmethod
    def _validate_data_values(records: dict[str, Data]) -> None:
        """Content/origin integrity independent of allocation identities."""
        content_edges: dict[str, list[str]] = {}
        parent_edges: dict[str, list[str]] = {}
        for data_id, data in records.items():
            origin, content = data.origin, data.content
            refs = [*origin.inputs, *(d.data for d in origin.dependencies)]
            edges: list[str] = []
            if origin.part_of is not None:
                refs.append(origin.part_of)
            parent_edges[data_id] = [origin.part_of] if origin.part_of is not None else []
            if isinstance(content, KnownPartsContent):
                edges.extend(p.data for p in content.parts)
            elif isinstance(content, WholeExceptContent):
                edges.append(content.base)
            elif isinstance(content, FieldUpdatesContent):
                edges.extend([content.base, *(part.data for part in content.updates)])
            refs.extend(edges)
            for ref in refs:
                if ref not in records:
                    raise DataReferenceError(f"{data_id} references unknown data {ref}")
            content_edges[data_id] = edges
        DataRegistry._acyclic(content_edges, "content composition")
        DataRegistry._acyclic(parent_edges, "part origin")
        for data_id, data in records.items():
            if data.origin.part_of is not None:
                if records[data.origin.part_of].origin.part_of is not None:
                    raise DataConflictError("part identity must use its canonical root and full path")
                resolved = DataRegistry._locate_data(records, data.origin.part_of, data.origin.path, set())
                if resolved != data_id:
                    raise DataConflictError("part origin is not bound to its own data ID")
            if isinstance(data.content, KnownPartsContent):
                # Overlapping explicit paths must not contradict their declared
                # enclosing object, a literal, or an exclusion view.
                parts = data.content.parts
                for outer in parts:
                    for inner in parts:
                        if len(outer.path) < len(inner.path) and _prefix(outer.path, inner.path):
                            remaining = inner.path[len(outer.path):]
                            DataRegistry._check_nested(records, outer.data, remaining, inner.data)

    @staticmethod
    def _check_nested(records: dict[str, Data], data_id: str, path: Path, expected: str) -> None:
        content = records[data_id].content
        if isinstance(content, LiteralContent):
            raise DataConflictError("cannot assert nested part identities through a literal")
        if isinstance(content, KnownPartsContent) and content.parts_complete:
            if not any(_prefix(p.path, path) or _prefix(path, p.path) for p in content.parts):
                raise DataConflictError("nested path contradicts complete composition")
        try:
            actual = DataRegistry._locate_data(records, data_id, path, set())
        except _MissingPart:
            return
        except DataReferenceError as exc:
            raise DataConflictError(f"nested path contradicts its enclosing content: {exc}") from exc
        if actual != expected:
            raise DataConflictError("overlapping paths refer to different data")

    @staticmethod
    def _acyclic(edges: dict[str, list[str]], label: str) -> None:
        # Only structural containment is acyclic. Input/derived/possible links
        # may be cyclic and are deliberately absent from this traversal.
        states: dict[str, int] = {}
        for root in edges:
            if states.get(root) == 2:
                continue
            stack = [(root, False)]
            while stack:
                node, leave = stack.pop()
                if leave:
                    states[node] = 2
                    continue
                state = states.get(node, 0)
                if state == 1:
                    raise DataConflictError(f"cycle in {label}")
                if state == 2:
                    continue
                states[node] = 1
                stack.append((node, True))
                stack.extend((child, False) for child in reversed(edges[node]))

    def validate(self) -> None:
        """Check shape and references, not the truth of supplied semantics."""
        records = {
            key: _Entry.model_validate(entry.model_dump(mode="python"))
            for key, entry in self._records.items()
        }
        self._validate_records(records)

    def to_dict(self) -> dict:
        self.validate()
        snapshot = _Snapshot(schema_version=SCHEMA_VERSION, namespace=self._namespace, records=[self._records[key] for key in sorted(self._records)])
        return deepcopy(snapshot.model_dump(mode="python"))

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, allow_nan=False, indent=indent)

    @classmethod
    def from_dict(cls, payload: dict) -> "DataRegistry":
        snapshot = _Snapshot.model_validate(payload)
        registry = cls(snapshot.namespace)
        for entry in snapshot.records:
            if entry.data.id in registry._records:
                raise DataConflictError("duplicate data ID or identity in snapshot")
            registry._records[entry.data.id] = entry.model_copy(deep=True)
        registry.validate()
        return registry

    @classmethod
    def from_json(cls, text: str) -> "DataRegistry":
        if type(text) is not str:
            raise DataRegistryError("JSON input must be a string")

        def unique_object(pairs: list[tuple[str, object]]) -> dict:
            obj: dict = {}
            for key, value in pairs:
                if key in obj:
                    raise DataRegistryError(f"duplicate JSON object key: {key!r}")
                obj[key] = value
            return obj

        def invalid_constant(value: str) -> None:
            raise DataRegistryError(f"non-JSON numeric constant: {value}")

        payload = json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)
        if type(payload) is not dict:
            raise DataRegistryError("registry snapshot must be a JSON object")
        return cls.from_dict(payload)


def validate_data_records(data: list[Data | dict]) -> list[dict]:
    """Check complete Data contents/references without allocation metadata.

    This accepts arbitrary stable Data IDs. Only restore_registry additionally
    verifies that those IDs were allocated from the declared identity keys.
    """
    _list_only(data)
    parsed: dict[str, Data] = {}
    for value in data:
        item = Data.model_validate(value.model_dump(mode="python") if isinstance(value, Data) else value)
        if item.id in parsed:
            raise DataConflictError("duplicate data ID")
        parsed[item.id] = item
    DataRegistry._validate_data_values(parsed)
    return [parsed[key].model_dump(mode="json") for key in sorted(parsed)]


def export_identity_index(registry: DataRegistry) -> dict:
    """Export only namespace and allocation keys, never Data contents."""
    if not isinstance(registry, DataRegistry):
        raise DataRegistryError("registry must be a DataRegistry")
    snapshot = registry.to_dict()
    return _IdentityIndex(schema_version=SCHEMA_VERSION, namespace=snapshot["namespace"],
                          identities={entry["data"]["id"]: entry["identity"]
                                      for entry in snapshot["records"]}).model_dump(mode="json")


def restore_registry(data: list[Data | dict], index: dict) -> DataRegistry:
    """Restore a registry by joining checked contents with separate identities."""
    checked = validate_data_records(data)
    parsed = _IdentityIndex.model_validate(index)
    if set(parsed.identities) != {item["id"] for item in checked}:
        raise DataConflictError("identity index must cover the Data IDs exactly")
    return DataRegistry.from_dict({
        "schema_version": SCHEMA_VERSION, "namespace": parsed.namespace,
        "records": [{"identity": parsed.identities[item["id"]].model_dump(mode="json"), "data": item}
                    for item in checked],
    })
