# google-search 静态审计结果

原始 Skill 共两个文件，合计 2,045 字节。这次从原包得到的 CFG 有 50 个基本块、84 条 IR、59 条控制边。每个基本块都有一条终结指令，因此 84 条中有 35 条分派和 15 条返回，余下 34 条表示读取、计算、调用或交付等操作。18 处分派分别标出了正常和异常去向。[原始 Skill 包](google-search.zip) · [自动生成的 CFG 和逐条标注](supplement-results/index.html)

## 最终选图和两次本地核验

组会图从完整 CFG 中选出两个入口、Google 请求和 CLI 错误分支，标出前向字段来源与反向任务需求。图中节点可以点开查看原始 IR。[英文组会示意图](revalidated-results/meeting-example.svg)

| 使用的材料 | 前向传播 | DOE 结果 |
| --- | --- | --- |
| 线上最终选中的标注，有 82 条 IR 具备处理语义 | 61 条已处理，1 条使用占位语义，1 条未建模，21 条受阻 | DOE 在核对一条缺少执行记录的异常分派时抛出异常。该轮未生成比较结果。[线上原始结果](supplement-results/index.html) |
| 保留完全相同的标注、前向记录和复审依据，只修复 DOE 校验 | 沿用上述 62 条前向记录 | 完成 8 项比较，全部来自独立函数的 Google 请求。CLI 请求和错误打印仍受阻。[正式 DOE 报告](selected-propagation-doe/report.html) |
| 在同一张图上恢复经源码核实的本地函数实参绑定 | 79 条已处理，1 条使用占位语义，1 条未建模，3 条受阻；两个入口均到达 Google | 完成 20 项比较，182 项输入评估。保留了其余 82 条已选标注和 10 项源码证据缺口。这份更新的标注没有经过新的模型复审。[完整标注图与逐条证据](revalidated-results/index.html) · [DOE 原始结果](revalidated-results/doe.json) |

两次本地核验均未调用模型。恢复的 `ir_045` 使用模型原先提交的处理记录，程序核对了源码中的被调用函数、进入函数体的控制边，以及四个实参到四个形参的逐项对应。原先的校验在这处本地传参要求额外提供一次外部调用的证据，阻断了 CLI 路径。[该条 IR](revalidated-results/annotations.html#ir-ir_045) · [来源与校验记录](revalidated-results/receipt.json)

两处修复合入后，在同一次定向验证中通过了 90 项测试，覆盖调用绑定、异常分派、传播记录回读及反向需求。原始线上记录和最初选中的图均已保留。[合并后的测试记录](post-recovery-integration.xml)

### 密钥的两个去向

- **Google 请求。** CLI 的 `GOOGLE_API_KEY` 从 `ir_034` 读取，经本地调用进入 `ir_049` 的 `params.key`。独立函数从 `ir_067` 接收调用方传入的 `api_key`，在 `ir_076` 交付给同一 Google 接口。每处请求都区分发送前失败与发送后失败。任务 R9 明确列出请求参数；反向需求在 GET 处覆盖整个请求，并可回溯到各自的密钥来源。此次分析没有单独证明 `key` 是 GET 的最小必要字段集。[两个入口的字段、版本与任务依据](revalidated-results/boundary-comparisons.json)
- **CLI 错误输出。** 五处受保护操作抛出的异常在 `ir_060–061` 汇合并匹配 `except Exception`。任务 R12 对应错误输出和退出行为。`ir_063` 包含异常转字符串、格式化及打印；最终选中的处理标注没有表示前一步失败时哪些后续值仍可用。此处没有已计算的打印载荷，无法证实密钥进入错误文本，也没有删减建议。复审前的自动标注可在格式化成功的条件下走到打印；它同样没有建立错误文本携带密钥的证据。[最终错误输出节点](revalidated-results/annotations.html#ir-ir_063) · [复审前标注对照](revalidated-results/initial-control/index.html)

20 项比较中，8 项对应两个入口的 `params.key`，8 项对应 `params.cx`，4 项对应正常结果输出中的潜在敏感内容。比较按字段、数据版本和交付位置计数。这些记录均为 `no_excess_established`，没有生成缩减建议。[全部比较记录](revalidated-results/doe.json)

首次线上运行发起 7 次模型调用，记录 195,270 个 token。经授权的下游补跑发起 9 次，记录 513,536 个 token。合计 16 次调用、708,806 个 token。两轮均对发行包进行静态审计，没有执行 Skill 或向 Google 发送请求。

## 首次线上运行

这次线上运行从原始发行包的 `SKILL.md`（946 字节）和 `scripts/search.py`（1,099 字节）重新开始。模型自动生成的第一份 CFG 有 50 个基本块、84 条 IR 和 59 条控制边。线上校验误拒了其中已有的异常类型判断，纠正与复审均未恢复该图，后续标注、传播、DOE 未执行。因此本轮的线上比较数和删减数都记为未运行。7 次模型调用共记录 195,270 个 token，首次原生调用开始至最后一次结束约 9 分 5 秒。[线上结果](online-results/index.html) · [边界核对](boundary-verification.json)

## 从原始回答核对修复

初次回答已经把五处抛出的异常送入同一个判断。匹配 `except Exception` 时，CLI 进入错误处理；不匹配时，CLI 将同一异常向外抛出。校验器误以为还需插入一道判断，并把纠正限制在异常合并指令的输入列表。该范围无法表达它要求的控制结构变更。

修复后的前端根据源码验证已有判断，保留两个后继。独立函数已显式判断可选参数是否传入时，前端保留原始实参，在省略分支取默认值 5。相同原始模型回答现已在离线环境通过编译和 CFG 回读，18 处分派都保留正常与异常去向。图中标出了程序从源码恢复的六条处理关系。其他位置的线上标注和任务绑定均未产生。[84 条 IR 完整结构图](online-draft/annotated-cfg.svg) · [原始回答与逐块查看](online-draft/index.html) · [复验记录](recompiled-online-graph-verification.json)

## 两个入口与错误输出

另用上一轮原始 75 条 IR 进行工程回归。19 处受保护操作通过现有纠正接口绑定去向，新增两条 IR 表达异常匹配，共 77 条。此图使用按源码编写的测试标注，覆盖了真实编译、前向传播、反向分析和 DOE 入口。四组离线输入合计到达全部 19 处分派。[完整标注图](offline-demonstration/annotated-cfg.svg) · [逐条标注与记录](offline-demonstration/annotations.html)

| 离线边界 | 已核对的事实 |
| --- | --- |
| 独立函数 GET（`ir_020`） | Google 接收的请求参数 `key` 来自该次调用的 `api_key` 实参。前向版本与该边界上任务 R9 对 `key` 的需求对应。 |
| CLI GET（`ir_057`） | 同一接收方收到的 `key` 来自 CLI 读取的 `GOOGLE_API_KEY`，对应另一份请求载荷和密钥版本。 |
| CLI 错误输出（`ir_071`） | 匹配分支可到达错误打印。源码要求报告异常消息，当前证据无法确定该消息包含密钥，因此无法据此提出删减。 |

在配好凭据且省略数量的场景中，67 条 IR 已处理，1 条使用占位语义，9 条在该场景不可行。离线 DOE 对敏感数据执行了 7 项比较，其中 4 项核对两个入口正常发送和发送后失败路径的密钥，全部比较均未建立可删减的过量暴露。[离线 DOE 明细](offline-demonstration/doe.html) · [分支、版本和任务依据](offline-acceptance.json)

首次图修复通过 250 项定向测试，覆盖正常返回假值、异常类型匹配与外抛、显式空值与省略参数，以及前向记录回读和反向分析的一致性。本地实参绑定修复另通过包含异常分派、调用点和反向需求在内的 110 项定向测试。[主要测试记录](acceptance-tests.xml) · [显式控制结构回归](explicit-controls.xml) · [本地调用与传播回归](final-handoff-suite.xml)
