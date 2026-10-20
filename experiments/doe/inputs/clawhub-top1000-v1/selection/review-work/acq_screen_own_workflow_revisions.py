"""Preserve and revise source-only eligibility when applying the own-workflow rule."""
from pathlib import Path
import json
from tools.doe.real_comparison.selection import validate_evidence
C=Path('experiments/doe/inputs/clawhub-top1000-v1'); B=C/'selection/review-batches'; H=C/'selection/review-history';H.mkdir(exist_ok=True)
R={}
for snap in ['acq_screen_0301_0400_snapshot.json','acq_screen_0626_0750_complete_snapshot.json']:
 R.update({x['rank']:x for x in json.loads((C/'selection'/snap).read_text(encoding='utf-8'))['entries']})
def ev(rank,path,a,b):
 L=(C/R[rank]['source_dir']/path).read_text(encoding='utf-8-sig').splitlines()
 return {'path':path,'start_line':a,'end_line':b,'quote':'\n'.join(L[a-1:b])}
def feat(rank,name,path,a,b,reason):return {'feature':name,'reason':reason,'evidence':[ev(rank,path,a,b)]}
def change(old,new,ranks):
 p=B/old; archive=H/(old[:-5]+'-before-own-workflow.json')
 data=json.loads((p if p.exists() else archive).read_text(encoding='utf-8'))
 for rank,mutate in ranks.items():mutate(data['decisions'][R[rank]['canonical_id']])
 for ident,d in data['decisions'].items():
  row=next(v for v in R.values()if v['canonical_id']==ident); texts={}
  for f in(C/row['source_dir']).rglob('*'):
   if f.is_file():
    try:texts[f.relative_to(C/row['source_dir']).as_posix()]=f.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:pass
  for ft in d['features']:validate_evidence(texts,ft['evidence'])
  if d['decision']=='exclude':validate_evidence(texts,d['exclusion_evidence'])
 raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
 if p.exists():
  if archive.exists():assert archive.read_bytes()==p.read_bytes()
  else:archive.write_bytes(p.read_bytes())
  p.unlink()
 out=B/new
 if out.exists():assert out.read_bytes()==raw
 else:out.write_bytes(raw)
 print(new,len(data['decisions']))
def rejected(rank,reason,spans):
 def apply(d):
  d.update(decision='exclude',reason=reason,features=[],exclusion_evidence=[ev(rank,*s)for s in spans]);d['source_closure']['status']='complete_for_static_audit';d['source_closure']['reason']='All operative source is retained. Exclusion concerns the absence of two independently supported features in the Skill\'s own workflow, rather than missing implementation. Generated-program or reference-example execution is not treated as current Skill processing.'
 return apply
def replacefeatures(features):
 def apply(d):d['features']=features
 return apply
change('acq_screen_0301_0400_0001.json','acq_screen_0301_0400_0001r1.json',{304:rejected(304,'The declared scope is read-only frontend patterns/tooling/responsive guidance. Mobile layout conditions and table-to-card examples describe eventual user-application behavior. Two required features in the guidance Skill\'s own processing cannot be established without importing those hypothetical program events.',[('SKILL.md',80,94)])})
change('acq_screen_0301_0400_0002r1.json','acq_screen_0301_0400_0002r2.json',{
334:rejected(334,'The source explicitly says all examples are reference patterns for the user to implement and that this Skill never executes code or generates files directly. PDF merging/page pairing in the examples therefore cannot establish its own versions/element-processing features; two independent qualifying own-workflow features are not supported.',[('SKILL.md',14,26)]),
335:replacefeatures([feat(335,'conditions_or_retries','SKILL.md',64,66,'A proposed monitoring-coverage reduction selects an options-and-choice handoff before any change.'),feat(335,'versions_or_transformations','SKILL.md',41,48,'The offered current audit mode turns identified setup/context/routing issues into a prioritized recommendation and rollback/config proposal, retaining its advisory-only scope.')])})
change('acq_screen_0301_0400_0003r1.json','acq_screen_0301_0400_0003r2.json',{
338:rejected(338,'The published task is implementation guidance/code output for database operations. Cache-hit branching and Redis retention belong to the emitted cache-aside program example, not an independently specified current Skill runtime. Two qualifying own-workflow features cannot be confirmed from the source.',[('SKILL.md',23,25),('SKILL.md',358,368)]),
345:rejected(345,'The source offers patterns for building E2E suites. The cited CI retry, screenshot and report behavior occurs in an example future Playwright configuration. Counting those test-program events as this Skill\'s own processing would violate the uniform eligibility rule, and two other qualifying own-workflow features are not established.',[('SKILL.md',26,32),('SKILL.md',95,103)])})
change('acq_screen_0301_0400_0006.json','acq_screen_0301_0400_0006r1.json',{396:replacefeatures([feat(396,'conditions_or_retries','SKILL.md',19,23,'Before writing a script, the Skill checks the environment and target response/JavaScript/paywall characteristics to choose and justify the extraction strategy.'),feat(396,'persistence_or_cross_session','SKILL.md',9,11,'The declared current deliverables are created Python scripts, YAML configurations and JSON output files. This feature is confined to those output artifacts and does not claim the generated scripts have executed.')])})
change('acq_screen_0626_0750_0004.json','acq_screen_0626_0750_0004r1.json',{659:replacefeatures([feat(659,'conditions_or_retries','SKILL.md',70,82,'The current PRD creation task splits oversized stories according to the one-context-window sizing requirement.'),feat(659,'persistence_or_cross_session','SKILL.md',119,123,'The current create-PRD workflow saves the structured PRD to agents/prd.json; subsequent implementation-loop events are not counted here.')])})
change('acq_screen_0626_0750_0005.json','acq_screen_0626_0750_0005r1.json',{671:replacefeatures([feat(671,'conditions_or_retries','SKILL.md',23,35,'The declared observability setup workflow selects different tools and configuration references according to the user\'s monitoring need.'),feat(671,'persistence_or_cross_session','prometheus.md',25,38,'In the supported Prometheus Docker setup mode, the supplied deployment configuration mounts persistent metric storage and sets a 30-day retention parameter. This is setup of durable external service state, not a claim that incidents or observations have occurred.')])})
