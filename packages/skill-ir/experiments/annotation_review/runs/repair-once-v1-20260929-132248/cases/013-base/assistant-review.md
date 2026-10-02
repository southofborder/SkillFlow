# 013-base 助手复核

结论：来源整体与取值字段、首次／重试／回退的独立获取身份、body 原值、工具实参及四个终态的状态追加在本次事实中保持。初审没有提出问题，本次重点复核也未确认新的实质错转；不据此声称真实执行必然遵循全部关系。

本页是助手对实际新产物的独立复核，不是用户／人工确认，也不是语义正确性证明。没有执行 Skill，没有计算 DOE 结论。已只读加载并核验完整传播运行；DOE 中源文、CFG 与冻结基线逐字段一致，审计中的原标注与本次重建候选一致。

本例初审一次逻辑调用、一次 HTTP 尝试，无重试；请求 `deepseek-v4-flash`，实际返回名 `deepseek-flash`。合法响应为 `outcome=completed、findings=[]`，因此没有调用修复或复审，选用 `original`。这里的 original 是本轮有差异清单的显式实验重建候选，不是伪造的一次新版标注响应。

## 来源与模型可见版本

传播状态 `complete`，26/26 条 IR 形成记录，20 份 Data，动态诊断为空。零 API 重放为 `matched`，无差异。

- ir_001：读取用户请求整体 **D017** → 观察 D017 → select_part(source_id) 得 **D019**。公开 result_001 仅绑定 D019。
- ir_003：读取环境整体 **D013** → 观察 D013 → select_part(FAST_KEY) 得 **D012**。公开 result_002 仅绑定 D012。
- D017、D013 的 `parts_complete=false`，没有编造其它字段或把整体声称成只含已选字段。FAST_KEY 的父来源明确是环境，未重新生成无父容器的叶子来源。

这是源文 `SKILL.md:8 / src_003` 的来源／字段关系与统一运行时默认共同得到的静态结果。源文没有具体 getter 或隔离机制；不能从“可以用命令行读取指定字段”推导这里已经提供 local 例外。也不能反过来说真实智能体已被测得读过完整环境。

## 获取、参数与返回身份

| 路径 | 获取与实际参数 | 明确字段与 CFG return |
|---|---|---|
| 首次 fast.fetch | ir_007 receive → D003；参数 D019(source_id)、D012(FAST_KEY) | D003.body=D014；ir_020 return result_006，入口实际绑定 D014。 |
| fast.fetch 重试 | ir_011 receive → D018；仍为 D019、D012 | D018.body=D020；ir_022 return result_009，实际绑定 D020。 |
| archive.fetch | ir_015 receive → D009；**仅 D019** | D009.body=D005，ir_024 返回 D005；D009.error=D011，ir_026 返回 D011。 |

三份响应都有工具 `acquired_from` 和适用的请求 possible 依赖；首次与重试虽然使用同一工具及相同参数，仍保留两个不同 Data 身份。响应的来源没有被错误写成纯请求计算。

完整记录中共 **9 个编译观察阶段**：请求整体、环境整体、key 存在性检查输入、三个获取返回、三个响应分类／字段处理输入。获取返回观察均绑定各自响应，而非请求参数。整体可能被模型观察，没有使 archive 实参扩大为 key 或整个环境。

## 状态追加与普通 return

ir_019/021/023/025 分别追加首次 outcome D006、重试 outcome D007、archive outcome D015 至 status.txt。旧文件 D016 与追加值形成新的结果；追加内容本身仅为该状态值。四条 return 的身份在 CFG 中保留，空 events 不表示返回丢失，也没有添加用户输出或新 public output。

源文的暂态重试、无 key 回退、非暂态失败回退、成功停止及 archive 最多一次由 CFG 控制与约束承载。工作队列采用保守 may 分析，不能把所有分支结果说成同一次执行中全部发生。

## 解释边界

- body 原文明确要求原值，当前使用 select_part；outcome 是分类计算，使用 compute(derived)。两者没有合并成 opaque 依赖。
- “return its error”支持错误内容的返回，CFG 也有 archive_fetch_error 输出；当前 `["error"]` 是逻辑部分表示，未验证真实工具的物理 JSON 形状。不能仅因缺少接口 Schema 判它必然错转，也不能因此机械改成 compute 并丢掉错误内容身份。
- 状态对响应、响应对请求的依赖不能推导 FAST_KEY 明文写入 status.txt。与此同时，本轮没有敏感性判断和脱敏证明，不能宣称所有可能间接影响均不敏感。
- 未知源码或缺少真实运行细节没有被转成泛化未决或额外隔离步骤；可计算的可能关系仍在事实里。

[初审](refinement/initial-review/report.html) · [传播页](propagation/report.html) · [DOE 原始事实](propagation/doe-input.json) · [零 API 重放](propagation/replay/summary.json)
