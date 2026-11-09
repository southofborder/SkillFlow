"""Prepare exactly one authorized GA4 run after offline acceptance; zero model calls."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import prepare
from tools.doe.document_guided_client import resolve_executable

PROJECT = Path('D:/projects/SkillFlow')
VERIFY = PROJECT / 'output/verification/compact-review-v7'
BASE = PROJECT / 'experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527'
PREVIOUS = PROJECT / 'experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632'
STATE = VERIFY / 'continuation-state.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    state = read(STATE)
    if state.get('new_target_run'):
        raise RuntimeError('The authorized run already has a directory; inspect it, never prepare a replacement.')
    acceptance = read(VERIFY / 'offline-acceptance.json')
    if acceptance['status'] != 'passed':
        raise RuntimeError('Offline acceptance is incomplete.')
    source = BASE / 'source/inputs/package'
    _, original, _ = read_snapshot(BASE / 'source')
    assert original['source_sha256'] == state['source_sha256']
    assert len(original['files']) == 16
    cli = resolve_executable()
    renderer = PROJECT / 'formal/.lake/build/bin/skill_ir_retell.exe'
    assert renderer.is_file()
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
    run = PROJECT / ('experiments/doe/runs/document-guided-ga4-compact-review-high-v7-' + stamp)
    state.update(phase='preparing', new_target_run=str(run), online_started=False,
                 updated_at=datetime.now(timezone.utc).isoformat())
    write(STATE, state)
    manifest = prepare(source, run_dir=run, config={'reasoning_effort': 'high'})
    _, frozen, _ = read_snapshot(run / 'source')
    assert frozen == original
    controller = (PREVIOUS / 'controller.py').read_text(encoding='utf-8').replace(
        'One authorized real GA4 boundary-aligned v6 run', 'One authorized real GA4 compact-review v7 run')
    (run / 'controller.py').write_text(controller, encoding='utf-8')
    protocol = {
        'authorization': state['authorization'],
        'runtime': {'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'provider': 'openai'},
        'normal_semantic_requests': 7, 'workers': 2, 'semantic_repairs': 1,
        'structural_corrections_per_stage': 1, 'native_timeout_seconds': 2700,
        'native_extra_transient_attempts': 2, 'source_directory': str(source),
        'source_sha256': frozen['source_sha256'], 'readable_files': len(frozen['files']),
        'source_utf8_bytes': sum(len(row['content'].encode('utf-8')) for row in frozen['files']),
        'implementation_sha256': manifest['implementation']['sha256'],
        'cli_executable': str(cli), 'cli_executable_sha256': hashlib.sha256(cli.read_bytes()).hexdigest(),
        'renderer_executable': str(renderer), 'renderer_sha256': hashlib.sha256(renderer.read_bytes()).hexdigest(),
        'configuration_confirmation_model_calls': 0, 'model_monitor_requests': 0,
        'skill_execution': False, 'historical_cfg_task_answers_reused': False,
        'review_view': 'compact-v1', 'review_failure_policy': 'diagnostic_continue',
        'primary_endpoint': 'Actual propagation coverage and useful DOE; source review completion is reported separately.',
        'freeze_policy': 'No edits during generation, no extra sampling, no old-run continuation. Preserve all attempts and failures.',
        'baseline_v5': {'run': str(BASE), 'requests': 17, 'known_public_tokens': 1757935, 'analysis_seconds': 4688.20623,
                        'scope': 'Partial DOE: 8 of 126 IR processed.'},
        'baseline_v6': {'run': str(PREVIOUS), 'requests': 8, 'known_public_tokens': 874398, 'unknown_usage_requests': 1,
                        'analysis_seconds': 2773.1653492999903, 'scope': 'Review input rejected; no propagation or DOE.'},
        'offline_acceptance': str(VERIFY / 'offline-acceptance.json')}
    write(run / 'run-protocol.json', protocol)
    snapshot = implementation_provenance()
    assert snapshot['sha256'] == manifest['implementation']['sha256']
    paths = dict(snapshot['files'])
    for name in ('tools/doe/document_guided_client.py', 'tools/doe/document_guided_metrics.py', 'tools/doe/document_guided_pilot.py'):
        paths[name] = hashlib.sha256((PROJECT / name).read_bytes()).hexdigest()
    for name in paths:
        destination = run / 'implementation-snapshot' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / name, destination)
    write(run / 'implementation-snapshot/snapshot.json', {**snapshot, 'files': paths})
    write(run / 'continuation-state.json', {'status': 'prepared', 'run_directory': str(run),
        'instructions': 'Root may launch controller.py exactly once after acceptance; no historical resume or other target.'})
    state.update(phase='prepared', updated_at=datetime.now(timezone.utc).isoformat())
    write(STATE, state)
    print(json.dumps({'run': str(run), 'config': manifest['config'], 'source': protocol['source_sha256'],
        'files': protocol['readable_files'], 'bytes': protocol['source_utf8_bytes'], 'implementation': snapshot['sha256']}, indent=2))


if __name__ == '__main__':
    main()
