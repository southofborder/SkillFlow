import json
from pathlib import Path

base = Path(__file__).resolve().parent
run_id = 'full-pipeline-v4-20260918-rerun-failed'
observations = {
'025': [
 '运行事实：第 0 轮核对提出 4 项差异，第 1 轮为 audit_passed；最终图 15 块、13 边、29 IR，29 份 profile 均通过记录格式校验、无 unresolved。这里是核对器通过和标注记录完整，不是语义正确证明。本意见为助手复核，未经人工确认。',
 '主要流程已记录：block_001 判断 pdftoppm 可用性；block_006 安装与 block_007 请用户本地查看是不可用时的两条路线；block_002 渲染后进入 block_003 检查，缺陷分支 block_004 不交付；零缺陷路线进入 block_005 确认和整理。reportlab 生成、更新后重渲染、pdfplumber/pypdf 文本提取、uv/pip 与 if-missing 守卫均有实际操作或声明。',
 '需优先确认传播入口的语义：唯一 entry_block_id 为 block_001，block_008 生成、block_009 更新、block_010 文本提取、block_011 依赖检查均没有来自入口的控制路径。这不违反现有结构良序性，也不能据此断言这些业务永远不可执行；但后续若仅从 entry 沿边传播，会漏掉这些子流程。必须明确当前图如何表示多个使用场景及其启动条件，不应静默按可达性丢弃它们。',
 'SKILL.md 第 47 行要求安装不可能时告知用户缺失依赖及本地安装方法。最终仅 ir_011、ir_026、ir_028 的约束保留该句，安装后的实际路径分别直接渲染或 return，没有失败告知操作/分支。finding_install_poppler 与 finding_uv_install 明确接受了声明。声明保留不等于该对用户输出动作已进入可传播图；如要求枚举所有可执行边界，应补足条件动作或明确声明由后续阶段解释的边界。现有 profile 未标出这一路 user_output，不能把约束视为已执行告知。',
 'ir_003 的 input_pdf/result_006/result_007 是不同场景的候选来源，finding_render_candidate_sources 用 DEP-SOURCE 显式保守接受，不能解释成同时传入三个 PDF；这是允许的依赖精度损失。第 0 轮 finding_8b 把 pdfplumber 与 pypdf 两个资源操作数直接当成同时工具实参，其结论偏强：资源标识及候选依赖并不自动给出实际实参语义；第 1 轮删去两个工具操作数、保留 opcode/约束的 or，并不证明旧版必然错误。',
 '安全标注需复核 actor/effects 一致性：025 全部 dispatch 仅凭 opcode 标 actor=llm，026 同类操作却标 agent_runtime，现有证据不足以唯一确定执行者。025 ir_017 被解释为“模型对 PDF 内容应用更新”且有 transform，却未给 model_observe，也未留未决；如果确为 LLM 内容处理应解释其观察边界，若只是调度工具则应修正 actor 理由。不能把调度自动等同观察，也不能由操作名直接断言主体。',
 'ir_019 引用 EM02 得到提取结果进入 LLM 上下文是公开执行假设，但因此加入 actor=llm 并称模型参与提取，混淆了结果接收者与动作执行者。ir_003/015 的 fs_read/fs_write/transform 有渲染/生成依据；ir_005/008 的视觉观察推断应标清依赖“代理实际检查图像”的执行解释。',
 'ir_011/026/028 的包安装标 net_send+net_receive 可作为需联网获取包时的效果推断，但当前命令本身不保证每次一定远程获取（缓存、已安装或本地源可能改变网络行为）；保留网络候选时需明确条件/分析假设，不能据此声称发生敏感信息外送。普通 return 未自动标 user_output，整理/删除无专门 effect 时未硬贴 transform，这两处边界处理合理。',
 '视觉复核：实际查看完整 4916×4685 PNG 与 6 处细节，标题 025/R01/r1、分支、候选输入、条件、约束和终态可读，未发现明显字形、节点遮挡或画布裁切。源码 metadata 不在 PNG 展开，已另读 CFG/源文件；视觉通过不能替代源码理解。'
],
'026': [
 '运行事实：第 0 轮提出 5 项差异；第 1 轮 CFG 通过结构及受控文本保真检查，但语义核对停止为 audit_error。最终图 14 块、18 边、27 IR，安全标注 27 份、1 条 unresolved，因此为 incomplete。本意见为助手复核，未经人工确认，不能把本图称为核对器通过图。',
 'audit_error 具体原因是已完整返回的核对响应引文校验失败，并非网络超时：r001/audit/a001 的 finding_12 将 PLAYWRIGHT_CLI_SESSION 引到 src_105（references/cli.md 第 111 行），该行实际为 Or set an environment variable once:，不包含该变量。程序拒绝整份核对结果符合契约；没有擅改引用、追认结论或对该完整响应自动重发。原始响应 finding_5 另提出参考文件并用路径问题，仅作为未通过校验的原始模型意见保留。',
 '相对第 0 轮，逐字安装说明的注释和空行已补回 ir_003；block_005–007 新增按需读取两个参考指南，block_012–013 新增 artifacts useful 守卫，原来无源文依据的完成字符串已删除，wrapper 已全局安装的例外补入图级声明。open→snapshot→最新 refs 交互→必要时重 snapshot 的环路及禁止 run-code 绕过 refs 保留。',
 '仍需确认暂停语义：源文 SKILL.md 第 20 行 pause and ask the user to install Node.js/npm。block_002 只有 ask_user_to_install_nodejs 与 dispatch，/edges/2 为 null 条件直接返回检查；无显式暂停/等待用户完成约束。第 0 轮 finding_5 已提醒这一点，第 1 轮只修复说明字面值而未补等待语义；原始第 1 轮 finding_3 却称全部保留。null 边不等于立即执行，开放 ask 也可能隐含交互等待，因此应称暂停约束未显式保留，而不是断言已形成忙循环。',
 '参考选择新增后，block_006 与 block_007 分别直接汇入 block_008，没有同一路线读取两者的连接。Open only what you need 不要求二者互斥，两个都需要时的可达流程未明确；单个 needed_reference 结果本身不能证明它只有一个值，更不能仅靠边标签推出逻辑互斥。建议确认按需访问的组合语义，避免为补两次读取反而加上无依据的互斥限制。',
 '通用交互只概括成 click/type/press/fill，产物操作概括成 screenshot/pdf/traces。参考中的上传、eval、trace-start→交互→trace-stop 等是可选能力/场景，不能要求每条示例无条件执行；但若宣称覆盖完整可选场景，当前图不能区分其内容输入、外部效果与开始/停止次序。尤其 trace 仅放在交互结束后的 capture 摘要中，不足以表达需提前开始的调试场景。传播前应明确这是主流程抽象还是完整能力覆盖。',
 'wrapper 源码被完整嵌入 5 个调用操作 metadata；--session 参数优先于非空 PLAYWRIGHT_CLI_SESSION 的条件、npx 缺失 stderr/exit 1 均在源码中存在。原图主层未显式展开这些内部控制是约定的不透明边界，不能据此声称已计算脚本内部传播，也不能把引用 metadata 当作源码已执行。',
 '唯一 unresolved 在 ir_019.effects：click/type/press/fill 是否提交表单/触发远端请求无法由该粗粒度动作确定，因此 net_send/net_receive 未决合理，不应靠工具名强行消除。ir_015 的网络双向标注引用真实 https URL 示例，有条件的远端浏览场景依据；但它不能证明每个 target_webpage 都是远端目标。snapshot 的页面状态经 EM02 进入模型，和浏览器仅加载页面但未回传全页内容应分开。',
 '安全标注中 ir_011/013/017/019 仅由 EM02 的结果进入模型推断 actor=llm，仍有把接收者当执行者的问题。ir_021 被解释为 LLM 判断 interaction_result 是否需重 snapshot，却以 EM03“调度不等于观察”给出 effects=[]；它实际有内容输入和判断输出，若该 actor 解释成立，应讨论 model_observe/transform，不能用纯调度边界排除所有内容处理。ir_025 捕获落盘但没有返回全部文件内容，不能把无 model_observe 解释成已证明文件隔离。',
 '视觉复核：实际查看完整 1801×8869 PNG 与 5 处细节，标题 026/R02/r1 正确保留 audit_error/incomplete，npx 回边、参考分支、重 snapshot 环路、artifact 条件与 return 均可见，长文本换行且无明显字形、节点边界或画布裁切问题。'
]
}
for case, items in observations.items():
    row = json.loads((base / f'preview-{case}/review-data.json').read_text(encoding='utf-8'))['cases'][0]
    review = {'run_id': run_id, 'case_id': case, 'reviews': [{
        'revision': row['selected_revision'], 'graph_sha256': row['graph_sha256'],
        'assessment': ('助手复核：核对器通过且标注记录完整，但声明动作、场景入口及主体/观察推断仍需重点确认；非人工确认。' if case=='025' else '助手复核：核对响应因错误引文被拒绝，保留最后有效图和含未决的标注；暂停与可选场景覆盖仍需复核，非人工确认。'),
        'observations': items}]}
    out = base / 'assistant-reviews' / (case + '.json')
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(out)
