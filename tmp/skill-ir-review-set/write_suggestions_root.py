"""Publish individually authored external review notes; never execute Skill inputs."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
BASE = ROOT / 'packages/skill-ir/experiments/semantics_baseline'
RUN = BASE / 'runs/baseline-deepseek-v4-flash-max-20260910'
plan = json.loads((WORK/'render-input.json').read_text(encoding='utf-8'))['samples']
notes = json.loads((WORK/'suggestions-root-notes.json').read_text(encoding='utf-8'))
statuses = {'preserved':'保留', 'partial':'部分保留', 'contradicted':'错转', 'missing':'遗漏', 'unassessable':'无法判定'}
output = ROOT/'result/suggestions'
output.mkdir(parents=True, exist_ok=True)

def link(path, label=None, line=None):
    return f'[{label or path.name}]({path.as_posix()}' + (f':{line}' if line else '') + ')'

for item in plan:
    sid = item['sample_id']
    if sid not in notes:
        continue
    note = notes[sid]
    package = Path(item['package_path'])
    def source(match):
        file, line = match.group(1), int(match.group(2))
        path = package/file
        assert 1 <= line <= len(path.read_text(encoding='utf-8').splitlines())
        return link(path, f'{file}:{line}', line)
    def expand(text):
        return re.sub(r'\{S:([^:}]+):(\d+)\}', source, text)
    annotation_path = BASE/'frozen/corpus/annotations'/f'{sid}.json'
    annotation = json.loads(annotation_path.read_text(encoding='utf-8'))
    old = json.loads((RUN/'reviews'/f'{sid}.json').read_text(encoding='utf-8'))
    judgments = {f['fact_id']: next(a for a in f['assessments'] if a['repetition'] == item['repetition']) for f in old['facts']}
    assert old['analysis_sha256'][str(item['repetition'])] == item['analysis_sha256']
    pieces = [f"# {item['index']:03d} {item['skill_name']}｜语义评审",
              f"样例：**{sid}**；选定轮次：**第 {item['repetition']} 次**；批次配置：deepseek-v4-flash-max。对应 " + link(ROOT/'dataset/skills'/f"{item['basename']}.zip",'ZIP 原始包') + ' · ' + link(ROOT/'result/ir-IPP'/f"{item['basename']}.png",'PNG 实际 CFG') + '。',
              note['overall'], '## 需修改或注意的问题']
    for index, (title, body) in enumerate(note['issues'], 1):
        pieces.append(f'{index}. **{title}。** {expand(body)}')
    pieces.extend(['## 已保留的关键内容', note['preserved'], '## 逐项核对',
                   f'以下对照{link(annotation_path,"外置事实标注")}的全部 {len(annotation["facts"])} 项，仅判断当前选定轮次。新增问题另列在上文，不把事实表当作真实 Skill 的全部语义。'])
    for fact in annotation['facts']:
        assessment = judgments[fact['id']]
        references = [re.sub(r'\bedge_0*(\d+)\b', lambda m: 'edge_'+str(int(m.group(1))), ref) for ref in assessment['references']]
        if sid == 'R01' and fact['id'] == 'R01-F02':
            references = ['block_023/ir_044（有动作但无入口）', 'block_009 → block_007', 'block_010 → block_007']
        evidence = fact['evidence']
        source_links = []
        seen = set()
        for ev in evidence:
            key = (ev['file'], ev['start_line'])
            if key not in seen:
                seen.add(key)
                source_links.append(link(package/ev['file'], f"{ev['file']}:{ev['start_line']}", ev['start_line']))
        pieces.append(f"- **{fact['id']}｜{statuses[assessment['verdict']]}**：{fact['statement']} 原文：" + '、'.join(source_links) + '；CFG：' + '、'.join('`'+r+'`' for r in references) + '。')
    pieces.extend(['## 复核边界', note['boundary'],
                   '本次同时核对了'+link(Path(item['analysis_path']),'选定 analysis.json')+'中的 CFG、diagnostics 与相关 metadata。PNG 按既定范围不显示脚本全文和诊断；不能把展示省略直接判为提取遗漏，也不能仅凭结构校验成功判语义正确。',
                   '这些文件是外置语义评审意见（由 Codex 复核），供对照讨论，不代表已经由用户逐项确认，也不是改写后的标准答案。本次未修改 Skill 输入、ZIP、PNG 或生产流程，未运行 Skill 脚本和远端 API。'])
    destination = output/(item['basename']+'.md')
    destination.write_text('\n\n'.join(pieces)+'\n',encoding='utf-8')
    print(destination.name)
