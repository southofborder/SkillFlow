"""Paired development validation with real, durable structural correction.

Selected starting chains share validators, v5 correction, and transport settings.
References and semantic expectations are external to every model request.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import re
from pathlib import Path
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.llm.config import LlmConfig
from skillflow.common.recording import (
    ResponseIntegrityError, SavedCallFailure, canonical_sha256,
    implementation_provenance, injected_factory, now, sha_file,
    streaming_factory, validated_trace,
)
from skillflow.common.runs import exclusive_run
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.structural_correction import ResponseChain, ResponseChainError, chain_counts
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.config import annotation_config, annotation_public_config, PUBLIC_CONFIG_FIELDS
from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt as review_prompt
from skillflow.propagation.review.services import validate_response as validate_review
from tools.doe.endpoint_validation_fixtures import endpoint_validation_fixtures
from tools.doe.prompt_screen import _read, _safe, _seal, _unseal, _render_snapshot, _sizes, _exact, _call_metrics
from tools.doe.summarize_pipeline_run import sum_usage

IDENTITY = "skillflow-endpoint-prompt-validation-v2"
LEGACY_IDENTITY = "skillflow-endpoint-prompt-validation-v1"
ARMS = ("baseline", "latest")
CASE_STAGES = {
    "annotation_ceramic_dispatch": "annotation",
    "annotation_folio_return": "annotation",
    "review_custody_release": "review",
    "review_voucher_delivery": "review",
}
CASE_ORDER = ("annotation_ceramic_dispatch", "review_custody_release",
              "annotation_folio_return", "review_voucher_delivery")
CLAIM = "Paired development validation; authored fixtures and assistant assessment are not independent expert ground truth."


def _schedule(cases):
    stages = {case["name"]: case["stage"] for case in cases}
    ordered = [name for name in CASE_ORDER if name in stages]
    return [{"case": name, "stage": stages[name], "arm": arm}
            for index, name in enumerate(ordered)
            for arm in (ARMS if index % 2 == 0 else tuple(reversed(ARMS)))]


def _implementation():
    names = ("endpoint_validation.py", "endpoint_validation_fixtures.py", "prompt_screen.py",
             "prompt_screen_fixtures.py", "summarize_pipeline_run.py")
    return {"production": implementation_provenance(),
            "tools": {name: sha_file(Path(__file__).with_name(name)) for name in names}}


def prepare_validation(run_dir, *, baseline_dir, config, case_names=None):
    directory, baseline = _safe(run_dir), _safe(baseline_dir)
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Prepare requires a new empty validation directory")
    if set(config) - set(PUBLIC_CONFIG_FIELDS):
        raise ValueError("Validation configuration must be public")
    config = annotation_config(config)
    LlmConfig(api_key="identity-check-only", **config)
    writer = ArtifactWriter(())
    frozen = {name: value for name, value in _read(baseline / "files.json").items() if name.startswith("src/")}
    if not frozen or any(not (baseline / name).is_file() or sha_file(baseline / name) != value
                         for name, value in frozen.items()):
        raise ResponseIntegrityError("Frozen baseline source differs from its receipt")
    cases = endpoint_validation_fixtures()
    if [(case["name"], case["stage"]) for case in cases] != list(CASE_STAGES.items()):
        raise ValueError("Validation requires four distinct cases")
    if case_names is not None:
        if (not isinstance(case_names, (list, tuple)) or not case_names
                or any(not isinstance(name, str) for name in case_names)
                or len(set(case_names)) != len(case_names)
                or set(case_names) - set(CASE_STAGES)):
            raise ValueError("Case selection must contain distinct supported case names")
        cases = [case for case in cases if case["name"] in case_names]
    inputs = []
    with exclusive_run(directory):
        snapshot = directory / "audit/baseline-source"
        for name, value in frozen.items():
            path = _safe(snapshot / name)
            if not path.is_relative_to(snapshot):
                raise ResponseIntegrityError("Snapshot path escaped its root")
            writer.text(path, (baseline / name).read_bytes().decode("utf-8"))
            if sha_file(path) != value:
                raise ResponseIntegrityError("Frozen source bytes changed")
        writer.json(directory / "audit/baseline-receipt.json", {"files": frozen,
            "original_receipt_sha256": sha_file(baseline / "files.json")})
        for case in cases:
            compile_response(case["reference"], case["material"])
            material = (prepare_review_material(case["material"], case["reference"])
                        if case["stage"] == "review" else case["material"])
            if case["stage"] == "review":
                validate_review(case["reference_response"], material)
            writer.json(directory / f"cases/{case['name']}/material.json", material)
            writer.json(directory / f"audit/fixtures/{case['name']}.json", case)
            inputs.append({"name": case["name"], "stage": case["stage"], "material": material})
        rendered = _render_snapshot(snapshot, inputs)
        writer.json(directory / "audit/baseline-render.json", {"imports": rendered["imports"], "network_disabled": True})
        for case in inputs:
            prompts = {"baseline": rendered["prompts"][case["name"]], "latest":
                (annotation_prompt if case["stage"] == "annotation" else review_prompt)(case["material"])}
            blocks = []
            for arm, prompt in prompts.items():
                if re.search(r"[\u4e00-\u9fff]", prompt):
                    raise ValueError("Validation prompts and inputs must use English")
                blocks.append(re.search(r"<!-- SKILLFLOW_PROMPT:INPUT:BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:INPUT:END -->", prompt, re.S).group(1))
                writer.text(directory / f"cases/{case['name']}/{arm}/prompt.txt", prompt)
                writer.json(directory / f"cases/{case['name']}/{arm}/prompt-sizes.json", _sizes(prompt))
            if blocks[0] != blocks[1]:
                raise ResponseIntegrityError("Paired arms must receive identical model inputs")
        schedule = _schedule(cases)
        writer.json(directory / "audit/preregistration.json", {
            "initial_chains": len(schedule), "structural_attempt_limit": None,
            "shared_correction": "Current production v5 for both arms; only initial prompt differs.",
            "task_calls": 0, "semantic_repairs": 0, "quality_reruns": 0,
            "semantic_checks": {c["name"]: c["semantic_checks"] for c in cases},
            "interpretation": "First response, correction counts, semantics and observed cost are separate outcomes; no generalized accuracy claim.",
            "formal_case_rerun": False})
        files = {p.relative_to(directory).as_posix(): sha_file(p) for p in directory.rglob('*')
                 if p.is_file() and p.name != '.runner.lock'}
        manifest = {"identity": IDENTITY, "created_at": now(), "config": config,
            "implementation": _implementation(), "files": files,
            "cases": [{"name": c["name"], "stage": c["stage"]} for c in cases],
            "schedule": schedule, "claim": CLAIM}
        writer.json(directory / "manifest.json", _seal(manifest))
    return manifest


def load_validation(run_dir, *, check_implementation=False):
    directory = _safe(run_dir)
    manifest = _unseal(_read(directory / "manifest.json"))
    if manifest.get('identity') not in {IDENTITY, LEGACY_IDENTITY}:
        raise ValueError("Unsupported endpoint validation identity")
    cases = manifest.get("cases")
    if (not isinstance(cases, list) or not cases
            or any(not isinstance(case, dict) or set(case) != {"name", "stage"}
                   or not isinstance(case["name"], str)
                   or case["name"] not in CASE_STAGES
                   or case["stage"] != CASE_STAGES[case["name"]] for case in cases)
            or cases != [{"name": name, "stage": stage}
                         for name, stage in CASE_STAGES.items()
                         if any(case["name"] == name for case in cases)]):
        raise ResponseIntegrityError("Validation case selection changed")
    if manifest['identity'] == LEGACY_IDENTITY and cases != [
            {"name": name, "stage": stage} for name, stage in CASE_STAGES.items()]:
        raise ResponseIntegrityError("Legacy validation requires its original four cases")
    if manifest.get('schedule') != _schedule(cases):
        raise ResponseIntegrityError("Validation schedule changed")
    for relative, value in manifest['files'].items():
        path = _safe(directory / relative)
        if not path.is_relative_to(directory) or not path.is_file() or sha_file(path) != value:
            raise ResponseIntegrityError("Frozen validation material changed: " + relative)
    if check_implementation and manifest['implementation'] != _implementation():
        raise ResponseIntegrityError("Validation implementation changed")
    return manifest


def _attempts(directory):
    traces = []
    for path in sorted(directory.glob('calls/*/a*/transport.json')):
        traces.extend(validated_trace(path))
    return traces, [a for group in traces for a in group.get('http_attempts', [])]


def _metrics(stage, prefix):
    counts = chain_counts(stage, prefix)
    if counts['record_integrity_errors']:
        raise ResponseIntegrityError("Call accounting integrity failure")
    calls = [{"call": path.parent.relative_to(stage).as_posix(), **_call_metrics(path.parent)}
             for path in sorted((stage / prefix).glob('a*/call.json'))]
    _, attempts = _attempts(stage)
    return {**counts, "usage": sum_usage(attempts),
            "call_seconds": sum(row['call_seconds'] or 0 for row in calls)}, calls


def _one(directory, manifest, item, *, writer, factory, stopping, replay=False, progress=None,
         factory_provider=None):
    stage = directory / 'cases' / item['case'] / item['arm']
    material = _read(directory / 'cases' / item['case'] / 'material.json')
    prompt = (stage / 'prompt.txt').read_bytes().decode('utf-8')
    if item['arm'] == 'latest' and prompt != (annotation_prompt if item['stage'] == 'annotation' else review_prompt)(material):
        raise ResponseIntegrityError("Latest prompt differs from its frozen builder")
    existing = _unseal(_read(stage / 'result.json')) if (stage / 'result.json').exists() else None
    if replay and existing is None:
        raise ResponseIntegrityError("Replay requires a recorded decision")
    if existing:
        for relative, value in existing['call_files'].items():
            if not (stage / relative).is_file() or sha_file(stage / relative) != value:
                raise ResponseIntegrityError("Recorded validation call changed: " + relative)
    prefix = 'calls/' + item['stage']
    validate = (lambda raw: compile_response(raw, material)) if item['stage'] == 'annotation' else (
        lambda raw: validate_review(raw, material).model_dump(mode='json'))
    chain = ResponseChain(stage, prefix=prefix, base_prompt=prompt,
        request_kind='endpoint_validation_' + item['stage'] + '_' + item['arm'],
        config=manifest['config'], writer=writer, validate=validate,
        client_factory=factory, factory_provider=factory_provider,
        stop_event=stopping, replay=replay, read_only=replay, progress=progress,
        interruption=existing['cursor'] if replay and existing['status'] == 'interrupted' else None)
    row = {**item, 'status': 'complete', 'error': None, 'artifacts': {}}
    try:
        result = chain.run()
        outputs = dict(zip(('raw-annotation.json', 'compiled-annotation.json', 'mapping.json'), result)) if item['stage'] == 'annotation' else {'review.json': result}
        for name, value in outputs.items():
            _exact(writer, stage / name, value, replay=replay)
            row['artifacts'][name] = sha_file(stage / name)
    except (ResponseIntegrityError, ResponseChainError):
        raise
    except SemanticFailure as error:
        row.update(status='semantic_failure', error=error.failure)
    except KeyboardInterrupt:
        row.update(status='interrupted', error='Stopped before starting a later request.')
    except Exception as error:
        recorded = sorted((stage / prefix).glob('a*/call.json'))
        if not recorded or _read(recorded[-1]).get('status') == 'complete':
            # An implementation fault is not evidence that the model should be
            # called again, nor a transport failure that permits the next case.
            raise
        kind = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
        row.update(status='interrupted' if kind == 'KeyboardInterrupt' else 'execution_error',
                   error={'type': kind, 'message': writer.clean(str(error))})
    metrics, calls = _metrics(stage, prefix)
    first_path = stage / prefix / 'a001/validation.json'
    first = _read(first_path) if first_path.exists() else None
    status = first['status'] if first else None
    row.update(first_response_status=status,
        first_response_valid=status in {'valid', 'semantic_failure'} if first else None,
        first_response_completed=status == 'valid' if first else None,
        first_response_valid_without_normalization=(status in {'valid', 'semantic_failure'} and first.get('normalization_sha256') is None) if first else None,
        accepted_call=chain.accepted_call, metrics=metrics, calls=calls, cursor=chain.cursor,
        response_chain=chain.snapshot(), call_files={p.relative_to(stage).as_posix(): sha_file(p)
            for p in (stage / 'calls').rglob('*') if p.is_file()})
    if existing and (replay or existing['status'] != 'interrupted') and row != existing:
        raise ResponseIntegrityError("Validation decision differs from accepted record")
    if not replay:
        writer.json(stage / 'result.json', _seal(row))
    return row


def _freeze_metrics(directory, summary, writer):
    path = directory / 'metrics.json'
    if path.exists():
        prior = _unseal(_read(path))
        if prior['summary_sha256'] != canonical_sha256(summary):
            raise ResponseIntegrityError("Frozen online summary changed")
        for name, value in prior['call_files'].items():
            if not (directory / name).is_file() or sha_file(directory / name) != value:
                raise ResponseIntegrityError("Frozen online call changed")
        return prior
    arms = {}
    for arm in ARMS:
        rows = [r for r in summary['results'] if r['arm'] == arm]
        attempts = [a for row in rows for a in _attempts(directory / 'cases' / row['case'] / arm)[1]]
        arms[arm] = {"initial_chains": len(rows), "completed": sum(r['status'] == 'complete' for r in rows),
            "first_response_valid": sum(r['first_response_valid'] is True for r in rows),
            "first_response_completed": sum(r['first_response_completed'] is True for r in rows),
            "first_response_unknown": sum(r['first_response_valid'] is None for r in rows),
            "logical_calls": sum(r['metrics']['logical_calls'] for r in rows),
            "structural_corrections": sum(r['metrics']['structural_corrections'] for r in rows),
            "json_normalizations": sum(r['metrics']['json_normalizations'] for r in rows),
            "http_attempts": sum(r['metrics']['http_attempts'] for r in rows),
            "http_attempts_observed": bool(rows) and all(r['metrics']['http_attempts_observed'] for r in rows),
            "http_retries": sum(r['metrics']['http_retries'] for r in rows), "usage": sum_usage(attempts),
            "returned_models": sorted({m for r in rows for m in r['metrics']['returned_models']}),
            "call_seconds": sum(r['metrics']['call_seconds'] for r in rows)}
    end = now(); start = _read(directory / 'online-state.json')['started_at']
    metrics = {'identity': summary['identity'], 'summary_sha256': canonical_sha256(summary), 'frozen_at': end,
        'online_timing': {'started_at': start, 'ended_at': end,
            'seconds': (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds(),
            'basis': 'Online execution through final decisions; excludes prepare and replay, includes interruption/resume intervals.'},
        'arms': arms, 'semantic_acceptance': 'pending_external_assessment',
        'call_files': {p.relative_to(directory).as_posix(): sha_file(p) for p in (directory / 'cases').rglob('*')
                       if p.is_file() and 'calls' in p.relative_to(directory / 'cases').parts}}
    writer.json(path, _seal(metrics))
    return metrics


def _report(directory, summary, writer):
    lines = ['# Endpoint prompt paired validation', '', CLAIM, '',
        f"Both arms use identical inputs, strict validators, current v5 correction, and transport configuration. {len(summary['cases']) * len(ARMS)} initial chains are scheduled; structural corrections are separately counted and unlimited. There are no Task-extraction, semantic-repair, or quality-rerun calls.", '',
        '| Case | Arm | Status | First legal | Calls | Corrections | HTTP attempts | Known total tokens | Call seconds |',
        '|---|---|---|---|---:|---:|---:|---:|---:|']
    for row in summary['results']:
        metrics = row['metrics']; usage = metrics['usage']['total_tokens']
        tokens = usage['total'] if usage['total'] is not None else str(usage['reported_subtotal']) + ' (known subtotal)' if usage['reported_subtotal'] is not None else 'Unknown'
        lines.append(f"| {row['case']} | {row['arm']} | {row['status']} | {row['first_response_valid']} | {metrics['logical_calls']} | {metrics['structural_corrections']} | {metrics['http_attempts']} | {tokens} | {metrics['call_seconds']:.2f} |")
    lines += ['', 'Reasoning and cache tokens are usage breakdowns, never added to total tokens. Missing usage remains unknown. A valid cannot_assess is a legal protocol response and a stopped semantic failure, not successful analysis. JSON normalization is separately recorded. First legal response and semantic correctness are different outcomes.', '',
        '## Evidence', '', '[Frozen expectations](audit/preregistration.json) · [Live decisions](summary.json)', '']
    if (directory / 'metrics.json').exists():
        lines += ['[Frozen online timing and usage](metrics.json)', '']
    if (directory / 'assessment.assistant.md').exists():
        lines += ['[Assistant semantic assessment](assessment.assistant.md)', '']
    for case in summary['cases']:
        name = case['name']
        lines.append(f"- [{name}: input](cases/{name}/material.json) · [external fixture and expectations](audit/fixtures/{name}.json)")
        for arm in ARMS:
            lines.append(f"  - [{arm} initial prompt](cases/{name}/{arm}/prompt.txt)" + (f" · [record](cases/{name}/{arm}/result.json)" if (directory / 'cases' / name / arm / 'result.json').exists() else ' · Not executed'))
    writer.text(directory / 'report.md', '\n'.join(lines) + '\n')
    import markdown_it
    body = markdown_it.MarkdownIt('commonmark').enable('table').render('\n'.join(lines))
    writer.text(directory / 'index.html', '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Endpoint prompt validation</title><style>body{max-width:1200px;margin:2rem auto;padding:0 1rem;font:16px/1.6 system-ui;color:#1e293b}table{border-collapse:collapse}td,th{padding:.4rem;border:1px solid #cbd5e1}</style>' + body + '</html>')


def run_validation(run_dir, *, env_file=None, clients=None, client_factory=None,
                   stop_event=None, replay=False, progress=None):
    directory = _safe(run_dir); manifest = load_validation(directory, check_implementation=True)
    if replay and (clients is not None or client_factory is not None):
        raise ValueError("Replay cannot use a live client")
    if clients is not None and client_factory is not None:
        raise ValueError("Choose injected clients or one factory")
    stopping, writer, factory = stop_event or Event(), ArtifactWriter(()), client_factory
    def provide(active_writer):
        nonlocal factory
        if replay:
            raise ResponseIntegrityError("Replay attempted to acquire a live client")
        if factory is None:
            factory, secrets = streaming_factory(manifest['config'], env_file=env_file)
            active_writer.secrets = tuple(secrets)
        if active_writer.clean(manifest) != manifest:
            raise ValueError("Credential overlaps frozen material")
        return factory
    with exclusive_run(directory):
        if not replay and not (directory / 'online-state.json').exists():
            writer.json(directory / 'online-state.json', {'started_at': now()})
        prior = _read(directory / 'summary.json') if (directory / 'summary.json').exists() else None
        summary = {'identity': manifest['identity'], 'cases': manifest['cases'], 'status': 'complete', 'results': [], 'claim': CLAIM}
        for item in manifest['schedule']:
            stage = directory / 'cases' / item['case'] / item['arm']
            if replay and not (stage / 'result.json').exists():
                continue
            if not replay and stopping.is_set():
                summary['status'] = 'interrupted'; break
            use_factory = factory
            if not replay:
                if clients is not None:
                    use_factory = injected_factory(clients[(item['case'], item['arm'])])
            if writer.clean(manifest) != manifest:
                raise ValueError("Credential overlaps frozen material")
            if progress:
                progress(item['case'] + '/' + item['arm'])
            row = _one(directory, manifest, item, writer=writer, factory=use_factory,
                       stopping=stopping, replay=replay, progress=progress,
                       factory_provider=provide if clients is None else None)
            summary['results'].append(row)
            if row['status'] == 'interrupted':
                summary['status'] = 'interrupted'; stopping.set()
            if not replay:
                writer.json(directory / 'summary.json', summary)
            if stopping.is_set():
                break
        if len(summary['results']) < len(manifest['schedule']) and summary['status'] == 'complete':
            summary['status'] = 'partial'
        if replay:
            if prior and prior['status'] == 'interrupted' and not prior['results'] and not summary['results']:
                summary['status'] = 'interrupted'
            if prior != summary:
                raise ResponseIntegrityError("Validation summary differs on zero-API replay")
            if (directory / 'metrics.json').exists():
                _freeze_metrics(directory, summary, writer)
            receipt = {'identity': manifest['identity'], 'status': 'matched', 'api_calls': 0,
                       'summary_sha256': canonical_sha256(summary)}
            writer.json(directory / 'replay.json', receipt)
            return receipt
        if summary['status'] == 'complete':
            _freeze_metrics(directory, summary, writer)
        writer.json(directory / 'summary.json', summary)
        _report(directory, summary, writer)
    return summary


def replay_validation(run_dir):
    return run_validation(run_dir, replay=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare'); prep.add_argument('--baseline-dir', required=True)
    prep.add_argument('--run-dir', required=True); prep.add_argument('--env-file')
    prep.add_argument('--case', action='append', dest='case_names', help='Select a supported case; repeat for a paired subset.')
    run = commands.add_parser('run'); run.add_argument('--run-dir', required=True); run.add_argument('--env-file')
    replay = commands.add_parser('replay'); replay.add_argument('--run-dir', required=True)
    args = parser.parse_args(argv)
    if args.command == 'prepare':
        result = prepare_validation(args.run_dir, baseline_dir=args.baseline_dir,
            config=annotation_public_config(LlmConfig.from_env(env_file=args.env_file)),
            case_names=args.case_names)
        print({'identity': result['identity'], 'cases': result['cases']})
    else:
        result = replay_validation(args.run_dir) if args.command == 'replay' else run_validation(
            args.run_dir, env_file=args.env_file, progress=lambda text: print(text, flush=True))
        print({'status': result['status']})


if __name__ == '__main__':
    main()
