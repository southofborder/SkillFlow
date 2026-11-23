"""Read and prove accepted flow/CFG artifacts without executing a saved runner."""
from copy import deepcopy
import json

from skillflow.common.json_normalization import NORMALIZATION_VERSION, normalize_response
from skillflow.common.recording import canonical_sha256, read_json, sha_file, validated_trace, verify_request_identity
from skillflow.common.structural_correction import VERSION, correction_prompt
from skillflow.common.upstream import checked_run_path
from skillflow.common.validation import StructuralValidationError, diagnostic_materials
from .online import read, validate_step


_STRATEGIES = {
    "skillflow-document-step-v13": "skillflow-document-fragments-v8:cfg:record-replacement-v1",
    "skillflow-document-step-v14": "skillflow-document-fragments-v9:cfg:record-replacement-v1",
    "skillflow-document-step-v15": "skillflow-graph-facts-correction-v1",
    "skillflow-document-step-v16": "skillflow-graph-facts-correction-v1",
    "skillflow-document-step-v17": "skillflow-graph-facts-correction-v2",
}


def _v15_graph_correction_prompt(strategy, candidate):
    """Reconstruct the original v15 presentation for its immutable requests."""
    from skillflow.common.prompt_format import compact_json, render_prompt_format
    from .graph_slots import GRAPH_UPDATES_SCHEMA
    from .prompts import _render
    from .source import source_packet

    plan = strategy._plan(candidate)["plan"]
    return _render("Supply only the listed, missing or challenged graph facts.",
        "AUTHORIZED GRAPH SLOTS\n" + compact_json(plan),
        "Inputs, outputs, conditions and effects at the region boundary are frozen. Check the complete source. "
        "Return updates only for facts supported by the source. Leave unsupported slots unfilled; never rewrite "
        "the graph, change an unlisted slot, or invent an effect.",
        source_packet(strategy.files), "GRAPH UPDATES FORMAT\n" + render_prompt_format(GRAPH_UPDATES_SCHEMA))


def accepted_stage_value(owner, manifest, *, source):
    """Verify bounded completed request evidence and derive its accepted value.

    Old prompts and producer identities remain unchanged. A correction is
    supported only when the unchanged correction rules and current strict CFG
    validator reproduce its exact archived diagnostics, prompt and merged value.
    This function creates no client, runner, lock or file.
    """
    owner = checked_run_path(owner)
    kind, identity = manifest.get("kind"), manifest.get("identity")
    from .graph_steps import FACTS, UPDATES
    current = identity in {"skillflow-document-step-v15", "skillflow-document-step-v16", "skillflow-document-step-v17"}
    kinds = {FACTS, UPDATES} if current else {"cfg_wire_v5"}
    if identity not in _STRATEGIES or kind not in {"flow_document", *kinds}:
        raise ValueError("Unsupported accepted upstream stage protocol")
    budget = 0 if kind == UPDATES else 1
    if manifest.get("max_corrections") != budget:
        raise ValueError("Accepted upstream stage has an unsupported correction budget")
    result, chain = read(owner / "result.json"), read(owner / "calls/chain.json")
    fields = {"identity", "accepted_call", "value_file", "value_sha256", "response_chain_sha256", "counts"}
    if set(result) != fields or result["identity"] != identity:
        raise ValueError("Accepted upstream result must have the exact successful result shape")
    from .online import _bind_strategy, _step_context
    context = {"source": source, "files": {"skill/" + row["path"]: row["content"] for row in source["files"]}}
    if kind == UPDATES:
        context = _step_context(owner, manifest)
    strategy = _bind_strategy(kind, context)
    strategy_id = _STRATEGIES[identity] if strategy else None
    expected = {"version": VERSION, "normalization_policy": NORMALIZATION_VERSION, "prefix": "calls",
        "request_kind": "document_guided_" + kind, "max_corrections": budget,
        **({"correction_strategy": strategy_id} if strategy_id else {})}
    if set(chain) != {*expected, "attempts", "accepted_call"} or any(chain[key] != value for key, value in expected.items()):
        raise ValueError("Unsupported accepted upstream response-chain protocol")
    attempts = chain["attempts"]
    if (not isinstance(attempts, list) or not 1 <= len(attempts) <= budget + 1
            or chain["accepted_call"] != f"calls/a{len(attempts):03d}"
            or result["accepted_call"] != chain["accepted_call"]
            or result["response_chain_sha256"] != canonical_sha256(chain)):
        raise ValueError("Accepted upstream terminal request or correction count differs")
    directories = {path.name for path in (owner / "calls").iterdir() if path.is_dir()}
    if directories != {f"a{number:03d}" for number in range(1, len(attempts) + 1)}:
        raise ValueError("Accepted upstream has unrecorded or missing call directories")
    base = (owner / "prompt.txt").read_bytes().decode("utf-8")
    previous, value = None, None
    for number, row in enumerate(attempts, 1):
        label = f"calls/a{number:03d}"
        status = "valid" if number == len(attempts) else "structural_invalid"
        if (not isinstance(row, dict) or set(row) != {"call", "request_sha256", "call_sha256", "status", "validation_sha256"}
                or row["call"] != label or row["status"] != status):
            raise ValueError("Accepted upstream request ordering or validation status differs")
        directory = checked_run_path(owner / label)
        if not directory.is_relative_to(owner):
            raise ValueError("Accepted upstream call escapes its stage")
        if previous is None:
            prompt = base
        elif identity == "skillflow-document-step-v15" and kind == FACTS:
            prompt = _v15_graph_correction_prompt(strategy, deepcopy(previous["candidate"]))
        elif identity == "skillflow-document-step-v16" and kind == FACTS:
            from .prompts import build_graph_updates_prompt
            prompt = build_graph_updates_prompt(files=strategy.files, plan=strategy._plan(previous["candidate"])["plan"],
                                                archived_v16=True)
        elif strategy:
            prompt = strategy.build_prompt(base, deepcopy(previous["candidate"]), deepcopy(previous["diagnostics"]))
        else:
            prompt = correction_prompt(base, previous["response"], previous["diagnostics"])
        request = {"version": VERSION, "index": number, "base_request_kind": expected["request_kind"],
            "kind": expected["request_kind"] if number == 1 else "structural_correction",
            "base_prompt_sha256": canonical_sha256(base), "prompt_sha256": canonical_sha256(prompt),
            "previous": None if previous is None else {key: previous[key] for key in ("call", "response_sha256", "validation_sha256")},
            **({"correction_strategy": strategy_id} if strategy_id else {})}
        if read(directory / "request.json") != request or canonical_sha256(request) != row["request_sha256"]:
            raise ValueError("Accepted upstream request linkage or correction prompt is unsupported or changed")
        if (directory / "prompt.txt").read_bytes().decode("utf-8") != prompt:
            raise ValueError("Accepted upstream delivered prompt differs from its request")
        call, response = read(directory / "call.json"), read_json(directory / "response.json")
        trace = validated_trace(directory / "transport.json")
        if (sha_file(directory / "call.json") != row["call_sha256"] or call.get("status") != "complete"
                or call.get("recording_failed") or call.get("response_rejected") or not call.get("finished_at")
                or call.get("response") != response or call.get("response_sha256") != canonical_sha256(response)
                or len(trace) != 1 or trace[0].get("status") != "complete"
                or trace[0].get("recording_failed") or trace[0].get("response_rejected")
                or trace[0].get("response") != response):
            raise ValueError("Accepted upstream complete response and transport evidence disagree")
        verify_request_identity(directory, manifest["config"], prompt=prompt)
        candidate, normalization = normalize_response(response)
        normalization_path = directory / "normalization.json"
        if ((normalization is None and normalization_path.exists())
                or (normalization is not None and (not normalization_path.is_file() or read(normalization_path) != normalization))):
            raise ValueError("Accepted upstream normalization receipt differs")
        merged = directory / "merged-candidate.json"
        if previous is not None and strategy:
            candidate = strategy.merge(deepcopy(previous["candidate"]), candidate)
            if not merged.is_file() or read_json(merged) != candidate:
                raise ValueError("Accepted upstream corrected candidate differs from the recorded merge")
        elif merged.exists():
            raise ValueError("Accepted upstream has a merge outside a supported correction")
        validation = {"version": VERSION, "response_sha256": canonical_sha256(response),
            "candidate_sha256": canonical_sha256(candidate),
            "normalization_sha256": None if normalization is None else canonical_sha256(normalization), "status": status}
        try:
            value = validate_step(kind, candidate, context=context)
        except StructuralValidationError as error:
            if status != "structural_invalid":
                raise ValueError("Accepted upstream candidate no longer passes strict validation") from error
            validation.update(diagnostic_materials(error.diagnostics))
            diagnostics = deepcopy(error.diagnostics)
        else:
            if status != "valid":
                raise ValueError("Archived upstream rejection is not reproduced by supported correction rules")
            diagnostics = []
        if read(directory / "validation.json") != validation or canonical_sha256(validation) != row["validation_sha256"]:
            raise ValueError("Accepted upstream validation evidence is unsupported or changed")
        previous = {"call": label, "response": deepcopy(response), "candidate": deepcopy(candidate), "diagnostics": diagnostics,
            "response_sha256": canonical_sha256(response), "validation_sha256": canonical_sha256(validation)}
    filename = "document.md" if kind == "flow_document" else "value.json"
    cached = ((owner / filename).read_bytes().decode("utf-8") if kind == "flow_document" else read(owner / filename))
    if result["value_file"] != filename or result["value_sha256"] != sha_file(owner / filename) or cached != value:
        raise ValueError("Accepted upstream cached value differs from its actual accepted response")
    return value


def checked_task_artifacts(owner, manifest, result, *, source):
    """Check Task's structural chain only; semantic reading remains copy-only."""
    from skillflow.propagation.contracts.task import TASK_SCHEMA_VERSION
    from skillflow.task.runner import _policy
    policy = manifest.get("policy", {})
    if (manifest.get("schema_version") != 3 or manifest.get("task_schema_version") != TASK_SCHEMA_VERSION
            or manifest.get("preparation_status") != "ready" or manifest.get("source_sha256") != source["source_sha256"]
            or policy != _policy(1, allow_cannot_assess=False, self_check=True)
            or manifest.get("request_kind") not in {"task_extraction", "task_revision"}):
        raise ValueError("Unsupported accepted Task producer or source-only policy")
    base = (owner / "inputs/prompt.txt").read_bytes().decode("utf-8")
    if manifest.get("prompt_sha256") != canonical_sha256(base):
        raise ValueError("Accepted Task base prompt changed")
    chain = read(owner / "calls/task/chain.json")
    expected = {"version": VERSION, "normalization_policy": NORMALIZATION_VERSION, "prefix": "calls/task",
        "request_kind": manifest["request_kind"], "max_corrections": 1,
        "correction_strategy": "skillflow-document-fragments-v8:task:record-replacement-v1"}
    attempts = chain.get("attempts")
    if (set(chain) != {*expected, "attempts", "accepted_call"} or any(chain[key] != value for key, value in expected.items())
            or not isinstance(attempts, list) or not 1 <= len(attempts) <= 2
            or chain["accepted_call"] != f"calls/task/a{len(attempts):03d}"
            or result.get("response_chain") != chain or result.get("accepted_call") != chain["accepted_call"]
            or result.get("source_sha256") != source["source_sha256"]):
        raise ValueError("Accepted Task request chain or source binding differs")
    actual = {path.name for path in (owner / "calls/task").iterdir() if path.is_dir()}
    if actual != {f"a{number:03d}" for number in range(1, len(attempts) + 1)}:
        raise ValueError("Accepted Task has unrecorded call directories")
    previous = None
    for number, row in enumerate(attempts, 1):
        label = f"calls/task/a{number:03d}"
        status = "valid" if number == len(attempts) else "structural_invalid"
        if (not isinstance(row, dict) or set(row) != {"call", "status", "request_sha256", "call_sha256", "validation_sha256"}
                or row["call"] != label or row["status"] != status):
            raise ValueError("Accepted Task request order or status differs")
        directory = checked_run_path(owner / label)
        prompt = (directory / "prompt.txt").read_bytes().decode("utf-8")
        request = {"version": VERSION, "index": number, "base_request_kind": manifest["request_kind"],
            "kind": manifest["request_kind"] if number == 1 else "structural_correction",
            "base_prompt_sha256": canonical_sha256(base), "prompt_sha256": canonical_sha256(prompt),
            "previous": previous, "correction_strategy": expected["correction_strategy"]}
        if (number == 1 and prompt != base or read(directory / "request.json") != request
                or canonical_sha256(request) != row["request_sha256"]):
            raise ValueError("Accepted Task request linkage differs")
        call, response, validation = read(directory / "call.json"), read_json(directory / "response.json"), read(directory / "validation.json")
        trace = validated_trace(directory / "transport.json")
        if (sha_file(directory / "call.json") != row["call_sha256"] or call.get("status") != "complete"
                or call.get("recording_failed") or call.get("response_rejected") or not call.get("finished_at")
                or call.get("response") != response or call.get("response_sha256") != canonical_sha256(response)
                or len(trace) != 1 or trace[0].get("status") != "complete" or trace[0].get("response") != response
                or trace[0].get("recording_failed") or trace[0].get("response_rejected")):
            raise ValueError("Accepted Task response and transport evidence disagree")
        verify_request_identity(directory, manifest["config"], prompt=prompt)
        candidate, normalization = normalize_response(response)
        normalization_path = directory / "normalization.json"
        if ((normalization is None and normalization_path.exists()) or normalization is not None
                and (not normalization_path.is_file() or read(normalization_path) != normalization)):
            raise ValueError("Accepted Task normalization differs")
        merged = directory / "merged-candidate.json"
        if number == 2:
            candidate = read_json(merged)
        elif merged.exists():
            raise ValueError("Accepted Task has an unexpected merged candidate")
        bindings = {"version": VERSION, "response_sha256": canonical_sha256(response),
            "candidate_sha256": canonical_sha256(candidate), "normalization_sha256": None if normalization is None else canonical_sha256(normalization),
            "status": status}
        if (any(validation.get(key) != value for key, value in bindings.items())
                or canonical_sha256(validation) != row["validation_sha256"]):
            raise ValueError("Accepted Task validation linkage differs")
        previous = {"call": label, "response_sha256": canonical_sha256(response), "validation_sha256": canonical_sha256(validation)}
