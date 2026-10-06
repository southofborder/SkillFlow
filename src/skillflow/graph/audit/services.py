"""Single-call source/controlled-text review and strict offline response parsing.

Evidence positions and explicit unit coverage are checked deterministically.
Semantic judgments remain model proposals, not program-established entailments.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import re
from typing import Any, Protocol

from skillflow.graph.semantic_contract import contract_binding
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import _checked_source
from skillflow.common.source_evidence import _digest
from skillflow.common.source_evidence import _exact
from skillflow.common.source_evidence import _fail
from skillflow.common.source_evidence import _json_object
from skillflow.common.source_evidence import _unique
from skillflow.common.source_evidence import _validate_source_ref

from skillflow.graph.audit.models import AuditResult
from skillflow.graph.audit.models import CannotAssessAudit
from skillflow.graph.audit.prompts import source_controlled_prompt
from skillflow.graph.audit.prompts import source_units


class CompletionClient(Protocol):
    def complete(self, prompt: str) -> Any: ...


def _checked_document(document: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(document, dict) or not isinstance(document.get("text"), str):
        _fail("controlled document requires complete text")
    if not re.fullmatch(r"[0-9a-f]{64}", str(document.get("graph_sha256", ""))):
        _fail("controlled document requires graph_sha256")
    units = document.get("units")
    if not isinstance(units, list) or not units:
        _fail("controlled document requires nonempty units")
    for unit in units:
        if not isinstance(unit, dict) or not isinstance(unit.get("id"), str) or not unit["id"].strip():
            _fail("controlled unit requires a nonempty id")
        if not isinstance(unit.get("text"), str) or not unit["text"].strip():
            _fail("controlled unit requires nonempty text")
        if unit["text"] not in document["text"]:
            _fail(f"controlled unit text is absent from complete document: {unit['id']}")
        if unit.get("basis") not in {"explicit_graph", "declared_constraint", "embedded_content", "mixed"}:
            _fail(f"invalid controlled evidence basis: {unit['id']}")
        refs = unit.get("graph_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) for ref in refs):
            _fail(f"controlled unit requires local graph references: {unit['id']}")
        for ref in refs:
            if (ref and not ref.startswith("/")) or re.search(r"~(?![01])", ref):
                _fail(f"invalid local graph pointer: {ref!r}")
    _unique([unit["id"] for unit in units], "controlled unit ids")
    # The runner independently verifies the Lean certificate. Recheck these
    # instance bindings locally without invoking Lean or trusting model hashes.
    certificate = document.get("certificate")
    if not isinstance(certificate, dict) or certificate.get("status") != "verified":
        _fail("controlled document requires an independently verified certificate")
    if certificate.get("graph_sha256") != document["graph_sha256"]:
        _fail("controlled graph digest differs from certificate")
    if certificate.get("text_sha256") != hashlib.sha256(document["text"].encode("utf-8")).hexdigest():
        _fail("controlled text digest differs from certificate")
    if certificate.get("units_sha256") != _digest(units):
        _fail("controlled units digest differs from certificate")
    links = document.get("derived_links")
    if not isinstance(links, list) or certificate.get("links_sha256") != _digest(links):
        _fail("controlled derived_links digest differs from certificate")
    _result_identities(links)
    return document


def _mapped_graph_refs(ids: list[str], units: dict[str, dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for unit_id in ids:
        if unit_id not in units:
            _fail(f"controlled unit does not exist: {unit_id}")
        for pointer in units[unit_id]["graph_refs"]:
            if pointer not in result:
                result.append(pointer)
    return result


def _result_identities(links: list[dict[str, Any]]) -> dict[str, str]:
    """Read already certified result links; never parse prose or infer from names."""
    identities: dict[str, str] = {}
    definitions: dict[str, str] = {}
    uses: set[str] = set()
    for link in links:
        if (not isinstance(link, dict) or set(link) != {"identifier", "use_ref", "definition_ref"}
                or any(not isinstance(value, str) or not value.strip() for value in link.values())):
            _fail("invalid controlled derived result link")
        identifier = link["identifier"]
        for field, direction in (("use_ref", "inputs"), ("definition_ref", "outputs")):
            pointer = link[field]
            if (not re.fullmatch(rf"/blocks/[^/]+/instructions/\d+/{direction}/\d+", pointer)
                    or re.search(r"~(?![01])", pointer)):
                _fail("invalid controlled result link pointer")
            if pointer in identities and identities[pointer] != identifier:
                _fail("controlled result links assign conflicting identities to an operand")
            identities[pointer] = identifier
        if link["use_ref"] in uses:
            _fail("controlled result links repeat a use location")
        uses.add(link["use_ref"])
        if identifier in definitions and definitions[identifier] != link["definition_ref"]:
            _fail("controlled result links assign multiple definitions to one identifier")
        definitions[identifier] = link["definition_ref"]
    return identities


def _checked_conservative(
    finding: dict[str, Any], units: dict[str, dict[str, Any]], result_identities: dict[str, str],
) -> None:
    """Check location eligibility, not the model's semantic candidate reasoning."""
    conservative = finding["conservative"]
    if conservative is None:
        return
    candidate_ids = conservative["candidate_fact_ids"]
    cited_ids = {ref["unit_id"] for ref in finding["controlled_refs"]}
    if not set(candidate_ids) <= cited_ids:
        _fail("conservative candidate_fact_ids must also appear in controlled_refs")
    candidates = set()
    for fact_id in candidate_ids:
        unit = units[fact_id]
        if unit["basis"] != "explicit_graph":
            _fail("conservative candidates require explicit operand/definition facts")
        # A complete operand or identity/payload field can identify a candidate.
        # Containers, constraint declarations and opaque metadata cannot. Do
        # not infer business semantics from the field's text or an opcode.
        for pointer in unit["graph_refs"]:
            match = re.fullmatch(
                r"(/blocks/[^/]+/instructions/\d+/(?:inputs|outputs)/\d+)"
                r"(?:/(identifier|literal_value)(?:/.*)?)?", pointer)
            if match is None:
                _fail(f"conservative candidate is not an operand/definition fact: {fact_id}")
            if conservative["rule_id"] == "DEP-MERGE" and match.group(2) == "literal_value":
                _fail("DEP-MERGE candidate cannot be a literal payload field")
            location = match.group(1)
            if (conservative["rule_id"] == "DEP-MERGE" and "/inputs/" in location
                    and location not in result_identities):
                # Every actual result input is represented in the independently
                # checked definition/use links. A literal, resource or context
                # input therefore cannot masquerade as a merge-result candidate
                # merely by citing its full operand or identifier field.
                _fail("DEP-MERGE input candidates require a certified result definition/use link")
            if location in result_identities:
                candidates.add(("result", result_identities[location]))
            else:
                # Unused definitions and non-result operands may have no link.
                # Preserve only a location check for these; do not guess an ID
                # from text, or claim this is a proof of distinct semantic sources.
                candidates.add(("location", location))
    if len(candidates) < 2:
        _fail("conservative candidates require at least two distinct operands/results; uses of one result do not count twice")
    conservative["graph_refs"] = _mapped_graph_refs(candidate_ids, units)


def validate_audit(raw: Any, source: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    source = _checked_source(source)
    document = _checked_document(document)
    paragraphs = {unit["id"]: unit for unit in source_units(source)}
    units = {unit["id"]: unit for unit in document["units"]}
    payload = _json_object(raw)
    if payload.get("outcome") == "cannot_assess":
        failure = CannotAssessAudit.model_validate(payload).model_dump(mode="json")["failure"]
        for ref in failure["source_refs"]:
            _validate_source_ref(ref, paragraphs)
        for ref in failure["controlled_refs"]:
            if ref["unit_id"] not in units:
                _fail(f"controlled unit does not exist: {ref['unit_id']}")
            if ref["quote"] is not None and ref["quote"] not in units[ref["unit_id"]]["text"]:
                _fail(f"controlled quote does not match unit: {ref['unit_id']}")
        failure["graph_refs"] = _mapped_graph_refs([ref["unit_id"] for ref in failure["controlled_refs"]], units)
        raise SemanticFailure(failure)
    parsed = AuditResult.model_validate(payload).model_dump(mode="json")
    result_identities = _result_identities(document["derived_links"])
    _exact(parsed["reviewed_source_unit_ids"], set(paragraphs), "reviewed_source_unit_ids")
    _exact(parsed["reviewed_controlled_unit_ids"], set(units), "reviewed_controlled_unit_ids")
    _unique([finding["id"] for finding in parsed["findings"]], "finding ids")
    seen_source: set[str] = set()
    seen_controlled: set[str] = set()
    for finding in parsed["findings"]:
        for ref in finding["source_refs"]:
            _validate_source_ref(ref, paragraphs)
            seen_source.add(ref["unit_id"])
        for ref in finding["controlled_refs"]:
            unit_id = ref["unit_id"]
            if unit_id not in units:
                _fail(f"controlled unit does not exist: {unit_id}")
            if ref["quote"] is not None and ref["quote"] not in units[unit_id]["text"]:
                _fail(f"controlled quote does not match unit: {unit_id}")
            seen_controlled.add(unit_id)
        finding["graph_refs"] = _mapped_graph_refs(
            [ref["unit_id"] for ref in finding["controlled_refs"]], units)
        _checked_conservative(finding, units, result_identities)
        for suggestion in finding["suggestions"]:
            _unique(suggestion["target_ids"], "suggestion target_ids")
            suggestion["graph_refs"] = _mapped_graph_refs(suggestion["target_ids"], units)
    if seen_source != set(paragraphs):
        _fail(f"findings do not cover source units: {sorted(set(paragraphs) - seen_source)}")
    if seen_controlled != set(units):
        _fail(f"findings do not cover controlled units: {sorted(set(units) - seen_controlled)}")
    parsed["source_units"] = deepcopy(list(paragraphs.values()))
    parsed["graph_sha256"] = document["graph_sha256"]
    parsed.update(contract_binding())
    parsed["representation_summary"] = {
        "represented_ids": [f["id"] for f in parsed["findings"]
                            if f["kind"] == "semantic" and f["status"] == "represented"],
        "conservative_ids": [f["id"] for f in parsed["findings"] if f["conservative"] is not None],
    }
    parsed["coverage_notice"] = (
        "定位、引文与单元覆盖已检查；这不是语义等价或语义完整性的证明。"
        "保守候选的依据及语义覆盖仍属于模型判断，不是程序证明。"
        "未填写保守说明不代表精确保留。")
    return parsed


def parse_response(raw: Any, *, source: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    """Offline parse/validation only: no client and no API fallback."""
    return validate_audit(raw, source, document)


def audit_source_controlled(
    source: dict[str, Any], document: dict[str, Any], client: CompletionClient
) -> dict[str, Any]:
    source = _checked_source(source)
    document = _checked_document(document)
    raw = client.complete(source_controlled_prompt(source, document))
    return validate_audit(raw, source, document)
