"""Offline synthetic diagnostic audit; no models or historic run execution."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.document_guided.test_source_review_locality import two_operations
from tests.doe.input_review_helpers import source_review_response
from tests.doe.test_demand_engine import candidate
from skillflow.document_guided.source_review import isolate_source_review
from skillflow.doe.input_contract_review import build_input_contract_review
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.input_assessments import InputReviewBarrierIndex
from skillflow.doe.review_barriers import barrier_diagnostic_value, operation_barriers, barrier_reason
from skillflow.propagation.contracts.demand import validate_demand_candidate
import json

values, material, _ = two_operations()
facts, task, annotation, targets = values
response = source_review_response(material, [])
response['outcome'] = 'invalid_outcome'
isolated = isolate_source_review(response, material)
receipt = build_input_contract_review(files=material['files'], cfg=facts.cfg, annotation=annotation,
    review={'status':'structural_failure', **isolated, 'availability':material['availability']}, review_material=material)
parsed = validate_demand_candidate(candidate(targets), task, material['files'], targets)
engine = DemandEngine(facts, task, annotation, parsed.model_dump(mode='json'), targets, input_contract_review=receipt)
result = engine.solve()
index = InputReviewBarrierIndex(engine)
expected = {barrier_diagnostic_value(b, a['instruction_id'], a['operation_id'])['id']
            for a in result['input_assessments'] if a['coverage'] != 'not_reached'
            for b in index.for_assessment(a)}
for d in result['diagnostics']:
    if d['code'] != 'input_contract_review_validation' or d['id'] in expected:
        continue
    op = d['operation_id']
    if op is None or not any(d['reason'] == barrier_reason(b) for b in operation_barriers(engine, op)):
        print(json.dumps({'unexpected':d, 'related_assessments':[a for a in result['input_assessments']
              if a['instruction_id']==d['instruction_id'] and a['operation_id']==op]}, ensure_ascii=False))
