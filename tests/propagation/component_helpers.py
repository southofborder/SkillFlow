"""Explicit current-contract fixtures; never migrate production runs."""
from copy import deepcopy
import json
from pathlib import Path

from skillflow.propagation.annotation.runner import prepare_run, run_annotation
from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts


def accepted_annotation(directory, material, raw):
    directory = Path(directory)
    package = directory.parent / (directory.name + '-source')
    package.mkdir(parents=True)
    for item in material['source']['files']:
        file = package / item['path']; file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(item['content'].encode('utf-8'))
    graph = directory.parent / (directory.name + '-cfg.json')
    graph.write_text(json.dumps({'cfg':material['cfg']},ensure_ascii=False),encoding='utf-8')
    from skillflow.task.runner import prepare_task_run, run_task
    from skillflow.propagation.contracts.task import CandidateTask
    task_directory = directory.with_name(directory.name + '-task')
    declaration = {name: material['task'][name] for name in CandidateTask.model_fields}
    class AuthoredTaskClient:
        def complete(self, prompt):
            return deepcopy(declaration)
    prepare_task_run(task_directory, material['source'], user_request=material['user_request'])
    assert run_task(task_directory, client=AuthoredTaskClient())['status'] == 'complete'
    prepare_run(package,graph,run_dir=directory, task_run=task_directory, user_request=material['user_request'])
    class Client:
        def complete(self,prompt): return deepcopy(raw)
    result = run_annotation(directory,client=Client())
    assert result['status'] == 'complete', result
    return directory


def components(cfg,annotation,solved):
    result = {'cfg':cfg,'annotation':deepcopy(annotation),
        'data':[entry['data'] for entry in solved.registry.to_dict()['records']],
        'records':solved.records.records_dict(),
        'sinks':resolved_sink_boundaries(annotation['locations'],solved.records.records_dict()),
        'status':solved.status,'coverage':solved.coverage,'diagnostics':solved.diagnostics}
    validate_propagation_facts(**result)
    return result
