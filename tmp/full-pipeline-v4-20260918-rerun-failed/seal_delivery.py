"""Seal the exact four authorized delivery directories after final checks."""
import importlib.util, json, hashlib, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
RUN=REPO/'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed'
STAGE=HERE/'staging'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=REPO/'packages/skill-ir/experiments/security_profile/tools/export_full_pipeline.py'
spec=importlib.util.spec_from_file_location('_final_delivery_exporter',tool)
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
plan=read(STAGE/'review-data.json')
assert len(plan['cases'])==30
checks=exporter.validate_staging(plan,STAGE)
assert len(checks)==30
visual=read(HERE/'final-visual-binding.json')
assert visual['status']=='passed' and len(visual['cases'])==30
for case in visual['cases']:
    assert digest(STAGE/case['png_file'])==case['png_sha256']
replay=read(HERE/'replay-acceptance/validation.json')
assert replay['status']=='passed' and replay['checks']['online_entries']==0
origins=read(RUN/'rerun-provenance.json')
assert len(origins['rerun_cases'])==len(origins['reused_cases'])==15
names={row['basename'] for row in plan['cases']}
assert {x.stem for x in (REPO/'dataset/skills').iterdir()}==names
for directory,suffix in [('ir-IPP','.png'),('suggestions','.md'),('security-profiles','.json')]:
    files=list((STAGE/directory).iterdir())
    assert len(files)==30 and {f.stem for f in files}==names
    assert all(f.is_file() and f.suffix==suffix for f in files)
for row in plan['cases']:
    review=read(RUN/'assistant-reviews'/f"{row['case_id']}.json")
    selected=[r for r in review['reviews'] if r['revision']==row['selected_revision'] and r['graph_sha256']==row['graph_sha256']]
    assert len(selected)==1
    assert digest(REPO/'dataset/skills'/(row['basename']+'.zip'))==row['zip_sha256']
assert (STAGE/'review/index.html').stat().st_size>0
assert (STAGE/'review/report.md').is_file()
files={f.relative_to(STAGE).as_posix():digest(f)
       for dirname in ('ir-IPP','suggestions','security-profiles','review')
       for f in sorted((STAGE/dirname).rglob('*')) if f.is_file() and f.relative_to(STAGE).as_posix()!='review/verification.json'}
assert all(not f.is_symlink() for dirname in ('ir-IPP','suggestions','security-profiles','review') for f in (STAGE/dirname).rglob('*'))
summary=read(RUN/'experiment-result.json')['summary']
doc={'schema_version':1,'identity':'skill-ir-thirty-case-delivery-verification-v1',
     'status':'passed','scope':'交付来源、配对、记录、离线重放和静态视觉验收；不代表30例语义核对或标注全部通过',
     'cases':30,'run_id':RUN.name,'summary':summary,'rerun_cases':origins['rerun_cases'],
     'reused_cases':origins['reused_cases'],'source_zip_unchanged':True,
     'assistant_reviewed':30,'human_confirmed':False,'visual_checks':visual,
     'replay_validation_sha256':digest(HERE/'replay-acceptance/validation.json'),
     'lineage_summary_sha256':digest(RUN/'lineage-summary.json'),
     'render_and_binding_checks':checks,'files':files,
     'browser_interaction':'实际30例file URL导航被工具拒绝，未绕过；静态验证不替代用户浏览器交互验收。'}
target=STAGE/'review/verification.json'
target.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copy2(target,RUN/'delivery-acceptance/verification.json')
shutil.copy2(STAGE/'export-manifest.json',RUN/'delivery-acceptance/export-manifest.json')
shutil.copy2(STAGE/'review-data.json',RUN/'delivery-acceptance/review-data.json')
print(json.dumps({'status':'passed','cases':30,'sealed_files':len(files),'verification_sha256':digest(target)},ensure_ascii=False))
