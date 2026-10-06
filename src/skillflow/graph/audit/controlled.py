"""Checked boundary to the Lean controlled-retelling printer and parser.

Python never prints a retelling. It sends the complete normalized graph to Lean,
parses the actual returned text with Lean, and independently reconstructs the
public CFG from that parsed rich graph. No hidden CFG is used for reconstruction.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.common.paths import project_root, formal_root

from skillflow.graph.audit.evidence import canonical_graph_sha256
from skillflow.graph.audit.evidence import definition_refs
from skillflow.graph.audit.evidence import json_pointer
from skillflow.graph.audit.evidence import normalize_cfg
from skillflow.graph.audit.evidence import resolve_pointer


SCHEMA_VERSION = 2


class ControlledVerificationError(ValueError):
    """The concrete printer/parser boundary failed; no semantic audit may run."""


def _fail(message: str) -> None:
    raise ControlledVerificationError(message)


def _canonical(value: Any) -> str:
    canonical_graph_sha256(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_text(value: str) -> str:
    return _sha_bytes(value.encode("utf-8"))


def _json(raw: str) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _fail(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        _fail(f"Non-JSON numeric constant: {value}")

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, TypeError, UnicodeError) as error:
        raise ControlledVerificationError(f"Invalid JSON: {error}") from error


def _object(value: Any, names: set[str], location: str) -> dict:
    if type(value) is not dict or set(value) != names:
        _fail(f"Unexpected rich fields at {location}")
    return value


def _strings(value: Any, location: str) -> list[str]:
    if type(value) is not list or any(type(item) is not str for item in value):
        _fail(f"Expected string list at {location}")
    return value


def _string(value: Any, location: str, *, nullable: bool = False) -> str | None:
    if type(value) is str or (nullable and value is None):
        return value
    _fail(f"Expected {'nullable ' if nullable else ''}string at {location}")


def _list(value: Any, location: str) -> list:
    if type(value) is not list:
        _fail(f"Expected list at {location}")
    return value


def _payload(raw: Any, location: str) -> Any:
    _string(raw, location)
    value = _json(raw)
    if _canonical(value) != raw:
        _fail(f"Opaque JSON payload changed or is noncanonical at {location}")
    return value


def to_rich(graph: dict[str, Any]) -> dict[str, Any]:
    """A full field-preserving wire graph, including opaque JSON payload bytes."""
    def operand(item):
        return {
            "kind": item["type"], "identifier": item["identifier"],
            "semantic_name": item.get("semantic_name"),
            "literal_json": _canonical(item["literal_value"]) if item["type"] == "literal" else None,
        }

    blocks = []
    for key in sorted(graph["blocks"]):
        block = graph["blocks"][key]
        blocks.append({
            "key": key, "id": block["block_id"], "name": block["block_name"],
            "source": block["data_source_kind"], "constraints": deepcopy(block["constraints"]),
            "instructions": [{
                "id": item["id"], "opcode": item["opcode"], "draft": item["draft_instruction_id"],
                "inputs": [operand(value) for value in item["inputs"]],
                "outputs": [operand(value) for value in item["outputs"]],
                "constraints": deepcopy(item["constraints"]), "metadata_json": _canonical(item["metadata"]),
            } for item in block["instructions"]],
        })
    return {
        "entry": graph["entry_block_id"], "contexts": deepcopy(graph["declared_context_keys"]),
        "constraints": deepcopy(graph["constraints"]), "blocks": blocks,
        "edges": [{"source": edge["source_block_id"], "target": edge["target_block_id"],
                   "condition": edge["condition_text"]} for edge in graph["edges"]],
    }


def from_rich(rich: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct every public CFG field using only the parsed rich records."""
    _object(rich, {"entry", "contexts", "constraints", "blocks", "edges"}, "/")

    def operand(item, path):
        _object(item, {"kind", "identifier", "semantic_name", "literal_json"}, path)
        kind = _string(item["kind"], path + "/kind")
        if kind not in {"literal", "context_key", "external_resource", "result"}:
            _fail(f"Unknown operand type at {path}")
        restored = {"type": kind, "identifier": _string(item["identifier"], path + "/identifier", nullable=True)}
        semantic_name = _string(item["semantic_name"], path + "/semantic_name", nullable=True)
        if semantic_name is not None:
            restored["semantic_name"] = semantic_name
        if kind == "literal":
            restored["literal_value"] = _payload(item["literal_json"], path + "/literal_json")
        elif item["literal_json"] is not None:
            _fail(f"Nonliteral operand owns a payload at {path}")
        return restored

    blocks = {}
    for index, block in enumerate(_list(rich["blocks"], "/blocks")):
        path = f"/blocks/{index}"
        _object(block, {"key", "id", "name", "source", "constraints", "instructions"}, path)
        key = _string(block["key"], path + "/key")
        if key in blocks:
            _fail(f"Duplicate rich block key: {key}")
        instructions = []
        for position, item in enumerate(_list(block["instructions"], path + "/instructions")):
            here = f"{path}/instructions/{position}"
            _object(item, {"id", "opcode", "draft", "inputs", "outputs", "constraints", "metadata_json"}, here)
            metadata = _payload(item["metadata_json"], here + "/metadata_json")
            if type(metadata) is not dict:
                _fail(f"Metadata must remain an object at {here}")
            instructions.append({
                "id": _string(item["id"], here + "/id"), "opcode": _string(item["opcode"], here + "/opcode"),
                "draft_instruction_id": _string(item["draft"], here + "/draft", nullable=True),
                "inputs": [operand(value, f"{here}/inputs/{i}") for i, value in enumerate(_list(item["inputs"], here + "/inputs"))],
                "outputs": [operand(value, f"{here}/outputs/{i}") for i, value in enumerate(_list(item["outputs"], here + "/outputs"))],
                "constraints": deepcopy(_strings(item["constraints"], here + "/constraints")), "metadata": metadata,
            })
        blocks[key] = {
            "block_id": _string(block["id"], path + "/id"), "block_name": _string(block["name"], path + "/name"),
            "data_source_kind": _string(block["source"], path + "/source", nullable=True),
            "constraints": deepcopy(_strings(block["constraints"], path + "/constraints")), "instructions": instructions,
        }
    edges = []
    for index, edge in enumerate(_list(rich["edges"], "/edges")):
        path = f"/edges/{index}"
        _object(edge, {"source", "target", "condition"}, path)
        edges.append({"source_block_id": _string(edge["source"], path + "/source"),
                      "target_block_id": _string(edge["target"], path + "/target"),
                      "condition_text": _string(edge["condition"], path + "/condition", nullable=True)})
    graph = {"entry_block_id": _string(rich["entry"], "/entry"),
             "declared_context_keys": deepcopy(_strings(rich["contexts"], "/contexts")),
             "constraints": deepcopy(_strings(rich["constraints"], "/constraints")), "blocks": blocks, "edges": edges}
    try:
        normalized = normalize_cfg(ControlFlowGraph.model_validate(deepcopy(graph)))
    except (ValueError, TypeError) as error:
        raise ControlledVerificationError(f"Recovered graph is not a valid CFG: {error}") from error
    if _canonical(normalized) != _canonical(graph):
        _fail("Recovered rich fields would require normalization")
    return graph


def _executable(executable: str | Path | None) -> Path:
    default = formal_root() / ".lake/build/bin/skill_ir_retell.exe" if executable is None else Path(executable)
    if executable is None and not default.exists():
        default = default.with_suffix("")
    path = Path(executable) if executable is not None else default
    path = path.resolve()
    if not path.is_file():
        _fail(f"Lean retelling executable does not exist; build skill_ir_retell first: {path}")
    return path


def _provenance(executable: Path) -> dict[str, Any]:
    paths = {Path(__file__).resolve(), Path(__file__).with_name("evidence.py").resolve()}
    proof_root = formal_root()
    paths.update(path for path in proof_root.rglob("*.lean") if ".lake" not in path.relative_to(proof_root).parts)
    paths.update(proof_root / name for name in ("lakefile.toml", "lake-manifest.json", "lean-toolchain"))
    files = {path.relative_to(project_root()).as_posix(): _sha_bytes(path.read_bytes()) for path in sorted(paths)}
    return {"source_files": files, "source_sha256": canonical_graph_sha256(files),
            "binary_sha256": _sha_bytes(executable.read_bytes())}


def _lean(executable: Path, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        process = subprocess.run([str(executable)], input=(_canonical(payload) + "\n").encode("utf-8"),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=executable.parent,
                                 check=False, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ControlledVerificationError(f"Lean subprocess failed: {error}") from error
    if process.returncode:
        _fail(f"Lean exited {process.returncode}: {process.stderr.decode('utf-8', errors='replace')}")
    try:
        response = _json(process.stdout.decode("utf-8"))
    except UnicodeError as error:
        raise ControlledVerificationError("Lean output is not UTF-8") from error
    if type(response) is not dict or response.get("ok") is not True:
        _fail(f"Lean rejected the document: {response.get('error') if isinstance(response, dict) else response}")
    return response


def _rich_pointer(graph: dict[str, Any], rich: dict[str, Any], pointer: str) -> str:
    """Translate an existing wire location to the public CFG, without guessing IDs."""
    resolve_pointer(rich, pointer)
    if pointer == "":
        return ""
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]
    first = parts[0]
    if first in {"entry", "contexts", "constraints"}:
        mapped = [{"entry": "entry_block_id", "contexts": "declared_context_keys"}.get(first, first), *parts[1:]]
    elif first == "edges":
        mapped = parts[:2]
        if len(parts) > 2:
            mapped.extend([{"source": "source_block_id", "target": "target_block_id", "condition": "condition_text"}[parts[2]], *parts[3:]])
    elif first == "blocks":
        if len(parts) == 1:
            return "/blocks"
        key = rich["blocks"][int(parts[1])]["key"]
        mapped = ["blocks", key]
        if len(parts) > 2:
            field = parts[2]
            mapped.append({"key": "block_id", "id": "block_id", "name": "block_name", "source": "data_source_kind"}.get(field, field))
            if field != "instructions":
                mapped.extend(parts[3:])
            elif len(parts) > 3:
                mapped.append(parts[3])
                if len(parts) > 4:
                    field = parts[4]
                    mapped.append({"draft": "draft_instruction_id", "metadata_json": "metadata"}.get(field, field))
                    if field not in {"inputs", "outputs"}:
                        mapped.extend(parts[5:])
                    elif len(parts) > 5:
                        mapped.append(parts[5])
                        if len(parts) > 6:
                            field = parts[6]
                            operand = resolve_pointer(graph, json_pointer(*mapped))
                            # Public serialization omits absent optional names and
                            # nonliteral payload slots. Their containing operand
                            # is the exact evidence for that documented absence.
                            public = {"kind": "type", "literal_json": "literal_value"}.get(field, field)
                            if public in operand:
                                mapped.extend([public, *parts[7:]])
    else:
        _fail(f"Unsupported rich evidence location: {pointer}")
    result = json_pointer(*mapped)
    resolve_pointer(graph, result)
    return result


def _expected_links(rich: dict[str, Any]) -> list[dict[str, str]]:
    definitions = {}
    for block_index, block in enumerate(rich["blocks"]):
        for position, instruction in enumerate(block["instructions"]):
            for index, operand in enumerate(instruction["outputs"]):
                if operand["kind"] == "result":
                    identifier = operand["identifier"]
                    if identifier in definitions:
                        _fail(f"Duplicate result definition in rich graph: {identifier}")
                    definitions[identifier] = f"/blocks/{block_index}/instructions/{position}/outputs/{index}"
    links = []
    for block_index, block in enumerate(rich["blocks"]):
        for position, instruction in enumerate(block["instructions"]):
            for index, operand in enumerate(instruction["inputs"]):
                if operand["kind"] == "result":
                    identifier = operand["identifier"]
                    if identifier not in definitions:
                        _fail(f"Undefined result in rich graph: {identifier}")
                    links.append({"identifier": identifier,
                                  "use_ref": f"/blocks/{block_index}/instructions/{position}/inputs/{index}",
                                  "definition_ref": definitions[identifier]})
    return links


def _basis(pointer: str, rich: dict[str, Any]) -> str:
    parts = pointer.split("/")[1:]
    if "constraints" in parts:
        return "declared_constraint"
    if parts and parts[-1] == "metadata_json":
        return "embedded_content"
    return "explicit_graph"


def _checked_units(response: dict[str, Any], rich: dict[str, Any], graph: dict[str, Any], text: str) -> list[dict[str, Any]]:
    units = []
    ids = set()
    for raw in _list(response.get("units"), "/units"):
        _object(raw, {"id", "text", "kind", "ref"}, "/units/item")
        for name in ("id", "text", "kind", "ref"):
            _string(raw[name], "/units/item/" + name)
        if not raw["id"] or raw["id"] in ids:
            _fail("Controlled unit identifiers must be nonempty and unique")
        if raw["id"] not in {"fact:" + raw["ref"], "fact:" + raw["ref"] + ":link"}:
            _fail("Controlled unit identifier does not encode its exact evidence location")
        ids.add(raw["id"])
        if (not raw["text"] or raw["text"] not in text
                or json.dumps(raw["id"], ensure_ascii=False) not in raw["text"]
                or json.dumps(raw["ref"], ensure_ascii=False) not in raw["text"]):
            _fail(f"Controlled unit is not an anchored substring of the actual text: {raw['id']}")
        pointer = _rich_pointer(graph, rich, raw["ref"])
        units.append({"id": raw["id"], "text": raw["text"], "kind": raw["kind"],
                      "basis": _basis(raw["ref"], rich), "graph_refs": [pointer], "rich_ref": raw["ref"]})
    if not units:
        _fail("Lean returned no controlled evidence units")
    return units


def _checked_links(response: dict[str, Any], rich: dict[str, Any], graph: dict[str, Any]) -> list[dict[str, str]]:
    links = _list(response.get("links"), "/links")
    expected = _expected_links(rich)
    # Occurrences matter: repeated reads must not disappear or merge.
    if _canonical(links) != _canonical(expected):
        _fail("Lean definition/use links differ from independently recomputed references")
    actual_definitions = definition_refs(graph)
    restored = []
    for link in links:
        use = _rich_pointer(graph, rich, link["use_ref"])
        definition = _rich_pointer(graph, rich, link["definition_ref"])
        if actual_definitions[link["identifier"]] != [definition]:
            _fail("Recovered reference points to the wrong public CFG definition")
        restored.append({"identifier": link["identifier"], "use_ref": use, "definition_ref": definition})
    return restored


def _checked_text(text: str, executable: Path) -> tuple[dict[str, Any], dict[str, Any], list, list]:
    """Parse the actual text, reconstruct independently, then check canonical printing."""
    if type(text) is not str or not text:
        _fail("Controlled text must be a nonempty string")
    parsed = _lean(executable, {"command": "parse", "text": text})
    rich = parsed.get("recovered_graph")
    graph = from_rich(rich)
    printed = _lean(executable, {"command": "render", "graph": rich})
    if printed.get("text") != text:
        _fail("Controlled text is not the canonical Lean rendering of its parsed records")
    if _canonical(printed.get("recovered_graph")) != _canonical(rich):
        _fail("Lean render and parse recovered different rich graphs")
    units = _checked_units(printed, rich, graph, text)
    links = _checked_links(printed, rich, graph)
    return rich, graph, units, links


def _certificate(text: str, rich: dict[str, Any], graph: dict[str, Any], units: list, links: list,
                 provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "status": "verified",
        "graph_sha256": canonical_graph_sha256(graph), "rich_sha256": canonical_graph_sha256(rich),
        "text_sha256": _sha_text(text), "units_sha256": canonical_graph_sha256(units),
        "links_sha256": canonical_graph_sha256(links), **provenance,
        "checks": {"actual_text_parsed": True, "canonical_lean_text": True,
                   "complete_cfg_reconstructed": True, "exact_reference_links": True,
                   "exact_evidence_identifiers": True, "opaque_json_payloads_preserved": True},
        "boundary": "Normalized explicit CFG records only; no claim about source equivalence, predicate truth, runtime success, or opaque-code interpretation.",
    }


def render_controlled(cfg: ControlFlowGraph, executable: str | Path | None = None) -> dict[str, Any]:
    """Print in Lean and certify this exact graph/text instance before returning it."""
    graph = normalize_cfg(cfg)
    rich = to_rich(graph)
    binary = _executable(executable)
    provenance = _provenance(binary)
    printed = _lean(binary, {"command": "render", "graph": rich})
    parsed_rich, restored, units, links = _checked_text(printed.get("text"), binary)
    if _canonical(restored) != _canonical(graph) or _canonical(parsed_rich) != _canonical(rich):
        _fail("Actual Lean text does not reconstruct the complete input CFG exactly")
    if _canonical(_checked_units(printed, rich, graph, printed["text"])) != _canonical(units):
        _fail("Lean render evidence changed across the actual-text round trip")
    _checked_links(printed, rich, graph)
    if _provenance(binary) != provenance:
        _fail("Printer source or executable changed during controlled rendering")
    return {"schema_version": SCHEMA_VERSION, "method": "controlled", "text": printed["text"],
            "graph_sha256": canonical_graph_sha256(graph), "units": units, "derived_links": links,
            "certificate": _certificate(printed["text"], parsed_rich, restored, units, links, provenance)}


def verify_controlled(document: dict[str, Any], cfg: ControlFlowGraph | None = None,
                      executable: str | Path | None = None) -> dict[str, Any]:
    """Independently reparse stored text and verify bindings without a model client."""
    _object(document, {"schema_version", "method", "text", "graph_sha256", "units", "derived_links", "certificate"}, "/document")
    if document["schema_version"] != SCHEMA_VERSION or document["method"] != "controlled":
        _fail("Unsupported controlled document version or method")
    binary = _executable(executable)
    provenance = _provenance(binary)
    rich, graph, units, links = _checked_text(document["text"], binary)
    if cfg is not None and _canonical(normalize_cfg(cfg)) != _canonical(graph):
        _fail("Controlled text does not reconstruct the supplied CFG")
    if document["graph_sha256"] != canonical_graph_sha256(graph):
        _fail("Controlled document graph digest mismatch")
    if _canonical(document["units"]) != _canonical(units) or _canonical(document["derived_links"]) != _canonical(links):
        _fail("Controlled evidence units or definition/use links changed")
    expected = _certificate(document["text"], rich, graph, units, links, provenance)
    if _canonical(document["certificate"]) != _canonical(expected):
        _fail("Controlled certificate does not match actual text, graph, source, or binary")
    if _provenance(binary) != provenance:
        _fail("Printer source or executable changed during controlled verification")
    return expected
