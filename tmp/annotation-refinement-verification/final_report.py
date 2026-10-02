"""Generate the externally evaluated, human-facing experiment review."""
import json
from collections import Counter
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parents[2]
run = Path((Path(__file__).parent / 'run-path.txt').read_text(encoding='utf-8-sig').strip())
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
summary = read(run/'summary.json')
replay = read(run/'replay-validation.json')
engineering = read(run/'engineering-validation.json')
history = read(run/'historical-integrity.json')
labels = {
 '001-base': '001 原候选', '010-base': '010 原候选', '013-base': '013 原候选',
 '013-local': '013：无依据局部隔离', '013-field': '013：原字段关系降精度',
 '010-source': '010：工具获取来源被抹掉', '001-version': '001：交付整个元素而非正文',
}
conclusions = {
 '001-base': '初审没有提出实质问题；未调用修复。助手复核保留筛选、同元素字段配对及宽观察关系。',
 '010-base': '初审没有提出实质问题；未调用修复。工具获取来源、可选参数与实际请求值仍分开。',
 '013-base': '初审没有提出实质问题；未调用修复。环境整体、凭据字段和首次／重试／回退身份仍分开。',
 '013-local': '已实际修复：local 改为 default；恢复对环境整体的契约观察，FAST_KEY 仍仅是显式选取的参数。',
 '013-field': '已实际修复：首次响应 body 从 compute(possible) 改为 select_part；状态分类计算与后续返回身份保持。',
 '010-source': '初审准确命中，但修复传输中断，未取得完整新标注；没有复审，缺陷仍在原候选中。',
 '001-version': '已实际修复：通知正文实参由 record 改为 summary_value；同元素接收者配对、筛选、计数及先前观察保持。',
}
status_zh = {'review_passed':'本轮审查未报实质问题','execution_error':'执行失败，未修复',
             'repair_limit':'一次修复后仍有问题','semantic_failure':'无法完成必要语义判断',
             'invalid_response':'响应不合法','audit_passed':'核对器通过','revision_limit':'发现差异；未启动修复'}
cases=[]
requests=[]
models=set()
usage=Counter()
for row in summary['cases']:
    key=row['case']
    solved=read(run/'cases'/key/'propagation/doe-input.json')
    item={**row,'label':labels[key],'assistant_conclusion':conclusions[key],
          'assistant_review':f'cases/{key}/assistant-review.md',
          'controlled_defect_detected':bool(row['initial_issues']) if not key.endswith('-base') else None,
          'controlled_defect_fixed':row['selected']=='repair' if not key.endswith('-base') else None,
          'records':len(solved['records']),'data_count':len(solved['data']),
          'diagnostics':solved['diagnostics']}
    cases.append(item)
    for stage in ('initial-review','repair','final-review'):
        p=run/'cases'/key/'refinement'/stage/'result.json'
        if p.exists():
            d=read(p); c=d.get('counts',{})
            requests.append({'case':key,'stage':stage,'status':d['status'],'counts':c})
            models.update(c.get('returned_models',[]))
            usage.update({k:v for k,v in (c.get('known_token_usage') or {}).items()
                          if isinstance(v,(int,float)) and not isinstance(v,bool)})
cfg=[]
for row in summary['cfg_reviews']:
    d=read(run/'cfg-reviews'/row['sample']/'result.json')
    audit=d['rounds'][0].get('audit') or {}
    findings=audit.get('findings',[])
    cfg.append({**row,'reason':d['reason'],
                'business_findings':sum(f.get('kind')=='semantic' for f in findings),
                'verdict_counts':dict(Counter(f['status'] for f in findings)),
                'differences':[f for f in findings if f['status']!='represented']})
evaluation={'kind':'assistant_post_run_review','not_human_confirmed':True,
            'cases':cases,'cfg_reviews':cfg,
            'controlled_detection':{'detected':4,'total':4,'boundary':'仅四个受控缺陷，不是泛化准确率'},
            'repair':{'attempted':4,'accepted_complete':3,'assistant_verified_fixed':3,'transport_failed':1},
            'logical_calls':summary['logical_calls'],'limit':summary['max_logical_calls'],
            'requested_model':'deepseek-v4-flash','returned_models':sorted(models),
            'annotation_stage_known_token_usage':dict(usage),
            'usage_boundary':'这里只合计标注审查／修复阶段已知用量；失败请求用量可能不完整，CFG调用另在原记录中。',
            'stage_requests':requests,'replay':replay,'engineering_passed':engineering['effective_counts']['passed'],
            'historical_unexpected_changes':history['unexpected_changes'],
            'boundaries':['原候选不预设零问题标准答案。','传播 complete 不代表语义正确。',
                          '实际网络或工具行为未动态测量。','候选关系与 possible 依赖不代表明文包含。']}
(run/'evaluation/results.json').write_text(json.dumps(evaluation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lines=['# 表示契约补全与一次修复：助手复核', '',
 '**工程实现与规定实验已完成。四类受控缺陷初审全部命中；三个取得完整修复并经助手核对已改正，一个在修复响应传输中失败，明确保留未修复。**', '',
 '这是助手对已保存材料的事后复核，不冒充人工确认。原始三例没有预设为零问题标准答案；复审空问题清单不直接充当修复正确的证据。', '',
 '## 先看实际结果', '',
 '| 案例 | 初审问题数 | 一次修复及独立复审 | 调用 |', '|---|---:|---|---:|']
html_rows=[]
for row in cases:
    key=row['case']; conclusion=conclusions[key]
    lines.append(f"| [{labels[key]}](cases/{key}/assistant-review.md) | {row['initial_issues']} | {conclusion} | {row['logical_calls']} |")
    links=f'<a href="cases/{key}/assistant-review.md">助手复核</a> · <a href="cases/{key}/refinement/report.html">闭环记录</a> · <a href="cases/{key}/propagation/report.html">传播</a> · <a href="cases/{key}/propagation/doe-input.json">DOE 文件</a>'
    html_rows.append(f'<tr><td>{escape(labels[key])}</td><td>{row["initial_issues"]}</td><td>{escape(conclusion)}</td><td>{row["logical_calls"]}</td><td>{links}</td></tr>')
lines += ['', '三份成功修复均完成独立复审，复审发现为 0；助手另行比较了原始标注、实际修复字段、编译观察和最终 DOE 关系，未发现修复引入新的实质关系错误。', '',
 '## 010-source 失败具体意味着什么', '',
 '这是人工构造的“工具获取来源丢失”变体，不是 010 原候选。初审准确指出：工具响应不能只作为请求参数的 compute 结果，应保留 receive 与工具获取边界。', '',
 '修复请求收到 HTTP 200 并开始流式接收后发生 `IncompleteRead(0 bytes read)`，没有完整接受的新标注。不能据此判断模型修复内容正确或错误，也不能说请求没有到达服务端。该例共 2 次逻辑调用，没有自动重发，没有独立复审。', '',
 '**该例当前 DOE 文件仍是原缺陷候选的诊断传播。** 其 `complete` 只表示现有规格可以求解；工具响应的获取来源仍未修复。最后有效候选明确标为 `original`。', '',
 '[查看该例失败、原候选及停止决定](cases/010-source/refinement/report.html)。', '',
 '## 三份 CFG 单次核对', '', '| 样例 | 结论 | 业务核对项 | 说明 |', '|---|---|---:|---|']
cfg_html=[]
for row in cfg:
    label=status_zh.get(row['status'],row['status'])
    lines.append(f"| [{row['sample']}](cfg-reviews/{row['sample']}/report.md) | {label} | {row['business_findings']} | {row['reason']} |")
    cfg_html.append(f'<li><a href="cfg-reviews/{row["sample"]}/report.md">{row["sample"]}</a>：{escape(label)}；{row["business_findings"]} 项业务核对。</li>')
lines += ['', '三份图均复用既有 CFG，未重新提取，未启动 CFG 修复。核对器通过不等于已经证明自然语言与图完全等价。详见 [CFG 助手复核](cfg-reviews/assistant-review.md)。', '',
 '## 本轮改变了什么', '',
 '- 表示契约明确 CFG、传递规格和观察编译的责任。普通 return 由 CFG 输入表达返回值，不要求虚构公开输出、用户交付或调用者内部状态。',
 '- 正常 CFG 核对不再返回 unknown；聚焦审查只返回具体 issue。确实无法完成必要判断使用经证据校验的 cannot_assess，运行状态为 semantic_failure，不当作通过。',
 '- 联合标注不再有泛化 unresolved；每条传递规格明确 order=fixed/partial。partial 继续计算候选次序并保留必要因果，不是等待人工判断。',
 '- 自动修复有严格上限：无问题只审一次；有明确问题才完整修复一次，再用独立上下文复审。不会因格式错误、复审仍有问题或响应传输不确定而无界重试。',
 '- 修复请求、材料身份、接受响应、编译映射及停止决定均可重放；复审不读取初审意见或外置预期。', '',
 '## 验证与材料保护', '',
 f"- 全包回归及受影响测试复跑合计覆盖 {engineering['effective_counts']['passed']} 个通过测试。第一次全量运行的 6 个旧协议断言失败和 5 个测试导入错误均已在测试侧修正并复跑；不把第一次运行写成全绿。",
 '- Lean 实际构建与公理审计通过，原证明实现未改变；这不扩张为模型语义判断正确的证明。',
 f"- 共 {summary['logical_calls']} 次计划内逻辑调用，低于 24 次上限；请求 deepseek-v4-flash，实际返回模型记录为 {', '.join(sorted(models))}。",
 f"- 完整七例闭环、七份传播和三份 CFG 核对已在阻断 Python 网络连接的条件下离线重放：{replay['status']}，新增调用 0，原调用记录摘要不变。010-source 的执行失败也原样恢复。",
 f"- 比较了 {history['existing_files_checked']} 个既有文件摘要：{history['unchanged_files']} 个不变；其余为逐项列明的 19 个活跃工具或说明更新，没有非预期历史材料改动。",
 '- 原 IR、Data、生产提取 Prompt、Lean 实现、冻结语料及已有交付物保持。旧候选在新实验显式重建，有逐项差异清单，不冒充新版模型响应。', '',
 '[工程记录](engineering-validation.json) · [离线重放凭据](replay-validation.json) · [历史摘要检查](historical-integrity.json) · [外置评测](evaluation/results.json)', '',
 '## 保留的分析边界', '',
 '网络分类及可能观察仍属于源文／接口／统一契约下的静态推断，未做动态运行验证。分支 may 汇合不完整保留所有参数相关性；013 的 error 等逻辑字段不自动证明实际接口物理 JSON 布局。当前没有发现这些边界在本轮产生新的实质修复错误，也不据此宣布它们已获得更强保证。', '',
 '013 的 CFG 核对理由提到密钥没有进入写出／追加，这只能解读为“没有直接把密钥作为那些动作的参数”，不能证明工具响应或状态结果中不存在密钥的间接影响或内容。保留禁传声明与正确的直接实参，不等于已经证明无泄露；后续传播和 DOE 不能据此提前判安全。这是该项解释应保留的边界，不需要虚构 CFG 修改或新增泛化未决。', '',
 '本轮小规模结果支持：明确表示层职责后，审查能避免普通 return 的表示误报，并识别四种影响数据暴露分析的受控关系缺陷。它不足以证明所有 Skill 的审查或修复都正确。', '']
(run/'assistant-review.md').write_text('\n'.join(lines),encoding='utf-8')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>一次修复：助手复核</title><style>body{font-family:system-ui,"Microsoft YaHei",sans-serif;max-width:1400px;margin:32px auto;padding:0 20px;color:#233044;line-height:1.75;background:#f6f8fb}h1,h2{line-height:1.35}article{background:white;padding:24px;border:1px solid #d9e1eb;border-radius:12px;margin:18px 0}.warning{background:#fff4ed;border-left:6px solid #c55221}table{border-collapse:collapse;width:100%;min-width:800px}td,th{border-bottom:1px solid #d9e1eb;padding:12px;text-align:left;vertical-align:top}th{background:#edf2f9}a{color:#1757a0}code{background:#e9edf3;padding:2px 5px;border-radius:4px}.scroll{overflow:auto}.stats{font-size:1.1rem;color:#154d37}</style><h1>表示契约补全与一次修复</h1><p>先看具体修改及失败，再展开调用和证据。这里是助手复核，不是人工确认或执行日志。</p>'''
page+=f'<article class="stats">四类受控缺陷全部命中；三个实际修复；一个修复传输失败。已记录 {summary["logical_calls"]} / 24 次逻辑调用。</article>'
page+='<article class="warning"><strong>010-source 尚未修复。</strong> 修复响应传输中断，没有完整接受的新标注。该例传播虽能完成，DOE 文件仍表示带缺陷的原候选，不能作为修复成功结果。<a href="cases/010-source/assistant-review.md">查看详情</a></article>'
page+='<article><h2>七例结果与实际修改</h2><div class="scroll"><table><thead><tr><th>案例</th><th>初审问题</th><th>实际结果</th><th>调用</th><th>可审计材料</th></tr></thead><tbody>'+''.join(html_rows)+'</tbody></table></div></article>'
page+='<article><h2>三份 CFG：只核对，不重新建图</h2><ul>'+''.join(cfg_html)+'</ul><a href="cfg-reviews/assistant-review.md">CFG 助手复核</a></article>'
page+=f'<article><h2>工程验收</h2><p>{engineering["effective_counts"]["passed"]} 个测试经全量与针对性复跑通过；Lean 构建和公理审计通过；完整闭环、CFG 核对和传播在网络阻断下重放一致，新增调用为 0。历史材料无非预期改变。</p><p>泛化未决出口已删除；候选来源、可能依赖、partial 顺序继续计算。确实不能判断时明确失败，不把失败写成通过。</p></article>'
page+='<article><h2>详细说明</h2><p>原候选没有预设零问题标准答案；三份成功修复已另行检查实际关系。未做动态运行验证，未实施 DOE 判断，也不由七例实验推导泛化正确率。</p><a href="assistant-review.md">完整助手报告</a> · <a href="index.html">执行总览</a> · <a href="evaluation/results.json">外置评测</a> · <a href="engineering-validation.json">测试记录</a> · <a href="replay-validation.json">零 API 重放</a> · <a href="historical-integrity.json">历史保护</a></article></html>'
(run/'assistant-review.html').write_text(page,encoding='utf-8')
print(json.dumps({'written':['assistant-review.md','assistant-review.html','evaluation/results.json'], 'logical_calls':summary['logical_calls']},ensure_ascii=False))
