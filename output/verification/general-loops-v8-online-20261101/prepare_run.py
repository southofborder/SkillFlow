"""Prepare the one user-authorized full GA4 v8 run; no model calls."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil
import sys

PROJECT = Path('D:/projects/SkillFlow')
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.document_guided.runner import prepare
from tools.doe.document_guided_client import resolve_executable

VERIFY = Path(__file__).resolve().parent
OLD = PROJECT / 'experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749'

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def main():
    if (VERIFY / 'continuation-state.json').exists():
        raise ValueError('This authorization already has a recorded run; inspect it, do not prepare another')
    created = datetime.now(timezone(timedelta(hours=8)))
    run = PROJECT / ('experiments/doe/runs/document-guided-ga4-general-loops-high-v8-' + created.strftime('%Y%m%d-%H%M%S'))
    source = OLD / 'source/inputs/package'
    original = read_snapshot(OLD / 'source')
    current = implementation_provenance()
    baseline = json.loads((PROJECT / 'output/verification/general-loops-v8/implementation-final.json').read_text(encoding='utf-8'))
    differences = [key for key in sorted(set(current['files']) | set(baseline['files']))
                   if current['files'].get(key) != baseline['files'].get(key)]
    assert differences == ['src/skillflow/graph/audit/prompts.py'], differences
    assert current['sha256'] == 'a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b'
    state = {'phase': 'preparing', 'created_china': created.isoformat(), 'run_directory': str(run),
             'authorization': 'User requested one fresh complete GA4 online coverage, accuracy and actual-cost verification.',
             'normal_semantic_requests': 7, 'workers': 2, 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
             'provider': 'openai', 'implementation_sha256': current['sha256'],
             'instructions': 'Root is sole dispatch owner. No second controller, target restart, probe, Skill execution or old-run continuation. Freeze implementation and prompts through analysis and one zero-call replay.'}
    save(VERIFY / 'continuation-state.json', state)
    manifest = prepare(source, run_dir=run, config={'reasoning_effort': 'high'})
    frozen = read_snapshot(run / 'source')
    assert original[1] == frozen[1]
    assert len(frozen[1]['files']) == 16
    extras = ['tools/doe/document_guided_client.py', 'tools/doe/document_guided_metrics.py',
              'tools/doe/document_guided_pilot.py', 'formal/.lake/build/bin/skill_ir_retell.exe']
    inventory = dict(current['files'])
    for name in extras:
        inventory[name] = hashlib.sha256((PROJECT / name).read_bytes()).hexdigest()
    for name in inventory:
        target = run / 'implementation-snapshot' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / name, target)
    save(run / 'implementation-snapshot/snapshot.json', {'files': inventory, 'implementation_sha256': current['sha256']})
    cli = resolve_executable()
    protocol = {'authorization': state['authorization'], 'runtime': {'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'provider': 'openai'},
        'normal_semantic_requests': 7, 'workers': 2, 'semantic_repairs': 1, 'structural_corrections_per_stage': 1,
        'native_timeout_seconds': 2700, 'native_extra_transient_attempts': 2,
        'source_directory': str(source), 'source_sha256': frozen[1]['source_sha256'], 'readable_files': 16,
        'source_utf8_bytes': sum(len(row['content'].encode('utf-8')) for row in frozen[1]['files']),
        'implementation_sha256': current['sha256'], 'offline_accepted_sha256': baseline['sha256'],
        'post_acceptance_changed_files': differences,
        'post_acceptance_change_note': 'Standalone graph-audit output examples were clarified; the seven-call guided route uses its own unified source review. Current source is frozen with focused prelaunch tests.',
        'cli_executable': str(cli), 'cli_executable_sha256': hashlib.sha256(cli.read_bytes()).hexdigest(),
        'cli_identity_note': 'Installed CLI selected locally; no configuration-confirmation model request or equivalence claim.',
        'renderer_executable': str(PROJECT / extras[-1]), 'renderer_sha256': inventory[extras[-1]],
        'configuration_confirmation_model_calls': 0, 'model_monitor_requests': 0, 'skill_execution': False,
        'historical_cfg_task_answers_reused': False, 'review_view': 'compact-v1', 'review_failure_policy': 'diagnostic_continue',
        'primary_endpoint': 'Resolved propagation and source-boundary coverage; source-supported useful DOE; actual cost including all corrections, failures and retries.',
        'accuracy_policy': 'Source-based assistant audit after closure, independent of target contexts. No human gold, measured global precision/recall, or comparative advantage is presumed.',
        'freeze_policy': state['instructions'],
        'prelaunch_tests': str(VERIFY / 'prelaunch-focused.xml'),
        'offline_acceptance': str(PROJECT / 'output/verification/general-loops-v8/verification-summary.json')}
    save(run / 'run-protocol.json', protocol)
    controller = (OLD / 'controller.py').read_text(encoding='utf-8')
    controller = controller.replace('One authorized real GA4 compact-review v7 run', 'One authorized real GA4 general-loops v8 run')
    controller = controller.replace('import traceback\n', "import traceback\nimport sys\nsys.path.insert(0, 'D:/projects/SkillFlow')\n")
    (run / 'controller.py').write_text(controller, encoding='utf-8')
    save(run / 'prelaunch-check.json', {'source_byte_identical_to_v7': True, 'source_sha256': frozen[1]['source_sha256'],
        'implementation_sha256': current['sha256'], 'changed_since_offline_acceptance': differences,
        'historical_source_reused_only': True, 'new_target_starts': 0})
    save(VERIFY / 'prepared-run.json', {'run_directory': str(run), 'manifest_identity': manifest['identity'], 'protocol': protocol})
    print(json.dumps({'run_directory': str(run), 'implementation_sha256': current['sha256'], 'source_sha256': frozen[1]['source_sha256'], 'files': 16}, indent=2))

if __name__ == '__main__':
    main()
