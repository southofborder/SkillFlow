"""Prepare three explicitly requested development cases, without target calls."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import shutil
import sys

PROJECT = Path('D:/projects/SkillFlow')
sys.path.insert(0, str(PROJECT))
from skillflow.document_guided.runner import prepare
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import implementation_provenance

VERIFY = Path(__file__).resolve().parent
GA4 = Path(json.loads((VERIFY / 'prepared-run.json').read_text(encoding='utf-8'))['run_directory'])
PREFIX = PROJECT / 'experiments/doe/runs/latest-prompts-pipeline-v1-20261018-124304/audit/english-inputs'
CASES = {
    '001': ('conditional-notification', PREFIX / '001/package'),
    '010': ('catalog-query', PREFIX / '010/package'),
    '013': ('source-fetch-with-fallback', PROJECT / 'experiments/doe/runs/case-013-rerun-v1-20261019-105450/cases/013/inputs/package'),
}

def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def main():
    if (VERIFY / 'small-queue.json').exists():
        raise ValueError('The requested cases are already prepared; never prepare duplicates')
    protocol = json.loads((GA4 / 'run-protocol.json').read_text(encoding='utf-8'))
    current = implementation_provenance()
    assert current['sha256'] == protocol['implementation_sha256']
    tag = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
    rows = []
    for case, (name, source) in CASES.items():
        directory = PROJECT / f'experiments/doe/runs/document-guided-{case}-general-loops-high-v8-{tag}'
        prepare(source, run_dir=directory, config={'reasoning_effort': 'high'})
        material = read_snapshot(directory / 'source')[1]
        source_files = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in source.rglob('*') if p.is_file()}
        frozen_files = {p.relative_to(directory / 'source/inputs/package').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (directory / 'source/inputs/package').rglob('*') if p.is_file()}
        assert source_files == frozen_files
        shutil.copytree(GA4 / 'implementation-snapshot', directory / 'implementation-snapshot')
        controller = (GA4 / 'controller.py').read_text(encoding='utf-8').replace(
            'One authorized real GA4 general-loops v8 run', f'One authorized real development-case {case} general-loops v8 run')
        (directory / 'controller.py').write_text(controller, encoding='utf-8')
        (directory / 'implementation-snapshot/controller.py').write_text(controller, encoding='utf-8')
        snap_path = directory / 'implementation-snapshot/snapshot.json'
        snap = json.loads(snap_path.read_text(encoding='utf-8'))
        snap['run_controller_sha256'] = hashlib.sha256((directory / 'controller.py').read_bytes()).hexdigest()
        snap_path.write_text(json.dumps(snap,indent=2)+'\n', encoding='utf-8')
        p = {**protocol, 'authorization': 'User explicitly requested adding the three previously used small Skills without interrupting the active GA4 run.',
             'case_id': case, 'skill_name': name, 'source_directory': str(source),
             'source_sha256': material['source_sha256'], 'readable_files': len(material['files']),
             'source_utf8_bytes': sum(len(row['content'].encode('utf-8')) for row in material['files']),
             'source_file_sha256': source_files,
             'source_note': 'Historical audited English development package; new Task/CFG/fragments, no historical answer imports. Case001 is a recorded assistant English projection;010/013 retain original English source.',
             'queue_policy': 'Start once after GA4 controller closure, sequentially in001/010/013 order; one controller/two workers globally; no resampling.'}
        save(directory / 'run-protocol.json', p)
        save(directory / 'continuation-state.json', {'status': 'queued_not_started', 'run_directory': str(directory),
            'case_id': case, 'instructions': 'Queue supervisor owns the sole future launch; do not launch independently.'})
        rows.append({'case_id': case, 'skill_name': name, 'run_directory': str(directory),
                     'source_directory': str(source), 'source_sha256': material['source_sha256'],
                     'source_files': len(material['files']), 'status': 'queued_not_started'})
    save(VERIFY / 'small-queue.json', {'authorization': 'User requested adding the common three small Skills to the active validation.',
         'after_run': str(GA4), 'after_pid': json.loads((GA4 / 'controller-started.json').read_text(encoding='utf-8'))['pid'],
         'implementation_sha256': current['sha256'], 'run_order': rows, 'global_analysis_workers': 2,
         'target_cfg_task_annotation_imports': 0, 'native_starts_at_preparation': 0})
    print(json.dumps(rows, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
