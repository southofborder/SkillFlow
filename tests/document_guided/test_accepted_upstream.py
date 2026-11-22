"""Fresh processing-onward runs across producer versions; synthetic replies only."""
from copy import deepcopy
from unittest.mock import patch
import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.llm.request_errors import ModelRequestFailure
from skillflow.document_guided import runner, accepted_upstream
from skillflow.document_guided.online import inventory, read
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner,"_certificate",lambda *args,**kwargs:None)


class Downstream(Harness):
    def __init__(self,*args,fail_processing=False,**kwargs):
        super().__init__(*args,**kwargs)
        self.fail_processing=fail_processing

    def complete(self,stage,prompt):
        if stage in {"task","flow","graph"}:
            raise AssertionError("An inherited upstream stage must not acquire a new answer")
        if stage=="processing" and self.fail_processing:
            self.calls.append(stage)
            raise ModelRequestFailure("Synthetic confirmed-ended processing delivery")
        return super().complete(stage,prompt)


def parent_run(tmp_path):
    parent=Harness(tmp_path/'parent')
    parent.prepare(tmp_path/'source')
    assert runner.run(parent.directory,client_factory=parent.factory)['status']=='complete'
    return parent


def change_producer(monkeypatch):
    current=runner.implementation_provenance()
    files={**current['files'],'synthetic/changed-producer.py':'f'*64}
    changed={**current,'files':files,'sha256':canonical_sha256(files)}
    for module in ('skillflow.document_guided.runner','skillflow.document_guided.online',
            'skillflow.document_guided.accepted_upstream','skillflow.document_guided.source_review',
            'skillflow.task.runner','skillflow.propagation.runner','skillflow.doe.formal_runner'):
        monkeypatch.setattr(module+'.implementation_provenance',lambda:deepcopy(changed))
    return changed


def matching_replay(directory,result):
    original=runner._save
    def checked(run,state,*,replay=False):
        assert not (replay and state['status']=='failed'),state.get('reason',state)
        return original(run,state,replay=replay)
    with patch.object(runner,'_save',checked):
        assert runner.replay(directory)==result


@pytest.mark.parametrize('repair',[False,True])
def test_changed_producer_reuses_accepted_values_without_resampling(tmp_path,monkeypatch,repair):
    parent=parent_run(tmp_path)
    before=inventory(parent.directory)
    changed=change_producer(monkeypatch)
    child=Downstream(tmp_path/'child',domains=('cfg',) if repair else (),precise_repair=True)
    manifest=runner.prepare_from_accepted_cfg(parent.directory,run_dir=child.directory)
    assert manifest['implementation']==changed
    copied=read(child.directory/'accepted-upstream.json')
    assert copied['parent_implementation']!=changed
    assert copied['inherited_logical_calls']==3
    result=runner.run(child.directory,client_factory=child.factory)
    assert result['status']=='complete',result
    assert len(child.calls)==(9 if repair else 4)
    assert result['counts']['logical_calls']==len(child.calls)+3
    assert result['repair_used'] is repair
    for name in ('task','flow','graph'):
        assert result['stages'][name]=={'status':'complete','origin':'accepted_upstream'}
    assert (child.directory/'graph/initial.json').read_bytes()==(parent.directory/'graph/initial.json').read_bytes()
    matching_replay(child.directory,result)
    assert inventory(parent.directory)==before
    assert len(child.calls)==(9 if repair else 4)


def test_inherited_cfg_fatal_processing_frontier_replays_without_calls(tmp_path):
    parent=parent_run(tmp_path)
    before=inventory(parent.directory)
    child=Downstream(tmp_path/'child',fail_processing=True)
    runner.prepare_from_accepted_cfg(parent.directory,run_dir=child.directory)
    result=runner.run(child.directory,client_factory=child.factory)
    assert result['status']=='failed' and result['stage']=='processing',result
    assert result['fatal_frontier']
    assert child.calls==['processing']
    assert runner.replay(child.directory)==result
    assert child.calls==['processing'] and inventory(parent.directory)==before


@pytest.mark.parametrize('relative',['graph/initial.json','inherited/steps/flow/document.md',
    'inherited/task/calls/task/a001/response.json'])
def test_changed_inherited_bytes_are_rejected_before_any_new_call(tmp_path,relative):
    parent=parent_run(tmp_path)
    child=Downstream(tmp_path/'child')
    runner.prepare_from_accepted_cfg(parent.directory,run_dir=child.directory)
    path=child.directory/relative
    assert path.is_file(),relative
    path.write_bytes(path.read_bytes()+b'\n')
    with pytest.raises(ValueError,match='Accepted upstream bytes changed'):
        runner.run(child.directory,client_factory=child.factory)
    assert child.calls==[]


def test_parent_selection_mismatch_rejected_before_creating_child(tmp_path):
    parent=parent_run(tmp_path)
    runner.WRITER.json(parent.directory/'graph/selected.json',{'cfg':{}})
    with pytest.raises(ValueError,match='Retained CFG differs'):
        runner.prepare_from_accepted_cfg(parent.directory,run_dir=tmp_path/'child')
    assert not (tmp_path/'child').exists()


def test_reuse_of_a_closed_descendant_retains_original_owners(tmp_path):
    parent=parent_run(tmp_path)
    child=Downstream(tmp_path/'child')
    runner.prepare_from_accepted_cfg(parent.directory,run_dir=child.directory)
    assert runner.run(child.directory,client_factory=child.factory)['status']=='complete'
    before=inventory(child.directory)
    grandchild=Downstream(tmp_path/'grandchild')
    runner.prepare_from_accepted_cfg(child.directory,run_dir=grandchild.directory)
    result=runner.run(grandchild.directory,client_factory=grandchild.factory)
    assert result['status']=='complete',result
    assert len(grandchild.calls)==4
    matching_replay(grandchild.directory,result)
    assert inventory(child.directory)==before
