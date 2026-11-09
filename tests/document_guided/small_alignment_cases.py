"""Source-derived, authored v9 candidates. No model or Skill execution.

Concrete inputs are test inputs, not invented source constants. Original v8
answers remain untouched. Each candidate retains the frozen source package.
"""
from copy import deepcopy
from pathlib import Path

from skillflow.common.inputs.snapshot import _describe
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files


ROOT = Path(__file__).parents[1] / "fixtures/cfg_processing_alignment_v9"
UNKNOWN = object()


def inp(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def lit(value):
    return {"kind": "literal", "value": value}


def operand(name, kind="result"):
    return {"type": kind, "identifier": name}


def ir(name, inputs=(), outputs=(), opcode=None):
    return {"id": "ir_" + name, "opcode": opcode or name,
            "inputs": list(inputs), "outputs": [operand(value) for value in outputs]}


def graph(blocks, edges=(), entry="entry"):
    return {"entry_block_id": entry, "blocks": {
        name: {"block_id": name, "block_name": name, "instructions": rows}
        for name, rows in blocks.items()}, "edges": [
        {"source_block_id": left, "target_block_id": right} for left, right in edges]}


def evidence(case, line=1, end=None):
    return {"file": "skill/" + ("references/workflow.md" if case == "010" else "SKILL.md"),
            "start_line": line, "end_line": end or line,
            "reason": "Source-backed authored interface regression; reference validity is not a model accuracy measurement."}


def spec(case, ops=(), outputs=(), *, line=1, gaps=None):
    return {"evidences": [evidence(case, line)],
            "segments": [{"mode": "local", "returns": [], "ops": list(ops)}] if ops else [],
            "output_bindings": [{"output_index": i, "value": value} for i, value in enumerate(outputs)]}


def location(case, kind, name, *, line=1):
    return {"kind": kind, "name": name, "evidences": [evidence(case, line)]}


def base(case, cfg, semantics, locations, *, issues=(), requirement=None, additional_requirements=()):
    directory = ROOT / case
    rows = [(path.relative_to(directory).as_posix(), path.read_bytes())
            for path in sorted(directory.rglob("*")) if path.is_file()]
    rows.sort(key=lambda row: row[0])
    _, source, _ = _describe({"original_path": str(directory), "storage": "authored-source-regression",
        "root_name": case, "archive_sha256": None}, rows)
    text = requirement or {"001": "Notify selected records using their own recipient and original summary; save the processed-record count.",
        "010": "Call search with original required and present optional values; save response.total and return response.items unchanged.",
        "013": "Fetch with the credential-gated preferred tool and bounded fallback; append the final status before returning."}[case]
    candidate = {"purpose": {"text": text, "evidences": [evidence(case)]},
        "requirements": [{"id": "R1", "text": text, "evidences": [evidence(case)]}, *additional_requirements], "issues": list(issues)}
    task = validate_task_candidate(candidate, source_files=task_source_files(source), source_sha256=source["source_sha256"])
    material = prepare_material(source, cfg, task_baseline=task)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": row["id"]} for row in candidate["requirements"]],
        "demands": [], "locations": locations, "ir_semantics": semantics}
    return material, wire


def goal(target, *, kind="input", index=0, path=None, preserve="value", reason="Preserve this actual required endpoint value."):
    value = {"requirement_id": "R1", "target": {"kind": kind, **({"index": index} if kind == "input" else {})},
             "preserve": preserve, "reason": reason}
    if path is not None:
        value["path"] = path
    target.setdefault("demands", []).append(value)


def catalog_fixture(from_date=False, limit=False, *, save_mode=None):
    case = "010"
    cfg = graph({"entry": [ir("acquire", [operand("request.json", "external_resource")], ["request"]),
        ir("search", [operand("request")], ["response"]),
        ir("select", [operand("response")], ["total", "items"]),
        ir("save", [operand("total")]), ir("return", [operand("items")], opcode="return")]})
    # Explicit test inputs exercise all four optional member combinations.
    request = {"term": "original term"}
    if from_date:
        request["from_date"] = "2026-11-02"
    if limit:
        request["limit"] = 7
    parts = [{"path": ["query"], "value": local("term")}]
    select = [{"op": "select_part", "input": inp(), "path": ["term"], "output": "term"}]
    for name, present in (("from_date", from_date), ("limit", limit)):
        if present:
            select.append({"op": "select_part", "input": inp(), "path": [name], "output": name})
            parts.append({"path": [name], "value": local(name)})
    build = {"op": "build", "container": "object", "parts": parts, "output": "arguments"}
    call = {"op": "call", "location": "search", "inputs": [local("arguments")], "output": "response"}
    goal(call)
    write = {"op": "write", "target": "count", "input": inp()}
    if save_mode is not None:
        write["mode"] = save_mode
    goal(write)
    semantics = {
        "ir_acquire": spec(case, [{"op": "read", "location": "request", "output": "request"}], [local("request")], line=5),
        "ir_search": spec(case, [*select, build, call], [local("response")], line=7),
        "ir_select": spec(case, [{"op": "select_part", "input": inp(), "path": [name], "output": name}
                                      for name in ("total", "items")], [local("total"), local("items")], line=21),
        "ir_save": spec(case, [write], line=21), "ir_return": spec(case, line=23)}
    locations = {"request": location(case, "storage", "request.json", line=5),
        "search": location(case, "tool", "index.search", line=7), "count": location(case, "storage", "count.txt", line=21)}
    material, wire = base(case, cfg, semantics, locations)
    wire["demands"].append({"requirement_id": "R1", "target": {"instruction_id": "ir_return", "side": "input", "index": 0},
                            "preserve": "value", "reason": "Return the actual response.items value unchanged."})
    return material, wire, {("storage", "request.json"): request}


def catalog_sensitive_variant(*, required=False):
    """Separate declared-sensitivity mutation, never an online target input."""
    import hashlib
    from skillflow.common.source_evidence import _digest
    material, wire, seeds = catalog_fixture()
    source = deepcopy(material["source"])
    text = ("Independent offline variant: request.json contains private_note, a sensitive private note. "
            "Additionally send request.term unchanged as query to diagnostic.send. "
            + ("This variant also requires diagnostic.send to receive private_note unchanged."
               if required else "Only query is required by diagnostic.send; private_note is not required."))
    source["files"].append({"path": "offline-variant.md", "content": text,
                             "sha256": hashlib.sha256(text.encode()).hexdigest()})
    source["files"].sort(key=lambda row: row["path"])
    source["source_sha256"] = _digest([{"path": row["path"], "sha256": row["sha256"]} for row in source["files"]])
    ev = {"file": "skill/offline-variant.md", "start_line": 1, "end_line": 1,
          "reason": "Explicit independent variant sensitivity/requirement, not a label for the frozen original."}
    candidate = {key: deepcopy(material["task"][key]) for key in ("purpose", "requirements", "issues")}
    candidate["requirements"][0]["text"] += " Send query to diagnostic.send." + (" Also send private_note unchanged." if required else "")
    candidate["requirements"][0]["evidences"].append(ev)
    task = validate_task_candidate(candidate, source_files=task_source_files(source), source_sha256=source["source_sha256"])
    cfg = deepcopy(material["cfg"])
    cfg["blocks"]["entry"]["instructions"].insert(2, ir("diagnostic", [operand("request")]))
    material = prepare_material(source, cfg, task_baseline=task)
    seeds[("storage", "request.json")]["private_note"] = "sensitive-note"
    delivery = {"op": "deliver", "target": "diagnostic", "inputs": [local("arguments")]}
    goal(delivery, path=["query"])
    if required:
        goal(delivery, path=["private_note"], reason="The independent variant explicitly requires this sensitive parameter.")
    wire["locations"]["diagnostic"] = {"kind": "tool", "name": "diagnostic.send", "evidences": [ev]}
    wire["ir_semantics"]["ir_diagnostic"] = {"evidences": [ev], "segments": [{"mode": "local", "returns": [], "ops": [
        {"op": "select_part", "input": inp(), "path": ["term"], "output": "query"},
        {"op": "select_part", "input": inp(), "path": ["private_note"], "output": "private_note"},
        {"op": "build", "container": "object", "parts": [
            {"path": ["query"], "value": local("query")}, {"path": ["private_note"], "value": local("private_note")}], "output": "arguments"}, delivery]}]}
    wire["ir_semantics"]["ir_acquire"]["sensitivity"] = [{"value": local("request"), "path": ["private_note"],
        "label": "Explicit variant private note", "evidences": [ev]}]
    return material, wire, seeds


def notification_fixture(records=None, *, leak=False):
    case = "001"
    records = records if records is not None else [
        {"recipient": "a", "summary": "one", "record_id": "r", "value": 101, "urgent": False, "opted_out": False, "access_token": "private"},
        {"recipient": "a", "summary": "one", "record_id": "r", "value": 101, "urgent": False, "opted_out": False, "access_token": "private"},
        {"recipient": "b", "summary": "two", "record_id": "s", "value": 1, "urgent": True, "opted_out": False, "access_token": "other"}]
    cfg = graph({"entry": [ir("acquire", [operand("events.json", "external_resource")], ["records"]),
                ir("filter", [operand("records")], ["selected"]), ir("start", opcode="dispatch")],
        "head": [ir("guard", [operand("selected")], opcode="dispatch")],
        "body": [ir("member", [operand("selected")], ["record"]),
                 ir("notify", [operand("record")]), ir("back", opcode="dispatch")],
        "exit": [ir("count", [operand("records"), operand("selected")], ["count"]),
                 ir("save", [operand("count")]), ir("return", opcode="return")]},
        [("entry", "head"), ("head", "body"), ("head", "exit"), ("body", "head")])
    ref = {"op": "ref", "value": inp()}
    field = lambda name: {"op": "field", "arg": ref, "path": [name]}
    predicate = {"op": "and", "args": [
        {"op": "ne", "left": field("opted_out"), "right": {"op": "literal", "value": True}},
        {"op": "or", "args": [{"op": "eq", "left": field("urgent"), "right": {"op": "literal", "value": True}},
                               {"op": "ge", "left": field("value"), "right": {"op": "literal", "value": 100}}]}]}
    selects = [{"op": "select_part", "input": inp(), "path": [name], "output": name}
               for name in ("recipient", "summary", "access_token")]
    parts = [{"path": ["recipient"], "value": local("recipient")}, {"path": ["body"], "value": local("summary")}]
    if leak:
        parts.append({"path": ["access_token"], "value": local("access_token")})
    call = {"op": "call", "location": "notify", "inputs": [local("arguments")], "output": "ack"}
    goal(call, path=["recipient"])
    goal(call, path=["body"])
    semantics = {"ir_acquire": spec(case, [{"op": "read", "location": "events", "output": "records"}], [local("records")], line=8),
        "ir_filter": spec(case, [{"op": "filter_items", "input": inp(), "predicate": "opted_out is not true AND (urgent is true OR value >= 100)",
            "expression": {"expression": predicate}, "output": "selected"}], [local("selected")], line=9),
        "ir_start": spec(case), "ir_guard": spec(case, [{"op": "branch", "input": inp(), "predicate": "has_member", "true_target": "body", "false_target": "exit"}], line=11),
        "ir_member": spec(case, [{"op": "member", "input": inp(), "output": "record"}], [local("record")], line=11),
        "ir_notify": spec(case, [*selects, {"op": "build", "container": "object", "parts": parts, "output": "arguments"}, call], line=11),
        "ir_back": spec(case), "ir_count": spec(case, [{"op": "compute", "inputs": [inp(), inp(1)], "output": "count"}], [local("count")], line=16),
        "ir_save": spec(case, [{"op": "write", "target": "count", "input": inp()}], line=16), "ir_return": spec(case)}
    semantics["ir_acquire"]["sensitivity"] = [{"value": local("records"), "path": [{"kind": "each"}, "access_token"], "label": "Recipient-prohibited access token", "evidences": [evidence(case, 14)]}]
    issue = {"id": "count-scope", "kind": "ambiguity", "requirement_ids": ["R_COUNT"], "resolution": "unresolved",
        "reason": "Processed records does not uniquely specify all input records versus selected/notified records.", "evidences": [evidence(case, 16)]}
    material, wire = base(case, cfg, semantics, {"events": location(case, "storage", "events.json", line=8),
        "notify": location(case, "tool", "notify.send", line=11), "count": location(case, "storage", "count.txt", line=16)}, issues=[issue],
        requirement="Notify each selected record using its original recipient and summary; never send access_token.",
        additional_requirements=[{"id": "R_COUNT", "text": "Write the number of processed records to count.txt.", "evidences": [evidence(case, 16)]}])
    wire["realizations"][1]["gaps"] = [{"reason": issue["reason"], "evidences": issue["evidences"]}]
    return material, wire, {("storage", "events.json"): records}


def fallback_fixture(*, key=True, first=True, transient=False, retry=False, archive=True):
    case = "013"
    blocks = {"entry": [ir("context", [operand("source_id", "context_key"), operand("FAST_KEY", "context_key")], ["source", "key", "has_key"]), ir("key_guard", [operand("has_key")], opcode="dispatch")],
        "fast": [ir("fast", [operand("source"), operand("key")], ["first_body", "first_success", "first_transient"]), ir("first_guard", [operand("first_success")], opcode="dispatch")],
        "failure": [ir("transient_guard", [operand("first_transient")], opcode="dispatch")],
        "retry": [ir("retry", [operand("source"), operand("key")], ["retry_body", "retry_success"]), ir("retry_guard", [operand("retry_success")], opcode="dispatch")],
        "archive": [ir("archive", [operand("source")], ["archive_body", "archive_error", "archive_success"]), ir("archive_guard", [operand("archive_success")], opcode="dispatch")]}
    terminals = {"first_done": ("first_body", "fast_success"), "retry_done": ("retry_body", "retry_success"),
                 "archive_done": ("archive_body", "archive_success"), "archive_failed": ("archive_error", "archive_failure")}
    for block, (value, status) in terminals.items():
        blocks[block] = [ir(block + "_status"), ir(block + "_return", [operand(value)], opcode="return")]
    edges = [("entry", "fast"), ("entry", "archive"), ("fast", "first_done"), ("fast", "failure"),
        ("failure", "retry"), ("failure", "archive"), ("retry", "retry_done"), ("retry", "archive"),
        ("archive", "archive_done"), ("archive", "archive_failed")]
    cfg = graph(blocks, edges)
    cfg["declared_context_keys"] = ["source_id", "FAST_KEY"]
    cfg["blocks"]["entry"]["data_source_kind"] = "context"
    semantics = {"ir_context": spec(case, [{"op": "read", "location": "source", "output": "source"},
        {"op": "read", "location": "key", "output": "key"}], [local("source"), local("key"), lit(key)], line=8)}
    guards = {"key_guard": ("fast", "archive"), "first_guard": ("first_done", "failure"),
              "transient_guard": ("retry", "archive"), "retry_guard": ("retry_done", "archive"),
              "archive_guard": ("archive_done", "archive_failed")}
    for name, (yes, no) in guards.items():
        semantics["ir_" + name] = spec(case, [{"op": "branch", "input": inp(), "predicate": "truthy", "true_target": yes, "false_target": no}], line=9)
    for name, succeeds, credential in (("fast", first, True), ("retry", retry, True), ("archive", archive, False)):
        arguments = [inp(), inp(1)] if credential else [inp()]
        boundary = name if name == "archive" else "fast"
        operations = [{"op": "call", "location": boundary, "inputs": arguments, "output": "response"}
                      if succeeds else {"op": "deliver", "target": boundary, "inputs": arguments}]
        for index in range(len(arguments)):
            goal(operations[0], index=index)
        # The actual error is separately acquired at the protected boundary;
        # it is never projected from the normal response or computed from ID.
        if not succeeds:
            operations += [{"op": "receive", "location": name + "_error", "inputs": [], "output": "error"}]
        else:
            operations += [{"op": "select_part", "input": local("response"), "path": ["body"], "output": "body"}]
        if name == "fast":
            outputs = [local("body") if succeeds else local("error"), lit(succeeds), lit(transient)]
        elif name == "retry":
            outputs = [local("body") if succeeds else local("error"), lit(succeeds)]
        else:
            outputs = [local("body") if succeeds else local("error"), local("error") if not succeeds else local("body"), lit(succeeds)]
        semantics["ir_" + name] = spec(case, operations, outputs, line=9 if credential else 12)
    for block, (value, status) in terminals.items():
        write = {"op": "write", "target": "status", "mode": "append", "input": lit(status)}
        goal(write)
        # Append consumes the previous storage version. Normal solver seeding
        # supplies unknown content; explicit test state supplies the same source.
        semantics["ir_" + block + "_status"] = spec(case, [write], line=16)
        semantics["ir_" + block + "_return"] = spec(case, line=13)
    locations = {"source": location(case, "runtime_context", "source_id", line=8),
        "key": location(case, "runtime_context", "FAST_KEY", line=8),
        "fast": location(case, "tool", "fast.fetch", line=9), "archive": location(case, "tool", "archive.fetch", line=12),
        "status": location(case, "storage", "status.txt", line=16)}
    for name in ("fast", "retry", "archive"):
        locations[name + "_error"] = {**location(case, "tool", name + " protected-call exception", line=10), "access_scope": "task"}
    semantics["ir_context"]["sensitivity"] = [{"value": local("key"), "label": "Preferred-tool credential", "evidences": [evidence(case, 15)]}]
    material, wire = base(case, cfg, semantics, locations)
    for block in terminals:
        wire["demands"].append({"requirement_id": "R1", "target": {"instruction_id": "ir_" + block + "_return", "side": "input", "index": 0},
            "preserve": "value", "reason": "Return this terminal's actual successful body or actual archive error unchanged."})
    return material, wire, {("runtime_context", "source_id"): "source-17", ("runtime_context", "FAST_KEY"): "private-key" if key else None,
                            ("storage", "status.txt"): UNKNOWN}
