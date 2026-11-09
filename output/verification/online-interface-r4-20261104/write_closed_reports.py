"""Assemble reports from closed, independently audited r4 artifacts only."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

V = Path(__file__).resolve().parent
ROOT = V.parents[2]

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def link(label, p):
    return f'[{label}]({p.as_posix()})'

def write_case(case, assessment):
    prepared = read(V / 'prepared-runs.json')
    config = next(x for x in prepared['run_order'] if x['case_id'] == case)
    run = Path(config['run_directory'])
    read(run / 'controller-finished.json')
    mechanical = read(run / 'mechanical-evidence.json')
    receipts = read(V / 'receipt-audit' / (case + '.json'))
    assert receipts['status'] == 'passed', receipts['issues']
    summary = {**mechanical, 'kind': 'source_reviewed_closed_run_summary',
        'source_assessment': assessment, 'source_package': config,
        'configuration': {'model': 'gpt-6.1-sol', 'effort': 'high', 'provider': 'openai', 'workers': 2,
            'normal_semantic_calls': 7, 'structural_correction_per_stage': 1, 'shared_semantic_repair_rounds': 1},
        'receipt_audit': str(V / 'receipt-audit' / (case + '.json')),
        'created_at': datetime.now(timezone.utc).isoformat()}
    summary['transport']['call_group_costs'] = receipts['groups']
    summary['transport']['stage_costs'] = receipts['stages']
    summary['transport']['public_identity_crosscheck'] = {'unique_count': receipts['unique_public_identities'], 'status': receipts['status']}
    summary['transport']['public_reconnect_notices'] = sum(len(n['events']) for n in receipts['internal_notices'])
    summary['transport']['internal_http_attempts_and_unreported_usage'] = None
    summary['transport']['cost_limit'] = 'Complete saved public final-turn counters are available; unreported provider-internal attempts/usage remain unknown. Cached input is included in input, not added again.'
    summary['implementation_sha256'] = receipts['implementation_sha256']
    (run / 'run-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    g = mechanical['propagation']['generated_ir']; t = mechanical['transport']; d = mechanical['doe']
    lines = [assessment['headline'], '', assessment['interpretation'], '',
        'This is the one authorized fresh interface-r4 run, with newly generated Task, flow, CFG and semantic fragments. No historical answers were imported. All observations below use the closed saved result and the controller-owned sole replay; this report did not run another analysis, replay, model, or Skill.', '',
        '| Completion evidence | Actual result |', '| --- | --- |',
        f"| Generated IR | {g['by_status']['processed']}/{g['total']} processed; {g['cutoff_count']} cutoff, {g['by_status']['blocked']} blocked, {g['by_status']['not_reached']} not reached |",
        f"| Source-boundary audit | {assessment['source_coverage_text']} |",
        f"| DOE | {d['status']}; {d['sinks']} sink positions; {d['comparisons']} sensitive comparisons; {d['engine_conclusions']} |",
        f"| Review | graph={mechanical['analysis']['graph_review']}; annotation={mechanical['analysis']['annotation_review']} |",
        f"| Replay | {mechanical['timing']['replay']['status']}; {mechanical['timing']['replay']['elapsed_seconds']:.3f} s; {mechanical['timing']['replay']['new_native_markers']} new native starts |", '',
        'Generated-IR coverage and source-site representation are distinct denominators. A processed instruction may retain opaque behavior, candidate ambiguity or a source relationship gap. A `no_excess_established` result with unresolved limitations is not a safety verdict.', '',
        'Source-supported findings and remaining limits:', '']
    lines += ['- ' + x for x in assessment['findings']]
    lines += ['', 'The four interface changes in this generated run:', '']
    lines += ['- ' + x for x in assessment['fix_observations']]
    lines += ['', 'The remaining blockers are classified by layer:', '']
    lines += ['- ' + x for x in assessment['blockers']]
    lines += ['', 'Independent source evidence:', '']
    lines += ['- ' + link(Path(p).name, Path(p)) for p in assessment['evidence_paths']]
    lines += ['', 'These are finite assistant source-audit criteria, not human gold. Supported/contradicted/unresolved relationship labels are not a general accuracy rate, precision, recall, proof of no DOE, or a comparison with direct GPT.', '',
        '| Request category | Actual starts | Input tokens | Cached input (subset) | Output tokens | Public total |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for name, row in receipts['groups'].items():
        lines.append(f"| {name} | {row['requests']} | {row['input_tokens']:,} | {row['cached_input_tokens']:,} | {row['output_tokens']:,} | {row['total_tokens']:,} |")
    u = receipts['known_public_usage']
    lines += [f"| Total | {receipts['native_starts']} | {u['input_tokens']:,} | {u['cached_input_tokens']:,} | {u['output_tokens']:,} | {u['total_tokens']:,} |", '',
        f"There were {t['network_retry_attempts']} outer transport retries, {t['unknown_usage_requests']} unknown public final-turn usage requests, and {summary['transport']['public_reconnect_notices']} public CLI reconnect/wait notices. Internal HTTP attempt counts and any unreported internal-attempt usage are unknown; the notices are not counted as extra model finals. Cached input is already part of input. No currency or hidden-reasoning estimate is made. Raw stdout final turns, final-answer association, process markers, usage sidecars and aggregate counters reconcile in the independent receipt audit.", '',
        '| Model stage, including its correction if any | Starts | Request elapsed sum (s) | Public total tokens |', '| --- | ---: | ---: | ---: |']
    for name, row in receipts['stages'].items():
        lines.append(f"| {name} | {row['requests']} | {row.get('request_seconds', 0):.3f} | {row['total_tokens']:,} |")
    lines += ['', 'Request elapsed sums include saved request intervals and can overlap across the two workers. They are not the analysis wall clock.', '',
        '| Local component | Measured seconds |', '| --- | ---: |']
    for row in mechanical['timing']['component_records']:
        if row['phase'] == 'analysis': lines.append(f"| {row['component']} | {row['elapsed_seconds']:.3f} |")
    for row in mechanical['timing']['doe_post_compute_publication']:
        if row['phase'] == 'analysis': lines.append(f"| DOE post-compute publication | {row['seconds']:.3f} |")
    lines += [f"| Main analysis wall | {mechanical['timing']['analysis_seconds']:.3f} |", f"| Sole replay wall | {mechanical['timing']['replay']['elapsed_seconds']:.3f} |", f"| Controller wall, analysis through replay closure | {mechanical['timing']['controller_wall_seconds']:.3f} |", '',
        'Component intervals are nested and must not be added to form another total. Propagation total includes its compute/save intervals; DOE total includes load/compute/publication. Unmeasured divisions remain unmeasured.', '',
        assessment['comparison'], '',
        'Saved artifacts: ' + ', '.join(link(n, run / n) for n in ['run-summary.json', 'mechanical-evidence.json', 'metrics.json', 'component-timing.json', 'propagation/manifest.json', 'doe/doe-result.json', 'replay-check.json']) + '.', '',
        'The archived and current pinned implementation files matched during receipt audit. Source hashes are checked separately by the source audit. Old failures, raw answers and paused v9 processes are preserved. No additional target sampling was added.', '']
    (run / 'assessment.en.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('cases', nargs='+', choices=['ga4', '001', '010', '013'])
    for c in p.parse_args().cases:
        x = write_case(c, read(V / 'report-inputs' / (c + '.json')))
        print(c, x['analysis']['status'], x['propagation']['generated_ir']['processed_fraction'])
