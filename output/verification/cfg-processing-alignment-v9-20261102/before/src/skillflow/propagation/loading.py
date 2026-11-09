"""Read-only component access for propagation consumers, without a JSON handoff."""
from __future__ import annotations

from copy import copy, deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts, _normalized_cfg
from skillflow.propagation.records import PropagationRecords, cfg_sha256


class PropagationMaterials:
    """A checked in-memory view. Properties detach mutable values from the owner.

    It deliberately has no mapping or whole-object serialization interface.
    Source and semantic material have one upstream owner; fact files retain only
    propagation outputs. A consumer must request the components it uses.
    """

    def __init__(self, *, material, raw_annotation, compiled_annotation, mapping,
                 source_metadata, solved, sinks, manifest=None, provenance=None, wire_annotation=None):
        self._annotation = deepcopy({"material": material, "task": material["task"], "raw_annotation": raw_annotation,
                                     "compiled_annotation": compiled_annotation, "mapping": mapping})
        if wire_annotation is not None:
            self._annotation["wire_annotation"] = deepcopy(wire_annotation)
        self._source_metadata = deepcopy(source_metadata)
        self._data = solved.registry.to_dict()
        self._records = solved.records.records_dict()
        self._sinks = deepcopy(sinks)
        self._status = solved.status
        self._coverage, self._diagnostics = deepcopy(solved.coverage), deepcopy(solved.diagnostics)
        self._initial_data, self._initial_state = deepcopy(solved.initial_data), deepcopy(solved.initial_state)
        self._stats = deepcopy(solved.stats)
        self._manifest = deepcopy(manifest or {})
        self._provenance = deepcopy(provenance or {"kind": "hand_authored_specification"})

    def _with_manifest(self, manifest):
        """Attach publication identity to the same checked, privately owned facts."""
        result = copy(self)
        result._manifest = deepcopy(manifest)
        return result

    @property
    def annotation(self): return deepcopy(self._annotation)
    @property
    def material(self): return deepcopy(self._annotation["material"])
    @property
    def raw_annotation(self): return deepcopy(self._annotation["raw_annotation"])
    @property
    def compiled_annotation(self): return deepcopy(self._annotation["compiled_annotation"])
    @property
    def mapping(self): return deepcopy(self._annotation["mapping"])
    @property
    def source(self): return deepcopy(self._annotation["material"]["source"])
    @property
    def source_metadata(self): return deepcopy(self._source_metadata)
    @property
    def cfg(self): return deepcopy(self._annotation["material"]["cfg"])
    @property
    def runtime_contract(self): return deepcopy(self._annotation["material"]["runtime_contract"])
    @property
    def locations(self): return deepcopy(self._annotation["compiled_annotation"]["locations"])
    @property
    def actions(self):
        specs = self._annotation["compiled_annotation"]["ir_semantics"]
        return {ir["id"]: {"operator": deepcopy(specs.get(ir["id"], {}).get("operator"))}
                for block in self.cfg["blocks"].values() for ir in block["instructions"]}
    @property
    def data(self): return [deepcopy(entry["data"]) for entry in self._data["records"]]
    @property
    def registry(self): return DataRegistry.from_dict(deepcopy(self._data))
    @property
    def records(self): return deepcopy(self._records)
    @property
    def sinks(self): return deepcopy(self._sinks)
    @property
    def status(self): return self._status
    @property
    def coverage(self): return deepcopy(self._coverage)
    @property
    def diagnostics(self): return deepcopy(self._diagnostics)
    @property
    def processing_gaps(self): return deepcopy(self.compiled_annotation.get("processing_gaps", []))
    @property
    def boundary_coverage(self):
        from skillflow.propagation.facts import declared_boundary_coverage
        return declared_boundary_coverage(self.compiled_annotation, self.sinks, self.coverage)
    @property
    def initial_data(self): return deepcopy(self._initial_data)
    @property
    def initial_state(self): return deepcopy(self._initial_state)
    @property
    def stats(self): return deepcopy(self._stats)
    @property
    def manifest(self): return deepcopy(self._manifest)
    @property
    def provenance(self): return deepcopy(self._provenance)
    @property
    def upstream_identity(self):
        return {key: deepcopy(self._manifest[key]) for key in
                ("identity", "schema_version", "manifest_sha256") if key in self._manifest} | {
                    "accepted_response_sha256": self._provenance.get("accepted_response_sha256")}
    @property
    def record_store(self):
        from skillflow.propagation.annotation.services import to_payload
        return PropagationRecords.from_records(self.records, cfg=self.cfg,
            annotation=to_payload(self.compiled_annotation), data_registry=self.registry,
            initial_data=self.initial_data, initial_state=self.initial_state)


def materials_from_result(solved, *, material, raw_annotation, compiled_annotation, mapping,
                          source_metadata=None, manifest=None, provenance=None, wire_annotation=None,
                          _validated_annotation=False):
    """Validate facts; raw callers also reconstruct annotation compilation.

    ``_validated_annotation`` is private to the persisted-run loader, which has
    already checked the bound manifest, inputs and compiled artifact hashes.
    """
    from skillflow.propagation.material import checked_material
    from skillflow.propagation.annotation.services import compile_response, to_payload
    material = checked_material(material)
    if _validated_annotation:
        raw, compiled, actual_mapping = raw_annotation, compiled_annotation, mapping
    elif wire_annotation is None:
        raw, compiled, actual_mapping = compile_response(raw_annotation, material)
    else:
        from skillflow.document_guided.annotation_wire import compile_flat_response
        _, raw, compiled, actual_mapping = compile_flat_response(wire_annotation, material)
    if not _validated_annotation and any(canonical_sha256(actual) != canonical_sha256(supplied) for actual, supplied in
           ((raw, raw_annotation), (compiled, compiled_annotation), (actual_mapping, mapping))):
        raise ValueError("Propagation annotation or compilation differs from its source")
    payload = to_payload(compiled)
    if (cfg_sha256(solved.records.cfg) != cfg_sha256(_normalized_cfg(material["cfg"]))
            or canonical_sha256(solved.records.annotation) != canonical_sha256(payload)
            or canonical_sha256(solved.initial_data) != canonical_sha256(solved.records.initial_data)
            or canonical_sha256(solved.initial_state) != canonical_sha256(solved.records.initial_state)):
        raise ValueError("Propagation result differs from its bound source, annotation or seeds")
    if canonical_sha256(solved.registry.to_dict()) != canonical_sha256(solved.records.data_registry.to_dict()):
        raise ValueError("Propagation registry differs from the record registry")
    solved.records.validate()
    data = [entry["data"] for entry in solved.registry.to_dict()["records"]]
    sinks = resolved_sink_boundaries(compiled["locations"], solved.records.records_dict())
    outcome = validate_propagation_facts(cfg=material["cfg"], annotation=payload, data=data,
        records=solved.records.records_dict(), sinks=sinks, status=solved.status,
        coverage=solved.coverage, diagnostics=solved.diagnostics)
    result = PropagationMaterials(material=material, raw_annotation=raw, compiled_annotation=compiled,
        mapping=mapping, source_metadata=source_metadata or {}, solved=solved, sinks=sinks,
        manifest=manifest, provenance=provenance, wire_annotation=wire_annotation)
    result._diagnostics = outcome["diagnostics"]
    return result
