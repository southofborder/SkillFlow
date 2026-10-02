# 来源范围、工具返回与模型观察：三例实施与复核结果

工程与离线恢复已完成；方法尚未验收通过。尤其 013 仍无依据地把环境读取收窄为单个 FAST_KEY，不能说本轮已解决该核心问题。

本报告为助手事后复核，不是人工确认。模型原始判断、未决项及传播事实均未改写；本轮不作 DOE、风险或必要性判断。

## 1. 工程改动与运行

- CFG 提取与源文核对区分逻辑来源入口、目标字段与结果绑定；原 IR 字段保持。
- 联合标注和执行模型明确整体读取／局部机制、模型观察、选取与实际参数。
- 工具内容获取允许 receive + tool + 无标签事件，不以网络确定性作为获取前提；仍保留实际输入和 possible 依赖。
- 种子、输入解析和循环依赖共用位置解析；未使用的位置不自动生成 Data，未知内容不自动扩大地址别名。
- 版本为联合标注/执行模型 v6、解释契约 v3、传播记录 v5、DOE 输入 v2、传播运行 v4；Data v3 保持。

实际 14 次逻辑调用（上限 63），其中 3 次联合标注；15 次 HTTP 尝试，只有 001 的一次传输重试。没有质量择优重跑。请求 deepseek-v4-flash，全部实际返回名为 deepseek-flash。

| 样例 | 核对/标注 | 原传播保存 | 恢复后传播 | IR / Data | 逻辑 / HTTP |
|---|---|---|---|---:|---:|
| 001/N01 | audit_passed / complete | execution_error | complete | 10 / 4 | 8 / 9 |
| 010/Q04 | audit_passed / complete | complete | complete | 12 / 9 | 3 / 3 |
| 013/F01 | audit_passed / complete | complete | complete | 26 / 19 | 3 / 3 |

## 2. 逐例方法结果

三例原始 unresolved 与 diagnostics 均为空；以下问题由助手复核另行指出，未伪装成模型已经报告的未决。

### 001/N01：整体观察已补上，字段交付仍不够精确

**已补上的关系：**events.json 整体先被读取并进入模型观察；未臆造密钥清洗。

**仍存在的问题：**逐记录 summary 和 recipient 的关联退化为 opaque 派生及符号边界；处理条数的修复还存在解释歧义。

- 来源：用户提供的 events.json 文件整体。
- 读取：整体 opaque，没有缩到 summary。
- 观察：原始文件整体进入模型上下文。
- 取值：筛选与 summary 取值被概括为不透明派生，缺少明确部分关系。
- 交付：派生载荷交付动态 recipient 边界；不能据此证明只含 summary，也不能断言 access_token 已外发。

[传播审查](cases/001/propagation/report.html) · [唯一 DOE 业务文件](cases/001/propagation/doe-input.json) · [完整助手意见](../cases/001/assistant-review.md) · [选定 CFG](../cases/001/selected-analysis.json)

### 010/Q04：工具新来源已补上，可选参数关系出现退步

**已补上的关系：**request.json 整体观察；index.search 返回来自 tool 边界，并被整体观察。

**仍存在的问题：**核对器接受了未定义的可选参数机制，receive 输入包含值和存在标记；普通 return 又被过度标为 user_output。

- 来源：request.json；另外从 tool:index.search 获取新响应。
- 读取：请求整体保留未知剩余。
- 观察：完整请求与完整工具响应。
- 取值：term/from_date/limit、响应 total/items 有部分关系；缺参省略却没有落实。
- 交付：获取记录包含五项值/标记，不等于已证实五项网络发送；直接用户输出的依据不足。

[传播审查](cases/010/propagation/report.html) · [唯一 DOE 业务文件](cases/010/propagation/doe-input.json) · [完整助手意见](../cases/010/assistant-review.md) · [选定 CFG](../cases/010/selected-analysis.json)

### 013/F01：环境范围仍被错误收窄，本轮核心方法目标未达成

**已补上的关系：**CFG 保留 user_request 与 environment；请求整体观察、source_id 选取和三个工具返回新来源成立。

**仍存在的问题：**标注无依据假设“显式 key-only getter”，只读 environment.FAST_KEY；环境整体 Data 与观察仍缺失。

- 来源：图中有 environment，但标注实际只读取 environment.FAST_KEY。
- 读取：请求整体正确；环境整体没有进入 Data。
- 观察：请求和三个工具响应被观察；环境整体及取得的密钥均没有对应观察记录。
- 取值：source_id 使用 select_part；FAST_KEY 变成无父容器的叶子；body/error 仍是 opaque 派生。
- 交付：fast 使用 source_id+key，archive 仅 source_id；返回身份、重试和状态追加保留，普通返回的 user_output 推断仍过强。

[传播审查](cases/013/propagation/report.html) · [唯一 DOE 业务文件](cases/013/propagation/doe-input.json) · [完整助手意见](../cases/013/assistant-review.md) · [选定 CFG](../cases/013/selected-analysis.json)

## 3. 报告保存错误及可信离线恢复

001 原保存发生 TypeError：合法 literal 带 identifier:null，旧报告代码按 identifier 键存在与否显示，尝试拼接 None。现改为按 operand.type 选择 JSON 字面值。这是展示错误；原 001 没有提交 manifest，仍保留原失败状态。

先在原源码身份下重新解析、核对并离线重放 feedback/annotation，保存材料捕获回执；只修改 propagation/report.py 后，再用原接受响应在此新目录求解和保存。恢复保留原调用、原模型名、用量和原 manifest，另记新实现摘要。源码变化白名单和实际业务完全一致检查均通过。

三例恢复均为零模型调用、零网络尝试；旧新 DOE 逐字段相等，独立加载、完整运行加载及新身份离线重放均通过。原结果未被补写成成功，也没有迁移旧版本。

[原始运行总览](../index.html) · [原始运行核验（保留 001 未提交失败）](../verification/original-run-check.json) · [恢复验证汇总](verification/final-checks.json)

## 4. 验证与保证边界

- 修改前完整离线回归：1949 passed；报告修复后的相关回归：1236 passed，包含新增的字面量保存与恢复测试。这两组存在重叠，不相加声称独立测试数。
- Lean 构建及公理审计通过，原结构/受控文本证明未修改；依赖仅为既有标准 propext、Quot.sound、Classical.choice。
- 9315 个受保护历史/输入文件摘要不变；未发现凭据模式；调用预算满足。
- HTML/Markdown 与共用渲染器一致，锚点及业务文件引用有效。未进行像素级浏览器视觉核验。
- 当前 Prompt 不保证模型遵守所有规则；真实引文校验也不能证明模型从引文作出的推断正确。

**本轮结论：**工具返回来源和部分整体观察得到补充，工程可复核；方法上仍不能宣称来源范围完整或接收边界准确。013 的错误例外推断是下一轮必须优先处理的通用问题，不能以节点/字段名补丁消除。001 的集合字段关系、010 的条件参数、普通 return 的接收边界也必须保留为未解决事项。
