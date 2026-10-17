"""Assistant-authored task candidates for three pinned, offline examples.

These are transparent authoring recipes, not extraction rules, model outputs,
ground truth, or semantic verification. Their IR identities and source lines
belong exclusively to the frozen baseline identified below.
"""
from __future__ import annotations

from skillflow.common.source_evidence import json_pointer
from skillflow.propagation.contracts.task import build_task_target_index


BASELINE = "experiments/propagation/runs/sink-tightening-v1-20261002-205045/cases"
INPUT_SHA256 = {
    "001": "00775915301392d5f01ec49d246fa356442fac5c355f4789e109c850d1717f39",
    "010": "a70679af37f3c261c5aa2a8c896ca6a7e5952db0ca3304151dc0f6d01706a560",
    "013": "ae238aa341a176ac6c8dbc96aa603819c28ea85dd3d030d432e1954179fed90a",
}


def _bound_recipe(case: str, cfg: dict) -> dict:
    """Locate explicitly authored requirements in the already verified CFG."""
    targets = build_task_target_index(cfg)
    by_pointer = {target["pointer"]: key for key, target in targets.items()}
    irs = {ir["id"]: json_pointer("blocks", block_id, "instructions", position)
           for block_id, block in cfg["blocks"].items()
           for position, ir in enumerate(block["instructions"])}

    def evidence(start, end, reason, file="SKILL.md"):
        return {"file": "skill/" + file, "start_line": start, "end_line": end, "reason": reason}

    def binding(pointer, reason):
        return {"target": targets[by_pointer[pointer]]["target"], "reason": reason}

    def ir(identifier, suffix, reason):
        return binding(irs[identifier] + suffix, reason)

    def constraint(index, reason):
        return binding(json_pointer("constraints", index), reason)

    def edge(source, target, reason):
        matches = [index for index, item in enumerate(cfg["edges"])
                   if item["source_block_id"] == source and item["target_block_id"] == target]
        if len(matches) != 1:
            raise ValueError("pinned example edge identity differs")
        return binding(json_pointer("edges", matches[0], "condition_text"), reason)

    requirements = []

    def requirement(text, evidences, bindings):
        requirements.append({"id": f"R{len(requirements) + 1:03d}", "text": text,
                             "evidences": evidences, "bindings": bindings})

    if case == "001":
        purpose = {"text": "Notify eligible event recipients with each record's unchanged summary, then save the processed count.",
                   "evidences": [evidence(9, 13, "These instructions define eligibility, per-record recipients, original message bodies, and the exclusion of unselected records."),
                                 evidence(16, 16, "The final step requires the processed count to be saved.")]}
        requirement("Use the user-supplied events.json as the event source; its listed fields describe the input, not permission to disclose them all.",
                    [evidence(8, 8, "The instruction identifies the source file and its record fields.")],
                    [ir("ir_001", "/inputs/0", "This is the specified file source, not a claim that all its fields are required at every boundary.")])
        requirement("Select a record only if opted_out is not true and either urgent is true or value is at least 100; urgency does not override opted_out.",
                    [evidence(9, 10, "The selection condition and the explicit limitation on the urgency exception must be retained together.")],
                    [ir("ir_003", "/constraints/0", "This constraint records the selection predicate."),
                     ir("ir_003", "/constraints/1", "This constraint preserves the non-overridable subscription restriction.")])
        requirement("Call notify.send once for each selected record, and never for an unselected record.",
                    [evidence(11, 11, "The call is quantified over selected records and has per-record multiplicity one."),
                     evidence(13, 13, "Unselected records must not cause a notification call.")],
                    [ir("ir_005", "/metadata/per_record", "The current graph records the per-record scope here; this does not certify all call arguments as necessary."),
                     ir("ir_005", "/constraints/0", "The call constraint retains the once-per-selected-record requirement."),
                     ir("ir_005", "/constraints/2", "This excludes notifications for unselected records.")])
        requirement("For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged.",
                    [evidence(11, 12, "The recipient and body requirements refer to that same record, and explicitly require the original summary value.")],
                    [ir("ir_005", "/inputs/2", "The recipient field selector is retained, not the whole record as a recipient."),
                     ir("ir_005", "/inputs/3", "The body field selector denotes summary, not the complete record."),
                     ir("ir_005", "/constraints/1", "This preserves original-value body semantics."),
                     ir("ir_005", "/metadata/per_record", "The shared per-record scope ties both selected fields to one element.")])
        requirement("Do not send access_token to any recipient anywhere in this workflow.",
                    [evidence(14, 14, "This is a workflow-wide prohibition; it is not a demand to create or preserve a prohibited send.")],
                    [constraint(0, "The global restriction applies even when the current graph contains no violating operation.")])
        requirement("Field retrieval must not introduce summary generation, content rewriting, or extra format conversion.",
                    [evidence(15, 15, "The source distinguishes original field retrieval from new content processing.")],
                    [constraint(1, "This constrains field-value handling rather than adding a transformation operation.")])
        requirement("After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.",
                    [evidence(16, 16, "The specified final side effect is saving the processed count.")],
                    [ir("ir_007", "/outputs/0", "This is the count result used by the implementation; the binding does not itself prove the counting interpretation."),
                     ir("ir_009", "/inputs/1", "This is the value written to the file."),
                     ir("ir_009", "/inputs/0", "This identifies the required local destination."),
                     ir("ir_009", "/constraints/0", "The file write is required after processing.")])
    elif case == "010":
        def workflow(start, end, reason):
            return evidence(start, end, reason, "references/workflow.md")
        purpose = {"text": "Query the index once with the supplied request values and optional-argument semantics, save the response total, and return items unchanged.",
                   "evidences": [evidence(8, 8, "The entry file explicitly incorporates the workflow instructions."),
                                 workflow(7, 15, "These requirements establish the single query and conditional original-value arguments."),
                                 workflow(21, 23, "These instructions specify the saved total and returned items.")]}
        requirement("Use the user-supplied request.json, including term and any present from_date and limit values.",
                    [workflow(5, 5, "The workflow names the source and distinguishes the optional fields.")],
                    [ir("ir_001", "/inputs/0", "This binds the request source, not a requirement to transmit the whole request.")])
        requirement("Call index.search exactly once, passing request.term unchanged as query.",
                    [workflow(7, 7, "The source specifies both call multiplicity and the original query value.")],
                    [constraint(0, "This preserves the global single-call restriction."),
                     ir("ir_007", "/inputs/1", "This is the query value rather than the full request."),
                     ir("ir_007", "/constraints/0", "The parameter must preserve the original term.")])
        requirement("Pass from_date unchanged only when present; omit the argument when absent. Its stated accepted format does not request a preprocessing step.",
                    [workflow(10, 11, "The argument carries its original value when present and is absent otherwise."),
                     workflow(15, 15, "The separate configuration applies to the same call."),
                     evidence(1, 2, "The configuration explicitly sets the missing from_date behavior to omit.", "query.yaml"),
                     workflow(19, 19, "The format description does not require validation or normalization.")],
                    [ir("ir_007", "/inputs/2", "This is the optional business value."),
                     ir("ir_007", "/inputs/3", "This is an existence control value, not an extra request member."),
                     ir("ir_007", "/constraints/1", "This preserves the present-value requirement."),
                     ir("ir_007", "/constraints/2", "This preserves omission when absent.")])
        requirement("Pass limit unchanged only when present; omit the argument when absent.",
                    [workflow(12, 13, "The two cases specify original value versus argument omission."),
                     workflow(15, 15, "The configuration applies to the same search call."),
                     evidence(1, 3, "The missing-argument configuration includes limit: omit.", "query.yaml")],
                    [ir("ir_007", "/inputs/4", "This is the optional limit value."),
                     ir("ir_007", "/inputs/5", "This is the existence control, not part of the request payload."),
                     ir("ir_007", "/constraints/3", "This retains the original present value."),
                     ir("ir_007", "/constraints/4", "This retains omission when absent.")])
        requirement("Do not invoke index.delete anywhere in this workflow.",
                    [workflow(17, 17, "This explicitly prohibits deletion throughout the workflow.")],
                    [constraint(1, "The global restriction is meaningful without an existing delete operation.")])
        requirement("Do not introduce fuzzy expansion, pre-call validation, or normalization from capability or parameter descriptions.",
                    [workflow(3, 3, "Fuzzy matching is described as capability, explicitly not requested behavior."),
                     workflow(19, 19, "The argument descriptions do not instruct validation or normalization.")],
                    [constraint(2, "This preserves the no-preprocessing distinction."),
                     constraint(3, "This keeps the capability note from becoming an additional task.")])
        requirement("After the search, write that response's total value to local count.txt.",
                    [workflow(21, 21, "The side effect names a specific response field and destination.")],
                    [ir("ir_009", "/outputs/0", "This is the extracted total from the search response."),
                     ir("ir_010", "/inputs/1", "This is the actual saved value; extra response content is not made required."),
                     ir("ir_010", "/inputs/0", "This is the required count-file destination.")])
        requirement("Return that search response's items value unchanged.",
                    [workflow(23, 23, "The requirement is the items field, not the complete response.")],
                    [ir("ir_011", "/outputs/0", "This binds the items extraction result."),
                     ir("ir_012", "/inputs/0", "Ordinary return is represented by its actual input; no public output or user-delivery event is invented."),
                     ir("ir_012", "/constraints/0", "The return must preserve the original items value.")])
    elif case == "013":
        purpose = {"text": "Fetch the requested source through a credential-gated preferred tool and bounded fallback, preserve the appropriate returned value, and append final status before every return.",
                   "evidences": [evidence(3, 3, "The declared purpose specifies preferred fetching and a bounded fallback."),
                                 evidence(9, 16, "The detailed instructions establish control, argument, return, prohibition, and status requirements.")]}
        requirement("Obtain source_id from the user's request and FAST_KEY from the environment; these origins do not mandate whole-container disclosure.",
                    [evidence(8, 8, "The instruction separates each value from its named source.")],
                    [ir("ir_001", "/inputs/0", "The logical source is the user request."),
                     ir("ir_001", "/outputs/0", "The obtained target is source_id."),
                     ir("ir_003", "/inputs/0", "The logical credential source is the environment."),
                     ir("ir_003", "/outputs/0", "The obtained target is FAST_KEY, not a requirement to expose all environment contents.")])
        requirement("When FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; when absent, go directly to archive.fetch without a fast.fetch call.",
                    [evidence(9, 9, "The instruction makes credential presence control both the selected tool and its arguments.")],
                    [ir("ir_005", "/outputs/0", "This is the credential-presence control result."),
                     edge("block_003", "block_004", "This is the credential-present branch."),
                     edge("block_003", "block_008", "This is the credential-absent branch."),
                     ir("ir_007", "/inputs/1", "The first preferred call receives source_id."),
                     ir("ir_007", "/inputs/2", "The first preferred call receives FAST_KEY.")])
        requirement("Retry fast.fetch exactly once only after a transient first failure; do not retry a non-transient first failure.",
                    [evidence(10, 10, "The instruction jointly restricts the retry trigger and count.")],
                    [ir("ir_011", "/constraints/0", "This limits the retry call."),
                     edge("block_005", "block_006", "Only the transient first-failure branch reaches the retry."),
                     edge("block_005", "block_008", "The non-transient first failure goes to fallback instead.")])
        requirement("After a non-transient first failure or any failed preferred retry, use archive.fetch with source_id.",
                    [evidence(11, 11, "These are the two failure conditions that trigger fallback.")],
                    [edge("block_005", "block_008", "This is fallback after a non-transient first failure."),
                     edge("block_007", "block_008", "This is fallback after any failed retry."),
                     ir("ir_015", "/inputs/1", "The fallback receives source_id.")])
        requirement("Call archive.fetch at most once and pass source_id as its only argument.",
                    [evidence(12, 12, "The instruction restricts both multiplicity and the complete business-argument set.")],
                    [ir("ir_015", "/inputs/1", "This is the sole permitted business argument; the tool identity is not a payload."),
                     ir("ir_015", "/constraints/0", "This retains the at-most-once and only-argument restrictions.")])
        requirement("On success, return the body of the response from that successful attempt unchanged, and perform no further fetch calls.",
                    [evidence(13, 13, "The successful attempt determines the returned body, and success stops fetching.")],
                    [ir("ir_020", "/inputs/0", "The first-success terminal returns the first response's body."),
                     ir("ir_022", "/inputs/0", "The retry-success terminal returns the retry response's body."),
                     ir("ir_024", "/inputs/0", "The fallback-success terminal returns the archive response's body."),
                     constraint(4, "The global success rule preserves the original value and stops further fetches.")])
        requirement("If archive.fetch fails, stop and return its error without retrying archive.fetch.",
                    [evidence(14, 14, "The failure terminal has a distinct return identity and a no-retry restriction.")],
                    [ir("ir_026", "/inputs/0", "The terminal return uses the archive error rather than a successful body."),
                     binding(json_pointer("blocks", "block_013", "constraints", 0), "This failure-scope restriction prohibits another archive attempt.")])
        requirement("Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in the workflow.",
                    [evidence(15, 15, "The prohibition has named receiving boundaries and global scope.")],
                    [constraint(6, "The restriction applies without inventing a diagnostic-output operation."),
                     ir("ir_015", "/constraints/1", "This additionally locates the restriction at the existing archive call.")])
        requirement("Before every success or failure return, append the final status to local status.txt; this does not require appending complete responses or credentials.",
                    [evidence(16, 16, "The source requires an append of final status on every terminal path, without specifying a new record format.")],
                    [ir(identifier, "/inputs/1", "This terminal path supplies its own final status value to the append.")
                     for identifier in ("ir_019", "ir_021", "ir_023", "ir_025")]
                    + [constraint(7, "The global restriction places status append before every return.")])
    else:
        raise ValueError("task example must be one of 001, 010, 013")
    return {"purpose": purpose, "requirements": requirements}


ASSISTANT_REVIEWS = {
    "001": "The candidate retains the subscription/urgency/value predicate, same-record recipient and unchanged summary, the workflow-wide token prohibition, and processed-count persistence. Source acquisition is not a blanket requirement to expose the whole record. The count binding follows the selected-record result in the current graph; reference checks do not prove that this interpretation or actual delivery count is correct.",
    "010": "The candidate cites the entry file, workflow, and query configuration. Optional values remain distinct from existence controls; omission is not null substitution. The capability note does not create a fuzzy-search task. The saved total and ordinary returned items have different bindings, and the absent delete operation does not prevent recording the global prohibition.",
    "013": "The candidate preserves named sources, credential-controlled routing, one transient retry, at-most-once archive fallback with source_id only, separate first/retry/archive return identities, forbidden credential receivers, and all four terminal status appends. These bindings locate the declared requirements; they do not establish full CFG equivalence or authorize whole-environment observation.",
}


def authored_bindings(case, cfg):
    """Separately authored graph correspondences; never Task extraction input."""
    return {r["id"]: r["bindings"] for r in _bound_recipe(case, cfg)["requirements"]}


def authored_candidate(case, cfg):
    """Explicit source-only baseline; graph bindings stay in their own recipe.

    The pinned readable files are test inputs, not accepted model responses.
    Physical accounting is a fixture projection of authored evidence, not an
    extraction heuristic or semantic completeness claim.
    """
    import json
    from skillflow.common.paths import project_root
    from skillflow.common.source_evidence import source_lines
    from skillflow.propagation.contracts.task import task_source_files
    from copy import deepcopy
    value = deepcopy(_bound_recipe(case, cfg))
    for requirement in value["requirements"]:
        requirement.pop("bindings")
    material = json.loads((project_root() / BASELINE / case / "annotation/inputs/material.json").read_bytes())
    files = task_source_files(material["source"])
    accounting = []
    for file, text in files.items():
        for number, line in enumerate(source_lines(text), 1):
            if not line.strip():
                continue
            refs = [r["id"] for r in value["requirements"] if any(e["file"] == file
                and e["start_line"] <= number <= e["end_line"] for e in r["evidences"])]
            accounting.append({"file": file, "start_line": number, "end_line": number,
                "disposition": "requirement" if refs else "supporting_context",
                "requirement_ids": refs, "issue_ids": [],
                "reason": "离线人工编写样例的物理行处置；不声称语义提取完备。"})
    return {**value, "source_accounting": accounting, "issues": []}
