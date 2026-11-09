"""Alternative call paths must not be counted as a serial execution."""
from skillflow.doe.constraint_engine import ConstraintEngine
from tests.doe.test_constraints_engine import World, bounded, prior


def label(world, ir, event, name, *, disposition="return", group="call"):
    world.semantics[ir]["events"][event]["case"] = {
        "group": group, "id": name, "name": name, "phase": "normal" if disposition == "return" else "post_request_error",
        "disposition": disposition, "condition": "Source-supported candidate " + name}


def result(world, constraint):
    return next(iter(ConstraintEngine(world.engine(constraint)).check().values()))


def test_alternative_requests_are_not_two_actual_attempts():
    world = World()
    a, b = world.op("main", "a"), world.op("main", "b")
    label(world, "main", 0, "cached")
    label(world, "main", 1, "created")
    assert result(world, bounded([a, b]))["status"] == "satisfied"


def test_order_in_another_alternative_cannot_satisfy_prior_requirement():
    world = World()
    a, b = world.op("main", "authorize"), world.op("main", "send")
    label(world, "main", 0, "authorized")
    label(world, "main", 1, "unrelated")
    assert result(world, prior([a], [b]))["status"] == "potential_violation"


def test_throw_preserves_request_prefix_without_following_return_path():
    world = World()
    sent = world.op("main", "sent")
    label(world, "main", 0, "failed", disposition="throw")
    saved = world.op("main", "saved", target="archive")
    world.semantics["main"]["events"][1]["requires_completion"] = ["call"]
    later = world.op("after", "returned")
    world.edge("main", "after")
    assert result(world, bounded([sent], limit=0))["status"] == "potential_violation"
    assert result(world, bounded([saved, later], limit=0))["status"] == "satisfied"


def test_caught_error_return_can_continue_and_save():
    world = World()
    failed = world.op("main", "failed")
    label(world, "main", 0, "caught")
    saved = world.op("main", "saved", target="archive")
    world.semantics["main"]["events"][1]["requires_completion"] = ["call"]
    assert result(world, bounded([saved], limit=0))["status"] == "potential_violation"


def test_case_report_exposes_conditions_and_state_precision():
    from skillflow.doe.report import _outcome_note
    text = _outcome_note({"case": {"id": "failed", "phase": "pre_request_error", "disposition": "throw", "condition": "credential validation failed"},
                          "requires_completion": ["batch"], "may_state": True})
    assert "pre_request_error" in text and "credential validation failed" in text
    assert "Normal completion required: batch" in text and "Exact occurrence count is unresolved" in text


def test_mapped_collection_report_keeps_occurrences_and_alternatives_separate():
    from skillflow.doe.report import _content_lines
    rows = _content_lines({"content": {"form": "mapped_collection", "base": "source", "scope": "loop",
        "members": [{"selector": 0, "element": "first", "values": ["normal", "error"]},
                    {"selector": 1, "element": "second", "values": ["other"]}]}},
        {name: name for name in ("source", "first", "second", "normal", "error", "other")})
    assert len(rows) == 3
    assert "Index 0: source first → one of {normal, error}" == rows[1]
    assert "Index 1: source second → one of {other}" == rows[2]
    assert "not additional members" in rows[0]
