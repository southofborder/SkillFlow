"""Measure public guided schemas without invoking a model or a Skill.

Counts describe unique schema definitions, not per-response tokens or an upper
bound on emitted records. Use a frozen implementation's src directory to obtain
a historical comparison without modifying or replaying its run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Measuring an archived implementation must not add interpreter cache files to it.
sys.dont_write_bytecode = True


def schema_counts(schema):
    result = {"property_slots": 0, "required_property_slots": 0, "union_branches": 0}

    def visit(value):
        if isinstance(value, dict):
            result["property_slots"] += len(value.get("properties", {}))
            result["required_property_slots"] += len(value.get("required", []))
            result["union_branches"] += sum(len(value.get(k, [])) for k in ("oneOf", "anyOf"))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(schema)
    return result


def measure():
    from skillflow.common.prompt_format import render_prompt_format
    from skillflow.document_guided.cfg_wire import CFGWire
    from skillflow.document_guided.fragments import fragment_adapter
    from skillflow.document_guided.prompts import build_compact_graph_prompt, build_fragment_prompt
    from skillflow.propagation.contracts.runtime_contract import runtime_contract

    schemas = {"cfg": CFGWire.model_json_schema(), **{
        kind: fragment_adapter(kind).json_schema()
        for kind in ("processing", "task-correspondence", "sensitivity")}}
    files = {"skill/SKILL.md": "Analyze the supplied source and retain actual data boundaries.\n"}
    shared = {"files": files, "global_requirements": "Preserve source-supported relationships.", "self_check": True}
    flow = {"flow": "Inspect skill/SKILL.md:1-1."}
    processing = {"ir_semantics": {}, "locations": {}, "expressions": [], "processing_gaps": []}
    cfg = {"entry_block_id": "entry", "blocks": {}, "edges": [], "constraints": [], "declared_context_keys": []}
    prompts = {"cfg": build_compact_graph_prompt(documents=flow, **shared)}
    for kind in ("processing", "task-correspondence", "sensitivity"):
        prompts[kind] = build_fragment_prompt(kind, cfg=cfg,
            documents=flow if kind == "processing" else {"processing": processing},
            runtime_contract=runtime_contract() if kind == "processing" else None,
            task={"purpose": {}, "requirements": [], "issues": []} if kind == "task-correspondence" else None,
            **shared)
    extra = {}
    try:
        from skillflow.document_guided.cfg_wire import cfg_contract_rules
        from skillflow.document_guided.fragments import fragment_contract_rules
        from skillflow.document_guided.interface_examples import phase_examples
        for kind in schemas:
            rules = cfg_contract_rules() if kind == "cfg" else fragment_contract_rules(kind)
            extra[kind] = {"cross_field_rule_chars": len(rules),
                           "validated_example_chars": len(phase_examples(kind))}
    except ImportError:
        # Historical implementations did not publish these measured sections.
        # The complete prompt length remains comparable using the same context.
        pass
    return {"measurement": "schema_definitions_and_identical_minimal_context_not_token_counts",
        "phases": {kind: {**schema_counts(schema), **extra.get(kind, {}),
            "schema_json_chars": len(json.dumps(schema, ensure_ascii=False, separators=(",", ":"))),
            "format_instruction_chars": len(render_prompt_format(schema)),
            "output_requirements_chars": len(prompts[kind].split("OUTPUT REQUIREMENTS\n", 1)[1]),
            "minimal_context_prompt_chars": len(prompts[kind])}
            for kind, schema in schemas.items()}, "model_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Read a frozen implementation src directory")
    args = parser.parse_args()
    if args.source_root is not None:
        sys.path.insert(0, str(args.source_root.resolve(strict=True)))
    print(json.dumps(measure(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
