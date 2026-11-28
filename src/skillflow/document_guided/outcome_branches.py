"""Identify multi-port branches at physically straight-line Python statements."""
import ast
from functools import lru_cache


@lru_cache(maxsize=32)
def _operation_sites(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return frozenset(), {}
    sites, defaults, ambiguous = set(), {}, set()
    nested_control = (ast.IfExp, ast.BoolOp, ast.comprehension, ast.Lambda, ast.Await, ast.Yield, ast.YieldFrom)
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Match)):
            control = (node.test if isinstance(node, (ast.If, ast.While)) else
                       node.subject if isinstance(node, ast.Match) else node.iter)
            ambiguous.update(range(node.lineno, control.end_lineno + 1))
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            eligible = len(node.names) == 1
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr, ast.Return)):
            if isinstance(node.value, ast.IfExp):
                for active, other in ((node.value.body, node.value.orelse), (node.value.orelse, node.value.body)):
                    if (isinstance(active, (ast.Call, ast.Subscript, ast.Attribute))
                            and isinstance(other, ast.Constant) and type(other.value) in {int, float, bool, str, type(None)}
                            and not any(isinstance(child, nested_control) for child in ast.walk(active))):
                        defaults[node.lineno, node.end_lineno] = other.value
            eligible = isinstance(node.value, (ast.Call, ast.Subscript, ast.Attribute, ast.JoinedStr))
        else:
            continue
        if eligible and not any(isinstance(child, nested_control) for child in ast.walk(node)):
            site = (node.lineno, node.end_lineno)
            if site in sites:
                ambiguous.add(node.lineno)
            sites.add(site)
    def clear(site):
        return not any(line in ambiguous for line in range(site[0], site[1] + 1))
    return frozenset(site for site in sites if clear(site)), {site: value for site, value in defaults.items() if clear(site)}


def needs_outcome_targets(block, files, blocks):
    """The evidence proves there is no ordinary source test, not which arm throws."""
    exit = block.exit
    if (exit.kind != "branch" or not block.operations or len(exit.arms) != 2
            or len({arm.target for arm in exit.arms}) != 2):
        return False
    producer, source = block.operations[-1], exit.source
    inputs = [getattr(operand, "result", None) for operand in exit.conditions]
    if (len(set(inputs)) < 2 or not set(inputs) <= set(producer.outputs)
            or source is None or producer.source is None or producer.source.file != source.file
            or not producer.source.start_line <= source.start_line <= source.end_line <= producer.source.end_line
            or not source.file.endswith(".py") or source.file not in files):
        return False
    straight, defaults = _operation_sites(files[source.file])
    site = (source.start_line, source.end_line)
    if site in straight:
        return True
    if site not in defaults:
        return False
    # For a conditional expression, its source test may already have selected
    # the operation. Require the other arm's actual literal and common join.
    parents = [b for b in blocks.values() if b.exit.kind == "branch" and any(a.target == block.ref for a in b.exit.arms)]
    if len(parents) != 1:
        return False
    test = parents[0].exit
    if test.source != source or len(test.conditions) != 1 or len(test.arms) != 2:
        return False
    siblings = [blocks.get(a.target) for a in test.arms if a.target != block.ref]
    if len(siblings) != 1 or siblings[0] is None:
        return False
    sibling = siblings[0]
    if (sibling.exit.kind != "jump" or sibling.exit.target not in {a.target for a in exit.arms}
            or len(sibling.operations) != 1 or sibling.operations[0].source != source):
        return False
    values = sibling.operations[0].inputs
    return (len(values) == 1 and hasattr(values[0], "literal") and type(values[0].literal) is type(defaults[site])
            and values[0].literal == defaults[site])
