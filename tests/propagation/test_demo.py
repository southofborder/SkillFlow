"""One offline example entrypoint shares business generation and save/replay."""

from skillflow.common.paths import project_root, resolve_material_path
from pathlib import Path
import json
import runpy
import socket

from skillflow.propagation import PropagationRecords
from skillflow.propagation.runner import replay_propagation


def example():
    return runpy.run_path(str(project_root() / 'examples/propagation/propagation_demo.py'))


def test_demo_is_offline_and_records_only_is_the_same_compact_result(monkeypatch, capsys):
    monkeypatch.setattr(socket.socket, 'connect', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network')))
    module = example()
    result = module['build_demo']()
    assert result.status == 'complete' and len(result.records) == 13
    result.records.validate(require_complete=True)
    restored = PropagationRecords.from_records(result.records.records_dict(), cfg=result.records.cfg,
        annotation=result.records.annotation, data_registry=result.registry,
        initial_data=result.initial_data, initial_state=result.initial_state)
    assert restored.records_dict() == result.records.records_dict()
    assert module['main'](['--records-only']) == 0
    assert json.loads(capsys.readouterr().out) == result.records.records_dict()
    assert not (project_root() / 'examples/propagation/propagation_record_demo.py').exists()


def test_demo_default_prints_counts_without_a_full_fact_wrapper(capsys):
    assert example()['main']([]) == 0
    value = json.loads(capsys.readouterr().out)
    assert value['status'] == 'complete' and value['record_count'] == 13
    assert set(value) == {'status','data_count','record_count','sink_count'}


def test_authored_display_does_not_masquerade_as_model_run(tmp_path, monkeypatch):
    monkeypatch.setattr(socket.socket, 'connect', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network')))
    directory = tmp_path / 'authored'
    facts = example()['save_demo'](directory)
    for name in ('data', 'records', 'sinks'):
        assert json.loads((directory / (name + '.json')).read_text(encoding='utf-8')) == getattr(facts, name)
    assert not (directory / 'manifest.json').exists()
    assert not (directory / 'doe-input.json').exists()
    assert 'not a committed propagation run' in (directory / 'NOTICE.txt').read_text(encoding='utf-8')
    assert (directory / 'report.html').is_file()
