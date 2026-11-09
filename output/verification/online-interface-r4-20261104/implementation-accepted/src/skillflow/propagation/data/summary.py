"""Finite shape queries through immutable loop/selection relation views.

Never unfold recursive accumulations or execute user opcodes. Re-entering a
family leaves shape unknown, while explicit finite source lists remain exact.
"""
from __future__ import annotations


def content_options(data, identity, seen=frozenset()):
    if identity in seen:
        return [{"form": "opaque"}]
    value = data.get(identity)
    value = value.model_dump(mode="json") if hasattr(value, "model_dump") else value
    return _contents(data, value["content"], seen | {identity})


def _contents(data, content, seen):
    if content["form"] == "loop_summary":
        return [result for variant in content["variants"] for result in _contents(data, variant["content"], seen)] or [{"form": "opaque"}]
    if content["form"] == "selection":
        return _select(data, content["base"], content["path"], seen)
    return [content]


def _select(data, base, path, seen):
    values = content_options(data, base, seen)
    if not path:
        return values
    result = []
    for content in values:
        form = content["form"]
        if form == "literal":
            pending = [content["value"]]
            for step in path:
                selected = []
                for value in pending:
                    if type(step) is int and type(value) is list and 0 <= step < len(value):
                        selected.append(value[step])
                    elif type(step) is str and type(value) is dict and step in value:
                        selected.append(value[step])
                    elif type(step) is dict and step.get("kind") == "element" and type(value) is list:
                        selected.extend(value)
                pending = selected
            result.extend({"form": "literal", "value": value} for value in pending)
        elif form == "known_parts":
            matching = [part for part in content["parts"] if path[:len(part["path"])] == part["path"]]
            descendants = [part for part in content["parts"] if part["path"][:len(path)] == path and len(part["path"]) > len(path)]
            for part in matching:
                result.extend(_select(data, part["data"], path[len(part["path"]):], seen))
            if not matching and descendants:
                result.append({"form": "known_parts", "parts_complete": content.get("parts_complete", False),
                    "parts": [{"path": part["path"][len(path):], "data": part["data"]} for part in descendants]})
            elif not matching and not content.get("parts_complete"):
                result.append({"form": "opaque"})
        elif form == "whole_except":
            if not any(path[:len(excluded)] == excluded for excluded in content["excluded_parts"]):
                result.extend(_select(data, content["base"], path, seen))
        elif form == "field_updates":
            updates = [part for part in content["updates"] if path[:len(part["path"])] == part["path"]]
            if updates:
                for part in updates:
                    result.extend(_select(data, part["data"], path[len(part["path"]):], seen))
            elif any(part["path"][:len(path)] == path for part in content["updates"]):
                # Selecting an ancestor includes these updates. Returning its
                # old base could incorrectly prove an empty collection.
                result.append({"form": "opaque"})
            else:
                result.extend(_select(data, content["base"], path, seen))
        else:
            result.append({"form": "opaque"})
    return result
