import sys
from pathlib import Path

base = Path(__file__).parent
sys.path[:0] = [str(base / "src"), str(base.parent.parent / "google-search-online-rerun-20261125" / "test-deps")]
from test_mixed_outcome_demand import routed_call
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from skillflow.doe import sensitivity_material, demand_results
from skillflow.doe.material import _id
from skillflow.doe.demand_engine import DemandEngine
from skillflow.common.recording import canonical_sha256

material, wire = routed_call()
saved, raw, compiled, mapping = compile_flat_response(wire, material)
solved = propagate(material['cfg'], to_payload(compiled))
facts = materials_from_result(solved, material=material, raw_annotation=raw,
    compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)

solve = DemandEngine.solve
def echo_solve(self, **kwargs):
    r = solve(self, **kwargs)
    for label, key, row in [("candidate", key, row) for key, row in r['derivations'].items()]:
        if row['node']['kind'] not in ['ir_input', 'ir_output'] or row['node']['instruction_id'] not in ['ir_call','ir_use','ir_ready']:
            continue
        print(label, key, row)
    for node in self.nodes.values():
        if node['kind'] not in ['ir_input','ir_output'] or node['instruction_id'] not in ['ir_call','ir_use','ir_ready']:
            continue
        print('node', node['kind'], node['instruction_id'], node['slot'])
        for i in node['data_ids']:
            print(i, self.index.data[i]['content'], self.index.data[i]['origin'])
    print('diagnostics', r['diagnostics'])
    return r
DemandEngine.solve = echo_solve

from skillflow.doe import selector_demands
def echo_validate(rows, engine):
    nodes = {canonical_sha256(node): key for key, node in engine.nodes.items()}
    for key, row in rows.items():
        if not row.get('selector_ref'):
            continue
        node = nodes.get(canonical_sha256(row['node']))
        n = {k: row[k] for k in ['property', 'path', 'each', 'excluded_paths', 'selector_ref']}
        n.update({k: row[k] for k in ['outcome_data_ids'] if k in row})
        expected = _id('demand_', [node,n,row['requirement_id'],row['seed_goal_id'],row['conservative'],row.get('information_bound',False)])
        if expected != key or node is None:
            print('selector discrepancy:', expected, node, row)
selector_demands.validate_bindings = echo_validate
sensitivity_material.prepare_joint_sensitivity_review(facts, facts.annotation)
