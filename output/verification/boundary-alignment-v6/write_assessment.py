"""Write additive assessment artifacts for the closed run; never call a model."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import SavedCallFailure

ROOT = Path('D:/projects/SkillFlow')
RUN = ROOT / 'experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632'
VERIFY = ROOT / 'output/verification/boundary-alignment-v6'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    finish = read(RUN / 'controller-finished.json')
    analysis = read(RUN / 'analysis-finished.json')
    metrics = read(RUN / 'metrics.json')
    result = read(RUN / 'result.json')
    replay = read(RUN / 'replay-check.json')
    implementation = read(RUN / 'implementation-check.json')
    assert finish['status'] == result['status'] == 'failed'
    assert implementation['unchanged'] and replay['new_native_markers'] == 0
    assert not (RUN / 'propagation').exists() and not (RUN / 'doe').exists()
    _, source, _ = read_snapshot(RUN / 'source')
    assert source['source_sha256'] == '3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd'
    prompt = (RUN / 'review/prompt.txt').read_text(encoding='utf-8')
    head, body = prompt.split('\nINPUT_JSON\n', 1)
    payload_text, source_text = body.split('\nCOMPLETE SOURCE\n', 1)
    payload = json.loads(payload_text)
    catalog_chars = len(json.dumps(payload['target_index'], ensure_ascii=False, separators=(',', ':')))
    attempt = next((RUN / 'transport/review').rglob('process.json')).parent
    delivered = (attempt.parent / 'prompt.txt').read_bytes().decode('utf-8')
    assert len(delivered) == 2002990
    failed_call = read(RUN / 'review/calls/review/a001/call.json')
    error = SavedCallFailure(failed_call['error_type'], failed_call['error'])
    replay_reason = type(error).__name__ + ': ' + str(error)
    assert replay_reason != result['reason']
    events = [json.loads(line) for line in (RUN / 'stage-events.jsonl').read_text(encoding='utf-8').splitlines()]
    timings = {}
    for event in events:
        stage = event['stage']
        when = datetime.fromisoformat(event['observed_at'])
        if event['stage_state']['status'] == 'running':
            timings[stage] = {'started_at': when.isoformat()}
        else:
            row = timings[stage]
            row.update(finished_at=when.isoformat(), status=event['stage_state']['status'],
                       wall_seconds=(when - datetime.fromisoformat(row['started_at'])).total_seconds())
    timings['review'].update(status='failed_input_delivery', finished_at=analysis['finished_at'],
        wall_seconds=(datetime.fromisoformat(analysis['finished_at']) - datetime.fromisoformat(timings['review']['started_at'])).total_seconds())
    item_types, catalog_timeouts = Counter(), 0
    for path in (RUN / 'transport').rglob('stdout.jsonl'):
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') == 'item.completed':
                item_types[event.get('item', {}).get('type')] += 1
    for path in (RUN / 'transport').rglob('stderr.txt'):
        catalog_timeouts += path.read_text(encoding='utf-8', errors='replace').count('failed to refresh available models: request timed out')
    public_audit = {'completed_item_types': dict(item_types),
        'unexpected_completed_item_types': sorted(k for k in item_types if k not in ('agent_message', 'reasoning')),
        'model_catalog_refresh_timeout_lines': catalog_timeouts,
        'scope': 'Public native event types only; no hidden session or reasoning content inspected or exported.'}
    failure = {'schema_version': 'boundary-alignment-failure-assessment-v1',
        'primary': {'category': 'engineering_input_delivery', 'stage': 'unified_source_review',
            'provider_or_cli_error': 'input_too_large', 'max_chars': 1048576,
            'delivered_chars': len(delivered), 'saved_review_body_chars': len(prompt),
            'delivery_envelope_chars': len(delivered) - len(prompt),
            'target_index_entries': len(payload['target_index']), 'target_index_chars': catalog_chars,
            'body_without_expanded_index_chars': len(prompt) - catalog_chars,
            'source_chars': len(source_text),
            'stderr': str((attempt / 'stderr.txt').relative_to(RUN)),
            'model_answer': False, 'structural_retry': False, 'semantic_repair': False},
        'replay': {'actual_result': replay, 'original_reason': result['reason'],
            'stored_error_type': failed_call['error_type'], 'replay_wrapper_class': type(error).__name__,
            'reason_produced_by_existing_outer_handler': replay_reason,
            'diagnosis': 'The saved error is ValueError, but offline replay raises SavedCallFailure. The outer runner serializes the wrapper class name and compares it with the original class name. This proves at least one differing decision field. No second whole-run replay was performed.'},
        'monitoring': {'stale_stage_state': result['stages']['review']['status'],
            'authoritative_run_state': result['status'],
            'limitation': 'The failed run retained review=running in its stage table; the controller then performed offline replay. Root initially misread that stale stage as a live review request and corrected the user-facing status after inspecting native and completion artifacts.'},
        'character_count_notice': 'These are exact delivery-limit measurements, not estimates of model tokens or money.'}
    summary = {'schema_version': 'boundary-alignment-assessment-v1',
        'assessed_at': datetime.now(timezone.utc).isoformat(), 'run': str(RUN),
        'outcome': 'failed_before_propagation_and_doe', 'complete_useful_doe': False,
        'configured_runtime': read(RUN / 'run-protocol.json')['runtime'],
        'source_sha256': source['source_sha256'], 'source_files': len(source['files']),
        'implementation_sha256': implementation['implementation_sha256'],
        'implementation_unchanged': True, 'normal_semantic_stages': 7,
        'completed_semantic_stages': 6, 'actual_cli_starts': metrics['native_process_starts'],
        'complete_model_answers': metrics['complete_usage_requests'],
        'structural_corrections': result['counts']['structural_corrections'],
        'semantic_repair_used': False, 'outer_network_retries': metrics['network_retry_attempts'],
        'known_public_tokens': metrics['known_token_usage'],
        'unknown_usage_attempts': metrics['unknown_usage_requests'], 'currency_amount': None,
        'analysis_seconds': analysis['analysis_seconds'], 'replay': replay,
        'controller_wall_seconds': (datetime.fromisoformat(finish['finished_at']) - datetime.fromisoformat(analysis['started_at'])).total_seconds(),
        'stage_timings': timings,
        'artifacts': {'cfg_blocks': 140, 'cfg_instructions': 349, 'cfg_edges': 162,
            'task_requirements': 48, 'task_issues': 8, 'processing_records': 349,
            'processing_limitations': 19, 'declared_unmodeled_processing_gaps': 0,
            'call_cases': 27, 'may_state_writes': 7, 'for_each_records': 3,
            'task_realizations': 48, 'top_level_demands': 87, 'operation_demand_records': 83,
            'sensitivity_declarations': 80, 'assembled_compilable_candidate': True,
            'source_review_answer': False, 'propagation_executed': False, 'doe_executed': False,
            'computed_ir_coverage': None, 'computed_sink_coverage': None, 'doe_findings': None},
        'public_protocol_observation': public_audit,
        'comparison': {'baseline_requests': 17, 'baseline_known_public_tokens': 1757935,
            'baseline_analysis_seconds': 4688.20623,
            'baseline_scope': 'Partial DOE: 8 of 126 IR processed; 5 resolved and 8 unresolved known sink positions.',
            'speed_or_accuracy_gain_established': False,
            'reason': 'The new run stopped before source review, propagation and DOE; lower spend and shorter time to failure are not an efficiency gain.'}}
    write(RUN / 'failure-analysis.json', failure)
    write(RUN / 'run-summary.json', summary)
    rows = []
    for row in metrics['requests']:
        stage = row['request'].split('/')[1]
        label = stage + (' correction' if row.get('structural_correction') else '')
        usage = row['complete_token_usage']
        rows.append(f"| {label} | {row['elapsed_seconds']:.2f} | {usage.get('input_tokens', 'unknown')} | {usage.get('cached_input_tokens', 'unknown')} | {usage.get('output_tokens', 'unknown')} | {usage.get('total_tokens', 'unknown')} |")
    report = f'''# GA4 boundary-alignment v6: closed-run assessment

**This run did not produce a complete or useful DOE conclusion. It stopped at delivery of the unified source-review request, before propagation or DOE ran.** The model did not refuse to annotate the Skill: all six preceding semantic stages produced usable structural artifacts, and the program assembled a compilable candidate. The immediate blocker was an oversized program-generated review input. This is an engineering failure in input construction and delivery, not a demonstrated semantic limitation of GPT or a successful capability result.

## Run and preservation

The sole new run used configured `gpt-6.1-sol / high / openai`, two workers and the seven-stage protocol. It began on 2026-10-29 at 00:17:31 China time. The same frozen 16-file, 155170-byte source was used, with source digest `{source['source_sha256']}`. Task, CFG and all fragments were regenerated; no historical answers were reused. The implementation digest was `{implementation['implementation_sha256']}` and its final check found no changed files. No Skill was installed or executed, and there were no model probes or model-based monitoring calls. Runtime identity here describes the explicit launch configuration; it is not an independent server attestation.

Original requests, both processing answers, all other answers, the rejected review input, stderr, failure records and the failed replay remain intact. This assessment adds records; it does not relabel or repair the frozen run.

## Actual completion

| Component | Result |
|---|---|
| Task | First answer accepted; 48 requirements and 8 recorded issues |
| Flow | First answer accepted |
| CFG | First answer accepted; 140 blocks, 349 IR, 162 edges |
| Processing | 349 records accepted after one selected-record structural correction |
| Task correspondence | First answer accepted; 48 realizations, 87 top-level demands and 83 operation-demand records |
| Sensitivity | First answer accepted; 80 declarations |
| Program assembly | Compiled candidate saved; 19 processing limitations retained |
| Unified source review | Request rejected before a review answer existed |
| Semantic repair | Not used; no review findings existed to authorize its dependency closure |
| Propagation / DOE | Not executed; computed coverage and findings are unknown, not zero exposure |

The processing fragment contains 27 case summaries, 7 may-state writes and 3 for_each records. All 349 IR have records and none of the 19 gaps is marked unmodeled. **These are structural coverage facts, not proof that all 349 IR propagate correctly or that the model's semantics are correct.** The three for_each records describe URL normalization and file-path construction. The API batch/reindex paths instead retain explicit CFG loops and declared limitations about dynamic selection and member pairing. Their requested occurrence-level properties were not established by this run. Cross-invocation cache transitions, exact counts, result-file ownership, summary implementation and installer effects also remain recorded limits or source questions. The missing source review means none should be presented as independently adjudicated.

The processing correction addressed source-evidence inheritance and invalid placement of cases in a segment slot. It replaced selected records rather than requesting another complete annotation. Its complete answer is retained separately from the initially invalid answer.

## Why the run stopped

The native CLI rejected `turn/start` with `input_too_large` (code -32602): **2,002,990 delivered characters exceeded the 1,048,576-character maximum**. It exited after 3.47 seconds, with no complete review answer or usage receipt. The review body contains 2,002,778 Unicode characters, plus a 212-character delivery envelope. These are character-limit measurements, never substitutes for actual tokens.

The expanded `target_index` contains **8,040 mechanical locators and 1,264,426 characters**. It alone exceeds the delivery limit and accounts for most of the prompt. Arithmetically removing that expanded directory leaves about 738,352 body characters, including source and semantic material. This is evidence for a narrow next change: use existing record IDs and checked field paths instead of shipping the full expanded leaf directory. It is not a validated replacement prompt, and no material was dropped or resent in this run.

The offline tests covered the new semantic mechanisms and representative source projections but did not catch the actual large graph's final delivery-size limit. That is an acceptance gap in this implementation. The correct next fix is input organization, not a weaker semantic standard or a new sampling attempt inside the stopped run.

There were {catalog_timeouts} background model-catalog refresh timeout lines in native stderr. Earlier stages nevertheless returned complete answers. These warnings are separate from the explicit input_too_large failure; their causal effect on latency is not established. There were zero outer transport retries.

## Replay and monitoring defects

The one automatic zero-model replay lasted **903.68 seconds (15 min 3.68 sec)**. It launched **zero new native requests**, but its result-consistency check failed: `Replayed guided decisions differ from saved results`. This is a failed replay, not a pass with a caveat.

The live outer handler recorded `ValueError: {failed_call['error']}`. Saved-call restoration raises `SavedCallFailure` while retaining `error_type=ValueError`; the outer handler formats the wrapper class name instead. The constructed replay reason is `{replay_reason}`. Comparing those strings proves at least one differing decision field. This diagnosis used saved records and the existing exception constructor; no second whole-run replay was performed.

The saved top-level run status is failed, but the last stage table still says review=running. The controller then spent time in offline replay. Root initially treated the stale stage as an ongoing review and corrected that statement after inspecting completion and native records. Future observation must prioritize run completion/failure markers, and terminal error handling should close the active stage. No frozen stage record was rewritten here.

## Cost and time

There were **8 actual CLI process starts**: seven planned semantic stage requests, including the rejected review request, plus one processing correction. Seven complete model answers were saved; one of them was the initially invalid processing answer. Six semantic stages completed. Public known usage totals **874,398 tokens**: 708,965 input and 165,433 output. Cached input is 299,648 and reported reasoning output is 27,373; these are subsets and are not added again. The rejected request has unknown usage. Native internal HTTP attempt counts and monetary cost are unavailable. Public completed events contained seven agent messages and no observed tool execution or delegation; hidden reasoning was neither read nor exported.

| Native request | Seconds | Input | Cached input subset | Output | Known total |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The main analysis took **2773.17 seconds (46 min 13.17 sec)** to fail. Program assembly/compilation alone occupied **{timings['assembly']['wall_seconds']:.2f} seconds (about 11 min 46 sec)**. The controller, including the one replay and closure checks, lasted **{summary['controller_wall_seconds']:.2f} seconds (about 61 min 17 sec)**. Per-request times overlap because of the two-worker schedule; their sum is not wall-clock duration.

The preceding High run used 17 requests, 1,757,935 known public tokens and 78 min 8.21 sec, and reached a partial DOE result with only 8/126 IR processed. This run used fewer requests and known tokens, but stopped earlier in the pipeline and produced no DOE. **No speed, accuracy or completeness advantage is established by that difference.** The increase from 126 to 349 IR also changes the amount of represented work and does not by itself demonstrate improved source coverage.

## Implementation and offline evidence

Implemented components include shared boundary granularity, nonrecursive call outcomes, bounded may-state summaries, a single each after field prefixes, source-evidence and complete-fragment checks, program assembly and sparse review ownership. The affected-interface suite passed 473 tests in 234.26 seconds. A fresh post-fix suite passed 100 in 60.86 seconds; these suites overlap. Independent final integration checks passed 11 in 14.41 seconds. A wider historical suite was stopped and is not claimed to have passed. All of these were zero-model engineering checks.

The next narrow work is to replace the expanded review locator directory with compact record-level addressing, apply a local delivery-length check, normalize saved failure identity during replay, and close terminal progress states. The ordinary boundary and loop semantics still require a completed source review and actual propagation/DOE on a future authorized run. No generic cache or exception engine is indicated by the observed delivery failure.

## Evidence

- [Machine summary]({RUN.as_posix()}/run-summary.json), [failure attribution]({RUN.as_posix()}/failure-analysis.json), [public cost ledger]({RUN.as_posix()}/metrics.json).
- [Original run decision]({RUN.as_posix()}/result.json), [main completion]({RUN.as_posix()}/analysis-finished.json), [replay failure]({RUN.as_posix()}/replay-check.json), [unchanged implementation]({RUN.as_posix()}/implementation-check.json).
- [Compiled candidate]({RUN.as_posix()}/annotation/audit/compiled-response.json), [model-facing assembled annotation]({RUN.as_posix()}/annotation/audit/wire-annotation.json), [processing fragment and limits]({RUN.as_posix()}/steps/processing/value.json).
- [Rejected review prompt]({RUN.as_posix()}/review/prompt.txt), [native rejection]({(attempt / 'stderr.txt').as_posix()}), [frozen run protocol]({RUN.as_posix()}/run-protocol.json).
- [Chinese design/offline report]({ROOT.as_posix()}/docs/doe/abstraction-alignment-v6-offline.zh.md), [machine offline acceptance]({VERIFY.as_posix()}/offline-acceptance.json).
'''
    (RUN / 'assessment.en.md').write_text(report, encoding='utf-8')
    state = read(VERIFY / 'continuation-state.json')
    state.update(phase='closed_report_ready', updated_at=datetime.now(timezone.utc).isoformat(),
                 report=str(RUN / 'assessment.en.md'), replay_status=replay['status'],
                 remaining=['Deliver the verified assessment to the user; no further model run is authorized by this one-run request.'])
    write(VERIFY / 'continuation-state.json', state)
    print(json.dumps({'report': str(RUN / 'assessment.en.md'), 'known_tokens': metrics['known_token_usage']['total_tokens'],
                      'unknown_usage_attempts': metrics['unknown_usage_requests'], 'analysis_seconds': analysis['analysis_seconds'],
                      'replay_status': replay['status'], 'controller_wall_seconds': summary['controller_wall_seconds']}))


if __name__ == '__main__':
    main()
