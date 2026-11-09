"""Typed, mechanical candidate diagnostics, separate from semantic findings.

Only raise these errors where a response violates an explicit representation
rule. Input identities, transport failures and unexpected implementation errors
must not be reclassified as model-correctable failures.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json
import re


class StructuralValidationError(ValueError):
    """A candidate can be corrected using the supplied mechanical diagnostics."""

    def __init__(self, diagnostics):
        if not isinstance(diagnostics, list) or not diagnostics:
            raise TypeError("structural diagnostics must be a nonempty list")
        rows = deepcopy(diagnostics)
        for item in rows:
            if not isinstance(item, dict) or any(not isinstance(item.get(key), str)
                                                 for key in ("code", "path", "message")):
                raise TypeError("a structural diagnostic requires code, path and message strings")
            if item["path"] and not item["path"].startswith("/"):
                raise TypeError("diagnostic path must be a JSON pointer")
        json.dumps(rows, ensure_ascii=False, allow_nan=False)
        self.diagnostics = rows
        super().__init__("; ".join((row["path"] + ": " if row["path"] else "") + row["message"] for row in rows))


def structural_error(code, path, message, **context):
    """Build a deterministic diagnostic without parsing human error messages."""
    row = {"code": code, "path": path, "message": message}
    if context:
        row["context"] = context
    return StructuralValidationError([row])


_ABSENT = object()


def diagnostic_materials(diagnostics):
    """Separate model-facing errors from their immutable validator provenance.

    Schema unions may yield many mutually exclusive branch errors. The model
    receives one error at the actual object; the audit retains every original
    error and an explicit many-to-one mapping. This never edits the candidate.
    """
    displayed, raw, mapping = [], [], []
    for index, diagnostic in enumerate(diagnostics):
        row = deepcopy(diagnostic)
        audit = row.pop("audit", None)
        displayed.append(row)
        originals = audit["raw_diagnostics"] if audit is not None else [row]
        for original in originals:
            mapping.append({"raw_index": len(raw), "diagnostic_index": index,
                            "candidate_path": row["path"]})
            raw.append(deepcopy(original))
    return {"diagnostics": displayed, "raw_diagnostics": raw,
            "diagnostic_mapping": mapping}


def _pointer(parts):
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _schema_node(node, schema):
    seen = set()
    while isinstance(node, dict) and "$ref" in node:
        ref = node["$ref"]
        if ref in seen or not ref.startswith("#/$defs/"):
            return {}
        seen.add(ref)
        name = ref[len("#/$defs/"):].replace("~1", "/").replace("~0", "~")
        node = schema.get("$defs", {}).get(name, {})
    return node if isinstance(node, dict) else {}


def _union_object(location, candidate, schema):
    """Find a named object union from schema structure, not stage/type names.

    Only aggregate nondiscriminated object alternatives. Discriminated branches
    are followed for accurate nested lookup, but their selected-branch errors
    remain specific. Unsupported shapes fall back to the original diagnostics.
    """
    node, current, parts, found = schema, candidate, [], None
    for part in location:
        node = _schema_node(node, schema)
        options = node.get("anyOf", node.get("oneOf", []))
        named = {option.get("$ref", "").rsplit("/", 1)[-1]: option for option in options
                 if isinstance(option, dict) and "$ref" in option}
        if options:
            selected = named.get(part) if isinstance(part, str) else None
            selected_name = part if selected is not None else None
            if selected is None and isinstance(part, str):
                # Pydantic wraps a model name when it has a model validator.
                # Match only names present in this schema union.
                matches = [name for name in named if re.fullmatch(
                    r"function-(?:after|before|wrap)\[.*,\s*" + re.escape(name) + r"\]", part)]
                if len(matches) == 1:
                    selected_name = matches[0]
                    selected = named[selected_name]
            if selected is None:
                ref = node.get("discriminator", {}).get("mapping", {}).get(str(part))
                if ref is not None:
                    selected = {"$ref": ref}
            if selected is not None:
                forms = [_schema_node(option, schema) for option in options]
                if ("discriminator" not in node and len(forms) > 1
                        and len(named) == len(options)
                        and all(form.get("type") == "object" for form in forms)):
                    compatible = [name for name, form in zip(named, forms)
                                  if isinstance(current, dict)
                                  and form.get("additionalProperties") is False
                                  and set(current) <= set(form.get("properties", {}))]
                    # This describes which complete object form admits the
                    # supplied keys. It never rewrites or selects evidence.
                    found = (list(parts), current, {"anyOf": deepcopy(options)}, forms,
                             compatible[0] if len(compatible) == 1 else None, selected_name)
                node = selected
                continue
        if isinstance(current, dict) and isinstance(part, str) and part in current:
            node = node.get("properties", {}).get(part, node.get("additionalProperties", {}))
            parts.append(part)
            current = current[part]
        elif isinstance(current, list) and type(part) is int and 0 <= part < len(current):
            node = (node.get("prefixItems", [])[part] if part < len(node.get("prefixItems", []))
                    else node.get("items", {}))
            parts.append(part)
            current = current[part]
    return found


def _current_context(current):
    context = {"present": current is not _ABSENT}
    if current is not _ABSENT:
        encoded = json.dumps(current, ensure_ascii=False, allow_nan=False, default=str)
        if len(encoded) <= 800:
            context["current"] = deepcopy(current)
        else:
            context["current_type"] = type(current).__name__
            if isinstance(current, (dict, list, str)):
                context["current_length"] = len(current)
            if isinstance(current, dict):
                context["current_keys"] = list(current)
    return context


def _union_format(forms):
    # Exact field constraints are copied from the validator's schema. Titles
    # alone are presentation metadata; references name the base format's types.
    return [{key: deepcopy(value) for key, value in form.items()
             if key not in {"title", "description"}} for form in forms]


def _candidate_location(location, candidate, error_type):
    """Map Pydantic branch labels to the actual candidate object.

    Union names/discriminator tags are not JSON keys. Walk only real candidate
    keys and indexes; a missing terminal field is the one permitted absent
    coordinate. Container/model errors therefore point at the actual parent.
    """
    current, parts = candidate, []
    for index, part in enumerate(location):
        if isinstance(current, dict) and type(part) is str and part in current:
            parts.append(part)
            current = current[part]
        elif isinstance(current, list) and type(part) is int and 0 <= part < len(current):
            parts.append(part)
            current = current[part]
        elif index == len(location) - 1 and error_type == "missing":
            parts.append(part)
            current = _ABSENT
    return parts, current


def schema_error(error, prefix="", *, candidate=_ABSENT, schema=None):
    """Convert only an explicit candidate-schema ValidationError boundary.

    Supplying the original candidate makes locations independent of Pydantic's
    internal union labels. Missing fields keep their intended child path, with
    ``present=false`` instead of inventing a current value.
    """
    from pydantic import ValidationError
    if not isinstance(error, ValidationError):
        raise TypeError("schema_error only accepts Pydantic ValidationError")
    rows, seen, unions, compatible_unions = [], {}, {}, set()
    for item in error.errors(include_url=False, include_context=False, include_input=False):
        location, current = item["loc"], _ABSENT
        original = {"code": "schema", "path": prefix + _pointer(location),
                    "message": item["msg"], "context": {"type": item["type"]}}
        union = (_union_object(location, candidate, schema)
                 if candidate is not _ABSENT and schema is not None else None)
        if union is not None:
            parts, current, union_schema, forms, compatible, selected = union
            path = prefix + _pointer(parts)
            key = (path, json.dumps(union_schema, sort_keys=True))
            if key in unions:
                row = rows[unions[key]]
                row["audit"]["raw_diagnostics"].append(original)
                if compatible is not None and selected == compatible:
                    actual, _ = _candidate_location(location, candidate, item["type"])
                    problem = {"path": prefix + _pointer(actual), "message": item["msg"]}
                    if problem not in row["context"].setdefault("violations", []):
                        row["context"]["violations"].append(problem)
                continue
            context = {"type": "object_union", **_current_context(current),
                       "allowed_forms": _union_format(forms),
                       "expected": "Use one complete allowed object form, without mixing alternative fields."}
            if compatible is not None and selected == compatible:
                actual, _ = _candidate_location(location, candidate, item["type"])
                context["violations"] = [{"path": prefix + _pointer(actual), "message": item["msg"]}]
            row = {"code": "schema", "path": path,
                   "message": "The object does not match any allowed reference or value form.",
                   "context": context, "audit": {"raw_diagnostics": [original]}}
            unions[key] = len(rows)
            if compatible is not None:
                compatible_unions.add(len(rows))
            rows.append(row)
            continue
        if candidate is not _ABSENT:
            location, current = _candidate_location(location, candidate, item["type"])
        path = prefix + _pointer(location)
        context = {"type": item["type"], "expected": item["msg"]}
        if candidate is not _ABSENT:
            context.update(_current_context(current))
        row = {"code": "schema", "path": path, "message": item["msg"], "context": context}
        identity = json.dumps(row, sort_keys=True, ensure_ascii=False, allow_nan=False)
        if identity not in seen:
            seen[identity] = len(rows)
            row["audit"] = {"raw_diagnostics": [original]}
            rows.append(row)
        else:
            rows[seen[identity]]["audit"]["raw_diagnostics"].append(original)
    # A nested object may be the sole failing part of one structurally
    # identified outer form. Keep the nested location and all raw sibling
    # alternatives, without telling a CFG citation to add source-span fields.
    removed = set()
    for index, row in enumerate(rows):
        context = row.get("context", {})
        if context.get("type") != "object_union" or context.get("violations"):
            continue
        if index not in compatible_unions:
            continue
        descendants = [other for offset, other in enumerate(rows)
                       if offset != index and other["path"].startswith(row["path"] + "/")
                       and other.get("context", {}).get("type") == "object_union"]
        if len(descendants) == 1:
            descendants[0]["audit"]["raw_diagnostics"].extend(row["audit"]["raw_diagnostics"])
            removed.add(index)
    return StructuralValidationError([row for index, row in enumerate(rows) if index not in removed])


@contextmanager
def validation_at(prefix):
    """Locate typed child errors; never catch arbitrary ValueError failures."""
    try:
        yield
    except StructuralValidationError as error:
        rows = deepcopy(error.diagnostics)
        for row in rows:
            row["path"] = prefix + row["path"]
            for original in row.get("audit", {}).get("raw_diagnostics", []):
                original["path"] = prefix + original["path"]
        raise StructuralValidationError(rows) from error
