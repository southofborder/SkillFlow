"""Publish the closed four-case report from saved, audited case summaries."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path

V = Path(__file__).resolve().parent
ROOT = V.parents[2]

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def duration(s):
    h, rem = divmod(s, 3600); m, sec = divmod(rem, 60)
    return f'{int(h)}时{int(m)}分{sec:.2f}秒' if h else f'{int(m)}分{sec:.2f}秒'

def link(label, p):
    return f'[{label}]({p.as_posix()})'

prepared = read(V / 'prepared-runs.json')
queue = read(V / 'queue-live.json')
assert queue['phase'] == 'all_four_closed'
summaries, receipts = [], []
for row in prepared['run_order']:
    run = Path(row['run_directory'])
    read(run / 'controller-finished.json')
    summaries.append(read(run / 'run-summary.json'))
    receipts.append(read(V / 'receipt-audit' / (row['case_id'] + '.json')))

groups = defaultdict(Counter)
usage = Counter()
identities = []
for r in receipts:
    assert r['status'] == 'passed'
    usage.update(r['known_public_usage'])
    for category, counts in r['groups'].items(): groups[category].update(counts)
    for request in r['requests']: identities.extend(tuple(x) for x in request['public_identities'])
assert len(identities) == len(set(identities))
first = datetime.fromisoformat(read(V / 'queue-started.json')['started_at'])
last = datetime.fromisoformat(queue['observed_at'])
old = read(ROOT / 'output/verification/backend-r3-online-20261104/four-run-summary.json')
cost = {'native_starts': sum(r['native_starts'] for r in receipts), 'logical_requests': sum(s['transport']['logical_requests'] for s in summaries),
    'call_group_costs': dict(groups), 'known_public_tokens': dict(usage),
    'complete_usage_requests': sum(s['transport']['complete_usage_requests'] for s in summaries),
    'unknown_usage_requests': sum(s['transport']['unknown_usage_requests'] for s in summaries),
    'network_extra_attempts': sum(r['outer_retries'] for r in receipts),
    'unique_public_thread_turn_or_order_identities': len(set(identities)), 'duplicate_public_identities': len(identities)-len(set(identities)),
    'public_cli_reconnect_notices': sum(len(x['events']) for r in receipts for x in r['internal_notices']),
    'provider_http_attempts': None, 'unreported_internal_failed_attempt_usage': None,
    'audit_assistant_usage': None, 'currency': None,
    'analysis_seconds_sum': sum(s['timing']['analysis_seconds'] for s in summaries),
    'replay_seconds_sum': sum(s['timing']['replay']['elapsed_seconds'] for s in summaries),
    'controller_wall_seconds_sum': sum(s['timing']['controller_wall_seconds'] for s in summaries),
    'sequence_seconds_including_gaps_and_replays': (last-first).total_seconds(),
    'replay_new_native_starts': sum(s['timing']['replay']['new_native_markers'] for s in summaries),
    'all_implementation_hash_checks_unchanged': all(not r['current_changes'] and not r['frozen_changes'] for r in receipts),
    'scope': 'Target calls including corrections/repairs, complete public final-turn usage. Cached input is included in input. Audit assistant usage and unreported provider-attempt usage are unknown, not included. Component intervals are nonadditive.'}
summary = {'identity': 'interface-r4-four-case-source-reviewed-report', 'created_at': datetime.now(timezone.utc).isoformat(),
    'all_controllers_closed': True, 'all_sole_replays_matched': all(s['timing']['replay']['status']=='matched' for s in summaries),
    'complete_generated_propagation_cases': 4, 'complete_semantic_doe_cases': 0,
    'source_audit_authority': 'Finite independent assistant criteria, not human gold; no general accuracy, precision, recall or direct-GPT superiority inference.',
    'cases': summaries, 'cost': cost, 'previous_backend_r3_cost': old['cost'],
    'comparison': 'GA4 now computes/publishes full generated propagation instead of failing before it; 013 computes all generated writes/returns. Different generated graphs, scopes and reconnect histories prevent a whole-system speedup claim. All DOE remains partial.',
    'limitations': ['Generated-IR completion does not prove whole-source semantic coverage.', 'All270 sensitive comparisons are explicitly unresolved;010has no declared sensitive basis.', 'Constraint potential_violation is distinct from an actionable DOE conclusion or observed disclosure.', 'GA4 uses shared/opaque boundaries and unresolved model/task relationships; helper and cache identities remain imperfect.', 'Oldv9 remains paused; no historical replay/resume or extra sampling occurred.'],
    'combined_chinese_report': str(V/'assessment.zh.md'), 'delivery_status': 'ready_for_delivery'}
(V/'four-run-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lines = ['本轮四个案例都完成了生成 CFG 的全部传播，也都保存了 DOE 并通过各自唯一一次零模型调用重放；但四例的语义／DOE 终态仍全部是 partial。**传播工程链路已走通，完整、可执行的 DOE 结论仍未得到。**', '',
'GA4 的 250 项、001 的 5 项、013 的 15 项敏感比较全部明确未决，没有可执行的 reduction。010 没有源文支持的敏感类别声明，零比较可以接受，但不能据此判定安全。现有结果的价值在于可核查的边界、载荷、成员／接收方／版本关系和局部限制告警。', '',
'本轮使用同一冻结实现、gpt-6.1-sol / high / openai、最多两个 worker、正常七调用入口；每阶段一次结构纠正、全流程一轮语义修复。四例从各自完整冻结源包重新生成，未导入历史答案。GA4 仍为原来的 16 文件。旧 v9 继续暂停；本批结束后没有恢复旧进程、额外采样、再重放或执行 Skill。', '',
'| Skill | 生成 IR 实际处理 | 截断／阻断／未到达 | DOE 与审查的实际结论 |', '| --- | ---: | --- | --- |']
descriptions = {'ga4':'250 比较全部未决；85 个边界，最终审查保留 7 findings；无 reduction。', '001':'5 比较全部未决；另有模型观察路径的 token 禁止约束告警；审查 diagnostic_only。', '010':'0 敏感比较；无删除限制未表达，两个 presence 约束仍有 potential_violation；审查无 findings。', '013':'15 比较全部未决；四个追加与返回路径均计算；presence 表示及失败接口仍有精度限制，审查 diagnostic_only。'}
for s in summaries:
    g=s['propagation']['generated_ir'];lines.append(f"| {s['case_id'].upper()} | {g['by_status']['processed']}/{g['total']}（100%） | {g['cutoff_count']}／{g['by_status']['blocked']}／{g['by_status']['not_reached']} | {descriptions[s['case_id']]} |")
lines += ['', '这里的 100% 分母是本轮生成的 IR，不能替代源码语义覆盖率。源码对照的结果如下：', '',
'- **GA4：**既有清单的 13/13 API 点、25/25 saveResult 点、3/3 显式循环均有表示和计算记录。它们分别合并到 7 个主要 API IR 和 18 个主要保存 IR。38 个远程发送／接收位置的请求、响应、endpoint 和候选绑定对应；18 个主要保存摘要使用实际结果身份，而非请求参数。58 个写位置包括 44 个 storage write 和 14 个 context write，均为 replace。共享调用摘要、opaque 序列化、可能别名的文件位置以及循环多代候选仍限制精确语义；不能把这些数字解释为整个 Skill 每项用途都已实现。',
'- **001：**读取 events、opted_out 优先拒绝、urgent 与 value >= 100 选择、同成员 recipient/body、通知后继续、最终计数保存均有计算记录。正文使用原 summary，没有增加总结。processed records 究竟指全部检查记录还是选中记录，继续保留源文歧义。符号成员不是一次真实事件列表执行，也不证明实际次数。',
'- **010：**三份源码逐字来源保持；四种可选参数组合保留，缺失字段不变成 null。每个请求对应自己的响应，count.txt 消费同响应 total，返回同响应 items。没有添加 fuzzy 扩展、删除动作或虚构返回接收方。',
'- **013：**首轮成功、重试成功、archive 成功、archive 失败四个终止路径均有追加和返回记录。各终止分支的状态追加顺序、响应和终止值由独立审计核对；FAST_KEY presence 的具体运行值和接口表示仍有限制，R3 警告未证明可行违规；archive 参数明确只有 source_id。', '',
'剩余阻断已从“后端根本算不完／接口截断”转移到以下层面：', '',
'1. **任务对应与未决范围。**GA4 的 39 个需求中 12 expressed、20 partial、7 retained_only。27 条表达缺口、7 条未绑定要求、5 条 Task source issue 被作为全局阻断带入全部 85 个 sink，使全部 250 项比较未决。有些是实际源码缺口；有些只是运行时参数未知，属于静态分析的正常符号输入，不应当被解释成天然不可分析。本报告指出这一判断问题，没有修改本次冻结产物。',
'2. **标注的真实身份关系。**GA4 缓存读位置 caches 与写位置 ga_cache/sc_cache/index_cache 没连接；保存 payload 有记录，但 filepath、resultsDir、条件建目录和“本次分析对应的文件→Markdown 总结”关系仍不完整。inspection 结果字段投影与共享操作的需求适用条件仍有缺口。这些不能靠成功编译或完成传播来宣布正确。',
'3. **条件与约束精度。**GA4 的三条 requires_prior 达到有限资源上限；ir_323 的成功分支还保留了错误包装候选，产生一条 missing_part，合法结果仍可返回。部分循环集合存在 multiple_generations 歧义。010 和 013 的 presence only_if 存在 potential_violation；它们不是已证明可执行的违规路径。',
'4. **全局限制的表达能力。**010 未出现 delete 动作，但任务中的全局禁止删除要求仍因没有适用目标而未表达。001 的计数歧义、013 的未指定的工具失败接口／presence 表示等也保留未决。没有把 gap 登记等同于问题解决。', '',
'四项接口修复的线上证据必须分别看：', '',
'| 修复 | 实际验证范围 |', '| --- | --- |',
'| 可选 case body 默认值 | GA4 本次 33 个所选 case 全部显式写 segments，4 个为空；空 body 合法运行，但“省略字段”默认值分支没有被这次在线答案直接触发，其证据仍是离线回归。 |',
'| 多余文件写入输出 | 013 四个 append 不再返回无用的文件整体状态，追加之后的返回都被计算；001/010 的普通保存也无虚构 public output。 |',
'| 任务对应表达式引用 | 010 和 013 实际复制现有 operation/self 表达式，引用有效；表达式引用有效不等于约束被满足。GA4/001 未使用 condition/success，不冒称该分支在线覆盖。 |',
'| 审查归属 | GA4 初次 correspondence 意见和 001 的收件方禁止修复路由正确，隔离保持。GA4 最终 F006 仍把 necessity demand 问题标成 processing，是残留模型归属错误；没有第二轮修复或自动文本改派。 |', '',
'准确性采用有限源码关系逐项核对。GA4 的 API／保存配对与 001/010 的字段配对得到支持，同时 GA4 缓存身份存在明确矛盾，文件身份、共享需求和候选关系仍未决。001 的 forbid_information 告警针对契约补充的可能模型观察，不能写成 notify.send 已发送 token；计数值的 possible 影响也不等于 token 明文。没有已确认的正向 DOE 缩减可统计为检出，也没有正向 DOE verdict 可统计成误报。这些助手审计标准不是人工金标准，不推导通用准确率、precision/recall 或优于直接 GPT。', '',
'完整可得成本如下，已包含结构纠正和语义修复。缓存输入是输入的子集，不重复相加：', '',
'| Skill | 实际启动（正常＋结构纠正＋修复） | 输入 tokens | 其中缓存 | 输出 tokens | 公开总 tokens | 主分析 | 唯一重放 |', '| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |']
for s,r in zip(summaries,receipts):
    u=r['known_public_usage'];g=r['groups'];breakdown='+'.join(str(g.get(n,{}).get('requests',0)) for n in ['normal_generation','structural_correction','semantic_repair_generation'])
    lines.append(f"| {s['case_id'].upper()} | {r['native_starts']}（{breakdown}） | {u['input_tokens']:,} | {u['cached_input_tokens']:,} | {u['output_tokens']:,} | {u['total_tokens']:,} | {duration(s['timing']['analysis_seconds'])} | {duration(s['timing']['replay']['elapsed_seconds'])} |")
lines += [f"| 合计 | {cost['native_starts']}（28＋8＋7） | {usage['input_tokens']:,} | {usage['cached_input_tokens']:,} | {usage['output_tokens']:,} | {usage['total_tokens']:,} | {duration(cost['analysis_seconds_sum'])} | {duration(cost['replay_seconds_sum'])} |", '',
f"整个串行队列包含间隔与重放共 {duration(cost['sequence_seconds_including_gaps_and_replays'])}。43 个公开 thread/turn-or-order 身份互不重复，43 份最终用量均可核对；外层传输重试 0，公开最终回执缺失用量 0。CLI 另记录 19 条重连／等待提示，它们不是额外模型答案或可靠的 HTTP 尝试计数；服务端内部尝试及未报告用量仍未知。四次重放均 matched，新增模型调用和 tokens 为 0。审计助手的工作不计入目标运行成本，未估算费用。", '',
'| Skill | 传播计算 | 传播保存 | 传播整体 | DOE 加载 | DOE 计算 | DOE 整体 |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for s in summaries:
    c={r['component']:r['elapsed_seconds'] for r in s['timing']['component_records'] if r['phase']=='analysis'}
    lines.append('| '+s['case_id'].upper()+' | '+' | '.join(f"{c[k]:.3f}s" for k in ['propagation_compute','propagation_save','propagation_total','doe_load','doe_compute','doe_total'])+' |')
lines += ['', '这些区间有包含关系，不能再相加当总耗时。GA4 传播计算约 4 分钟，传播连保存约 7 分 50 秒；DOE 连加载／发布约 19 分 44 秒。主要模型请求跨度约 2 小时 16 分钟，包含生成、纠正、修复、复审及传输间隔。逐阶段请求耗时、成本和保存区间见每例英文报告与 structured summary。', '',
'与 backend-r3 比较时，GA4 从传播前 KeyError 失败变为 369/369 传播和 DOE 发布，013 从 19/27 处理、4 写入截断和 4 返回阻断变为 31/31。它们覆盖的工作明显不同。001 本次调用与耗时下降，但生成图和比较数量也变了；010 tokens 下降而耗时上升，且有重连延迟。上一批 37 次调用、1,409,599 tokens 与本批 43 次、3,486,080 tokens 不构成同范围速度对照。旧 v8、暂停的 v9 和不同固定输入的 offline r2 同样不能拿来计算整链加速比。', '',
'交付产物：', '']
for s in summaries:
    run=Path(s['run_directory']);lines.append('- '+s['case_id'].upper()+': '+link('English assessment',run/'assessment.en.md')+'；'+link('run-summary.json',run/'run-summary.json'))
lines += ['- '+link('四例结构化总汇',V/'four-run-summary.json')+'；'+link('公开调用与哈希核账脚本',V/'audit_closed_receipts.py')+'；'+link('离线验收',V/'offline-assessment.zh.md')+'。', '',
'本轮到此闭合。当前实现确实能够完成这四份新生成材料的传播与 DOE 发布；下一步若继续改进，重点应是需求的局部适用范围、真实状态／文件身份和条件约束精度，而不是继续把传播完成率当作 DOE 成功率。此报告没有启动下一轮运行或改写本轮结果。', '']
(V/'assessment.zh.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'cost':cost,'reports':4,'generated_propagation_complete':4,'semantic_doe_complete':0},ensure_ascii=False,indent=2))
