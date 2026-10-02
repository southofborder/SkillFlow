"""Independent regressions for propagation identity and feedback boundaries."""

from pathlib import Path
import runpy

from skill_ir.data import DataRegistry, KnownPartsContent, OpaqueContent
from skill_ir.propagation import FlowLocation, FlowState, propagate


DEMO = runpy.run_path(str(Path(__file__).resolve().parents[2] / "examples" / "propagation_demo.py"))
instruction, operand = DEMO["instruction"], DEMO["operand"]
literal, local, input_ref = DEMO["literal"], DEMO["local"], DEMO["input_ref"]
annotate = DEMO["fixture_annotation"]


def only_result(result, ir_id, name):
    values = result.records.get(ir_id).exit_state.get(FlowLocation(kind="result", name=name))
    assert values is not None and len(values) == 1
    return next(iter(values))


def test_reusing_seed_namespace_cannot_merge_results_of_different_specs():
    cfg = {"entry_block_id": "main", "blocks": {"main": {
        "block_id": "main", "block_name": "identity",
        "instructions": [instruction("read", outputs=["B"]),
                         instruction("work", [operand("B")], ["C"]),
                         instruction("end", opcode="return")],
    }}, "edges": []}
    common = {"read": (["context_read"], [(0, [
        {"op": "read", "location": "doc", "output": "b"},
    ])], [local("b")])}
    compute = {**common, "work": (["transform"], [(0, [
        {"op": "compute", "inputs": [input_ref()], "dependencies": ["derived"], "output": "c"},
    ])], [local("c")])}
    build = {**common, "work": (["transform"], [(0, [
        {"op": "build", "container": "object", "parts": [{"path": ["wrapped"], "value": input_ref()}], "output": "c"},
    ])], [local("c")])}
    locations = {"doc": ("runtime_context", "doc")}
    cfg, first_annotation = annotate(cfg, compute, locations)
    _, second_annotation = annotate(cfg, build, locations)
    seeds = DataRegistry("user-controlled-seed-namespace")
    source = seeds.register_source("doc", acquired_from="doc")
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="doc"): frozenset([source.id])})
    first = propagate(cfg, first_annotation, initial_registry=seeds, initial_state=state)
    assert first.status == "complete"
    first_id = only_result(first, "ir_work", "C")
    before = first.registry.to_dict()
    second = propagate(cfg, second_annotation, initial_registry=first.registry, initial_state=state)
    assert second.status == "complete", second.diagnostics
    second_id = only_result(second, "ir_work", "C")
    assert first_id != second_id
    assert first.registry.to_dict() == before
    assert isinstance(second.registry.get(first_id).content, OpaqueContent)
    assert isinstance(second.registry.get(second_id).content, KnownPartsContent)
    assert second.registry.get(first_id).origin.inputs == second.registry.get(second_id).origin.inputs == [source.id]


def test_strong_reset_before_loop_read_breaks_generation_feedback():
    cfg = {"entry_block_id": "loop", "blocks": {
        "loop": {"block_id": "loop", "block_name": "reset before reading", "instructions": [
            instruction("reset"), instruction("read", outputs=["B"]),
            instruction("compute", [operand("B")], ["C"]), instruction("save", [operand("C")]),
            instruction("repeat", [{"type": "literal", "literal_value": True}], opcode="dispatch"),
        ]},
        "end": {"block_id": "end", "block_name": "end", "instructions": [instruction("end", opcode="return")]},
    }, "edges": [{"source_block_id": "loop", "target_block_id": target} for target in ("loop", "end")]}
    plans = {
        "reset": (["context_write"], [(0, [{"op": "write", "target": "doc", "mode": "replace", "input": literal("fixed")}])], []),
        "read": (["context_read"], [(0, [{"op": "read", "location": "doc", "output": "b"}])], [local("b")]),
        "compute": (["transform"], [(0, [{"op": "compute", "inputs": [input_ref()], "dependencies": ["derived"], "output": "c"}])], [local("c")]),
        "save": (["context_write"], [(0, [{"op": "write", "target": "doc", "mode": "replace", "input": input_ref()}])], []),
    }
    cfg, annotation = annotate(cfg, plans, {"doc": ("runtime_context", "doc")})
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.stats["block_evaluations"] < 10
    read_id = only_result(result, "ir_read", "B")
    compute_id = only_result(result, "ir_compute", "C")
    assert result.registry.get(read_id).content.value == "fixed"
    assert result.registry.get(compute_id).origin.inputs == [read_id]
    assert propagate(cfg, annotation, schedule="lifo").records.to_dict() == result.records.to_dict()


def test_ir_inputs_and_output_bindings_use_entry_values_after_context_write():
    for order in ('fixed', 'partial'):
        cfg = {'entry_block_id':'main','declared_context_keys':['ctx'],'blocks':{'main':{
            'block_id':'main','block_name':'entry operand','data_source_kind':'context','instructions':[
                instruction('act',[operand('ctx','context_key')],['original','computed','fresh']),
                instruction('end',opcode='return')]}},'edges':[]}
        plans={'act':(['context_write','transform','context_read'],[
            (0,[{'op':'write','target':'ctx','mode':'replace','input':literal('replacement')}]),
            (1,[{'op':'compute','inputs':[input_ref()],'dependencies':['derived'],'output':'copy'}]),
            (2,[{'op':'read','location':'ctx','output':'fresh'}])],
            [input_ref(),local('copy'),local('fresh')])}
        cfg,annotation=annotate(cfg,plans,{'ctx':('runtime_context','ctx')},['ir_act'] if order=='partial' else [])
        result=propagate(cfg,annotation)
        assert result.status=='complete',result.diagnostics
        record=result.records.get('ir_act')
        original=record.entry_state.get(FlowLocation(kind='runtime_context',name='ctx'))
        assert record.exit_state.get(FlowLocation(kind='result',name='original'))==original
        assert record.events[1].atomic_ops[0].inputs==[original]
        for data_id in record.events[1].atomic_ops[0].outputs[0]:
            assert set(result.registry.get(data_id).origin.inputs)==set(original)
        # Stage reads, unlike IR inputs, deliberately inspect changed memory.
        fresh=record.events[2].atomic_ops[0].outputs[0]
        assert any(result.registry.get(d).content.form=='literal' and result.registry.get(d).content.value=='replacement' for d in fresh)
        if order=='fixed': assert not original & fresh


def test_loop_feedback_tracks_context_input_at_entry_not_after_same_ir_reset():
    cfg={'entry_block_id':'loop','declared_context_keys':['ctx'],'blocks':{
        'loop':{'block_id':'loop','block_name':'context feedback','data_source_kind':'context','instructions':[
            instruction('act',[operand('ctx','context_key')],['next_value']),
            instruction('repeat',[{'type':'literal','literal_value':True}],opcode='dispatch')]},
        'exit':{'block_id':'exit','block_name':'exit','instructions':[instruction('done',opcode='return')]}},
        'edges':[{'source_block_id':'loop','target_block_id':target} for target in ('loop','exit')]}
    plans={'act':(['context_write','transform','context_write'],[
        (0,[{'op':'write','target':'ctx','mode':'replace','input':literal('reset')}]),
        (1,[{'op':'compute','inputs':[input_ref()],'dependencies':['derived'],'output':'next'}]),
        (2,[{'op':'write','target':'ctx','mode':'replace','input':local('next')}])],[local('next')])}
    cfg,annotation=annotate(cfg,plans,{'ctx':('runtime_context','ctx')})
    result=propagate(cfg,annotation)
    assert result.status=='unsupported_feedback',result.diagnostics
    assert result.stats['block_evaluations']==0
