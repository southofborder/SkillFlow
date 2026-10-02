from pathlib import Path
import json,sys
base=Path('packages/skill-ir/experiments/semantics_baseline')
samples=json.loads(Path('tmp/skill-ir-review-set/render-input.json').read_text(encoding='utf-8'))['samples']
for s in samples:
 if s['sample_id'] not in sys.argv[1:]: continue
 print('\nSAMPLE',s['index'],s['sample_id'],s['basename'],'rep',s['repetition'])
 for f in sorted(Path(s['package_path']).rglob('*')):
  if f.is_file():
   print('SOURCE',f.relative_to(Path(s['package_path'])))
   print('\n'.join(f'{i}: {line}' for i,line in enumerate(f.read_text(encoding='utf-8').splitlines(),1)))
 a=json.loads((base/'frozen/corpus/annotations'/f"{s['sample_id']}.json").read_text(encoding='utf-8'))
 for f in a['facts']: print('FACT',f['id'],f['statement'],'EVIDENCE',','.join(str(e['file'])+':'+str(e['start_line'])+'-'+str(e['end_line']) for e in f['evidence']))
 print('VARIANTS',json.dumps(a['acceptable_variants'],ensure_ascii=False))
 print('OPEN',json.dumps(a['open_questions'],ensure_ascii=False))
 g=s['cfg'];print('SKILL',json.dumps({k:v for k,v in g.items() if k not in ['blocks','edges']},ensure_ascii=False))
 for b in g['blocks'].values():
  print(b['block_id'],b['block_name'],'CONSTRAINTS',json.dumps(b['constraints'],ensure_ascii=False),'SOURCE',b['data_source_kind'])
  for i in b['instructions']:
   z={k:v for k,v in i.items() if k not in ['draft_instruction_id']}
   z['inputs']=[{k:v for k,v in o.items() if v is not None} for o in i['inputs']]
   z['outputs']=[{k:v for k,v in o.items() if v is not None} for o in i['outputs']]
   print(json.dumps(z,ensure_ascii=False))
 for e in g['edges']: print('EDGE',e['source_block_id'],e['target_block_id'],repr(e['condition_text']))
