"""One authorized interface r4 online case; no extra target or monitoring requests."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import time
import traceback
import sys
sys.path.insert(0, 'D:/projects/SkillFlow')

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import run as analyze, replay
from tools.doe.document_guided_client import Client
from tools.doe.document_guided_metrics import transport_metrics
from local_timing import LocalTiming

RUN = Path(__file__).resolve().parent
PROJECT = Path('D:/projects/SkillFlow')


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(name, value):
    path = RUN / name
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main():
    started, counter = stamp(), time.perf_counter()
    marker = {'pid': os.getpid(), 'started_at': started,
              'started_china': datetime.now(timezone(timedelta(hours=8))).isoformat()}
    with (RUN / 'controller-started.json').open('x', encoding='utf-8') as handle:
        json.dump(marker, handle, indent=2)
    manifest = json.loads((RUN / 'manifest.json').read_text(encoding='utf-8'))
    protocol = json.loads((RUN / 'run-protocol.json').read_text(encoding='utf-8'))
    write('continuation-state.json', {**marker, 'status': 'running', 'run_directory': str(RUN),
        'instructions': 'A single controller is running. Observe its artifacts and PID only. Do not start another controller or change source/prompts. Root owns reporting.'})

    def progress(value):
        event = {'observed_at': stamp(), 'stage': value['stage'],
                 'stage_state': value['stages'].get(value['stage']), 'counts': value.get('counts', {}),
                 'repair_used': value.get('repair_used', False)}
        # runner.mark already isolates optional observer errors and preserves
        # KeyboardInterrupt; no second validation/error layer is needed here.
        with (RUN / 'stage-events.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + '\n')
        print(json.dumps(event, ensure_ascii=False), flush=True)

    timing = LocalTiming().install()
    outcome, crash = None, None
    try:
        outcome = analyze(RUN, client_factory=lambda name, owner: Client(
            RUN / 'transport' / name, owner=owner, executable=protocol['cli_executable'],
            timeout=2700, retries=2, config=manifest['config']), progress=progress)
    except BaseException as error:
        crash = {'type': type(error).__name__, 'reason': str(error)}
        (RUN / 'controller-traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
    elapsed = time.perf_counter() - counter
    write('analysis-finished.json', {'started_at': started, 'finished_at': stamp(),
        'analysis_seconds': elapsed, 'status': None if outcome is None else outcome['status'], 'controller_error': crash})
    try:
        write('metrics.json', transport_metrics(RUN))
    except Exception as error:
        write('metrics.json', {'status': 'unavailable', 'reason': type(error).__name__ + ': ' + str(error)})
    try:
        write('component-timing.json', timing.snapshot())
    except (OSError, ValueError):
        pass
    checked = {'status': 'not_attempted', 'new_native_markers': None}
    if outcome is None and (RUN / 'result.json').is_file():
        saved = json.loads((RUN / 'result.json').read_text(encoding='utf-8'))
        if saved.get('status') in ('failed', 'partial', 'complete', 'diagnostic_complete'):
            outcome = saved
    if outcome is not None and outcome['status'] != 'interrupted':
        before = len(list((RUN / 'transport').rglob('started.json')))
        replay_start = time.perf_counter()
        timing.phase = "replay"
        try:
            restored = replay(RUN)
            checked = {'status': 'matched' if restored == outcome else 'different',
                       'elapsed_seconds': time.perf_counter() - replay_start,
                       'new_native_markers': len(list((RUN / 'transport').rglob('started.json'))) - before}
        except Exception as error:
            checked = {'status': 'failed', 'reason': type(error).__name__ + ': ' + str(error),
                       'elapsed_seconds': time.perf_counter() - replay_start,
                       'new_native_markers': len(list((RUN / 'transport').rglob('started.json'))) - before}
    timing.restore()
    try:
        write('component-timing.json', timing.snapshot())
    except (OSError, ValueError):
        pass
    write('replay-check.json', checked)
    snapshot = json.loads((RUN / 'implementation-snapshot/snapshot.json').read_text(encoding='utf-8'))
    changes = [name for name, digest in snapshot['files'].items()
               if not (PROJECT / name).exists() or hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() != digest]
    write('implementation-check.json', {'unchanged': not changes, 'changed_files': changes,
        'implementation_sha256': implementation_provenance()['sha256']})
    write('controller-finished.json', {'pid': os.getpid(), 'finished_at': stamp(),
        'status': None if outcome is None else outcome['status'], 'analysis_seconds': elapsed,
        'controller_error': crash, 'replay': checked})
    write('continuation-state.json', {'status': 'generation_closed', 'run_directory': str(RUN),
        'controller_pid': os.getpid(), 'analysis_seconds': elapsed,
        'analysis_status': None if outcome is None else outcome['status'], 'replay': checked,
        'instructions': 'Generation is closed. Preserve all actual requests and results. Do not regenerate or resume targets. Inspect coverage and costs, then deliver the English assessment and Chinese answer.'})
    print(json.dumps({'controller_closed': True, 'status': None if outcome is None else outcome['status'],
                      'analysis_seconds': elapsed, 'replay': checked}), flush=True)
    return 0 if outcome is not None and outcome['status'] in ('complete', 'partial') else 1


if __name__ == '__main__':
    raise SystemExit(main())
