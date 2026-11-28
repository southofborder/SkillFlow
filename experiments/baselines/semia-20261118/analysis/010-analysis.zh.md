# SEMIA 010 终态分析

审阅完成于 2026-11-18T09:52:31.605105+00:00。管线正常完成（exit 0），第三次合成得到结构有效候选，detector输出0项，随后产生 Recommend with caution 推荐。这是受控文本分析结果，不是对Skill安全或全部源约束正确性的证明。

总耗时379.664秒，4次native starts：3次CGRS + 1次推荐。公开 input 51907 + output 10050 = 61,957 tokens；其中CGRS 49802、推荐 12155。4次都有唯一公开完成usage并与回执一致，全部native exit0，无超时/外层provider retry；缓存和reasoning为子计数，内部未公开使用量仍未知。

三份完整源文件在4次实际prompt中均出现；360官方源码、输入、CLI、runner和helper固定值一致。记录的controller及4个native PID全部退出，没有仍存的直接子进程；root已收回session99585并报告exit0。没有执行Skill、旧管线、回放、测试或额外模型请求。

## 结构失败与候选选择

前两候选分别有3个、7个SDL003错误，第三候选0错误/0警告。第一次是action_trigger、action_param、call_effect证据缺参；第二次是call_evidence_text多传action参数。001的实体级示例/通用描述不一致在第二次再次出现，但不能把它当作第一次annotation缺参的充分解释。

详细validation副本保留了代码、行号和谓词；实际重试prompt仍只收到errors/warnings计数和比率，没有具体错误或被拒候选全文。该反馈缺失在010重现；第三次独立生成恰好通过，并不证明前两次问题被定向修好。4份validation中最后一份只是选中候选的复核，不是第四个候选。

## 分数和覆盖的实际含义

选中iteration0在三次attempt后触发ceiling：0.5×1.0（证据匹配）+0.3×1.0（事实支持）+0.2×125/192（参考单元token覆盖）=0.930208，大于0.9即停止。参考覆盖是13/23单元、token权重65.104%；不是93.0%准确率，也不是只有65.1%源文送入模型。

from_date/limit的present/omit四条及query.yaml的两行全部已被sidecar引用。它们丢失的是detector-facing条件/省略语义：选中core只留下可能的call_input关系，_if_present只是ID，不是被规则解释的守卫。不能据这份抽象图证明正确省略，也不能反向断言运行时一定多传了参数。

| 源约束 | 实际保留与解释边界 |
|---|---|
| 读取 request.json 并执行单次 index.search，term 直传 query | 选中图有 read_request → index_search 的单一调用节点和 term 输入，源文证据引用了 exactly once/unchanged；core 没有命名 query 参数、调用次数或值相等的可执行约束，因此只是与要求相容的粗粒度图，未证明精确履约。 来源：inputs/010/references/workflow.md:5,7 |
| from_date 存在则原值传入，缺失则省略；YYYY-MM-DD 是调用要求 | present/omit/format 原句及配置行全部被 evidence sidecar 引用；core 只保留 call_input(index_search, request_from_date_if_present)。ID 字符串未被规则解释为存在性守卫；没有参数缺失/省略、格式或等值约束。本结果不能验证实际省略行为，也不能据抽象输入边断言运行时必然错误地传了该参数。 来源：inputs/010/references/workflow.md:10,11; inputs/010/query.yaml:2 |
| limit 存在则原值传入，缺失则省略，不新增回退值 | 两条要求和 limit: omit 都保留在证据中；core 仍是无守卫的可能输入关系，没有缺失/省略状态或命名参数语义。没有生成额外 fallback cap，但这不是对省略正确性的形式证明。 来源：inputs/010/references/workflow.md:12,13; inputs/010/query.yaml:3 |
| fuzzy matching 只是能力说明，本流程没有要求扩展 | 语义单元 su_10 未被引用。选中图未生成 fuzzy 扩展调用，这与源要求相容；core 也未保留禁止把能力说明升级成执行要求的约束。 来源：inputs/010/references/workflow.md:3 |
| 整个流程禁止 index.delete | su_19 未被引用，选中图没有 delete 调用或 db_write；但没有禁止 index.delete 的独立core事实/检查。未生成删除行为不等于该禁止条件已被检测器验证。 来源：inputs/010/references/workflow.md:17 |
| 参数描述不要求调用前验证或归一化 | su_20 未被引用。选中图未添加验证/归一化步骤，但该负面要求没有成为可审计core约束；不会据此宣称源规范已完整覆盖。 来源：inputs/010/references/workflow.md:19 |
| 搜索后将 response.total 写入固定 count.txt | core 保留 index_search → write_count、response_total 输入、fs_write 及 literal count_file region。精确 total 字段和 count.txt 路径只在ID/证据文本中，core 未编码值相等或完整路径字面值；源未说明覆盖/追加语义。 来源：inputs/010/references/workflow.md:21 |
| 将 response.items 原样返回 | core 保留 response_items 输入到 return_items/stdout，源原句在sidecar；没有显式字段投影或 unchanged 等值关系。这支持结果流向的粗粒度解释，不能证明逐值原样返回。 来源：inputs/010/references/workflow.md:23 |

未被引用的显式行为约束包括fuzzy仅为能力说明（su_10）、禁止index.delete（su_19）、不要预验证/归一化（su_20）；其余未匹配单元包括标题、引用引导和配置父键。精确清单与逐fact行号见机器回执。

## 检测与推荐

builtin实际输出13个关系：11个label关系为空，2个辅助可达性关系覆盖4个调用节点。index_search仅归为action_call，detector输入不含命名参数、缺失值或API调用次数约束，故0告警只意味着当前行为图没有触发这些标签，不能称为13类安全检查或源规范全部通过。

推荐另用一次模型读取完整源文和0告警报告，基本忠于源流程：未建议fuzzy扩展、删除、预归一化或强加limit回退。它提出count.txt可能覆盖和缺limit依赖服务默认值两条注意事项；前者原文未定义覆盖/追加方式，后者服务实际默认上限未提供，因此都是条件性建议，不是已证实漏洞，也不计入detector findings。推荐不构成对optional语义的形式验证。

无独立gold，精确率、召回率和方法胜负保持未评估。历史SkillFlow的版本、CLI、继承与预算不同，只能作同源工程参照。

原始证据：comparison/010/finished.json、validations/check-001至004、transport/call-001至004、artifacts/synthesis_metadata.json、synthesized_facts.dl、detection_input.dl、synthesis_evidence_alignment.json、detection_result.json、recommendation.md。逐项SHA、公开用量、15项最终一致性核对和PID观察见 [010-analysis.json](010-analysis.json)。
