"""Read-only JSON/string size audit; does not import SkillFlow or execute analyses."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"
OUT = Path(__file__).resolve().parent


def text(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def exact_share(payload):
    """Illustrative exact-subtree sharing, independent of production codecs."""
    counts, originals = Counter(), {}

    def visit(value):
        if isinstance(value, (dict, list, str)):
            key = text(value)
            counts[key] += 1
            originals[key] = value
        if isinstance(value, dict):
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(payload)
    if any('"$ref"' in key for key in counts):
        raise ValueError("Audit input contains reserved marker; escaping is needed")
    candidates = sorted((key for key, count in counts.items()
                         if count > 1 and len(key) > len(text({"$ref": "v0"}))),
                        key=lambda key: (len(key), key))
    chosen = set(candidates)
    while True:
        names = {key: f"v{index}" for index, key in enumerate(k for k in candidates if k in chosen)}

        def encode(value, defining=None):
            key = text(value) if isinstance(value, (dict, list, str)) else None
            if key in names and key != defining:
                return {"$ref": names[key]}
            if isinstance(value, dict):
                return {k: encode(v) for k, v in value.items()}
            if isinstance(value, list):
                return [encode(v) for v in value]
            return value

        encoded = encode(payload)
        definitions = {name: encode(originals[key], key) for key, name in names.items()}
        uses = Counter()

        def count_refs(value):
            if isinstance(value, dict):
                if set(value) == {"$ref"}:
                    uses[value["$ref"]] += 1
                else:
                    for item in value.values():
                        count_refs(item)
            elif isinstance(value, list):
                for item in value:
                    count_refs(item)

        count_refs(encoded)
        for definition in definitions.values():
            count_refs(definition)
        remove = set()
        for key, name in names.items():
            n, size = uses[name], len(text(definitions[name]))
            saving = (n - 1) * size - n * len(text({"$ref": name})) - len(text(name)) - 2
            if n < 2 or saving <= 0:
                remove.add(key)
        if not remove:
            break
        chosen.difference_update(remove)

    def expand(value):
        if isinstance(value, dict):
            if set(value) == {"$ref"}:
                return deepcopy(expand(definitions[value["$ref"]]))
            return {key: expand(item) for key, item in value.items()}
        if isinstance(value, list):
            return [expand(item) for item in value]
        return value

    assert text(expand(encoded)) == text(payload)
    envelope = {"format": "audit-exact-json-sharing-v1", "shared_values": definitions, "payload": encoded}
    return {"logical_chars": len(text(payload)), "encoded_chars": len(text(envelope)),
            "shared_definition_count": len(definitions), "exact_serialized_roundtrip": True,
            "reduction_percent": round((1-len(text(envelope))/len(text(payload)))*100, 3)}


def prompt_audit(name):
    path = RUN / "steps" / name / "calls/a001/prompt.txt"
    prompt = path.read_text(encoding="utf-8")
    sections = ["STEP RESPONSIBILITY", "PREVIOUS WORK", "GLOBAL REQUIREMENTS AND LIMITATIONS",
                "RELATED SOURCE", "OUTPUT REQUIREMENTS"]
    offsets = {key: prompt.index(key) for key in sections}
    lengths = {key: (offsets[sections[index+1]] if index+1 < len(sections) else len(prompt))-offsets[key]
               for index, key in enumerate(sections)}
    decoder = json.JSONDecoder()
    payload = {}
    payload["flow"] = prompt[prompt.index("DOCUMENT flow\n")+len("DOCUMENT flow\n"):prompt.index("\n\nCFG\n")]
    for marker, key in [("\n\nCFG\n", "cfg"), ("\n\nRUNTIME_CONTRACT\n", "runtime_contract"),
                        ("SOURCE REVIEW REPAIR\n", "repair_context")]:
        if marker in prompt:
            payload[key] = decoder.raw_decode(prompt[prompt.index(marker)+len(marker):])[0]
    source = prompt[offsets["RELATED SOURCE"]:offsets["OUTPUT REQUIREMENTS"]]
    return {"path": path.relative_to(ROOT).as_posix(), "prompt_chars": len(prompt),
            "sections_chars": lengths, "source_section_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "logical_previous_fields_chars": {key: len(text(value)) for key, value in payload.items()},
            "shared_previous_material": exact_share(payload)}


def main():
    result = {"method": "Read-only stdlib parse and exact JSON subtree-sharing size estimate; no production import, validator, backend, replay or model request.",
              "limits": "Character savings are not token savings or latency predictions; model-authored encoding adoption and generation speed remain unmeasured.",
              "run": RUN.relative_to(ROOT).as_posix(),
              "prompts": [prompt_audit(name) for name in ("processing", "revision-processing")], "responses": []}
    for relative in ("steps/processing/calls/a001/response.json", "steps/processing/calls/a002/response.json", "steps/processing/value.json"):
        value = json.loads((RUN/relative).read_text(encoding="utf-8"))
        if isinstance(value, str):
            value = json.loads(value)
        result["responses"].append({"path": relative, "modeled_ir_count": len(value["ir_semantics"]),
                                    "fields_chars": {key: len(text(item)) for key, item in value.items()},
                                    "shared_complete_response": exact_share(value)})
    destination = OUT / "design-size-evidence.json"
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(text(result))


if __name__ == "__main__":
    main()
