from pathlib import Path
import json, hashlib
from PIL import Image, ImageChops
import numpy as np
root = Path(__file__).resolve().parent
rows = json.loads((root/'final-visual-binding.json').read_text(encoding='utf-8'))['cases']
stats = []
for case in ['029','030']:
    row = next(r for r in rows if r['case_id']==case)
    oldroot = root/f'preview-{case}'
    meta = json.loads((oldroot/'review-data.json').read_text(encoding='utf-8'))['cases'][0]
    old = Image.open(oldroot / row['png_file']).convert('RGBA')
    new = Image.open(root/'staging'/row['png_file']).convert('RGBA')
    assert old.size == new.size
    d = np.abs(np.asarray(old).astype(int) - np.asarray(new).astype(int))
    changed = np.any(d!=0, axis=2)
    y,x = np.where(changed)
    stage = root/f'final-recheck-{case}'
    stage.mkdir(exist_ok=True)
    details = []
    for n,y0 in enumerate(range(max(0,int(y.min())-100), min(new.height,int(y.max())+101), 1500)):
        area=(max(0,int(x.min())-200),y0,min(new.width,int(x.max())+201),min(new.height,y0+1600))
        path=stage/f'detail-{n+1:02d}.png'
        new.crop(area).save(path)
        details.append({'png':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    stat={'case_id':case,'size':list(new.size),'changed_pixels':int(changed.sum()),'max_channel_difference':int(d.max()),'bbox':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1],
          'svg_equal':(oldroot/meta['svg_file']).read_bytes()==(root/'staging'/meta['svg_file']).read_bytes(),
          'png_sha256':hashlib.sha256((root/'staging'/row['png_file']).read_bytes()).hexdigest(),'detail_review':details}
    stats.append(stat)
    print(json.dumps(stat,ensure_ascii=False))
(root/'final-recheck-029-030-stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
