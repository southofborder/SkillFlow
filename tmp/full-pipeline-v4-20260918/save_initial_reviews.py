import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918'
OUT = Path(__file__).resolve().parent / 'assistant-reviews'
OUT.mkdir(exist_ok=True)

def save(case, revision, assessment, observations):
    round_data = json.loads((RUN / 'cases' / case / 'feedback/rounds' / f'r{revision:03}' / 'round.json').read_text(encoding='utf-8'))
    data = {'run_id': RUN.name, 'case_id': case, 'reviews': [{
        'revision': revision, 'graph_sha256': round_data['graph_sha256'],
        'assessment': assessment, 'observations': observations,
    }]}
    (OUT / f'{case}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

save('001', 0, '助手已复核完整源文、末图、有效核对及全部 12 条标注；关键流程未发现明显漏转，但安全主体推断仍存在依据不足。不是用户人工确认。', [
    '图保留用户 events.json 来源、七字段声明、opted_out 与 urgent/value 联合条件、选中逐条发送、recipient/summary 绑定、禁传 access_token 和处理后写 count.txt；没有把禁止声明补成遮蔽操作。核对器初轮通过与关键流程观察一致。',
    '处理条数没有被额外要求为发送成功条数；源文没有规定这层口径。保留图中实际计数表达，不凭更强业务假设判错。',
    'ir_001 的 fs_read 及按 EM02 的工具结果默认 model_observe 有相应证据；不能据此推导 events.json 之外的容器或敏感数据集合。',
    'ir_005 条件判断与 ir_007 字段选择被直接归给 llm，并据此标 model_observe，但源文、CFG 和固定规则未明确排除本地运行时执行。引用 EM03 的“内容实际由模型处理”不能反过来证明这个前提。建议将具体执行者及相应新增观察效果列为待澄清，或在后续执行模型中统一约定；本轮不改模型标签。',
    'ir_003/ir_010 同类选择、计算动作却推断为 agent_runtime，显示 actor 归属存在不一致的推断边界；程序证据匹配通过不能解决该问题。',
    'notify.send 的 sink/发送、count.txt 的 fs_write、纯 dispatch 和空 return 未硬贴 transform/user_output，符合本例记录。没有通信返回内容的证据，不强行增加 net_receive。',
])
save('003', 0, '助手对初轮修复依据的局部复核：来源/字段遗漏有依据，另有一项疑似命名误报；尚不是末次图验收。', [
    'finding_2 指出读取来源及记录字段模式未完整记录，尤其 record_id，在初轮实际 CFG 中有缺口。',
    'finding_5 仅因 opcode notify_send 与源文 notify.send 不同判 internal_conflict；block_003 名称以及 ir_005 同一操作约束均明确 notify.send，资源 notify 也属于该工具。开放操作名允许合理抽象，点号与下划线差异本身不足以证明行为矛盾。建议视作疑似误报，不能把它作为已证实业务错误。',
    '原始判断及触发的后续重新提取仍保留。最终通过不能抹去这项初轮判断问题；需要另行复核末次图。',
])
