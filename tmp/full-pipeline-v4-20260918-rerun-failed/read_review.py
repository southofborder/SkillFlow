from pathlib import Path
import json, sys
p=Path(__file__).resolve().parent
case, part=sys.argv[1:3]
r=json.loads((p/f'preview-{case}/review-data.json').read_text(encoding='utf-8'))['cases'][0]
if part=='source':
    for f in r['source']['files']:
        if f['path']=='SKILL.md' or (len(sys.argv)>3 and f['path']==sys.argv[3]):
            print(f['path'],f['content'])
elif part=='graph':
    g=r['cfg'];print('GLOBAL',json.dumps({k:v for k,v in g.items() if k not in ['blocks','edges']},ensure_ascii=False))
    for b in g['blocks'].values():
        print('BLOCK',json.dumps({k:v for k,v in b.items() if k!='instructions'},ensure_ascii=False))
        for i in b['instructions']:
            metadata=i.get('metadata',{})
            print('IR',json.dumps({**i,'metadata':{k:(f'<source/code {len(v)} chars>' if isinstance(v,str) and len(v)>2000 else v) for k,v in metadata.items()}},ensure_ascii=False))
    print('EDGES',json.dumps(g['edges'],ensure_ascii=False))
elif part=='profiles':
    lo=int(sys.argv[3]) if len(sys.argv)>3 else 0
    hi=int(sys.argv[4]) if len(sys.argv)>4 else 100000
    for k,v in list(r['profiles'].items())[lo:hi]:print(k,json.dumps(v,ensure_ascii=False))
    print('UNRESOLVED',json.dumps(r['unresolved'],ensure_ascii=False))
elif part=='rounds':
    root=p.parents[1]/'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed'
    d=json.loads((root/f'cases/{case}/result.json').read_text(encoding='utf-8'))
    print('STATUS',r['feedback_status'],r['feedback_reason'],r['annotation_status'],r['annotation_reason'])
    for x in d['feedback']['rounds']:
        print('ROUND',x['revision'],x['status'],'decision',x.get('decision'))
        if x.get('audit'):
            a=x['audit']
            print('AUDIT STATUS',a.get('status'),a.get('reason'))
            for f in a.get('findings',[]):
                if f['status']!='represented':print('FINDING',json.dumps(f,ensure_ascii=False))
elif part=='audit':
    print(json.dumps(r['audit'],ensure_ascii=False,indent=2))
