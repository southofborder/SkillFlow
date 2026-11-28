"""Read one scoped pytest receipt without re-executing tests or materials."""
from collections import Counter
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

if __name__=='__main__':
    path=Path(__file__).resolve().parent/sys.argv[1]
    rows=ET.parse(path).findall('.//testcase')
    counts=Counter()
    failures=[]
    for row in rows:
        label=next((name for name in ('failure','error','skipped') if row.find(name) is not None),'passed')
        counts[label]+=1
        if label in {'failure','error'}:
            error=row.find(label)
            failures.append({'classname':row.get('classname'),'name':row.get('name'),
                'status':label,'message':error.get('message',''),'detail':error.text or ''})
    report={'receipt':path.name,'counts':dict(counts),'failures':failures}
    destination=path.with_suffix('.diagnostics.json')
    with destination.open('x',encoding='utf-8') as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)
        handle.write('\n')
    print(json.dumps({'receipt':path.name,'counts':dict(counts),
        'failed_modules':dict(Counter(row['classname'] for row in failures)),
        'messages':list(dict.fromkeys(row['message'] for row in failures))},ensure_ascii=False,indent=2))
