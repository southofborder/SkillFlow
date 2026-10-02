from collections import Counter
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parent
repo=root.parents[1]
stage=root/'staging'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((stage/'review-data.json').read_text(encoding='utf8'))
html=(stage/'review/index.html').read_text(encoding='utf8')
module_path=repo/'packages/skill-ir/experiments/security_profile/tools/build_review_site.py'
spec=importlib.util.spec_from_file_location('static_site_review',module_path)
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.scripts=[];self.current=None;self.resources=[];self.event_attrs=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        for k,v in attrs.items():
            if k.startswith('on'):self.event_attrs.append((tag,k,v))
            if k in {'src','href','srcset','poster','data'}:self.resources.append((tag,k,v))
        if tag=='script':
            self.current={'attrs':attrs,'text':''};self.scripts.append(self.current)
    def handle_data(self,text):
        if self.current is not None:self.current['text']+=text
    def handle_endtag(self,tag):
        if tag=='script':self.current=None

p=Page();p.feed(html)
assert len(p.scripts)==2
embedded=next(s for s in p.scripts if s['attrs'].get('id')=='review-data')['text']
assert '<' not in embedded and '>' not in embedded and '&' not in embedded
payload=json.loads(embedded)
ids=[c['case_id'] for c in payload['cases']]
assert ids==[f'{i:03}' for i in range(1,31)]
assert Counter(c['execution_origin']['kind'] for c in payload['cases'])=={'reused':15,'rerun':15}
assert Counter(c['feedback_status'] for c in payload['cases'])=={'audit_passed':25,'audit_error':5}
assert Counter(c['annotation_status'] for c in payload['cases'])=={'complete':14,'incomplete':14,'invalid_response':1,'execution_error':1}
assert sum(len(c['profiles']) for c in payload['cases'])==483
assert sum(len(c['unresolved']) for c in payload['cases'])==54
failures=[]
case_rows=[]
expected_rerun={'008','009',*[f'{i:03}' for i in range(18,31)]}
for row in payload['cases']:
    original=next(c for c in data['cases'] if c['case_id']==row['case_id'])
    material=deepcopy(row);svg=material.pop('svg')
    assert material==original, row['case_id']
    assert svg==site.sanitize_svg((stage/row['svg_file']).read_text(encoding='utf8'),row['cfg'])
    assert (row['execution_origin']['kind']=='rerun')==(row['case_id'] in expected_rerun)
    review=row['assistant_review'];assert review['reviewer']=='assistant' and review['human_confirmed'] is False
    assert digest(Path(review['source_file']))==review['source_sha256']
    matches=[x for x in review['reviews'] if x.get('matches_selected_graph')]
    assert len(matches)==1
    assert matches[0]['graph_sha256']==row['graph_sha256'] and matches[0]['revision']==row['selected_revision']
    irs={i['id'] for b in row['cfg']['blocks'].values() for i in b['instructions']}
    if row['annotation_status'] in {'complete','incomplete'}:
        assert set(row['profiles'])==irs
    else:
        assert row['profiles']=={} and row['annotation_reason']
        failures.append({'case_id':row['case_id'],'status':row['annotation_status'],'accepted_profiles':0})
    for el in ET.fromstring(svg).iter():
        assert el.tag.rsplit('}',1)[-1] in site.ALLOWED_TAGS
        assert set(el.attrib)<=site.ALLOWED_ATTRIBUTES
        for k,v in el.attrib.items():
            assert not k.lower().startswith('on')
            if 'url(' in v.lower():assert re.fullmatch(r'url\(#[\w.:-]+\)',v)
    case_rows.append({'case_id':row['case_id'],'origin':row['execution_origin']['kind'],
        'feedback_status':row['feedback_status'],'annotation_status':row['annotation_status'],
        'profiles':len(row['profiles']),'unresolved':len(row['unresolved']),
        'selected_graph_review_matches':True,'source_full_text_preserved':True,'svg_whitelist_checked':True})
js=next(s['text'] for s in p.scripts if s['attrs'].get('id')!='review-data')
assert not p.resources and not p.event_attrs
assert all(token not in js for token in ['fetch(', 'XMLHttpRequest','WebSocket','innerHTML','outerHTML','insertAdjacentHTML','eval('])
assert "connect-src 'none'" in html and "default-src 'none'" in html
assert '这条 IR 没有经过接受的安全标注。完整响应未通过校验时，本页不展示为有效 profile。' in js
assert '[] · 未记录适用标签；请结合证据与未决项阅读' in js
assert 'if(!profile)' in js
rebuilt=root/'static-final-review-rebuilt.html'
site.build_review_site(stage/'review-data.json',rebuilt,assets_root=stage)
assert digest(rebuilt)==digest(stage/'review/index.html')
folders={folder:{'count':sum(1 for p in (stage/folder).rglob('*') if p.is_file()),
 'files':[p.relative_to(stage).as_posix() for p in sorted((stage/folder).rglob('*')) if p.is_file()]}
 for folder in ['ir-IPP','suggestions','security-profiles','review']}
for folder,extension in [('ir-IPP','.png'),('suggestions','.md'),('security-profiles','.json')]:
    assert folders[folder]['count']==30
    assert all(Path(p).suffix==extension for p in folders[folder]['files'])
assert {Path(p).stem for p in folders['ir-IPP']['files']}=={Path(p).stem for p in folders['suggestions']['files']}=={Path(p).stem for p in folders['security-profiles']['files']}
result={'status':'passed','scope':'static HTML/data/SVG verification only; no browser navigation or interaction; zero API calls',
 'run_id':payload['run_id'],'index_sha256':digest(stage/'review/index.html'),
 'review_data_sha256':digest(stage/'review-data.json'),'rebuilt_index_byte_identical':True,
 'counts':{'cases':30,'rerun':15,'reused':15,'feedback':dict(Counter(c['feedback_status'] for c in payload['cases'])),
 'annotation':dict(Counter(c['annotation_status'] for c in payload['cases'])),'profiles':483,'unresolved':54},
 'failed_annotations':failures,'automatic_external_resources':p.resources,'source_payload_script_escape_checked':True,
 'csp_network_disabled':True,'four_directory_snapshot':folders,'cases':case_rows,
 'observations':['30 例 HTML 内嵌材料除程序清洗的 SVG 外逐字段等于最终 review-data.json。完整源文未截断。',
 '30 例助手复核均有恰好一份绑定末图及轮次，来源文件摘要吻合；均非人工确认。',
 '028 与 029 无已接受 profile；状态与原因保留。选中 IR 时走无有效标注提示，不显示四字段空数组作为有效标注。',
 'HTML 源文 JSON 转义、SVG 白名单、无主动远程资源及 CSP 已静态核验。独立重建页面与现有 index.html 字节一致。',
 'review 目录仅记录检查时快照，后续报告及 verification 可以增加；本次不替代最终文件清单与发布摘要验收。',
 '本结论不声称完成最终 30 例页面的浏览器交互验收；未导航本地 HTML。']}
(root/'static-final-review-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(root/'static-final-review-check.md').write_text('# 最终审查页静态核验\n\n结果：通过。仅读取 staging 和现有源代码；输出只在 tmp，不调用 API、不导航浏览器。\n\n'+
 '\n'.join('- '+v for v in result['observations'])+'\n\n统计：30 例；15 新执行 / 15 复用；25 audit_passed / 5 audit_error；14 complete / 14 incomplete / 1 invalid_response / 1 execution_error；483 profiles / 54 unresolved。\n\n'+
 '交付目录快照：'+', '.join(f'{k}={v["count"]}' for k,v in folders.items())+'。\n',encoding='utf8')
print(json.dumps({'status':result['status'],'counts':result['counts'],'folder_counts':{k:v['count'] for k,v in folders.items()}},ensure_ascii=False))
