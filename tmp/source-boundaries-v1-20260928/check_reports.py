from pathlib import Path
from html.parser import HTMLParser
import json, sys
from skill_ir.propagation.handoff import load_doe_input
from skill_ir.propagation.runner import load_propagation_run
from skill_ir.propagation.report import render_html, render_markdown
root=Path.cwd();run=Path((root/'tmp/source-boundaries-v1-20260928/selected-run.txt').read_text(encoding='utf-8'))
if len(sys.argv) > 1:
    run = Path(sys.argv[1])
(run/'verification').mkdir(exist_ok=True)
class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        if tag=='a' and d.get('href','').startswith('#'):self.links.append(d['href'][1:])
rows=[]
for number in ['001','010','013']:
    p=run/'cases'/number/'propagation'
    if not (p/'manifest.json').exists():
        rows.append({'case':number,'status':'not_generated'});continue
    doe=load_propagation_run(p)
    assert load_doe_input(p/'doe-input.json')==doe
    audit={'annotation':json.loads((p/'audit/annotation.json').read_text(encoding='utf-8')),'location_evidences':json.loads((p/'audit/location-evidences.json').read_text(encoding='utf-8')),'stats':json.loads((p/'audit/stats.json').read_text(encoding='utf-8'))}
    html=(p/'report.html').read_text(encoding='utf-8');md=(p/'report.md').read_text(encoding='utf-8')
    assert html==render_html(doe,audit=audit)
    assert md==render_markdown(doe,audit=audit)
    parser=Links();parser.feed(html)
    assert len(parser.ids)==len(set(parser.ids)) and set(parser.links)<=set(parser.ids)
    assert not any((p/n).exists() for n in ['data.json','records.json','result.json','resolved-seed.json'])
    assert not (p/'replay/doe-input.json').exists()
    assert all(not d['annotations']['sensitivity'] and not d['annotations']['evidences'] for d in doe['data'])
    rows.append({'case':number,'status':'passed','propagation_status':doe['status'],'data_count':len(doe['data']),'records':len(doe['records']),'html_md_equal_to_renderer':True,'link_targets_valid':True,'single_business_file':True,'pixel_visual_check':'not_performed'})
output={'checks':rows,'passed':all(r['status'] in ['passed','not_generated'] for r in rows)}
(run/'verification/report-structure.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(output,ensure_ascii=False,indent=2))
