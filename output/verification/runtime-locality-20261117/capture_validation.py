"""Bind the implementation and affected test inventory before offline execution."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from skillflow.common.recording import implementation_provenance

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SCOPES=('tests/document_guided','tests/propagation','tests/doe','tests/task','tests/common','tests/graph')

if __name__=='__main__':
    files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for name in SCOPES for p in sorted((ROOT/name).rglob('*.py'))}
    value={'created_at':datetime.now(timezone.utc).isoformat(),
        'implementation':implementation_provenance(),'test_file_sha256':files,
        'scope':list(SCOPES),'review_render_measurement':'review-render-measurement-03.json',
        'statement':'Scoped offline suites with injected model responses; no historical run/replay, real model call or Skill execution.'}
    with (HERE/'final-validation-plan.json').open('x',encoding='utf-8') as handle:
        json.dump(value,handle,ensure_ascii=False,indent=2)
        handle.write('\n')
    print(json.dumps({'implementation_sha256':value['implementation']['sha256'],'test_files':len(files),'scope':SCOPES}))
