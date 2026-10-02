from pathlib import Path
from html.parser import HTMLParser
import json
from skill_ir.propagation import load_propagation_run
from skill_ir.propagation.report import render_html,render_markdown
from skill_ir.experiments.report import ArtifactWriter
r=Path.cwd();run=Path((r/'tmp/doe-input-v1-20260924/selected-run.txt').read_text(encoding='utf-8-sig').strip());writer=ArtifactWriter(())
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.hrefs=[];self.h2=[];self.heading=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if 'href' in a:self.hrefs.append(a['href'])
  if tag=='h2':self.heading=True;self.h2.append('')
 def handle_endtag(self,tag):
  if tag=='h2':self.heading=False
 def handle_data(self,data):
  if self.heading:self.h2[-1]+=data
checks=[]
for n in ('001','010','013'):
 p=run/f'cases/{n}/propagation';doe=load_propagation_run(p);audit={k:json.loads((p/f'audit/{filename}.json').read_text(encoding='utf-8')) for k,filename in [('annotation','annotation'),('location_evidences','location-evidences'),('stats','stats')]}
 html=(p/'report.html').read_text(encoding='utf-8');md=(p/'report.md').read_text(encoding='utf-8');assert html==render_html(doe,audit=audit);assert md==render_markdown(doe,audit=audit)
 dom=Parser();dom.feed(html);assert len(dom.ids)==len(set(dom.ids));assert all(h[1:] in dom.ids for h in dom.hrefs if h.startswith('#'))
 expected=[ir['id'] for b in doe['cfg']['blocks'].values() for ir in b['instructions'] if ir['id'] in doe['records']]
 actual=[t.split(' · ')[0] for t in dom.h2 if t.split(' · ')[0] in doe['records']];assert actual==expected
 assert all(not d['annotations']['sensitivity'] and not d['annotations']['evidences'] for d in doe['data'])
 checks.append({'case':n,'status':'passed','html_and_markdown_reproducible':True,'ir_order':actual,'data_links':len(dom.ids),'data':len(doe['data']),'unresolved':len(doe['unresolved']),'kind':'document_structure_and_link_check','pixel_visual_check':False})
writer.json(run/'verification/report-structure.json',{'cases':checks,'passed':True})
summary=json.loads((r/'tmp/doe-input-v1-20260924/verification.json').read_text(encoding='utf-8-sig'));writer.json(run/'verification/summary.json',summary)
writer.json(run/'verification/tests.json',{'full_regression':{'passed':1900,'elapsed_seconds':524.21,'log':'pytest-full.log'},'focused_data_propagation_security':{'passed':718,'elapsed_seconds':83.90,'log':'pytest-focused.log'},'updated_tool_tests':{'passed':9,'elapsed_seconds':4.22,'scope':'verify_pilot failure and optional visual-status handling'},'current_collected_tests':1905,'note':'工具更新增加5项测试，9项工具测试含原有4项；不重复计作1909项。'})
print(json.dumps({'case_checks':len(checks),'protected':summary['protected_file_count'],'protected_changed':summary['changed_protected_files'],'credentials':summary['credential_pattern_files'],'verified':summary['passed']},ensure_ascii=False))
