"""Lossless schema *instructions* and marked sections for model requests.

This is not a second validator. The real JSON Schema and application validators
remain authoritative. Unsupported schema keywords fail rather than disappear.
"""
from __future__ import annotations

import json
import re
from typing import Any


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def prompt_block(name: str, body: str) -> str:
    if not re.fullmatch(r"[A-Z_]+", name):
        raise ValueError("invalid prompt section name")
    return f"<!-- SKILLFLOW_PROMPT:{name}:BEGIN -->\n{body.strip()}\n<!-- SKILLFLOW_PROMPT:{name}:END -->"


_KEYWORDS = frozenset({
    "$defs", "$ref", "title", "description", "type", "properties", "required",
    "additionalProperties", "patternProperties", "items", "prefixItems", "anyOf",
    "oneOf", "allOf", "enum", "const", "default", "discriminator", "minimum",
    "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "minLength",
    "maxLength", "pattern", "minItems", "maxItems", "uniqueItems", "minProperties",
    "maxProperties",
})
_LIMITS = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
           "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems",
           "minProperties", "maxProperties")


def render_prompt_format(schema: dict[str, Any]) -> str:
    """Render all current validation keywords, defining each named type once.

    ``?`` means omission is allowed, not that null is allowed. Union/intersection
    semantics, numeric/string limits, defaults and object openness stay explicit.
    JSON-Schema titles are presentation metadata and are deliberately omitted.
    """
    definitions = schema.get("$defs", {})
    if not isinstance(definitions, dict):
        raise ValueError("$defs must be a mapping")

    def reference(ref: str) -> str:
        if not isinstance(ref, str) or not ref.startswith("#/$defs/"):
            raise ValueError("only local named schema references are supported")
        name = ref[len("#/$defs/"):].replace("~1", "/").replace("~0", "~")
        if name not in definitions:
            raise ValueError(f"missing schema definition: {name}")
        return name

    def render(node: Any, path: str, *, root: bool = False) -> str:
        if isinstance(node, bool):
            return "JSON" if node else "FORBIDDEN"
        if not isinstance(node, dict):
            raise ValueError(f"invalid schema node at {path}")
        unknown = set(node) - _KEYWORDS
        if unknown:
            raise ValueError(f"unsupported schema keywords at {path}: {sorted(unknown)}")
        if "$defs" in node and not root:
            raise ValueError(f"nested definitions are not supported at {path}")
        typ = node.get("type")
        object_keys = {"properties", "required", "additionalProperties", "patternProperties"}
        array_keys = {"items", "prefixItems"}
        # Do not silently turn a conditional object/array constraint into a type
        # restriction, or discard the other members of a type union.
        if object_keys.intersection(node) and typ != "object":
            raise ValueError(f"object keywords require explicit object type at {path}")
        if array_keys.intersection(node) and typ != "array":
            raise ValueError(f"array keywords require explicit array type at {path}")
        types = typ if isinstance(typ, list) else ([] if typ is None else [typ])
        if any(t not in {"object", "array", "string", "integer", "number", "boolean", "null"} for t in types):
            raise ValueError(f"unsupported schema type at {path}")
        terms = []
        if "$ref" in node:
            terms.append(reference(node["$ref"]))
        for union, label in (("anyOf", "ANY"), ("oneOf", "ONE"), ("allOf", "ALL")):
            if union in node:
                terms.append(label + "(" + " | ".join(
                    render(child, f"{path}/{union}/{index}")
                    for index, child in enumerate(node[union])) + ")")
        if typ == "object":
            props = node.get("properties", {})
            required = set(node.get("required", []))
            fields = [f"{compact_json(key)}{'' if key in required else '?'}:{render(value, path + '/properties/' + key)}"
                      for key, value in props.items()]
            fields.extend(f"/{compact_json(pattern)}/:{render(value, path + '/patternProperties/' + pattern)}"
                          for pattern, value in node.get("patternProperties", {}).items())
            fields.append("extra:" + render(node.get("additionalProperties", True), path + "/additionalProperties"))
            if required - set(props):
                fields.append("required:" + compact_json(sorted(required - set(props))))
            terms.append("{" + ",".join(fields) + "}")
        elif typ == "array":
            prefix = [render(child, f"{path}/prefixItems/{index}")
                      for index, child in enumerate(node.get("prefixItems", []))]
            prefix.append("..." + render(node.get("items", True), path + "/items"))
            terms.append("[" + ",".join(prefix) + "]")
        elif typ is not None:
            terms.append(compact_json(typ) if isinstance(typ, list) else str(typ))
        if "enum" in node:
            terms.append("enum=" + compact_json(node["enum"]))
        if "const" in node:
            terms.append("const=" + compact_json(node["const"]))
        for key in _LIMITS:
            if key in node:
                terms.append(key + "=" + compact_json(node[key]))
        if "default" in node:
            terms.append("default=" + compact_json(node["default"]))
        if "description" in node:
            terms.append("meaning=" + compact_json(node["description"]))
        if "discriminator" in node:
            discriminator = node["discriminator"]
            if (not isinstance(discriminator, dict)
                    or set(discriminator) - {"propertyName", "mapping"}
                    or not isinstance(discriminator.get("propertyName"), str)):
                raise ValueError(f"unsupported discriminator at {path}")
            mapping = {key: reference(value) for key, value in discriminator.get("mapping", {}).items()}
            terms.append("tag=" + compact_json(discriminator["propertyName"]) + ":" + compact_json(mapping))
        return " & ".join(terms) if terms else "JSON"

    body = ["Format notation: fields are required unless suffixed ?. Omission is distinct from null. "
            "ANY allows one or more branches; ONE exactly one; ALL and & require all constraints. "
            "extra:FORBIDDEN rejects unknown object keys; extra:JSON permits them. "
            "Arrays preserve order; ... describes each remaining item. Defaults apply only on omission. "
            "JSON means any JSON value. pattern is a regular-expression constraint. "
            "Named types below are definitions, not additional response fields. Application rules follow.",
            "RESPONSE = " + render(schema, "$", root=True)]
    body.extend(name + " = " + render(node, "$/$defs/" + name)
                for name, node in definitions.items())
    return "\n".join(body)
