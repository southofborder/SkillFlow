"""Bounded evidence about rejected raw wire JSON, never an accepted candidate.

Call only after the authoritative processing parser/codec has rejected a raw
string. This scanner preserves ordered object members, including duplicates. It
does not select definitions, expand references, return a candidate, run semantic
validation or decide that a response is acceptable. Non-string inputs have no
exact raw text provenance and receive no supplemental diagnostic.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
import re

from .fragment_wire import (
    DEFINITION_NAME_PATTERN, PROCESSING_WIRE_IDENTITY, WIRE_MARKERS, WIRE_ROOT_FIELDS, valid_definition_name,
)


IDENTITY = "skillflow-processing-wire-diagnostics-v1"
MAX_RAW_CHARACTERS = 2 * 1024 * 1024
MAX_SCAN_NODES = 100_000
MAX_SCAN_DEPTH = 96
MAX_EXAMPLES_PER_GROUP = 3
MAX_EXAMPLE_CHARACTERS = 12_000
_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_MESSAGES = {
    "duplicate_member": "JSON member names must be unique in every object; do not choose or merge duplicate values.",
    "root_members": "The processing envelope requires exactly format, payload and one shared_values table.",
    "definition_table": "Each shared_values occurrence must be a JSON object.",
    "definition_name": f"Every definition name must match {DEFINITION_NAME_PATTERN}; mnemonic and leading-zero names are invalid.",
    "reference_name": f"A reference value must be a string matching {DEFINITION_NAME_PATTERN}; name resolution is not checked here.",
    "marker_shape": "An encoded marker object must contain exactly one $ref or $literal_object member and no other members.",
    "literal_pairs": "The $literal_object value must be an array of [distinct string key, encoded value] pairs.",
    "literal_duplicate": "Literal-object pair keys must be distinct; duplicate pair keys cannot be selected or merged.",
    "nonfinite_number": "JSON numbers must be finite under the strict processing codec.",
}


@dataclass(slots=True)
class _Node:
    kind: str
    start: int
    end: int
    value: object


@dataclass(slots=True)
class _Member:
    key: _Node
    value: _Node
    occurrence: int


class _ScanStop(Exception):
    def __init__(self, status, position, reason):
        self.status, self.position, self.reason = status, position, reason


class _Parser:
    """Small JSON syntax reader with budgets checked before each node allocation."""

    def __init__(self, raw):
        self.raw, self.position, self.nodes = raw, 0, 0

    def stop(self, reason, status="invalid_json"):
        raise _ScanStop(status, self.position, reason)

    def whitespace(self):
        while self.position < len(self.raw) and self.raw[self.position] in " \r\n\t":
            self.position += 1

    def node(self, depth):
        self.whitespace()
        if depth > MAX_SCAN_DEPTH:
            self.stop("Raw JSON nesting exceeds the diagnostic scan depth budget.", "limited")
        if self.nodes >= MAX_SCAN_NODES:
            self.stop("Raw JSON nodes exceed the diagnostic scan node budget.", "limited")
        self.nodes += 1
        start = self.position
        if start >= len(self.raw):
            self.stop("Unexpected end of raw JSON while reading a value.")
        token = self.raw[start]
        if token == '"':
            try:
                value, self.position = json.decoder.scanstring(self.raw, start + 1, True)
            except (ValueError, UnicodeError) as error:
                self.position = getattr(error, "pos", start)
                self.stop("Invalid raw JSON string syntax.")
            return _Node("string", start, self.position, value)
        if token in "{[":
            self.position += 1
            items, occurrences = [], {}
            closing = "}" if token == "{" else "]"
            self.whitespace()
            if self.position < len(self.raw) and self.raw[self.position] == closing:
                self.position += 1
                return _Node("object" if token == "{" else "array", start, self.position, items)
            while True:
                if token == "{":
                    self.whitespace()
                    if self.position >= len(self.raw) or self.raw[self.position] != '"':
                        self.stop("Object member name must be a JSON string.")
                    key = self.node(depth + 1)
                    self.whitespace()
                    if self.position >= len(self.raw) or self.raw[self.position] != ":":
                        self.stop("Expected a colon after an object member name.")
                    self.position += 1
                    value = self.node(depth + 1)
                    occurrence = occurrences.get(key.value, 0) + 1
                    occurrences[key.value] = occurrence
                    items.append(_Member(key, value, occurrence))
                else:
                    items.append(self.node(depth + 1))
                self.whitespace()
                if self.position >= len(self.raw):
                    self.stop("Unexpected end of a raw JSON container.")
                separator = self.raw[self.position]
                self.position += 1
                if separator == closing:
                    break
                if separator != ",":
                    self.stop("Expected a comma or the matching container terminator.")
            return _Node("object" if token == "{" else "array", start, self.position, items)
        for literal, kind in (("true", "boolean"), ("false", "boolean"), ("null", "null")):
            if self.raw.startswith(literal, start):
                self.position += len(literal)
                return _Node(kind, start, self.position, literal)
        match = _NUMBER.match(self.raw, start)
        if match is not None:
            self.position = match.end()
            return _Node("number", start, self.position, match.group())
        self.stop("Invalid raw JSON value syntax; no ambiguous value was repaired.")

    def parse(self):
        root = self.node(0)
        self.whitespace()
        if self.position != len(self.raw):
            self.stop("Trailing content after the raw JSON value.")
        return root


def _member_path(path, index, member):
    # Index plus same-key occurrence identifies even duplicated members without
    # copying arbitrarily large member names into the bounded report.
    return (*path, {"member_index": index, "occurrence": member.occurrence})


class _Findings:
    def __init__(self):
        self.groups, self.example_characters = {}, 0

    def add(self, code, node, path, **details):
        group = self.groups.setdefault(code, {"rule": code, "message": _MESSAGES[code],
                                               "count": 0, "examples": []})
        group["count"] += 1
        if len(group["examples"]) >= MAX_EXAMPLES_PER_GROUP:
            return
        example = {"span": [node.start, node.end], "occurrence_path": list(path), **details}
        size = len(json.dumps(example, ensure_ascii=True, separators=(",", ":")))
        if self.example_characters + size <= MAX_EXAMPLE_CHARACTERS:
            group["examples"].append(example)
            self.example_characters += size

    def rows(self):
        return [{**group, "undisplayed_occurrences": group["count"] - len(group["examples"])}
                for group in self.groups.values()]


def _preview(text):
    # ASCII display cannot turn an unpaired raw string surrogate into a report
    # serialization error. Exact identity remains the raw span and digest.
    escaped = json.dumps(text[:80], ensure_ascii=True)[1:-1]
    return escaped[:80]


def _raw_findings(node, path, findings):
    if node.kind == "object":
        first = {}
        for index, member in enumerate(node.value):
            child_path = _member_path(path, index, member)
            if member.occurrence > 1:
                findings.add("duplicate_member", member.key, child_path,
                             member_preview=_preview(member.key.value),
                             first_span=first[member.key.value])
            else:
                first[member.key.value] = [member.key.start, member.key.end]
            _raw_findings(member.value, child_path, findings)
    elif node.kind == "array":
        for index, child in enumerate(node.value):
            _raw_findings(child, (*path, {"array_index": index}), findings)
    elif node.kind == "number" and any(char in node.value for char in ".eE"):
        if not math.isfinite(float(node.value)):
            findings.add("nonfinite_number", node, path)


def _encoded_findings(node, path, findings):
    if node.kind == "array":
        for index, child in enumerate(node.value):
            _encoded_findings(child, (*path, {"array_index": index}), findings)
        return
    if node.kind != "object":
        return
    marker_members = [member for member in node.value if member.key.value in WIRE_MARKERS]
    if marker_members:
        if len(node.value) != 1:
            findings.add("marker_shape", node, path)
            # Its interpretation is already invalid; do not pretend to know
            # which of its alternative marker meanings was intended.
            return
        member = marker_members[0]
        child_path = _member_path(path, 0, member)
        if member.key.value == "$ref":
            if member.value.kind != "string" or not valid_definition_name(member.value.value):
                findings.add("reference_name", member.value, child_path)
            return
        pairs = member.value
        if pairs.kind != "array":
            findings.add("literal_pairs", pairs, child_path)
            return
        seen = {}
        for index, pair in enumerate(pairs.value):
            pair_path = (*child_path, {"array_index": index})
            if pair.kind != "array" or len(pair.value) != 2 or pair.value[0].kind != "string":
                findings.add("literal_pairs", pair, pair_path)
                continue
            key, value = pair.value
            if key.value in seen:
                findings.add("literal_duplicate", key, (*pair_path, {"array_index": 0}),
                             first_span=seen[key.value])
            else:
                seen[key.value] = [key.start, key.end]
            _encoded_findings(value, (*pair_path, {"array_index": 1}), findings)
        return
    for index, member in enumerate(node.value):
        _encoded_findings(member.value, _member_path(path, index, member), findings)


def _wire_findings(root, findings):
    if root.kind != "object":
        return False
    formats = [member for member in root.value if member.key.value == "format"]
    recognized = (len(formats) == 1 and formats[0].value.kind == "string"
                  and formats[0].value.value == PROCESSING_WIRE_IDENTITY)
    if not recognized:
        return False
    names = Counter(member.key.value for member in root.value)
    if set(names) != WIRE_ROOT_FIELDS or any(count != 1 for count in names.values()):
        findings.add("root_members", root, ())
    for index, member in enumerate(root.value):
        path = _member_path((), index, member)
        if member.key.value == "shared_values":
            if member.value.kind != "object":
                findings.add("definition_table", member.value, path)
                continue
            for entry_index, entry in enumerate(member.value.value):
                entry_path = _member_path(path, entry_index, entry)
                if not valid_definition_name(entry.key.value):
                    findings.add("definition_name", entry.key, entry_path,
                                 name_preview=_preview(entry.key.value))
                _encoded_findings(entry.value, entry_path, findings)
        elif member.key.value == "payload":
            _encoded_findings(member.value, path, findings)
    return True


def _raw_digest(raw):
    digest = hashlib.sha256()
    for start in range(0, len(raw), 64 * 1024):
        digest.update(raw[start:start + 64 * 1024].encode("utf-8", errors="surrogatepass"))
    return digest.hexdigest()


def scan_processing_wire(raw):
    """Return bounded raw evidence; no result field is an accepted candidate.

    Spans are zero-based, end-exclusive Unicode code-point offsets into the exact
    supplied string. Each path step is an array index or zero-based member index
    with a one-based same-key occurrence. No path denotes an expanded IR.
    Limits constrain diagnostics only and never alter response acceptance.
    """
    report = {"identity": IDENTITY, "purpose": "supplemental_rejection_evidence_only",
              "status": "not_applicable", "recognized_wire_format": False, "groups": [],
              "offset_unit": "unicode_code_points_zero_based_end_exclusive",
              "limits": {"raw_characters": MAX_RAW_CHARACTERS, "nodes": MAX_SCAN_NODES,
                         "depth": MAX_SCAN_DEPTH, "examples_per_group": MAX_EXAMPLES_PER_GROUP,
                         "example_characters": MAX_EXAMPLE_CHARACTERS}}
    if not isinstance(raw, str):
        return report
    report.update(raw_sha256=_raw_digest(raw), raw_hash_encoding="utf-8; surrogatepass for unpaired surrogates",
                  raw_characters=len(raw), coverage={"complete": False, "scanned_characters": 0,
                                                     "nodes": 0, "limitation": None})
    if len(raw) > MAX_RAW_CHARACTERS:
        report["status"] = "limited"
        report["coverage"]["limitation"] = "Raw response exceeds the diagnostic character budget; no text was truncated into a candidate."
        return report
    parser = _Parser(raw)
    try:
        root = parser.parse()
        findings = _Findings()
        _raw_findings(root, (), findings)
        report["recognized_wire_format"] = _wire_findings(root, findings)
        report["groups"] = findings.rows()
        report["status"] = "complete"
        report["coverage"].update(complete=True, scanned_characters=len(raw), nodes=parser.nodes)
    except _ScanStop as error:
        report["status"] = error.status
        report["coverage"].update(scanned_characters=error.position, nodes=parser.nodes,
                                   limitation=error.reason)
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, MemoryError) as error:
        # A supplementary reader cannot replace the authoritative rejection or
        # manufacture a usable interpretation when its own scan is incomplete.
        report["status"] = "limited"
        report["coverage"].update(scanned_characters=parser.position, nodes=parser.nodes,
                                   limitation=f"Raw diagnostic scan could not complete ({type(error).__name__}); preserve the original rejection and full replacement.")
    return report


def processing_wire_diagnostics(raw):
    """Supplement a prior strict rejection; never invoke this as a validator.

    Return root-only structural diagnostic rows for the existing one full
    correction. A complete empty scan proves no acceptance and returns no row.
    The primary parser/codec diagnostic must remain first and unchanged.
    """
    report = scan_processing_wire(raw)
    if report["status"] == "not_applicable" or report["status"] == "complete" and not report["groups"]:
        return []
    return [{"code": "processing_wire_raw_diagnostics", "path": "",
             "message": "Supplemental raw representation evidence only; the original response remains rejected. Return one complete replacement with all source and required contracts; do not select or merge duplicate tables.",
             "context": {"raw_wire_scan": report}}]
