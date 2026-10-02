from pathlib import Path
from html import escape
import json
import re
from skill_ir.propagation.runner import load_propagation_run
from skill_ir.recording import canonical_sha256, implementation_provenance

root = Path.cwd()
run = root / (root / 'tmp/source-boundaries-v1-20260928/selected-run.txt').read_text(encoding='utf-8').strip()
out = run / 'offline-recovery'
summary = json.loads((run / 'summary.json').read_text(encoding='utf-8'))
protected = json.loads((run / 'verification/original-run-check.json').read_text(encoding='utf-8'))
test_log = (root / 'tmp/source-boundaries-v1-20260928/pytest-final-related.log').read_text(encoding='utf-8')
passed = re.search(r'(\d+) passed in ([\d.]+)s', test_log)
if not passed:
    raise RuntimeError('final related test suite has not passed yet')
tests = int(passed.group(1))
assert not protected['changed_protected_files'] and not protected['credential_pattern_files']
assert protected['call_budget_ok'] and protected['offline_network_guard_passed']
assert [(r['case'], r['stage'], r['status']) for r in protected['replay_comparisons'] if r['equal'] is False] == [('001', 'propagation', 'uncommitted')]

findings = {
    '001': {
        'sample': 'N01', 'title': '整体观察已补上，字段交付仍不够精确',
        'gain': 'events.json 整体先被读取并进入模型观察；未臆造密钥清洗。',
        'issue': '逐记录 summary 和 recipient 的关联退化为 opaque 派生及符号边界；处理条数的修复还存在解释歧义。',
        'facts': ['来源：用户提供的 events.json 文件整体。', '读取：整体 opaque，没有缩到 summary。', '观察：原始文件整体进入模型上下文。', '取值：筛选与 summary 取值被概括为不透明派生，缺少明确部分关系。', '交付：派生载荷交付动态 recipient 边界；不能据此证明只含 summary，也不能断言 access_token 已外发。'],
    },
    '010': {
        'sample': 'Q04', 'title': '工具新来源已补上，可选参数关系出现退步',
        'gain': 'request.json 整体观察；index.search 返回来自 tool 边界，并被整体观察。',
        'issue': '核对器接受了未定义的可选参数机制，receive 输入包含值和存在标记；普通 return 又被过度标为 user_output。',
        'facts': ['来源：request.json；另外从 tool:index.search 获取新响应。', '读取：请求整体保留未知剩余。', '观察：完整请求与完整工具响应。', '取值：term/from_date/limit、响应 total/items 有部分关系；缺参省略却没有落实。', '交付：获取记录包含五项值/标记，不等于已证实五项网络发送；直接用户输出的依据不足。'],
    },
    '013': {
        'sample': 'F01', 'title': '环境范围仍被错误收窄，本轮核心方法目标未达成',
        'gain': 'CFG 保留 user_request 与 environment；请求整体观察、source_id 选取和三个工具返回新来源成立。',
        'issue': '标注无依据假设“显式 key-only getter”，只读 environment.FAST_KEY；环境整体 Data 与观察仍缺失。',
        'facts': ['来源：图中有 environment，但标注实际只读取 environment.FAST_KEY。', '读取：请求整体正确；环境整体没有进入 Data。', '观察：请求和三个工具响应被观察；环境整体及取得的密钥均没有对应观察记录。', '取值：source_id 使用 select_part；FAST_KEY 变成无父容器的叶子；body/error 仍是 opaque 派生。', '交付：fast 使用 source_id+key，archive 仅 source_id；返回身份、重试和状态追加保留，普通返回的 user_output 推断仍过强。'],
    },
}
rows = []
for case in summary['cases']:
    n = case['case_id']
    directory = out / 'cases' / n / 'propagation'
    doe = load_propagation_run(directory)
    original = json.loads((run / 'cases' / n / 'propagation/doe-input.json').read_text(encoding='utf-8'))
    check = json.loads((directory / 'recovery-check.json').read_text(encoding='utf-8'))
    capture = json.loads((out / 'cases' / n / 'capture/receipt.json').read_text(encoding='utf-8'))
    replay = json.loads((directory / 'replay/summary.json').read_text(encoding='utf-8'))
    assert doe == original and check['original_doe_equal'] and check['status'] == 'matched'
    assert check['network_guard']['network_attempts'] == capture['network_guard']['network_attempts'] == 0
    assert check['model_calls'] == capture['model_calls'] == replay['model_calls'] == 0
    assert replay['status'] == 'matched' and not replay['differences']
    assert (run / 'cases' / n / 'assistant-review.md').is_file()
    rows.append({'case_id': n, 'sample_id': findings[n]['sample'], 'feedback': case['feedback'],
                 'annotation': case['annotation'], 'original_propagation': case['propagation'],
                 'recovered_propagation': doe['status'], 'ir_count': len(doe['records']), 'data_count': len(doe['data']),
                 'unresolved_count': len(doe['unresolved']), 'diagnostic_count': len(doe['diagnostics']),
                 'logical_calls': case['logical_calls'], 'http_attempts': case['call_counts']['http_attempts'],
                 'new_model_calls_for_recovery': 0, 'doe_equal': True, 'replay': 'matched',
                 'doe_sha256': canonical_sha256(doe), **findings[n]})

verification = {'engineering_status': 'passed_after_report_only_recovery', 'original_run_status': '001_report_save_failed',
                'method_status': 'not_accepted', 'method_reason': '013 environment scope and observation are still omitted; 001/010 also retain precision or boundary errors.',
                'full_suite_before_report_fix': {'passed': 1949}, 'final_related_suite': {'passed': tests, 'seconds': float(passed.group(2))},
                'lean_build': 'passed', 'lean_axiom_audit': 'passed', 'protected_files': protected['protected_file_count'],
                'changed_protected_files': [], 'credential_pattern_files': [],
                'logical_calls': summary['logical_calls'], 'annotation_calls': summary['annotation_calls'],
                'http_attempts': protected['http_attempts'], 'requested_model': 'deepseek-v4-flash',
                'returned_models': sorted({m for c in summary['cases'] for m in c['call_counts']['returned_models']}),
                'recovery_new_model_calls': 0, 'implementation': implementation_provenance(), 'cases': rows}
(out / 'verification/final-checks.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding='utf-8')

intro = '工程与离线恢复已完成；方法尚未验收通过。尤其 013 仍无依据地把环境读取收窄为单个 FAST_KEY，不能说本轮已解决该核心问题。'
lines = ['# 来源范围、工具返回与模型观察：三例实施与复核结果', '', intro, '',
         '本报告为助手事后复核，不是人工确认。模型原始判断、未决项及传播事实均未改写；本轮不作 DOE、风险或必要性判断。', '',
         '## 1. 工程改动与运行', '',
         '- CFG 提取与源文核对区分逻辑来源入口、目标字段与结果绑定；原 IR 字段保持。',
         '- 联合标注和执行模型明确整体读取／局部机制、模型观察、选取与实际参数。',
         '- 工具内容获取允许 receive + tool + 无标签事件，不以网络确定性作为获取前提；仍保留实际输入和 possible 依赖。',
         '- 种子、输入解析和循环依赖共用位置解析；未使用的位置不自动生成 Data，未知内容不自动扩大地址别名。',
         '- 版本为联合标注/执行模型 v6、解释契约 v3、传播记录 v5、DOE 输入 v2、传播运行 v4；Data v3 保持。', '',
         f'实际 {summary["logical_calls"]} 次逻辑调用（上限 63），其中 3 次联合标注；15 次 HTTP 尝试，只有 001 的一次传输重试。没有质量择优重跑。请求 deepseek-v4-flash，全部实际返回名为 deepseek-flash。', '',
         '| 样例 | 核对/标注 | 原传播保存 | 恢复后传播 | IR / Data | 逻辑 / HTTP |', '|---|---|---|---|---:|---:|']
for row in rows:
    lines.append(f'| {row["case_id"]}/{row["sample_id"]} | {row["feedback"]} / {row["annotation"]} | {row["original_propagation"]} | {row["recovered_propagation"]} | {row["ir_count"]} / {row["data_count"]} | {row["logical_calls"]} / {row["http_attempts"]} |')
lines += ['', '## 2. 逐例方法结果', '', '三例原始 unresolved 与 diagnostics 均为空；以下问题由助手复核另行指出，未伪装成模型已经报告的未决。', '']
for row in rows:
    n = row['case_id']
    lines += [f'### {n}/{row["sample_id"]}：{row["title"]}', '', '**已补上的关系：**' + row['gain'], '', '**仍存在的问题：**' + row['issue'], '']
    lines += ['- ' + item for item in row['facts']]
    lines += ['', f'[传播审查](cases/{n}/propagation/report.html) · [唯一 DOE 业务文件](cases/{n}/propagation/doe-input.json) · [完整助手意见](../cases/{n}/assistant-review.md) · [选定 CFG](../cases/{n}/selected-analysis.json)', '']
lines += ['## 3. 报告保存错误及可信离线恢复', '',
          '001 原保存发生 TypeError：合法 literal 带 identifier:null，旧报告代码按 identifier 键存在与否显示，尝试拼接 None。现改为按 operand.type 选择 JSON 字面值。这是展示错误；原 001 没有提交 manifest，仍保留原失败状态。', '',
          '先在原源码身份下重新解析、核对并离线重放 feedback/annotation，保存材料捕获回执；只修改 propagation/report.py 后，再用原接受响应在此新目录求解和保存。恢复保留原调用、原模型名、用量和原 manifest，另记新实现摘要。源码变化白名单和实际业务完全一致检查均通过。', '',
          '三例恢复均为零模型调用、零网络尝试；旧新 DOE 逐字段相等，独立加载、完整运行加载及新身份离线重放均通过。原结果未被补写成成功，也没有迁移旧版本。', '',
          '[原始运行总览](../index.html) · [原始运行核验（保留 001 未提交失败）](../verification/original-run-check.json) · [恢复验证汇总](verification/final-checks.json)', '',
          '## 4. 验证与保证边界', '',
          f'- 修改前完整离线回归：1949 passed；报告修复后的相关回归：{tests} passed，包含新增的字面量保存与恢复测试。这两组存在重叠，不相加声称独立测试数。',
          '- Lean 构建及公理审计通过，原结构/受控文本证明未修改；依赖仅为既有标准 propext、Quot.sound、Classical.choice。',
          f'- {protected["protected_file_count"]} 个受保护历史/输入文件摘要不变；未发现凭据模式；调用预算满足。',
          '- HTML/Markdown 与共用渲染器一致，锚点及业务文件引用有效。未进行像素级浏览器视觉核验。',
          '- 当前 Prompt 不保证模型遵守所有规则；真实引文校验也不能证明模型从引文作出的推断正确。', '',
          '**本轮结论：**工具返回来源和部分整体观察得到补充，工程可复核；方法上仍不能宣称来源范围完整或接收边界准确。013 的错误例外推断是下一轮必须优先处理的通用问题，不能以节点/字段名补丁消除。001 的集合字段关系、010 的条件参数、普通 return 的接收边界也必须保留为未解决事项。', '']
(out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
(run / 'assistant-review.md').write_text('# 助手复核入口\n\n' + intro + '\n\n请从[本轮交付总览](offline-recovery/index.html)或[中文主报告](offline-recovery/report.md)审查。原始运行保留001报告保存失败；离线恢复另存，业务事实未改动。\n', encoding='utf-8')

cards = []
for row in rows:
    n = row['case_id']
    facts = ''.join('<li>' + escape(item) + '</li>' for item in row['facts'])
    cards.append(f'<article><h2>{n} / {row["sample_id"]} · {escape(row["title"])}</h2><p><b>已补上：</b>{escape(row["gain"])}</p><p class="issue"><b>仍有问题：</b>{escape(row["issue"])}</p><ol>{facts}</ol><p class="links"><a href="cases/{n}/propagation/report.html">查看数据和操作</a><a href="cases/{n}/propagation/doe-input.json">原始 DOE JSON</a><a href="../cases/{n}/assistant-review.md">逐项复核</a><a href="../cases/{n}/selected-analysis.json">CFG</a></p><p class="small">核对器：{row["feedback"]}；标注：{row["annotation"]}；恢复后传播：{row["recovered_propagation"]}；{row["ir_count"]} IR / {row["data_count"]} Data。原始未决为 0，不代表助手未发现问题。</p></article>')
html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'none'; connect-src 'none'"><title>来源与模型观察：三例审查</title><style>body{{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1160px;margin:32px auto;padding:0 24px;background:#f4f7fa;color:#203044}}h1{{font-size:30px}}h2{{font-size:21px}}article{{background:white;border:1px solid #cbd6e1;padding:22px 28px;margin:24px 0}}.notice,.issue{{background:#fff1d4;border-left:4px solid #c78217;padding:12px 16px}}.small{{font-size:14px;color:#526575}}a{{color:#08688a;overflow-wrap:anywhere}}.links{{display:flex;gap:22px;flex-wrap:wrap}}li{{margin:8px 0}}code{{overflow-wrap:anywhere}}</style></head><body><h1>来源范围、工具返回与模型观察</h1><p class="notice">{escape(intro)}</p><p>按五个问题审查：来源是什么 → 读取多少 → 模型观察哪个版本 → 最后取出什么 → 交付给谁。</p><p>新实验：001、010、013 重新建图；14 次逻辑调用、15 次 HTTP 尝试，联合标注各一次。请求 deepseek-v4-flash，记录返回 deepseek-flash。</p><p class="links"><a href="report.md">完整中文主报告</a><a href="verification/final-checks.json">验证汇总</a><a href="../index.html">原始运行（保留001保存失败）</a></p>{''.join(cards)}<h2>为什么有离线恢复目录</h2><p>001 曾因合法字面量 identifier:null 触发报告保存错误。修复只改变展示逻辑，原失败及接受响应均保留；三例在零网络条件下重新求解、保存及重放，业务 JSON 与原计算完全相同。这里是新的提交结果，不是新的模型答案。</p><p>完整回归 1949 项通过；修复后相关回归 {tests} 项通过（两组有重叠）。Lean 构建/公理审计通过；{protected['protected_file_count']} 份受保护文件未变。报告结构与链接已检查，未进行像素级视觉核验。</p><p class="small">本页意见来自助手事后复核，不能冒充人工确认。complete/audit_passed 不证明语义等价，也不是 DOE 或安全结论。</p></body></html>'''
(out / 'index.html').write_text(html, encoding='utf-8')
print(json.dumps({'report':str(out/'report.md'),'index':str(out/'index.html'),'engineering':'passed_after_report_only_recovery','method':'not_accepted','tests':tests}, ensure_ascii=False))
