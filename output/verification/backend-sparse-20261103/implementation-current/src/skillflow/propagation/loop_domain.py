"""Finite loop equations, separate from the immutable published Data registry.

Only static producer sites, lexical member scopes and finite source selectors
allocate families. Inputs and structured contents are relation facts, not part
of allocation keys. No concrete counter or iteration trace is evaluated.
"""
from __future__ import annotations

import json
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.data import DataRegistry, Data, Origin, OpaqueContent
from skillflow.propagation.data import LoopSummaryContent, LoopVariant, SelectionContent
from skillflow.propagation.data.registry import _Identity, _Entry, IterationEntry, _content_references
from skillflow.propagation.data.models import ElementStep


def key(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      default=lambda value: value.model_dump(mode="json"))


class LoopFactRegistry(DataRegistry):
    """Working finite equations; seal() publishes a new ordinary registry once.

    Ordinary entries are never edited to stand for an evolving loop value.
    The private facts table is mutable during solving and is not a Data ledger.
    """

    def __init__(self, registry, scopes):
        super().__init__(registry.namespace)
        self._records = deepcopy(registry._records)
        self._revision = registry.revision
        self.scopes = dict(scopes)
        self.facts = {}
        self.fact_revision = 0
        self._fact_count = 0
        self.current_position = None
        self.max_facts = 100000
        self.regions = {}
        self.member_scopes = {}
        self.member_sources = {}
        self.ir_blocks = {}
        self.ir_orders = {}
        self.dominators = {}
        self.region_blocks = {}
        self._rebuild_part_index()
        if registry._computation.enabled:
            self.enable_computation()

    @property
    def revision(self):
        return self._revision + self.fact_revision

    def __len__(self):
        return len(self._records) + len(self.facts)

    def contains_data(self, identity):
        self._read_data(identity)
        return identity in self._records or identity in self.facts

    def data_ids(self):
        return (*self._records, *self.facts)

    def family_producer(self, identity):
        self._read_data(identity)
        fact = self.facts.get(identity)
        return fact["producer"] if fact is not None else identity

    def bindings(self, identity):
        self._read_data(identity)
        if identity in self.facts:
            return dict(self.facts[identity]["bindings"])
        value = self._records.get(identity)
        if value and value.data.origin.part_of:
            return self.bindings(value.data.origin.part_of)
        return {}

    def combine_bindings(self, inputs):
        bindings = {}
        for identity in inputs:
            for scope, selector in self.bindings(identity).items():
                if scope in bindings and bindings[scope] != selector:
                    return None
                bindings[scope] = selector
        return bindings

    def aggregate_bindings(self, position, inputs):
        bindings = self.combine_bindings(inputs)
        if bindings is None:
            return None
        instruction = position[0] if isinstance(position, list) else None
        region = self.regions.get(instruction)
        # A collection contains many members of its own loop, but remains
        # paired with any enclosing page/member. Never erase outer correlation.
        def owner(scope):
            for prefix in ("incoming:", "unresolved:"):
                if scope.startswith(prefix):
                    scope = scope[len(prefix):]
            return self.member_scopes.get(scope)
        return {scope: value for scope, value in bindings.items()
                if region is None or owner(scope) != region}

    def carried_bindings(self, identity, *, region=None):
        """Retain one incoming tuple choice independently of its next use.

        Views do not create a new generation. A newly computed value requiring
        more history is explicitly marked; multi-value uses cannot guess its
        missing relation. Keys and selector values come from finite CFG sites.
        """
        bindings = dict(self.bindings(identity))
        fact = self.facts.get(identity)
        def has_marker(value):
            if isinstance(value, list):
                return any(has_marker(item) for item in value)
            return value in ("stored-use", "carried-use")
        transparent = bool(fact and has_marker(json.loads(fact["producer"])))
        for scope, selector in list(bindings.items()):
            member = scope in self.member_scopes
            predecessor = scope.startswith("predecessor:")
            if not (member or predecessor):
                continue
            if region is not None and member and self.member_scopes[scope] != region:
                continue
            if region is not None and scope == "predecessor:" + region:
                # The new incoming edge replaces this header's old edge. Its
                # tuple choice is retained by member axes and relation states.
                del bindings[scope]
                continue
            incoming = "incoming:" + scope
            if incoming not in bindings:
                bindings[incoming] = selector
            elif bindings[incoming] != selector and not transparent:
                bindings["unresolved:" + scope] = "multiple_generations"
            del bindings[scope]
        return bindings

    def _entry(self, data_id):
        self._read_data(data_id)
        if data_id not in self.facts:
            return super()._entry(data_id)
        fact = self.facts[data_id]
        variants = [fact["variants"][identity] for identity in sorted(fact["variants"])]
        inputs = sorted({item for variant in variants for item in variant.inputs})
        dependencies = {(item.data, item.relation): item
                        for variant in variants for item in variant.dependencies}
        acquired = {variant.acquired_from for variant in variants if variant.acquired_from}
        if self._computation.enabled:
            content = LoopSummaryContent.model_construct(scope=fact["scope"], producer=fact["producer"],
                variants=variants, bindings=fact["bindings"])
            origin = Origin.model_construct(at=fact["producer"], inputs=inputs,
                dependencies=[dependencies[item] for item in sorted(dependencies)],
                acquired_from=next(iter(acquired)) if len(acquired) == 1 else None)
            return self._make_entry(fact["identity"], Data.model_construct(id=data_id, content=content, origin=origin))
        return _Entry(identity=fact["identity"], data=Data(id=data_id,
            content=LoopSummaryContent(scope=fact["scope"], producer=fact["producer"],
                variants=variants, bindings=fact["bindings"]),
            origin=Origin(at=fact["producer"], inputs=inputs,
                dependencies=[dependencies[item] for item in sorted(dependencies)],
                acquired_from=next(iter(acquired)) if len(acquired) == 1 else None)))

    def _all_entries(self):
        return {**self._records, **{identity: self._entry(identity) for identity in self.facts}}

    def _data_values(self):
        return super()._data_values()

    def _commit(self, updates):
        if any(identity in self.facts for identity in updates):
            raise ValueError("ordinary refinement cannot mutate a loop equation")
        if self._computation.enabled:
            return super()._commit(updates)
        self._validate_records({**self._all_entries(), **updates})
        self._apply_updates(self._changed_updates(updates))

    def family(self, scope, position, inputs, content, origin, bindings=None):
        bindings = self.combine_bindings(inputs) if bindings is None else dict(bindings)
        if bindings is None:
            raise ValueError("incompatible member/predecessor bindings cannot form a result")
        producer = key(position)
        identity = _Identity(kind="result", key="loop-family:" + key([scope, producer, bindings]))
        data_id = self._id(identity)
        if data_id in self._records:
            from skillflow.propagation.data import DataConflictError
            raise DataConflictError("ordinary Data identity cannot become a loop equation")
        # A summary may appear as the content of an alias. Keep a relation to
        # that source, not an embedded recursively growing summary descriptor.
        if isinstance(content, LoopSummaryContent):
            content = OpaqueContent()
        variant = LoopVariant(inputs=list(inputs), content=content,
            dependencies=origin.dependencies, acquired_from=origin.acquired_from)
        variant_id = canonical_sha256(variant.model_dump(mode="json"))
        fact = self.facts.get(data_id)
        if fact is None or variant_id not in fact["variants"]:
            if self._fact_count >= self.max_facts:
                from skillflow.propagation.interpreter import PropagationLimitError
                raise PropagationLimitError("finite loop relation resource budget exceeded")
            # Check local family shape once; later reads assemble only owned models.
            if fact is None:
                LoopSummaryContent(scope=scope, producer=producer, bindings=bindings)
            if self._computation.enabled:
                refs = [*variant.inputs, *(item.data for item in variant.dependencies),
                        *_content_references(variant.content)]
                for ref in refs:
                    if ref != data_id and not self.contains_data(ref):
                        from skillflow.propagation.data import DataReferenceError
                        raise DataReferenceError(f"{data_id} references unknown data {ref}")
            if fact is None:
                self._computation.remember(self.facts, data_id)
                fact = {"identity": identity, "scope": scope, "producer": producer,
                        "bindings": bindings, "variants": {}}
                self.facts[data_id] = fact
            values = fact["variants"]
            self._computation.remember(values, variant_id)
            values[variant_id] = variant
            self._fact_count += 1
            self.fact_revision += 1
            self._computation.changed(("data", data_id))
        return self.get(data_id)

    def scope_for(self, position, inputs):
        def first_text(value):
            if isinstance(value, str):
                return value
            return first_text(value[0]) if isinstance(value, list) and value else None
        instruction = first_text(position)
        if instruction in self.scopes:
            return self.scopes[instruction]
        scopes = set()
        for item in inputs:
            self._read_data(item)
            if item in self.facts:
                scopes.add(self.facts[item]["scope"])
        scopes = sorted(scopes)
        return scopes[0] if scopes else None

    def project(self, base, path, position):
        scope = self.scope_for(position, [base])
        if scope is None:
            return super().resolve_part_candidates(base, path)
        from skillflow.propagation.data.summary import _select
        if not _select(self, base, [item.model_dump(mode="json") if hasattr(item, "model_dump") else item for item in path], frozenset()):
            return ()
        from skillflow.propagation.data import Dependency
        origin = Origin(at=key(position), inputs=[base],
                        dependencies=[Dependency(data=base, relation="derived")])
        value = self.family(scope, position, [base], SelectionContent(base=base, path=path), origin)
        return (value,)

    def resolve_part_candidates(self, base, path):
        self._read_data(base)
        if base in self.facts:
            position = self.current_position or ["projection", key(path)]
            return self.project(base, path, position)
        return super().resolve_part_candidates(base, path)

    def resolve_iteration_entries(self, collection_id, scope):
        self._read_data(collection_id)
        if collection_id in self.facts:
            from skillflow.propagation.data.summary import content_options
            contents = content_options(self, collection_id)
            if contents and all(item["form"] == "literal" and type(item["value"]) is list for item in contents):
                indices = sorted({index for item in contents for index in range(len(item["value"]))})
                return tuple(IterationEntry(index, value) for index in indices
                    for value in self.project(collection_id, [index], ["member", scope, index]))
            selector = ElementStep(scope=scope)
            position = ["member", scope]
            return tuple(IterationEntry(selector, value)
                         for value in self.project(collection_id, [selector], position))
        return super().resolve_iteration_entries(collection_id, scope)

    def collection_truths(self, identity):
        from skillflow.propagation.data import LiteralContent, KnownPartsContent
        content = self.get(identity).content
        values = [item.content for item in content.variants] if isinstance(content, LoopSummaryContent) else [content]
        truths = set()
        for value in values:
            if isinstance(value, LiteralContent) and type(value.value) is list:
                truths.add(bool(value.value))
            elif isinstance(value, KnownPartsContent) and value.parts_complete:
                truths.add(bool(value.parts))
            else:
                truths.update((False, True))
        return truths or {False, True}

    def validate(self):
        self._validate_records(self._all_entries())

    def to_dict(self):
        from skillflow.propagation.data.registry import SCHEMA_VERSION
        return {"schema_version": SCHEMA_VERSION, "namespace": self.namespace,
                "records": [entry.model_dump(mode="json")
                            for _, entry in sorted(self._all_entries().items())]}

    def seal(self):
        """No later family mutation is visible to published immutable records."""
        if self._computation.enabled:
            registry = DataRegistry(self.namespace)
            registry._records = {identity: self._entry(identity).model_copy(deep=True)
                                 for identity in self.data_ids()}
            registry.enable_computation()
            return registry
        return DataRegistry.from_dict(self.to_dict())
