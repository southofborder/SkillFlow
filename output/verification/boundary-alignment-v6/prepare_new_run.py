"""Prepare the one authorized fresh GA4 run; no model process is started here."""
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
VERIFY = PROJECT / 'output/verification/boundary-alignment-v6'
BASE = PROJECT / 'experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527'
STATE = VERIFY / 'continuation-state.json'


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    state = json.loads(STATE.read_text(encoding='utf-8'))
    if state.get('new_target_run'):
        raise RuntimeError('The authorized fresh run is already prepared; inspect its saved state rather than creating another.')
    acceptance = json.loads((VERIFY / 'offline-acceptance.json').read_text(encoding='utf-8'))
    if acceptance['status'] != 'passed':
        raise RuntimeError('Offline acceptance is not complete.')
    source_path = BASE / 'source/inputs/package'
    _, original_source, _ = read_snapshot(BASE / 'source')
    assert original_source['source_sha256'] == '3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd'
    cli = resolve_executable()
    renderer = PROJECT / 'formal/.lake/build/bin/skill_ir_retell.exe'
    assert renderer.is_file()
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
    run = PROJECT / ('experiments/doe/runs/document-guided-ga4-boundary-high-v6-' + stamp)
    manifest = prepare(source_path, run_dir=run, config={'reasoning_effort': 'high'})
    _, new_source, _ = read_snapshot(run / 'source')
    assert new_source == original_source
    controller = (BASE / 'controller.py').read_text(encoding='utf-8').replace(
        'One authorized real GA4 v5 run', 'One authorized real GA4 boundary-aligned v6 run')
    (run / 'controller.py').write_text(controller, encoding='utf-8')
    protocol = {'authorization': 'Implement the approved abstraction-alignment plan, pass offline acceptance, then one fresh GA4 High run and one zero-model replay.',
        'runtime': {'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'provider': 'openai'},
        'normal_semantic_requests': 7, 'workers': 2, 'semantic_repairs': 1,
        'structural_corrections_per_stage': 1, 'native_timeout_seconds': 2700, 'native_extra_transient_attempts': 2,
        'source_directory': str(source_path), 'source_sha256': new_source['source_sha256'],
        'readable_files': len(new_source['files']),
        'source_utf8_bytes': sum(len(row['content'].encode('utf-8')) for row in new_source['files']),
        'implementation_sha256': manifest['implementation']['sha256'],
        'cli_executable': str(cli), 'cli_executable_sha256': hashlib.sha256(cli.read_bytes()).hexdigest(),
        'renderer_executable': str(renderer), 'renderer_sha256': hashlib.sha256(renderer.read_bytes()).hexdigest(),
        'configuration_confirmation_model_calls': 0, 'model_monitor_requests': 0,
        'skill_execution': False, 'historical_cfg_task_answers_reused': False,
        'primary_endpoint': 'Complete useful DOE, assessed by actual acquisition/delivery/save/return coverage, demand/sensitivity resolution and source review, not file existence.',
        'freeze_policy': 'No implementation or prompt edits after launch, no additional sampling or old-run continuation; retain all answers, corrections, failures and available usage.',
        'baseline': {'run': str(BASE), 'requests': 17, 'known_public_tokens': 1757935, 'analysis_seconds': 4688.20623},
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
        'instructions': 'Launch controller.py exactly once after root checks offline acceptance. Do not reuse old objects or start any other target.'})
    state.update(phase='prepared', updated_at=datetime.now(timezone.utc).isoformat(),
        new_target_run=str(run), online_started=False)
    write(STATE, state)
    print(json.dumps({'run': str(run), 'config': manifest['config'], 'source': protocol['source_sha256'],
        'files': protocol['readable_files'], 'bytes': protocol['source_utf8_bytes'], 'implementation': snapshot['sha256']}, indent=2))


if __name__ == '__main__':
    main()
