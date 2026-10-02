"""Assemble the final human-readable review from verified terminal artifacts."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
RUN=REPO/'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed'
STAGE=HERE/'staging'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
result=read(RUN/'experiment-result.json')
plan=read(STAGE/'review-data.json')
lineage=read(RUN/'lineage-summary.json')
replay=read(HERE/'replay-acceptance/validation.json')
visual=read(HERE/'final-visual-binding.json')
assert replay['status']=='passed' and visual['status']=='passed'
assert len(plan['cases'])==result['summary']['cases']==30
summary=result['summary']
fstatus=summary['feedback_statuses'];astatus=summary['annotation_statuses']
lines=[
'# 30 例端到端验证与助手复核报告', '',
f'当前交付运行：`{RUN.name}`。本报告汇总实际结果；助手意见未经过用户逐项确认。', '',
'本轮完成了失败案例的一次完整重跑、30 例材料整理和可复核交付，但没有达到“30 例全部核对通过、全部标注完整”。程序正确拒绝了不完整或证据无效的响应；这些失败不代表对应 Skill 本身一定有语义错误。', '',
f"**结果：{fstatus.get('audit_passed',0)} 例 audit_passed，{fstatus.get('audit_error',0)} 例 audit_error；{astatus.get('complete',0)} 例标注 complete、{astatus.get('incomplete',0)} 例 incomplete、{astatus.get('invalid_response',0)} 例 invalid_response、{astatus.get('execution_error',0)} 例 execution_error。30 例均有本批次结构有效的末图，共 {summary['profiles']} 份已接受 profile、{summary['unresolved']} 条模型已列明未决。**", '',
'`audit_passed` 是核对器通过，不是语义等价证明；`complete` 是标注记录完整，不是标签准确率。助手发现的问题可能并未包含在模型未决中。', '',
'## 打开和查看', '',
'在系统浏览器打开 `result/review/index.html`，无需启动服务或访问 API。左侧按编号、状态筛选；中间缩放矢量 CFG，点击具体 IR；右侧查看四字段标注、证据、原文、语义核对和助手复核。安全标注失败的样例明确显示无可用结果，不能把空结果当成没有安全效果。', '',
'独立图片在 `result/ir-IPP/`，对应意见在 `result/suggestions/`，新标注 JSON 在 `result/security-profiles/`。30 个 PNG 与 `dataset/skills/` 的 ZIP 基名逐一对应；ZIP 输入未改写。原完整响应、CFG、保真证书、修复轨迹及调用记录保存在当前实验运行。', '',
'## 哪些记录重新执行了', '',
'依用户“失败的全部重跑一下”的指示，008、009、018–030 共 15 例从源包重新开始；001–007、010–017 共 15 例原样复用已完成记录。页面、对应评审和运行来源清单明确区分两类。本批次的复用记录不会被重复统计为新的模型费用；旧失败记录没有改判或覆盖。', '',
'2026-09-20 恢复中，030 的第1轮第2次核对仍是上次中断留下的 running 请求。程序拒绝重发这一状态不确定的调用，将核对停为 audit_error；只启动此前未开始的唯一整图标注。恢复前已有的 622 个调用/终态文件摘要全部不变。', '',
'## 尚未完成核对或标注的案例', '',
'| 编号 | 失败层 | 已核实原因 | 当前可审查内容 |',
'|---|---|---|---|',
'| 026 Playwright | 核对 | 完整响应引用 PLAYWRIGHT_CLI_SESSION，但所指原文行仅为 Or set an environment variable once: | r1 末图；27 份标注，1 条未决 |',
'| 027 gh-fix-ci | 核对 | LICENSE.txt 引文在实际第75行，却标为第74行，整份响应被拒绝 | r3 末图；29 份完整标注 |',
'| 028 netlify-deploy | 核对、标注 | 核对引用行超出 src_057 范围；标注引文不属于 g_0070 定位 | r0 末图；无已接受 profile |',
'| 029 linear | 核对、标注 | 核对漏4个受控事实单元的覆盖记录；标注 IncompleteRead，响应未完整收齐 | r1 末图；无已接受 profile |',
'| 030 transcribe | 核对 | 首次核对传输中断后已开始有界重试，第二次请求又随进程中断；恢复不重发状态不确定请求 | r1 末图及本次唯一标注；具体未决见逐例评审 |', '',
'上述错误不会被算作通过。完整但证据有误的响应没有自动修改、补跑择优或只接收其中看似正确的部分。030 的运行中记录仍原样保留，不冒充已知远端失败；调用次数可观测不等于其远端结算和用量已知。', '',
'## 进入传播前优先审查的实际问题', '',
'1. **来源和写入内容。**009 有 request.json 文件身份，却缺“用户提供”来源；核对器承认未表示仍判保留。015 的四个最终状态追加，实际依赖是 body/error，缺少它们到最终状态值的明确映射。不能只看“有追加操作”就认定写入内容正确，也不能据依赖直接声称已写出完整响应或发生泄露。',
'2. **场景和操作能否进入分析。**025 的生成、更新、文本提取、依赖检查有节点，却没有从唯一 entry 到达的路径；安装失败后的告知只在声明中。结构合法不等于一个传播入口覆盖全部场景。应先约定独立场景的启动条件及传播根，或增加有源文依据的调度关系，不能自动把所有节点串起来。',
'3. **可选能力不能因不是主线就全部消失。**026 的 pause、两份参考指南组合和 trace 等场景仍有表示边界；028 缺 package.json 框架检测以及 build/publish-dir 错误恢复，token 替代仅在声明中；029 的 Tips/Troubleshooting 被广泛视为背景，菜单选项也不等于其内部行为已经展开。应区分可选行为、示例与背景，而不是一律执行或一律忽略。',
'4. **actor 与 model_observe 的依据仍不稳定。**同类 dispatch/筛选在不同例子中被推成 llm 或 runtime；“工具结果回到模型”不代表模型执行工具内部动作，EM04 也不能反过来证明模型处理的前提。网络工具名称、return、交付路径同样不能替代实际机制证据。027 的明确面向用户失败摘要没有 sink/user_output，值得核实；后续传播不能把没有标签解释为隔离保证。',
'5. **反馈可能过度具体化或误判层次。**005 把记录字段声明落实成额外提取；023 把“必要时保留顺序”加强成无条件按序；027 围绕外层 Skill 返回和脚本 stdout/exit-code 反复修改，存在层次混淆。反馈有实际收益，也会引入或保留问题，最终通过不能替代逐例复核。', '',
'6. **工具内部效果和外层动作可能重叠。**030 的完整脚本已包含 print/write_text，外层又在校验后显示输出动作；文件模式 stdout 实际仅为 Wrote path，但外层统一使用 transcript_output。传播前需明确这是同一效果的分层描述还是额外执行，并区分文件正文、stdout 路径、返回值。不能未经澄清就累计为两次写出或把文件全文当模型可见。', '',
'001–024 的详细汇总见 `review-synthesis-001-024.md`；全 30 例的具体图位置、引文和建议见对应 suggestions 及审查页的“助手复核”。这些是诊断意见，未自动改图或标签。', '',
'## 工程验收与信任边界', '',
'- 30 例输入字节、解码文本、选图轮次、图摘要、保真证书和标注图绑定经离线导出复核；源 ZIP 与冻结包的路径和内容摘要匹配。未执行 Skill 内脚本或命令。',
'- 零 API 重放完成：30 例完整结果、轮次、停止决策、调用计数和派生证据相等，在线入口尝试数为0；原始调用文件及父运行1398个文件、发布前203个受保护输入/交付文件均未变化。',
'- 先前完整相关离线回归1307项通过；交付工具最终定向55项通过（1项浏览器测试按访问限制排除），重放验收20项合成测试通过。重叠测试不相加宣称总数量。重跑来源与去重统计工具另有聚焦回归。',
'- 实际执行 Lean 公理审计，16个保持/结构定理只使用标准公理，无 sorryAx 或自定义占位公理。本次为保持绑定身份没有重建或重链打印器。实际转换每次均恢复文本并逐字段比对，保真仅覆盖规范化图明确记录的事实。',
'- 全30张实际PNG及关键细节经过助手查看；最终重新渲染后21张与预览字节一致，另9张底层SVG相同但有栅格像素差异，已再次查看最终整图及差异细节，记录见 final-visual-binding.json。渲染器另核验操作、边、文本、边界和样例身份。未发现可见中文缺字、文字遮挡或画布裁切。',
'- 实际30例HTML页面未能通过应用内浏览器交互检查：工具明确拒绝本地 file URL。没有改用其他浏览器、localhost 或低层接口绕过。此前小型页面测试及本次静态/数据/JavaScript回归不冒充30例实际页面交互验收；请在系统浏览器手动打开审查页。',
'- 生产 Prompt、IR 字段、结构规则、Lean 打印器和冻结输入没有因本轮交付而改变。没有实现传播、敏感数据集合、风险、必要性或 DOE 判断。', '',
'## 调用和来源去重', '',
'请求模型为 deepseek-v4-flash，实际响应记录返回名称为 deepseek-flash。原配置仍为600秒远程读取超时，HTTP重试与核对执行重试分别计数。用量缺失保留未知，不按0计，也不将复用的15例重新累计。', '',
'| 来源 | 逻辑调用 | 执行调用 | HTTP尝试 |',
'|---|---:|---:|---:|']
for key,title in [('parent','父批次全部'),('child_new','本次15例新增'),('lineage_unique','两个运行去重合计')]:
 x=lineage[key];lines.append(f"| {title} | {x['logical_calls']} | {x['execution_calls']} | {x['http_attempts']} |")
lines += ['', '逐调用摘要、未知用量和实际模型名称见 `lineage-report.md` 与实验目录的 `lineage-summary.json`。这不是服务商账单。', '',
'## 逐例结果', '', '| 编号／Skill | 来源 | 轮次 | 核对 | 标注 | profiles | 未决 |', '|---|---|---:|---|---|---:|---:|']
for row in plan['cases']:
 c=row['case_id'];d=result['cases'][c];origin='本次重跑' if c in lineage['rerun_cases'] else '父记录复用'
 lines.append(f"| {c} {row['skill_name']} | {origin} | {row['selected_revision']} | {d['feedback']['status']} | {d['annotation']['status']} | {len(d['annotation'].get('profiles',{}))} | {len(d['annotation'].get('unresolved',[]))} |")
lines += ['', '所有结果保留原判和失败状态；助手意见不会覆盖模型响应。交付验收清单为 `verification.json`，覆盖前版本另存于仓库 tmp 下的 published-prior 目录。', '']
text='\n'.join(lines)
(RUN/'acceptance-report.md').write_text(text,encoding='utf-8')
(STAGE/'review/report.md').write_text(text,encoding='utf-8')
print('Wrote acceptance-report.md and staged review/report.md')
