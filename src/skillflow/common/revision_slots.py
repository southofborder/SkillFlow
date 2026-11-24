"""Decode independently owned rows of a completed revision using its existing JSON keys."""
from __future__ import annotations

from dataclasses import dataclass, field as data_field
import json

from .json_normalization import _decoder
from .recording import canonical_sha256
from .source_evidence import json_pointer
from .validation import structural_error


@dataclass
class RevisionObject:
    value: dict
    diagnostics: list = data_field(default_factory=list)
    repairs: list = data_field(default_factory=list)


@dataclass
class DecodedSlots:
    rows: dict
    diagnostics: list
    repairs: list
    headers: dict
    submitted: set


def slot_wire_instructions(field, owner):
    return (f"Keep the JSON keys shown. Inside {field}, write each complete record on its own physical line "
            f"with {owner} first. In shared_values, write each vN member on its own physical line. "
            "Keep literal newlines within strings JSON-escaped. The program assembles independently validated records.")


def _one_closer(text, decoder, error):
    """Only edit the delimiter at the decoder's first mismatched closing token."""
    if not isinstance(error, json.JSONDecodeError) or error.msg != "Expecting ',' delimiter":
        return None
    pos = error.pos
    if pos >= len(text) or text[pos] not in ']}':
        return None
    options = [(text[:pos] + closer + text[pos:], "insert", closer) for closer in '}]']
    options.append((text[:pos] + text[pos + 1:], "remove", text[pos]))
    valid = []
    for candidate, operation, closer in options:
        try:
            value = decoder.decode(candidate)
        except (ValueError, RecursionError):
            continue
        valid.append((value, {"operation": operation, "offset": pos, "character": closer,
                              "raw_sha256": canonical_sha256(text), "candidate_sha256": canonical_sha256(candidate)}))
    return valid[0] if len(valid) == 1 else None


def _whitespace(text, pos):
    while pos < len(text) and text[pos] in ' \t\r\n':
        pos += 1
    return pos


def _owner_prefix(raw, keys):
    """Read owner members before the broken value; never inspect quoted payload as framing."""
    d = _decoder()
    i = _whitespace(raw, 0)
    if i >= len(raw) or raw[i] != '{':
        return {}
    found = {}
    i += 1
    while i < len(raw):
        try:
            key, i = d.raw_decode(raw, _whitespace(raw, i))
            i = _whitespace(raw, i)
            if not isinstance(key, str) or raw[i:i + 1] != ':':
                break
            value, i = d.raw_decode(raw, _whitespace(raw, i + 1))
            if key in keys and (isinstance(value, str) or key in {"scope_ids", "target_ids"}
                                and isinstance(value, list) and all(isinstance(v, str) for v in value)):
                found[key] = value
            i = _whitespace(raw, i)
            if raw[i:i + 1] != ',':
                break
            i += 1
        except (ValueError, RecursionError):
            break
    return found


# Recovery is limited to the owned collection members of a revision. Nested arrays,
# source evidence, positional data and scope hashes remain part of their owning row.
_COLLECTIONS = {"slots", "updates", "coverage_slots", "requirements", "issues", "unresolved_issues",
                "findings", "input_contract_checks", "input_projection_checks", "source_input_findings", "gap_checks",
                "replacements", "insertions", "declarations", "entry_gaps", "realizations", "demands", "operation_demands",
                "processing_gaps", "expressions", "ir_semantics", "locations", "shared_values"}
_OWNERS = {"instruction_id", "requirement_id", "slot_id", "id", "entry_id", "obligation_id", "gap_id", "record_id", "target_id", "target_ids", "scope_ids"}


class _RevisionReader:
    def __init__(self, raw):
        self.text, self.decoder = raw, _decoder()
        self.diagnostics, self.repairs = [], []

    def fail(self, pos):
        raise ValueError(f"Revision has no unambiguous JSON record boundary at character {pos}.")

    def member(self, pos, path, *, key=None):
        text = self.text
        try:
            value, end = self.decoder.raw_decode(text, pos)
            boundary = _whitespace(text, end)
            if text[boundary:boundary + 1] in (',', ']', '}'):
                return value, end, True
        except (ValueError, RecursionError):
            pass
        # The complete owner (or keyed definition) occupies exactly one line. The
        # outer separator and the next physical owner/closing delimiter stay intact.
        start = text.rfind('\n', 0, pos) + 1
        if key is None and text[start:pos].strip():
            self.fail(pos)
        end = text.find('\n', pos)
        if end < 0:
            self.fail(pos)
        content = text[pos:end].rstrip()
        comma = content.endswith(',')
        if comma:
            content = content[:-1].rstrip()
        end = pos + len(content)
        following = _whitespace(text, text.find('\n', pos) + 1)
        next_token = text[following:following + 1]
        if (comma and next_token not in ('{', '"')) or (not comma and next_token not in (']', '}')):
            self.fail(end)
        message = "Invalid JSON in this revision record."
        try:
            self.decoder.decode(content)
        except (ValueError, RecursionError) as error:
            repair = _one_closer(content, self.decoder, error)
            if repair:
                value, receipt = repair
                self.repairs.append({**receipt, "path": json_pointer(*path), "response_offset": pos + receipt["offset"]})
                return value, end, True
            message = str(error)
        owner = _owner_prefix(content, _OWNERS) if key is None else {"member": key}
        self.diagnostics.append({"code": "revision_record_json", "path": json_pointer(*path),
            "message": message, "context": {**owner, "raw_start": pos, "raw_end": end,
                                          "record_sha256": canonical_sha256(content)}})
        return None, end, False

    def container(self, pos, path):
        text = self.text
        opener = text[pos:pos + 1]
        if opener not in ('[', '{'):
            self.fail(pos)
        obj = opener == '{'
        closing = '}' if obj else ']'
        value, seen, repeated = ({} if obj else []), set(), set()
        pos = _whitespace(text, pos + 1)
        ordinal = 0
        while pos < len(text) and text[pos] != closing:
            key_start = pos
            if obj:
                key, pos = self.decoder.raw_decode(text, pos)
                if not isinstance(key, str):
                    self.fail(pos)
                pos = _whitespace(text, pos)
                if text[pos:pos + 1] != ':':
                    self.fail(pos)
                pos = _whitespace(text, pos + 1)
            else:
                key = ordinal
            child = (*path, key)
            if ((not path or path == ('payload',)) and key in _COLLECTIONS
                    and text[pos:pos + 1] in ('{', '[')) or (not path and key == 'payload' and text[pos:pos + 1] == '{'):
                item, pos = self.container(pos, child)
                good = True
            elif (path and path[-1] in _COLLECTIONS and len(path) <= 2) or (not path and key == "purpose"):
                if obj and text[text.rfind('\n', 0, key_start) + 1:key_start].strip():
                    # A legal compact dictionary is still accepted by the strict fast path.
                    item, pos = self.decoder.raw_decode(text, pos)
                    good = True
                else:
                    item, pos, good = self.member(pos, child, key=key if obj else None)
            else:
                item, pos = self.decoder.raw_decode(text, pos)
                good = True
            if obj:
                if key in seen:
                    if not path or path[-1] not in _COLLECTIONS:
                        raise ValueError(f"Duplicate revision envelope member {key!r}.")
                    repeated.add(key)
                    self.diagnostics.append({"code": "revision_duplicate", "path": json_pointer(*child),
                        "message": "This member occurs more than once.", "context": {"member": key}})
                seen.add(key)
                if good and key not in repeated:
                    value[key] = item
                else:
                    value.pop(key, None)
            elif good:
                value.append(item)
            ordinal += 1
            pos = _whitespace(text, pos)
            if text[pos:pos + 1] == closing:
                break
            if text[pos:pos + 1] != ',':
                self.fail(pos)
            pos = _whitespace(text, pos + 1)
            if text[pos:pos + 1] == closing:
                self.fail(pos)
        if text[pos:pos + 1] != closing:
            self.fail(pos)
        return value, pos + 1


def read_revision_object(raw):
    """Read old valid JSON exactly, or isolate independently framed damaged rows."""
    if isinstance(raw, RevisionObject):
        return raw
    if isinstance(raw, dict):
        raw = json.dumps(raw, ensure_ascii=False, allow_nan=False)
    if not isinstance(raw, str):
        raise structural_error("revision_json", "", "Revision must be a JSON object.")
    decoder = _decoder()
    try:
        value = decoder.decode(raw)
    except (ValueError, RecursionError) as error:
        repair = _one_closer(raw, decoder, error)
        if repair and isinstance(repair[0], dict):
            return RevisionObject(repair[0], repairs=[repair[1]])
        reader = _RevisionReader(raw)
        try:
            value, end = reader.container(_whitespace(raw, 0), ())
            if raw[end:].strip():
                reader.fail(end)
        except (ValueError, RecursionError) as failure:
            raise structural_error("revision_json", "", str(failure)) from error
        if not isinstance(value, dict):
            raise structural_error("revision_json", "", "Revision must be a JSON object.")
        return RevisionObject(value, reader.diagnostics, reader.repairs)
    if not isinstance(value, dict):
        raise structural_error("revision_json", "", "Revision must be a JSON object.")
    return RevisionObject(value)


def decode_revision_slots(raw, *, field, owner, authorized, required=True, header=None, siblings=(), shared=False):
    """Bind each existing row to exactly one authorized owner; report all discarded owners."""
    obj = read_revision_object(raw)
    value = obj.value
    diagnostics, repairs = list(obj.diagnostics), list(obj.repairs)
    headers = dict(header or {})
    definitions = None
    if shared and ({"format", "payload", "shared_values"} & value.keys()):
        if (set(value) != {"format", "payload", "shared_values"} or value["format"] != "skillflow-processing-json-v1"
                or not isinstance(value["shared_values"], dict) or not isinstance(value["payload"], dict)):
            raise structural_error("revision_envelope", "", "Invalid shared revision envelope.")
        definitions, value = value["shared_values"], value["payload"]
    if set(value) - ({field} | set(siblings) | headers.keys()) or not isinstance(value.get(field), list):
        raise structural_error("revision_envelope", "", "Expected the bound revision record collection " + field + ".")
    if any(value.get(name) != expected for name, expected in headers.items()):
        raise structural_error("revision_identity", "", "The revision header differs from its bound scope.")
    rows, indexes, invalid = {}, {}, set()
    for diagnostic in diagnostics:
        parts = diagnostic["path"].split("/")
        if len(parts) >= 3 and parts[-2] == field:
            name = diagnostic.get("context", {}).get(owner)
            if isinstance(name, str):
                invalid.add(name)
    candidates = dict(enumerate(value[field]))
    if definitions is not None:
        if not callable(shared):
            raise ValueError("A shared revision requires its stage's strict value decoder.")
        candidates, errors = shared(candidates, definitions, owner=owner, field=field)
        diagnostics.extend(errors)
    for index, row in candidates.items():
        name = row.get(owner) if isinstance(row, dict) else None
        ptr = json_pointer(field, index)
        allowed = isinstance(name, str) and (authorized(name) if callable(authorized) else name in authorized)
        if not allowed:
            diagnostics.append({"code": "revision_slot_owner", "path": ptr, "message": "Expected an authorized " + owner + ".",
                                "context": {owner: name} if isinstance(name, str) else {}})
            continue
        if name in indexes or name in invalid:
            invalid.add(name)
            diagnostics.append({"code": "revision_slot_duplicate", "path": ptr, "message": "A revision slot has conflicting records.",
                                "context": {owner: name}})
        indexes[name] = index
        rows[name] = row
    for name in invalid:
        rows.pop(name, None)
    required_set = set(authorized) if required is True else set(required or ())
    for name in sorted(required_set - rows.keys() - invalid):
        diagnostics.append({"code": "revision_slot_missing", "path": json_pointer(field, name),
                            "message": "The revision omitted this required slot.", "context": {owner: name}})
    submitted = set(indexes) | invalid
    for error in diagnostics:
        claimed = error.get("context", {}).get(owner)
        if (error["code"] == "revision_shared_reference" and isinstance(claimed, str)
                and (authorized(claimed) if callable(authorized) else claimed in authorized)):
            submitted.add(claimed)
    return DecodedSlots(rows, diagnostics, repairs, {k: v for k, v in value.items() if k != field}, submitted)
