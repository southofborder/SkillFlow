import hashlib
import json
from pathlib import Path
from PIL import Image
import numpy as np

root=Path(__file__).resolve().parent
binding=json.loads((root/'final-visual-binding.json').read_text(encoding='utf8'))
rows=[]
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for case in ['020','021','023','024']:
 row=next(r for r in binding['cases'] if r['case_id']==case)
 final=root/'staging'/row['png_file']
 prior=json.loads(Path(row['review_record']).read_text(encoding='utf8'))
 record=next(r for r in prior['cases'] if r['case_id']==case)
 preview=Path(record['png'])
 a=Image.open(preview).convert('RGBA');b=Image.open(final).convert('RGBA')
 aa=np.asarray(a,dtype=np.int16);bb=np.asarray(b,dtype=np.int16)
 delta=np.abs(aa-bb);mask=np.any(delta!=0,axis=2)
 ys,xs=np.where(mask)
 assert a.size==b.size
 bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 assert bbox==row['pixel_difference_bbox']
 final_svg=root/'staging/render'/final.with_suffix('.svg').name
 preview_svg=Path(record['svg']) if 'svg' in record else preview.parent.parent/'render'/final_svg.name
 svg_equal=digest(final_svg)==digest(preview_svg)
 assert svg_equal
 runs=[]
 for y in sorted(set(ys.tolist())):
  if not runs or y-runs[-1][-1]>30: runs.append([y])
  else:runs[-1].append(y)
 details=[]
 out=root/'final-visual-recheck-020-024';out.mkdir(exist_ok=True)
 for n,rr in enumerate(runs,1):
  box=(max(0,int(xs.min())-270),max(0,rr[0]-120),min(b.width,int(xs.max())+430),min(b.height,rr[-1]+150))
  fp=out/f'{case}-detail-{n:02}.png'; b.crop(box).save(fp)
  details.append({'png':str(fp),'sha256':digest(fp),'crop_box':box})
 rows.append({'case_id':case,'png':str(final),'png_sha256':digest(final),'preview_png':str(preview),
   'svg_equal':svg_equal,'svg_sha256':digest(final_svg),'width':b.width,'height':b.height,
   'rgba_changed_pixels':int(mask.sum()),'rgba_changed_channels':int((delta!=0).sum()),
   'maximum_channel_delta':int(delta.max()),'alpha_changed_pixels':int((delta[:,:,3]!=0).sum()),
   'difference_bbox':bbox,'detail_review':details})
(root/'final-visual-recheck-020-024-statistics.json').write_text(json.dumps({'run_id':binding['run_id'],'cases':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
