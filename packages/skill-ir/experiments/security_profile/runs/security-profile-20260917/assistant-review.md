# 30 例安全语义标注：助手逐例复核

这是助手复核，未由用户确认；原始模型标注、未决和执行状态保持不变。

30 例均已核查源文、实际 CFG 和已保存运行记录。其中只有 9 例存在经过严格校验接受的标注；
028、029 仅诊断未接受的完整原始候选，另外 19 例没有可接受标注，不能评价其标注语义。

[实施验收总报告](acceptance.md) · [机器可读复核](assistant-review.json) · [原始批次结果](experiment-result.json)

## 主要意见

- 执行者归属影响模型可见性，同类读取/提取操作的 runtime、tool、llm 分配存在证据不足和波动，不能用缺少观察标签证明模型不可见。
- 已明确记录 model_observe 的动作仍有漏记 sink 角色的情况；复合的修改/渲染操作也有只列 LLM 而遗漏工具参与的情况。
- 网络、文件和用户边界需要具体依据；工具名、delivery_path 或普通 return 本身不足以确定效果。
- 030 的观察理由混淆工具默认输出路径与 --stdout 输出正文；有 model_observe 不等于已看到文件正文，更不等于已完成传播判断。
- 028、029 的源文定位错误被严格拒收，分别发现 33、12 处错配；它们的其他语义观察只属于未接受候选诊断。
- 7 项模型未决保留原样。隐私声明没有被自动视为保护操作，脚本支持的多效果和部分网络双向效果得到了合理标注。

这些是方法诊断，不计算正确率，不把助手发现补写进模型 profiles 或 unresolved。

## 逐例结论

| 编号／样例 | 程序状态 | 助手结论 |
|---|---|---|
| [001 / N01](cases/001/assistant-review.md) | `complete` | 标注记录完整，但执行者归属、隐含模型观察和网络依据仍需复核；不能认定语义标注正确。 |
| [002 / N02](cases/002/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [003 / N03](cases/003/assistant-review.md) | `complete` | 标注记录完整，存在model_observe对应sink角色遗漏，以及执行者/网络效果依据不足。 |
| [004 / N04](cases/004/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [005 / N05](cases/005/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [006 / N06](cases/006/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [007 / Q01](cases/007/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [008 / Q02](cases/008/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [009 / Q03](cases/009/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [010 / Q04](cases/010/assistant-review.md) | `execution_error` | 执行失败，没有已接受或可诊断的部分标注；无法评价语义标注命中、遗漏或误标。 |
| [011 / Q05](cases/011/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [012 / Q06](cases/012/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [013 / F01](cases/013/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [014 / F02](cases/014/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [015 / F03](cases/015/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [016 / F04](cases/016/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [017 / F05](cases/017/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [018 / F06](cases/018/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [019 / D01](cases/019/assistant-review.md) | `execution_error` | 调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。 |
| [020 / D02](cases/020/assistant-review.md) | `complete` | 14条IR标注记录完整；关键脚本效果与回传路径边界表达合理，但有3处模型观察对应sink角色漏标，以及1处LLM执行者依据不足。不能把complete当成标注语义全部正确。 |
| [021 / D03](cases/021/assistant-review.md) | `execution_error` | 执行记录已复核；本次没有可接受标注，动作安全分类质量无法评价。 |
| [022 / D04](cases/022/assistant-review.md) | `complete` | 已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。 |
| [023 / D05](cases/023/assistant-review.md) | `complete` | 已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。 |
| [024 / D06](cases/024/assistant-review.md) | `complete` | 已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。 |
| [025 / R01](cases/025/assistant-review.md) | `incomplete` | 已逐条复核 45 条标注与 4 项未决。安装网络效果未决合理；复合动作执行主体有遗漏，最终交付的效果解释仍需补充。 |
| [026 / R02](cases/026/assistant-review.md) | `incomplete` | 已逐条复核 22 条标注及 2 项未决。网络效果未决与未知子命令相符；快照、捕获产物及 wrapper 返回处理未见明确相反证据。这不是通用正确性证明。 |
| [027 / R03](cases/027/assistant-review.md) | `execution_error` | 执行记录已复核；本次没有可接受标注，动作安全分类质量无法评价。 |
| [028 / R04](cases/028/assistant-review.md) | `invalid_response` | 完整原始响应因源文引文定位错误而被拒收，接受的 profiles 仍为 0。已逐条阅读未接受候选；以下额外语义观察仅作失败诊断，不作为已接受标注或正确率统计。 |
| [029 / R05](cases/029/assistant-review.md) | `invalid_response` | 完整原始响应因源文引文定位错误而被拒收，接受的 profiles 仍为 0。已逐条阅读未接受候选；以下额外语义观察仅作失败诊断，不作为已接受标注或正确率统计。 |
| [030 / R06](cases/030/assistant-review.md) | `incomplete` | 已逐条复核 22 条标注及 1 项未决。脚本读写、双向网络和编码有依据；正文与路径回传的观察边界需澄清，SDK 安装效果未决合理。 |

每例报告包含已阅读范围、具体 IR、原文/图/标注证据、未决边界与后续建议。

程序 complete 仅表示记录完整；助手复核也没有证明推断正确或运行行为。数据传播及综合安全判断仍未实施。
