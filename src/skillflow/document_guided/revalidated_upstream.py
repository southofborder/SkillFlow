"""Admit the first graph answer of a failed run under a separately identified validator."""
from hashlib import sha256
from pathlib import Path, PureWindowsPath
import shutil
from tempfile import TemporaryDirectory

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.json_normalization import normalize_response
from skillflow.common.recording import canonical_sha256, implementation_provenance, now, read_json, sha_file
from skillflow.common.source_evidence import _json_object
from skillflow.common.upstream import checked_run_path, resolve_run_reference
from .accepted_stage_reader import checked_task_artifacts
from .accepted_upstream import _SOURCE, _accepted_step, _collect_tree, _inside, _relative
from .failed_stage_material import capture_failed_stage
from .graph_steps import FACTS, ROUTE_CONTRACT, validate_graph
from .online import analysis_config, checked_manifest, file_reference, read, resolve_file, seal

IDENTITY = "skillflow-revalidated-first-graph-v1"
PATH = "revalidated-upstream.json"
_CFG = "graph/initial.json"
_ASSEMBLY = "graph/initial/revalidated-assembly.json"
_CERTIFICATE = "graph/initial/controlled.json"


def _cli_calls(donor, stage, owner, prefix, config):
    from tools.doe.document_guided_client import ENVELOPE, IDENTITY as CLI, command, inspect_output
    chain = read(owner / prefix / "chain.json")
    native = donor / "transport" / stage
    expected_dirs = set()
    receipts = []
    for row in chain["attempts"]:
        call = owner / row["call"]
        logical = row["call"] + "/call.json"
        key = sha256(logical.encode()).hexdigest()
        expected_dirs.add(key)
        folder = native / key
        request, accepted = read(folder / "request.json"), read(folder / "accepted.json")
        prompt = (call / "prompt.txt").read_bytes()
        delivery = ENVELOPE.encode("utf-8") + prompt
        answer = (folder / "answer.txt").read_bytes()
        count = accepted.get("attempt")
        if (request.get("identity") != CLI or request.get("logical_call") != logical
                or request.get("runtime") != {"model": config["model"], "provider": "openai", "effort": config["reasoning_effort"]}
                or sha256(prompt).hexdigest() != request.get("core_sha256")
                or sha256(delivery).hexdigest() != request.get("delivery_sha256")
                or (folder / "prompt.txt").read_bytes() != delivery
                or sha256(answer).hexdigest() != accepted.get("answer_sha256")
                or answer.decode("utf-8") != read_json(call / "response.json")
                or type(count) is not int or not 1 <= count <= 1 + request["network_retries"]):
            raise ValueError(f"Recorded native CLI request or answer differs at {stage}/{logical}")
        attempts = {f"attempt-{n:03d}" for n in range(1, count + 1)}
        if {p.name for p in folder.glob("attempt-*") if p.is_dir()} != attempts:
            raise ValueError("Native retry inventory differs from its accepted answer")
        for number in range(1, count + 1):
            attempt = folder / f"attempt-{number:03d}"
            launch = read(attempt / "launch.json")
            argv = launch.get("command", [])
            if "--output-last-message" not in argv or argv.index("--output-last-message") + 1 >= len(argv):
                raise ValueError("Native launch has no recorded CLI output path")
            output_arg = argv[argv.index("--output-last-message") + 1]
            # The captured executable/output locations belong to the producer host.
            output = PureWindowsPath(output_arg)
            expected_command = command(argv[0], attempt, config=config)
            expected_command[0] = argv[0]
            expected_command[expected_command.index("--output-last-message") + 1] = output_arg
            if (tuple(output.parts[-5:]) != ("transport", stage, key, attempt.name, "last-message.txt")
                    or argv != expected_command
                    or launch.get("stdin_sha256") != request["delivery_sha256"]
                    or not read(attempt / "process.json").get("exited")
                    or not (attempt / "started.json").is_file()):
                raise ValueError("Native attempt lacks a bound launch or confirmed exit")
            observed = inspect_output(attempt)["answer"]
            if observed != (answer.decode("utf-8") if number == count else None):
                raise ValueError("Native retry/terminal answer differs from the durable call")
        receipts.append({"call": row["call"], "request": file_reference(donor, folder / "request.json"),
                         "accepted": file_reference(donor, folder / "accepted.json"), "native_starts": count})
    if expected_dirs != {p.name for p in native.iterdir() if p.is_dir()}:
        raise ValueError("Native stage contains unbound call owners")
    return receipts


def _describe(donor, config):
    from .runner import IDENTITY as GUIDED
    from skillflow.task.runner import load_task_run
    from tools.doe import document_guided_client
    parent = checked_manifest(donor, GUIDED)
    result = read(donor / "result.json")
    stages = result.get("stages", {})
    if (parent["config"] != config or result.get("identity") != GUIDED or result.get("status") != "failed"
            or (donor / "selection.json").exists() or "accepted_upstream" in parent or "revalidated_upstream" in parent
            or any(stages.get(k, {}).get("status") != "complete" for k in ("task", "flow"))
            or stages.get("graph", {}).get("status") != "structural_failure"):
        raise ValueError("Requires a failed direct producer with complete Task/flow and a rejected initial graph")
    src, task, flow, graph = (donor / p for p in ("source", "task", "steps/flow", "steps/graph"))
    if resolve_file(donor, parent["source"]) != src / "manifest.json":
        raise ValueError("The failed parent source owner differs")
    checked_manifest(src, _SOURCE)
    source = read_snapshot(src)[1]
    task_manifest = checked_manifest(task, read(task / "manifest.json")["identity"])
    flow_manifest = checked_manifest(flow, read(flow / "manifest.json")["identity"])
    graph_manifest = read(graph / "manifest.json")
    if (task_manifest["config"] != config or resolve_run_reference(task, task_manifest["source_owner"]) != src
            or flow_manifest.get("context", {}).keys() != {"source_owner"}
            or resolve_run_reference(flow, flow_manifest["context"]["source_owner"]) != src
            or [resolve_file(flow, ref) for ref in flow_manifest["dependencies"]] != [src / "manifest.json"]
            or graph_manifest.get("graph_route_contract") != ROUTE_CONTRACT):
        raise ValueError("Task, flow or graph is bound to a different source or protocol")
    checked_task_artifacts(task, task_manifest, read(task / "result.json"), source=source)
    task_value = load_task_run(task)["task"]
    flow_value = _accepted_step(flow, kind="flow_document", config=config, source=source)
    files = {"skill/" + row["path"]: row["content"] for row in source["files"]}
    failure = capture_failed_stage(donor, stage="graph", attempt="graph", files=files, failure=stages["graph"])
    first = failure["material"]["attempts"][0]
    owner = graph / "calls/a001"
    if first["ordinal"] != 1 or first["status"] != "structural_invalid" or (owner / "merged-candidate.json").exists():
        raise ValueError("Only the original, structurally rejected, unmerged graph answer is admissible")
    answer = read_json(owner / "response.json")
    candidate, _ = normalize_response(answer)
    value = validate_graph(FACTS, _json_object(candidate), {"files": files})
    if value["assembly"]["gaps"] or value["assembly"]["patch_diagnostics"]:
        raise ValueError("Revalidated graph still contains unresolved assembly diagnostics")
    cli = {stage: _cli_calls(donor, stage, directory, prefix, config)
           for stage, directory, prefix in (("task", task, "calls/task"), ("flow", flow, "calls"), ("graph", graph, "calls"))}
    inventory = {p: sha_file(donor / p) for p in ("manifest.json", "result.json")}
    for directory in (src, task, flow, graph, *(donor / "transport" / stage for stage in cli)):
        _collect_tree(donor, directory, inventory, source=directory == src)
    detail = {"parent_manifest_sha256": parent["manifest_sha256"], "parent_implementation": parent["implementation"],
              "config": config, "source_sha256": source["source_sha256"], "original_task": file_reference(donor, task / "task.json"),
              "original_flow": file_reference(donor, flow / "result.json"), "graph_attempt": first,
              "graph_failure_material_sha256": failure["material_sha256"], "original_graph_chain": file_reference(donor, graph / "calls/chain.json"),
              "cli_calls": cli, "files": inventory, "selected_original_calls": {"task": read(task / "result.json")["accepted_call"],
                  "flow": read(flow / "result.json")["accepted_call"], "graph": "calls/a001"},
              "original_graph_status": "structural_failure", "current_graph_status": "strictly_validated_offline",
              "native_receipt_reader_sha256": sha_file(Path(document_guided_client.__file__)),
              "fresh_normal_stages": ["processing", "task-correspondence", "sensitivity", "review"]}
    return detail, value, task_value, flow_value


def prepare(parent, *, run_dir, config=None, renderer=None):
    from .runner import IDENTITY as GUIDED, POLICY, WRITER, _certificate, _initial, _save
    donor, run = checked_run_path(parent), checked_run_path(run_dir)
    if run.exists() or run.is_relative_to(donor) or donor.is_relative_to(run):
        raise ValueError("Revalidation requires a new, separate descendant directory")
    config = analysis_config(config or read(donor / "manifest.json")["config"])
    description, value, _, _ = _describe(donor, config)
    run.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=run.parent) as staging:
        child = checked_run_path(staging) / "prepared"
        for name, digest in description["files"].items():
            original = _relative(donor, name)
            target = child / "inherited" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            if sha_file(target) != digest:
                raise ValueError("Donor changed while preparing revalidated upstream: " + name)
        shutil.copytree(child / "inherited/source", child / "source")
        WRITER.json(child / _CFG, {"cfg": value["cfg"]})
        WRITER.json(child / _ASSEMBLY, value["assembly"])
        _certificate(child, "initial", value["cfg"], False, renderer)
        accepted = {p: sha_file(child / p) for p in (_CFG, _ASSEMBLY, _CERTIFICATE)}
        implementation = implementation_provenance()
        receipt = {"identity": IDENTITY, "parent_directory": str(donor), "origin": description,
                   "validated_with": implementation["sha256"], "accepted_files": accepted}
        WRITER.json(child / PATH, receipt)
        manifest = seal({"identity": GUIDED, "created_at": now(), "policy": POLICY, "implementation": implementation,
            "config": config, "source": file_reference(child, child / "source/manifest.json"),
            "files": {PATH: sha_file(child / PATH), **accepted}, "revalidated_upstream": file_reference(child, child / PATH)})
        WRITER.json(child / "manifest.json", manifest)
        load(child, manifest)
        _save(child, _initial())
        child.rename(run)
    return manifest


def load(run, manifest):
    from .runner import IDENTITY as GUIDED
    if manifest != checked_manifest(run, GUIDED, recompute=True):
        raise ValueError("Revalidated upstream belongs to a different prepared manifest")
    ref = _inside(run, resolve_file(run, manifest["revalidated_upstream"]))
    receipt = read(ref)
    if (ref != run / PATH or set(receipt) != {"identity", "parent_directory", "origin", "validated_with", "accepted_files"}
            or receipt["identity"] != IDENTITY or receipt["validated_with"] != manifest["implementation"]["sha256"]):
        raise ValueError("Invalid offline graph revalidation identity")
    donor = _inside(run, run / "inherited")
    description, value, task, flow = _describe(donor, manifest["config"])
    if (description != receipt["origin"] or receipt["accepted_files"] != {
            p: sha_file(run / p) for p in (_CFG, _ASSEMBLY, _CERTIFICATE)}
            or read(run / _CFG) != {"cfg": value["cfg"]} or read(run / _ASSEMBLY) != value["assembly"]):
        raise ValueError("Offline graph admission disagrees with its verified original inputs")
    for name, digest in description["files"].items():
        if name.startswith("source/") and sha_file(_relative(run, name)) != digest:
            raise ValueError("Descendant source differs from the revalidated source")
    read_snapshot(run / "source")
    return {"task": {"value": task, "path": donor / "task/task.json", "owner": donor / "task"},
            "flow": {"value": flow, "path": donor / "steps/flow/result.json", "step": donor / "steps/flow"},
            "graph": {"value": value["cfg"], "path": run / _CFG, "certificate_origin": None, "origin": "revalidated_upstream"}}
