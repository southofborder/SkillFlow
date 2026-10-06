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
    restored = PropagationRecords.from_json(result.records.to_json(), cfg=result.records.cfg,
        annotation=result.records.annotation, data_registry=result.registry,
        initial_data=result.initial_data, initial_state=result.initial_state)
    assert restored.to_dict() == result.records.to_dict()
    assert module['main'](['--records-only']) == 0
    assert json.loads(capsys.readouterr().out) == result.records.to_dict()['records']
    assert not (project_root() / 'examples/propagation/propagation_record_demo.py').exists()


def test_demo_default_is_self_contained_doe_input(capsys):
    module = example()
    assert module['main']([]) == 0
    doe = json.loads(capsys.readouterr().out)
    assert doe['schema_version'] == 'skillflow-doe-input-v7'
    assert len(doe['records']) == 13 and doe['data']
    assert set(doe['source']) == {'files', 'source_sha256', 'index', 'inventory', 'boundaries'}


def test_demo_shared_save_and_replay_do_not_copy_business_results(tmp_path, monkeypatch):
    monkeypatch.setattr(socket.socket, 'connect', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network')))
    module = example()
    directory = tmp_path / 'authored'
    doe = module['save_demo'](directory)
    assert replay_propagation(directory) == doe
    assert (directory / 'doe-input.json').is_file()
    for filename in ('result.json', 'data.json', 'records.json', 'resolved-seed.json'):
        assert not (directory / filename).exists()
    assert not (directory / 'replay/doe-input.json').exists()
    provenance = json.loads((directory / 'audit/provenance.json').read_text(encoding='utf-8'))
    assert provenance['kind'] == 'hand_authored_specification'
    assert '不是模型实测' in provenance['description']
    assert not (directory / 'audit/accepted-call').exists()
