from pathlib import Path
import datetime
import hashlib
import json
import re
import zipfile

ROOT = Path('D:/projects/SkillFlow')
BASE = ROOT / 'packages/skill-ir/experiments/semantics_baseline'
RUN = BASE / 'runs/baseline-deepseek-v4-flash-max-20260910'
SAMPLES = json.loads((ROOT / 'tmp/skill-ir-review-set/render-input.json').read_text(encoding='utf-8'))['samples'][10:20]

def source(sid, line, filename='SKILL.md'):
    path = BASE / 'frozen/corpus/inputs/controlled' / sid / filename
    return f'[{filename}:{line}]({path.as_posix()}:{line})'

def body(sid):
    S = lambda line, filename='SKILL.md': source(sid, line, filename)
    if sid == 'Q05':
        return {
            'overall': '选定第 1 轮完整保留本样例的查询语义：单次搜索和原值返回仍实际执行，历史 count.txt 示例没有变成写文件操作；未发现确定错转或事实遗漏。',
            'issues': [
                f'**等价表达：可选参数的省略依赖调用约束。** {S(12)}、{S(14)} 要求缺失时省略参数；CFG 的 `block_002 → block_004`（`from_date missing`）及 `block_005 → block_007`（`limit missing`）跳过字段提取，但 `block_008/ir_014` 仍列出 `result_005/result_006`。这两个输入应结合调用上的 omit 约束读取，不能据此认定缺失时发送了 null。建议保留这两条省略约束及分支条件；若以后需要更精确的执行解释，应明确输入受相应存在性条件约束，而非补空值。',
                f'**未知边界：存在判断不等于日期校验。** {S(11)} 规定日期格式，{S(16)} 又明确不要求调用前验证或规范化。`block_002/ir_004/ir_005` 只判断字段是否存在，`block_008/ir_014` 保留格式和原值约束，符合原文。显式 null、空字符串及畸形日期应如何处理仍未定义。建议保持未定，不增加解析、纠错、默认日期或失败分支。',
                f'**历史示例的排除范围正确。** {S(17)} 只把写 count.txt 标为不执行；`block_008 → block_009` 仍完成搜索和 items 返回。完整 analysis 的 diagnostics 也说明了这一排除。建议共同复核时不要把“没有 count 写入”误记为遗漏，更不能由此删除其余实际查询行为。',
            ],
            'kept': [
                '读取 request.json 后，term 经 `ir_003` 产生 `result_002`，唯一 `ir_014` 搜索使用该值；图中不存在第二次搜索或回到搜索的边。',
                'from_date 的 YYYY-MM-DD、原值传递以及 limit 原值传递都附在实际调用上；未生成模糊扩展、规范化或 index.delete 操作。',
                '`ir_016` 从本次 `search_response/result_007` 提取 items，`ir_017` 原值返回；返回数据没有被历史 total 示例替换。',
            ],
            'facts': [
                ('preserved','保留','`block_001/ir_001` 读取 request.json；`block_002/ir_003–005` 使用该读取结果。'),
                ('preserved','保留','唯一 `block_008/ir_014` 使用 `result_002`；Skill 约束保留 exactly once。'),
                ('preserved','保留','`block_003/ir_007` 提取日期；`ir_014` 附原值及 YYYY-MM-DD 约束。'),
                ('preserved','保留','缺失边 `block_002 → block_004` 跳过取值；`ir_014` 明确 omit。'),
                ('preserved','保留','存在边 `block_005 → block_006` 经 `ir_011` 取 limit；调用要求原值。'),
                ('preserved','保留','缺失边 `block_005 → block_007` 与 `ir_014` 省略约束一致，无默认常量。'),
                ('preserved','保留','`block_009/ir_016 → ir_017` 返回同次响应 items，保留 unchanged。'),
                ('preserved','保留','Skill 全局禁止 index.delete；全部操作没有该调用。'),
                ('preserved','保留','`block_001–009` 无 fuzzy 扩展；diagnostics 将能力说明留作非执行信息。'),
                ('preserved','保留','`ir_004/005` 是存在判断；全部图中无日期校验、规范化或内容转换。'),
                ('preserved','保留','`block_008 → block_009` 直接进入结果返回；无 total 提取或 count.txt 写入。'),
            ],
            'boundary': '本次仅评估 Q05 第 1 轮；“缺失”不擅自扩大为 null、空串或无效值。约束与控制边共同承载可选参数语义，不能只看 inputs 列表就推断实参一定发送。原文未定义搜索失败策略，不补重试或替代结果。',
        }
    if sid == 'Q06':
        return {
            'overall': '选定第 1 轮保留全部外置事实，尤其正确表达 limit 缺失时传 10 的最小变化；count.txt 写入及 items 返回均来自同一次搜索响应，未发现确定错转或遗漏。',
            'issues': [
                f'**等价表达：默认 10 是本样例的明确要求。** {S(14)} 规定缺失 limit 时传 10。CFG 的 `block_004 → block_006`（`limit is missing`）进入 `ir_012`，常量 10 经 `block_007/ir_014` 汇合为 `result_008`，再供搜索使用。此处增加参数选择操作落实了原文，并非凭空补默认值。建议保留与常规省略 limit 样例的差异，不把它改成 omit，也不把已有 limit 覆盖为 10。',
                f'**需注意的表达边界：汇合输入必须按分支选择。** {S(13)} 与 {S(14)} 分别描述已有值和缺失值；`ir_014 resolve_limit_argument` 同时列出两支的 `result_006/result_007` 及 `limit_present/result_005`。应理解为按存在性选取对应结果，并不要求两支都执行。日期缺失边 `block_002 → block_004` 同样跳过取值，而 `ir_016` 保留 omit 约束。建议在后续解释中沿用这套分支条件，不补空值或同时执行两支；当前不据此判定错转。',
                f'**未知边界：格式说明仍不是额外验证。** {S(11)}、{S(16)} 不定义畸形日期、显式 null 或不合理 limit 的处理。实际图只有存在判断、值选择和搜索，没有日期解析或参数规范化，符合要求。建议保留这条边界；默认 10 只适用于原文的 missing 条件，不能扩展到“值不合法”。',
            ],
            'kept': [
                '`block_001/ir_001` 读取 request.json，term 和两个可选字段均来自它；`block_008/ir_016` 是唯一搜索，query 原值及单次限制明确。',
                '`block_009/ir_018/ir_019` 先提取 `result_009` 的 total 并写 count.txt，再到 `block_010/ir_021/ir_022` 返回同一响应的 items。',
                'fuzzy 匹配仍是能力说明；禁止 index.delete 和不要求预校验的约束保持全流程范围，没有生成摘要、额外查询或写入以外的附加行为。',
            ],
            'facts': [
                ('preserved','保留','`block_001/ir_001` 读取 request.json，后续字段均引用 `result_001`。'),
                ('preserved','保留','唯一 `block_008/ir_016` 以 `result_002` 搜索，调用与全局均保留次数要求。'),
                ('preserved','保留','`block_003/ir_006` 取 from_date；`ir_016` 保留原值及日期格式。'),
                ('preserved','保留','`block_002 → block_004`（`from_date is missing`）跳过取值；调用保留 omit。'),
                ('preserved','保留','`block_005/ir_010` 取请求 limit，`ir_014` 选择它；`ir_016` 要求 unchanged。'),
                ('preserved','保留','缺失支 `block_006/ir_012` 的 literal 10 经 `ir_014` 到 `ir_016`。'),
                ('preserved','保留','`block_010/ir_021/ir_022` 从同次 `result_009` 取 items 并直接返回。'),
                ('preserved','保留','Skill 全局禁止 index.delete，全部可达路径没有删除调用。'),
                ('preserved','保留','Skill 保留 capability note；`block_001–010` 不含 fuzzy 扩展操作。'),
                ('preserved','保留','存在判断和默认值选择只落实参数规则；图中没有新增验证或规范化。'),
                ('preserved','保留','`block_008 → block_009 → block_010` 保证先搜索、写 total、再返回 items。'),
            ],
            'boundary': '仅对 Q06 第 1 轮给出结论；默认值分支不是所有查询样例的共同规则。条件值选择属于语义表示，不在本次将它改造成可执行程序或新增 IR 规则。日期、limit 的非法值处理及搜索错误处理均未定义，继续留待原文补充。',
        }
    if sid in ['F01','F02','F03','F04','F05','F06']:
        return fetch_body(sid, S)
    return document_body(sid, S)

def fetch_body(sid,S):
    data = {
        'F01': {'gate':3,'first':4,'retry':8,'archive':11,'firstir':7,'retryir':15,'archiveir':21,'returns':[12,20,26,28],'append':[11,19,25,27],'exits':[6,10,13,14],'status':[4,8,11,12],'lines':[8,9,9,10,11,12,13,14,15,16]},
        'F02': {'gate':3,'first':4,'retry':5,'archive':6,'firstir':7,'retryir':9,'archiveir':11,'returns':[14,16,18,20],'append':[13,15,17,19],'exits':[7,8,9,10],'status':[5,7,9,10],'lines':[8,8,8,10,10,12,12,14,14,16]},
        'F03': {'gate':3,'first':4,'retry':6,'archive':7,'firstir':7,'retryir':11,'archiveir':13,'returns':[16,18,20,22],'append':[15,17,19,21],'exits':[8,9,10,11],'status':[4,7,9,10],'lines':[10,11,11,12,13,14,15,16,17,18]},
        'F04': {'gate':2,'first':3,'retry':4,'archive':5,'firstir':5,'retryir':7,'archiveir':9,'returns':[12,14,16,18],'append':[11,13,15,17],'exits':[6,7,8,9],'status':[3,5,7,8],'lines':[3,5,5,8,9,13,15,17,19,21]},
        'F05': {'gate':3,'first':4,'retry':5,'archive':6,'firstir':7,'retryir':9,'archiveir':11,'returns':[13,14,15,16],'append':[],'exits':[7,8,9,10],'status':[5,7,9,10],'lines':[8,9,9,10,11,12,13,14,15,16]},
        'F06': {'gate':3,'first':4,'retry':5,'archive':6,'firstir':7,'retryir':9,'archiveir':11,'returns':[14,16,18,20],'append':[13,15,17,19],'exits':[7,8,9,10],'status':[5,8,11,12],'lines':[8,9,9,10,11,12,13,14,15,16]},
    }[sid]
    b=lambda n:f'block_{n:03d}'
    i=lambda n:f'ir_{n:03d}'
    res=lambda n:f'result_{n:03d}'
    gate,first,retry,arc=[b(data[k]) for k in ['gate','first','retry','archive']]
    fi,ri,ai=[i(data[k]) for k in ['firstir','retryir','archiveir']]
    ret=[i(n) for n in data['returns']]
    exits=[b(n) for n in data['exits']]
    l=data['lines']
    L=lambda n:S(l[n-1], 'references/workflow.md') if sid=='F04' else S(l[n-1])
    field='summary' if sid=='F06' else 'body'
    if sid=='F01':
        issues=[
            f'**未知边界：状态文字是结果的表示，不是源文指定的固定格式。** {L(10)} 只要求追加最终状态。`block_006/ir_011`、`block_010/ir_019`、`block_013/ir_025` 写 success，`block_014/ir_027` 写 failure；这些出口分别受真实成功或失败条件控制，覆盖关系正确。diagnostics 说明了文字未定义，因此不把这两种字面量本身判为错转。建议共同复核时保留这一未定项，不能再扩展日志字段、时间戳或新的格式要求。',
            f'**等价表达：错误判断的拆分没有增加重试。** {L(4)}、{L(5)} 要求仅首次瞬态失败重试一次。实际先在 `block_005` 分成功/失败，再在 `block_007/ir_013` 判断 transient；`block_007 → block_008` 仅瞬态，`block_007 → block_011` 非瞬态，`block_009 → block_011` 是重试失败。拆成多个判断块不改变次数；建议按这些边核对，不把“两个 fast 节点”误读成两次重试。',
        ]
    elif sid=='F02':
        issues=[
            f'**等价表达：多分支直接表达首次结果。** {L(4)} 的三种结果在 `block_004` 直接分流：成功到 `block_007`，瞬态失败到 `block_005`，非瞬态失败到 `block_006`；重试失败再由 `block_005 → block_006` 回退。无需额外拆一个“检查成功”节点才能成立。建议保持条件的首次/重试区别，不能把重试失败重新送回瞬态重试支。',
            f'**需注意作用范围：全局存放没有抹掉条件。** {L(2)}、{L(6)} 等段落被重复保留在 Skill constraints 中，但条件文字及局部实际路径仍一致；`block_006/ir_011` 的参数只有 source_id，四个出口先写状态再返回。因此当前没有无条件执行 archive 或越界重试的证据。建议审阅时联合检查条件和图路径，不仅凭约束位于页头就判它改成无条件行为。',
        ]
    elif sid=='F03':
        issues=[
            f'**可改进的名称表达，不是实际顺序错误。** {L(10)} 要求返回前追加状态；`block_008–011` 的块名采用 “Return … and append” 措辞，容易使人误读先返回。实际操作分别为 `ir_015/017/019/021` 先 append，再 `ir_016/018/020/022` return，顺序正确。建议后续只在展示名称中采用“追加状态后返回”的顺序，不能据块名把正确的实际指令判成颠倒。',
            f'**未知边界：状态字符串和响应拆分。** {L(7)}、{L(8)}、{L(10)} 要求返回对应 body/error 并记录最终状态，但未规定完整响应结构和状态格式。CFG 为工具分别产出 body/error，并在各最终出口使用 success/failure；diagnostics 明确记录了这两项表示选择。分支与返回结果一一对应，当前可接受；建议继续保留格式未定，不额外编造错误分类代码或状态字段。',
        ]
    elif sid=='F04':
        issues=[
            f'**等价表达：配置内容是本次采用的规则，不是新增读取动作。** {S(8)} 明确纳入工作流；{S(11,"references/workflow.md")} 又采用 {S(1,"retry.yaml")} 的固定策略。`block_004/ir_007` 保留 fast 最多两次及 transient_only，`block_005/ir_009` 保留 archive 最多一次，实际图没有把 YAML 添加为运行时读取节点。这样保留了跨文件语义；建议不要仅因存在 retry.yaml 就增添配置加载操作。',
            f'**未知边界：凭据存在与瞬态错误只保留命名条件。** {L(2)}、{L(4)} 并未给出空字符串、空白、错误码或重试等待时间的规则。`block_002` 直接按 FAST_KEY is present/absent 分流，`block_003 → block_004` 只在首次 transient 失败时执行。当前没有越界策略；建议维持这些原文条件，不将 YAML 的次数配置扩展成退避、超时或 archive 重试。',
        ]
    elif sid=='F05':
        issues=[
            f'**历史示例必须保持不执行，当前处理正确。** {L(10)} 只将追加 status.txt 改成历史示例；`block_007–010` 四个出口均直接 return，没有追加或其他文件写入。diagnostics 明确指出排除的是第 9 条。建议共同复核时不要按 F01 的正常状态记录规则“补齐”此样例，也不能把历史标记扩大到前面的实际获取、回退和返回。',
            f'**等价表达：短条件标签需结合起点理解。** {L(4)}、{L(5)} 在 `block_004 → block_005` 以 transient error 表示首次瞬态失败，`block_004 → block_006` 为 non-transient error；`block_005 → block_006` 的 failure 则指任意重试失败。标签虽短，但起点和局部约束消除了区别歧义。建议查看时保留起止块，不把这些边统一概括成“失败就重试”。',
        ]
    else:
        issues=[
            f'**关键差异已保留：summary 是响应字段，不是摘要生成命令。** {L(7)} 把成功返回字段明确改为 summary。`ir_007/009/011` 分别产出 `result_005/008/011`，`ir_014/016/018` 原值返回；实际图没有生成或改写摘要的操作。建议保留这一数据来源，不沿用其他 F 样例的 body，也不要看到 summary 就增加内容加工。',
            f'**未知边界：最终状态格式仍未定义。** {L(10)} 只要求追加最终状态；`ir_013/015/017` 写 success，`ir_019` 写 failure，分别由对应终态边控制，随后才 return，行为覆盖正确。此轮 diagnostics 没有补充格式说明，但源文仍未授权具体文件格式。建议把字面量当作语义状态表示，后续若要求精确字节格式再共同确认，不因此引入新日志策略。',
        ]
    returns_text='、'.join(f'`{r}`' for r in ret[:3])
    f4ref = '`block_007 → block_008`（first fast.fetch failure was transient）及 `ir_015`' if sid=='F01' else ('`block_005 → block_006`（first failure is transient）及 `ir_011`' if sid=='F03' else f'`{first} → {retry}` 的首次 transient 失败边及 `{ri}`')
    facts=[
        ('preserved','保留',f'`block_001/ir_001` 读请求，`block_002/ir_003` 读环境；结果分别供工具和门控使用。'),
        ('preserved','保留',f'`{gate} → {first}` 是有密钥支；`{gate} → {arc}` 是缺密钥直达 archive 支。'),
        ('preserved','保留',f'首次 `{first}/{fi}` 与重试 `{retry}/{ri}` 均消费已读 source_id、FAST_KEY。'),
        ('preserved','保留',f'{f4ref} 只允许一次重试；无返回 fast 的回边。'),
        ('preserved','保留',f'首次非瞬态失败与重试失败两条路径都进入 `{arc}/{ai}`。'),
        ('preserved','保留',f'`{arc}/{ai}` 只有 source_id 数据参数；最多一次约束和无回边的图相符。'),
        ('preserved','保留',f'{returns_text} 分别返回本次成功 {field}；之后没有 fetch。'),
        ('preserved','保留',f'archive 失败进入 `{exits[3]}/{ret[3]}`，返回本次 error；无 archive 重试。'),
        ('preserved','保留',f'Skill 全局禁止 FAST_KEY 进入 archive/diagnostic；`{ai}` 不接收该值。'),
    ]
    if sid=='F05':
        facts.append(('preserved','保留','`block_007–010/ir_013–016` 直接返回；全部 CFG 无 status.txt 写入，诊断解释历史示例。'))
    else:
        facts.append(('preserved','保留',f"四个终态各先由 `{'/'.join(i(n) for n in data['append'])}` 追加状态，再由对应 return 结束。"))
    return {
        'overall': f"选定第 {'3' if sid=='F03' else '1'} 轮保留全部十项外置事实：凭据门控、一次瞬态重试、一次 archive 回退和原值返回均成立；"+('历史状态示例未被执行。' if sid=='F05' else '每个最终出口均在返回前追加状态，未发现确定错转或遗漏。'),
        'issues': issues,
        'kept': [
            f'请求来源与环境来源保持区别，读取结果贯穿首次调用和重试。`{arc}/{ai}` 共享缺密钥、首次非瞬态失败、重试失败入口，但每条执行路径最多访问它一次。',
            f'成功的首次、重试和 archive 路径分别返回各自的 {field}；archive 失败返回自己的 error，没有误用首次失败或另一次调用的数据。',
            ('成功和失败仍正常结束；只有历史 status.txt 写入被排除，密钥的全局禁止流向以及工具参数没有随之删除。' if sid=='F05' else '状态记录保留为独立操作并覆盖三个成功出口和一个失败出口。FAST_KEY 只用于门控和 fast 调用，未进入 archive 或状态文件输入。'),
        ],
        'facts':facts,
        'boundary':'FAST_KEY 的精确存在性测试、上游 transient 分类规则、工具响应的完整结构均未定义；本次不补错误码、等待时长、退避或第三次尝试。返回前追加状态不授权额外诊断内容。语义相同的共享 archive 节点、拆开的判断块及不同结果名称均可接受，判断依据是实际边和数据依赖。',
    }

def document_body(sid,S):
    d1=sid=='D01'
    partial=f'**部分保留：逐文档调用及每次 stdout 的绑定粒度不足。** {S(9 if d1 else 8)} 要求逐个调用，而 {S(5,"scripts/convert.py")} 至第 10 行表明单次脚本只接收一个文档，最终打印一个路径。实际 `block_004/ir_007` 一次消费整份 `document_paths/result_002` 和 output_dir，输出路径集合 `result_005`；有 each 的名称及原样命令，却没有当前文档与每次 stdout 的逐项绑定。'+('' if d1 else ' diagnostics 还明确说明将 per-document loop 压缩为 batch operation。')+'这不足以单靠图验证列表中每个文档都对应一次调用及一项返回路径。建议在该操作的外层语义中明确逐项映射和收集关系，可用参数约束或外层控制表达；无需固定 loop 操作类型，也不要拆开脚本内部处理。此项不等同于断言模型只执行一次。'
    if d1:
        issues=[
            f'**确定错转：范围未知的备注被升级为全局规则。** {S(17)} 的“必要时保留原顺序”没有指定条件、对象或操作。实际 CFG 将它放入 `Skill.constraints[2]`，且 diagnostics 为空；于是读者会把它与两条明确的全局禁令同等适用于全部流程，这超过原文证据。建议从确定的全局规则中移出，作为范围待确认的外置问题保留；不能自行决定约束转换、打包还是交付，更不要据此补排序步骤。',
            partial,
        ]
    else:
        issues=[
            partial,
            f'**等价表达：固定输出文件不必伪造返回值。** {S(12)} 与 {S(21)} 明确采用打包命令；`block_005/ir_009.metadata.command` 包含 `--output bundle.zip`，完整脚本 {S(10,"scripts/package.py")} 实际以写模式创建它。虽然 `ir_009.outputs` 为空，后续 `block_006/ir_011` 沿无条件边消费同名 `bundle.zip` 资源及已读 `result_004`。文件副作用与交付目标已可追踪，不能仅因没有 result 输出而判产物遗漏。建议保留命令、文件名和依赖顺序，避免把该输出资源误称为必须由用户预先提供的文件。',
            f'**未知边界已经正确留下。** {S(16)} 的顺序备注没有限定对象，实际 diagnostics 明确说明不提升为 Skill 全局，图中也未添加顺序规则。建议继续把它作为待共同确认项；PNG 不展示 diagnostics 不代表它在 analysis 中丢失。',
        ]
    facts=[
        ('preserved','保留','`block_001/ir_001 → block_002/ir_003` 建立清单路径来源；`ir_005` 读取两个请求目录。'),
        ('partial','部分保留','`block_004/ir_007` 保留单文档命令和完整脚本，但列表到逐次调用、stdout 收集绑定不够明确。'),
        ('preserved','保留','`ir_007.constraints` 将保留标题限定于转换，未扩展至汇总或整份 Skill。'),
        ('preserved','保留','`ir_007` 以黑盒保留脚本、参数和路径结果；内部目录创建、读写没有拆成主流程操作。'),
        ('preserved','保留','`block_005/ir_009` 的命令及脚本明确 --paths、--output；ZIP 内使用 path.name。'),
        ('preserved','保留',('`ir_011` 消费打包结果 `result_006` 和早先读取的交付路径 `result_004`。' if d1 else '`ir_009` 写出的固定 bundle.zip 经顺序边供 `ir_011` 交付，并消费已读 `result_004`。')),
        ('preserved','保留','`block_007/ir_013` 独立写 receipt.txt，内容引用转换路径 `result_005`。'),
        ('preserved','保留','Skill 全局保留不得修改输入原文文件，未降低为仅转换阶段要求。'),
        ('preserved','保留','Skill 全局保留不得向外部服务上传文档，没有生成上传操作。'),
        (('contradicted','错转','`Skill.constraints[2]` 擅自提升未定范围的原顺序备注，且无诊断保留该不确定性。') if d1 else ('preserved','保留未知边界','analysis diagnostics 明确顺序备注对象未知，未提升全局；各操作也未擅定其范围。')),
    ]
    return {
        'overall':('选定第 1 轮的主要文件处理和交付链保留，但存在一项确定的约束范围错转，以及一项逐文档转换表达不足，建议共同复核后再确认其语义完整性。' if d1 else '选定第 1 轮保留主要文件处理、交付和未知顺序边界；需注意逐文档调用与每次 stdout 收集的表达粒度，其余事实未发现确定错转。'),
        'issues':issues,
        'kept':[
            '清单文档路径、output_dir、delivery_path 均有实际读取结果。转换输出 `result_005` 同时供打包和 receipt.txt，收据没有误写 ZIP 路径。',
            '核对两个完整脚本后，UTF-8 读取、按源主名写 .txt、标准输出路径，以及 ZIP 读取产物并用文件名入包，都保留在调用的 script_content 中；没有在主流程重复执行这些内部动作。',
            '转换局部标题约束与不得改输入、不得外传的全局禁令分开保存；明确采用的参考命令作为真实打包动作，交付使用先前读取的目标，不重复读取请求。',
        ],
        'facts':facts,
        'boundary':'“必要时”的条件与“原顺序”的对象仍须依据源文确认，不补排序或遍历顺序策略。重复文件名、输出与输入路径重合、路径不存在及转换失败的处理未定义，本次不替原文选择覆盖、去重或重试方案。脚本源码作为黑盒行为证据静态阅读，没有执行。对逐项转换的建议针对调用外层，不要求暴露脚本内部变量或控制流。',
    }

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    outdir=ROOT/'result/suggestions'
    outdir.mkdir(parents=True,exist_ok=True)
    export=json.loads((ROOT/'tmp/skill-ir-review-set/export-audit.json').read_text(encoding='utf-8'))
    pairs={p['basename']:p for p in export['verified_pairs']}
    reviewed=[]
    for s in SAMPLES:
        sid=s['sample_id']; name=s['basename']; rep=s['repetition']
        assert rep==(3 if sid=='F03' else 1)
        analysis_path=Path(s['analysis_path'])
        analysis=json.loads(analysis_path.read_text(encoding='utf-8'))
        assert analysis['status']=='complete'
        normalized_cfg=json.loads(json.dumps(analysis['cfg']))
        for block in normalized_cfg['blocks'].values():
            for instruction in block['instructions']:
                for operand in instruction['inputs']+instruction['outputs']:
                    for optional in ['identifier','literal_value','semantic_name']:
                        operand.setdefault(optional,None)
        assert normalized_cfg==s['cfg']
        assert sha(analysis_path)==s['analysis_sha256']
        annotation_path=BASE/'frozen/corpus/annotations'/f'{sid}.json'
        annotation=json.loads(annotation_path.read_text(encoding='utf-8'))
        zip_path=ROOT/'dataset/skills'/f'{name}.zip'
        png_path=ROOT/'result/ir-IPP'/f'{name}.png'
        zipsha=sha(zip_path); pngsha=sha(png_path)
        assert zipsha==pairs[name]['source']['zip_sha256']
        assert pngsha==pairs[name]['png_sha256']
        frozen=Path(s['package_path'])
        sources={p.relative_to(frozen).as_posix():p for p in frozen.rglob('*') if p.is_file()}
        with zipfile.ZipFile(zip_path) as z:
            members={i.filename:z.read(i) for i in z.infolist() if not i.is_dir()}
            # Packaging may use one skill-name root folder; compare all bytes after stripping it.
            if set(members)!=set(sources):
                members={k.split('/',1)[1]:v for k,v in members.items()}
            assert set(members)==set(sources),(sid,list(members),list(sources))
            assert all(members[n]==p.read_bytes() for n,p in sources.items()),sid
        d=body(sid)
        if sid=='Q05':
            d['issues'].append(f'**等价表达：未执行的说明不要求独立节点。** {source(sid,8)} 的模糊匹配能力说明与 {source(sid,17)} 的历史写入说明，均不是当前动作。实际 `block_001–009` 只有文件读取、取字段、条件分派、搜索和结果返回，diagnostics 分别解释了两类非执行内容的去向。因此，图中找不到“能力说明”节点或“历史示例”节点本身不是遗漏。建议把这些文本用于核对行为边界，而不是转成额外操作；与此同时，搜索响应仍须真正产生并供返回使用，不能用一个泛化的“支持查询”节点替代当前 `ir_014/ir_016/ir_017` 的数据链。当前图保留了这条链，未发现此类替代。')
        elif sid=='Q06':
            d['issues'].append(f'**需保留的副作用区别：写 total 与返回 items 是两件事。** {source(sid,17)}、{source(sid,18)} 分别要求写计数和返回查询项。实际 `block_009/ir_018` 消费 `result_009`，产出 total 后由 `ir_019` 写入本地 count.txt；随后 `block_010/ir_021` 再从同一个响应提取 items，并由 `ir_022` 返回。两个消费者使用同一响应标识，能够核对它们不是来自两次搜索。建议保持这条先写后返回的路径，不把 count.txt 的内容替换成 items 数量的重新计算，不把 items 改成计数文件，也不能因另一历史示例样例不写文件而删除本轮的真实写入。')
        elif sid.startswith('F'):
            data_archive={'F01':('block_011','ir_021',12),'F02':('block_006','ir_011',12),'F03':('block_007','ir_013',14),'F04':('block_005','ir_009',13),'F05':('block_006','ir_011',12),'F06':('block_006','ir_011',12)}
            ab,ai,line=data_archive[sid]
            origin=source(sid,line,'references/workflow.md' if sid=='F04' else 'SKILL.md')
            d['issues'].append(f'**等价表达：工具标识不算新增业务实参。** {origin} 要求 archive 只传 source_id。实际 `{ab}/{ai}` 的 inputs 还列有 external_resource 类型的 archive.fetch，这是被调用服务的身份；业务数据输入仅为已读 source_id，不包含 FAST_KEY。因此不能把这两个操作数简单计成两个 API 参数，也不能为了“只留一个”删掉服务定位。建议核对参数时区分工具标识与传递的数据，并沿结果标识确认 source_id 来自原请求。当前所有 archive 入口共享该调用，缺密钥支和失败回退支没有偷偷改变它的参数。')
            d['boundary']+=' 成功后的“停止进一步获取”并不排除原文明示的返回前状态追加；历史示例样例则应直接返回。应逐条沿终态路径核对允许的末尾动作，不能只凭节点总数或块名作结论。'
        if sid.startswith('Q'):
            d['boundary']+=' 本页所说“保留”指原文要求在操作、数据依赖或约束中有依据，并不要求每句文字都拥有独立节点；操作名称差异也不单独构成错误。'
        assert len(d['facts'])==len(annotation['facts'])
        parts=[f"# {s['index']:03d} {s['skill_name']}｜语义评审",f"样例：**{sid}**；选定轮次：**第 {rep} 次**；批次配置：deepseek-v4-flash-max。对应 [ZIP 原始包]({zip_path.as_posix()}) · [PNG 实际 CFG]({png_path.as_posix()})。",d['overall'],'## 需修改或注意的问题']
        parts.extend(f'{j}. {t}' for j,t in enumerate(d['issues'],1))
        parts.append('## 已保留的关键内容')
        parts.extend(f'- {t}' for t in d['kept'])
        parts.extend(['## 逐项核对',f"以下按[外置事实标注]({annotation_path.as_posix()})的全部 {len(annotation['facts'])} 项核对；状态只针对上述选定轮次。"])
        fact_records=[]
        for fact,(status,label,explanation) in zip(annotation['facts'],d['facts']):
            parts.append(f"- **{fact['id']}｜{label}**：{explanation}")
            fact_records.append({'fact_id':fact['id'],'status':status,'conclusion':explanation})
        parts.extend(['## 复核边界',d['boundary'],f"本评审同时检查了[选定 analysis.json]({analysis_path.as_posix()})中的完整 CFG、diagnostics 和 metadata。PNG 的展示范围不包含 metadata；图上没有脚本正文或命令文本，不能据此判为提取遗漏。建议文件属于外置语义评审意见（由 Codex 复核），未写回 Skill 输入，也未修改 ZIP、PNG、生产 Prompt、IR 或提取流程。"])
        text='\n\n'.join(parts)+'\n'
        output=outdir/f'{name}.md'
        output.write_text(text,encoding='utf-8')
        old=json.loads((RUN/'reviews'/f'{sid}.json').read_text(encoding='utf-8'))
        old_selected={f['fact_id']:next(a['verdict'] for a in f['assessments'] if a['repetition']==rep) for f in old['facts']}
        difference=[{'fact_id':f['fact_id'],'old_status':old_selected[f['fact_id']],'new_status':f['status']} for f in fact_records if old_selected[f['fact_id']]!=f['status']]
        reviewed.append({'number':f"{s['index']:03d}",'sample_id':sid,'selected_repetition':rep,'suggestion_path':output.as_posix(),'suggestion_sha256':sha(output),'chinese_character_count':len(re.findall(r'[\u4e00-\u9fff]',text)),'analysis_path':analysis_path.as_posix(),'analysis_sha256':sha(analysis_path),'cfg_matches_png_render_input':True,'zip_path':zip_path.as_posix(),'zip_sha256':zipsha,'zip_matches_frozen_package_bytes':True,'png_path':png_path.as_posix(),'png_sha256':pngsha,'final_hashes_match_export_audit':True,'annotation_path':annotation_path.as_posix(),'annotation_sha256':sha(annotation_path),'source_files_read':[{'path':p.as_posix(),'sha256':sha(p)} for p in sources.values()],'fact_coverage':{'expected':len(annotation['facts']),'reviewed':len(fact_records),'complete':True},'facts':fact_records,'overall':d['overall'],'differences_from_previous_selected_trial_review':difference,'additional_notes':'独立复读冻结原文、全部包内脚本/配置、选定 CFG 与 diagnostics 后形成中文建议；没有套用多轮 overall。'})
    report={'schema_version':1,'reviewer':'finish_prior_pdf','reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'range':'011–020','status':'complete','documents':reviewed,'total_facts':sum(d['fact_coverage']['reviewed'] for d in reviewed),'production_or_inputs_modified':False,'skills_executed':False,'remote_api_called':False}
    audit=ROOT/'tmp/skill-ir-review-set/suggestions-011-020-review.json'
    audit.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'documents':len(reviewed),'total_facts':report['total_facts'],'chinese_character_counts':{d['sample_id']:d['chinese_character_count'] for d in reviewed},'audit':audit.as_posix()},ensure_ascii=False))

if __name__=='__main__':
    main()
