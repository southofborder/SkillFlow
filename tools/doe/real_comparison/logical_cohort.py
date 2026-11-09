"""Assemble sealed epochs for analysis, without asserting one generation epoch.

This creates no target requests. Direct outcomes come from the prospective
direct-only epoch; paused SkillFlow outcomes remain the stopped donor outcomes.
The permanent output seal makes this analysis workspace nongenerating.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from . import direct_closure
from . import exploratory_cli as base
from .exploratory_grading import verify_closed_outputs
from .formal_cli import tree_hashes
from .protocol import sha256, utc_now, write_json

SCHEMA = 'skillflow-analysis-only-logical-cohort-v1'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_direct_seal(run):
    seal = read(run / 'output-freeze.json')
    require(seal.get('schema_version') == direct_closure.SCHEMA and seal.get('planned_outputs') == 192,
            'A genuine192-output direct lineage closure is required')
    actual = {'workflows/' + k: v for k, v in tree_hashes(run / 'workflows').items()}
    require(actual == seal['files'] and sha256(run / 'summary.json') == seal['summary_sha256']
            and sha256(run / 'lineage-verification.json') == seal['closure_lineage']['verification_sha256'],
            'Closed direct outputs or lineage verification changed')
    proof = read(run / 'lineage-verification.json')
    require(proof.get('status') == 'matched' and proof.get('model_calls') == 0
            and proof.get('logical_direct_outputs') == 192,
            'Direct lineage verification did not establish complete byte closure')
    base.verify_run(run, generation=False)
    return seal


def select_origins(entries, donor, direct):
    require(len(entries) == 264 and len({x['workflow_id'] for x in entries}) == 264,
            'All264 unique fixed logical identities are required')
    origins = {x['workflow_id']: donor if x['method'] == 'skillflow' else direct for x in entries}
    require(sum(path == donor for path in origins.values()) == 72
            and sum(path == direct for path in origins.values()) == 192
            and all(x['method'] in {'skillflow', 'audit', 'chain'} for x in entries),
            'The analysis must preserve72 paused SkillFlow and192 direct identities')
    return origins


def assemble(donor_dir, direct_dir, out_dir):
    donor, direct, out = map(lambda p: Path(p).resolve(), (donor_dir, direct_dir, out_dir))
    require(not out.exists() and not any(out.is_relative_to(p) or p.is_relative_to(out) for p in (donor, direct)),
            'Use a new analysis directory outside both generation runs')
    entries, donor_seal = verify_closed_outputs(donor)
    direct_seal = verify_direct_seal(direct)
    continuation = read(direct / 'direct-continuation.json')
    require(Path(continuation['donor_run']).resolve() == donor
            and direct_seal['closure_lineage']['donor_output_freeze_sha256'] == sha256(donor / 'output-freeze.json'),
            'The direct continuation must bind this exact stopped donor')
    origins = select_origins(entries, donor, direct)
    direct_items = {x['workflow_id']: x for x in base.planned(direct)}
    for item in entries:
        if item['method'] != 'skillflow':
            require(direct_items.get(item['workflow_id']) == item, 'A prospective direct schedule identity changed')
    out.mkdir(parents=True)
    original_input = read(donor / 'freeze.json')
    for name, digest in original_input['files'].items():
        require(sha256(donor / name) == digest, 'The donor input changed')
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(donor / name, target)
    lineage = []
    for item in entries:
        wid = item['workflow_id']
        source = origins[wid]
        prefix = 'workflows/' + wid + '/'
        seal = donor_seal if source == donor else direct_seal
        expected = {k[len(prefix):]: v for k, v in seal['files'].items() if k.startswith(prefix)}
        require(expected == tree_hashes(source / 'workflows' / wid), 'A logical source workflow changed')
        shutil.copytree(source / 'workflows' / wid, out / 'workflows' / wid)
        require(tree_hashes(out / 'workflows' / wid) == expected, 'Copied logical outcome bytes differ')
        lineage.append({'workflow_id': wid, 'source_run': str(source),
            'source_output_freeze_sha256': sha256(source / 'output-freeze.json'),
            'generation_epoch': 'stopped_original' if source == donor else 'prospective_direct_continuation',
            'source_result_sha256': expected['result.json']})
    assembly = {'schema_version': SCHEMA, 'created_at': utc_now(), 'target_model_calls': 0,
        'analysis_only': True, 'same_epoch_three_way_comparison_completed': False,
        'user_other_skillflow_process_included_or_controlled': False,
        'fixed_logical_outputs': 264, 'stopped_original_skillflow_outputs': 72,
        'prospective_direct_outputs_including28_original_imports': 192,
        'donor_run': str(donor), 'donor_output_freeze_sha256': sha256(donor / 'output-freeze.json'),
        'direct_run': str(direct), 'direct_output_freeze_sha256': sha256(direct / 'output-freeze.json'),
        'donor_closure_compatibility': donor_seal.get('closure_compatibility'),
        'workflow_origins': lineage,
        'inference_limit': 'All planned logical denominators are retained. Different generation epochs and the paused/stopped SkillFlow arm prevent a completed contemporaneous comparative advantage claim. Independent user-launched SkillFlow processes are excluded.'}
    write_json(out / 'logical-cohort-lineage.json', assembly, immutable=True)
    plan = read(out / 'plan.json')
    plan.update(analysis_only=True, generation_permanently_closed=True,
                same_epoch_three_way_comparison_completed=False,
                logical_lineage_sha256=sha256(out / 'logical-cohort-lineage.json'))
    write_json(out / 'plan.json', plan)
    write_json(out / 'freeze.json', {'schema_version': base.SCHEMA,
        'analysis_only': True, 'generation_permanently_closed': True,
        'files': tree_hashes(out), 'implementation': original_input['implementation'],
        'reference_and_scores_enter_target_inputs': False}, immutable=True)
    result = base.summary(out)
    result.update(analysis_only=True, same_epoch_three_way_comparison_completed=False,
                  logical_lineage_sha256=sha256(out / 'logical-cohort-lineage.json'),
                  global_stop=(donor / 'dispatch-stop.json').exists() or (direct / 'dispatch-stop.json').exists(),
                  source_run_global_stops={'stopped_original': (donor / 'dispatch-stop.json').exists(),
                                          'prospective_direct': (direct / 'dispatch-stop.json').exists()})
    write_json(out / 'summary.json', result, immutable=True)
    write_json(out / 'output-freeze.json', {'schema_version': base.SCHEMA, 'closed_at': utc_now(),
        'planned_outputs': 264, 'analysis_only': True, 'generation_permanently_closed': True,
        'same_epoch_three_way_comparison_completed': False,
        'files': {'workflows/' + k: v for k, v in tree_hashes(out / 'workflows').items()},
        'failed_results_remain_in_denominator': True, 'logical_lineage_sha256': sha256(out / 'logical-cohort-lineage.json'),
        'summary_sha256': sha256(out / 'summary.json'), 'assembler_sha256': sha256(__file__)}, immutable=True)
    verify_closed_outputs(out)
    return {'schema_version': SCHEMA, 'logical_outputs': 264, 'target_model_calls': 0,
            'analysis_only': True, 'same_epoch_three_way_comparison_completed': False,
            'output_freeze_sha256': sha256(out / 'output-freeze.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--donor-dir', required=True)
    parser.add_argument('--direct-dir', required=True)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()
    print(json.dumps(assemble(args.donor_dir, args.direct_dir, args.out_dir), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
