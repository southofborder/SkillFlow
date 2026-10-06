# 010 / Q04 助手复核

本文件是助手对本轮冻结产物的只读语义复核，不是人工确认，也不是新的模型标注或 DOE 判定。复核对象为本目录 `propagation/doe-input.json`、`propagation/audit/annotation.json`、`propagation/audit/material.json` 的执行模型，以及源包三份文件和完整 CFG。仅新增本文件；未修改 CFG、模型响应、传播结果或历史产物，未执行 Skill，未调用远程模型。

**结论：可选参数省略、原值流转、每条路径一次搜索、total/items 对应关系基本符合源文；未知 request 与 response 整体没有被收窄为已列字段。但搜索响应的新增来源没有进入 Data 来源链，最终 return 被确定为直接向用户输出也超出了当前证据。这两点连同现有五项未决，必须进入下一阶段 DOE 的解释边界。** 标注状态是 `incomplete`，传播状态是 `complete`；后者只表明 18 条 IR 已完成符号传播，不能解除前者的未决。

## 源文与 CFG 核对

主文件包含 `SKILL.md`、`query.yaml`、`references/workflow.md` 的完整源文；逐文件内容和 SHA-256 与审计材料一致，主文件 CFG 与审计材料 CFG 一致。`references/workflow.md:5–23` 及 `query.yaml:1–3` 的关键要求均可在现有 CFG 找到：

- `ir_001` 读取用户提供的 `request.json`，取得 term、可选字段及其存在标志。`ir_002` 按 from_date/limit 是否存在分为四条互斥路径，分别进入 `ir_003/005/007/009`。每条完整路径只有一次 `index.search`；四条搜索记录不是一次实际运行发出四个请求。
- 四种调用的内容参数依次为 `(term, from_date, limit)`、`(term, from_date)`、`(term, limit)`、`(term)`。缺失参数在调用操作数及传播计算输入中均被省略，未换成 `null`、空字符串或默认值。资源操作数 `index.search` 是边界名称，没有被当作请求内容。
- `term` 使用 D012，存在时 `from_date` 使用 D009、`limit` 使用 D016，均为 `ir_001` 明确选出的原字段。未发现额外的验证、规范化、日期改写、模糊展开或 `index.delete`。格式说明和禁用声明没有被伪装为实际过滤操作。
- 搜索之后，各路径写 total 到本地 `count.txt`，再原样返回同一响应的 items；未发现 total/items 对调或跨分支串接。当前未发现需要优先归因于源 CFG 的结构性错误。工具是否远程、最终返回是否直达用户，属于源文未说明的执行边界，不由 CFG 名称补足。

## 对 DOE 有实质影响的标注边界

**1. 搜索响应保留为未知整体，但来源链只有请求依赖，缺少可追溯的工具结果来源。**

`ir_003/005/007/009` 的 `source` 角色依据明确说工具返回搜索内容；实际传递规格却只有 `compute(请求字段) → search_response`、选取 total/items、向模型交付完整 response。对应的响应整体是 D017、D004、D002、D007，全部 `origin.acquired_from=null`，来源仅记录相应请求字段，依赖关系为 `derived`；这四条记录没有从 `index.search` 获取结果的 `read/receive` 事件或来源端点。初始数据只有 D014（`storage:request.json`）。

这不证明响应只由请求字节组成，也不证明检索没有带入新内容。被查询索引及工具结果的新内容来源尚未表达为可追溯 Data 来源。四个 response 都是 `known_parts` 且 `parts_complete=false`，因此结果本身仍保留 total/items 以外的未知部分，这是正确的保守范围；若下一阶段只沿请求来源链寻找候选数据，就可能漏掉响应中来自检索的数据。应保留“工具返回的未知整体及其来源尚未完整建模”的解释，不能把请求依赖当作完整来源清单，更不能凭空补成远程接收。这里是联合标注/来源表达的缺口；传播按已给规格产出依赖，未发现传播器自行删去一个已标注的结果来源。

`derived` 表示支持的依赖，也不意味着输入明文完整保留。实际 `possible` 依赖在 D011（from_date 存在标志）及 D005（limit 存在标志）上：它们依赖 D014，不能据此说布尔标志包含整个 request 明文。

**2. items 的返回范围正确，但直接向用户输出的接收方被过早确定。**

`ir_012/014/016/018` 分别原样交付 D010/D006/D008/D015，符合源文 `src_014` 的 “Return the search response's items value unchanged.”。然而标注将效果确定为 `user_output`，目标确定为 `loc_user={kind:user,name:user}`。其证据理由是“调用方或用户”，完整源文和 CFG 没有进一步证明这次 return 直接显示或提供给用户。固定词汇将 `user_output` 定义为直接向用户提供，EM06 与提示也明确普通 return 不自动证明 user-facing。

因此，可以确认 items 是工作流返回值；“终端用户直接可见”仍是额外推断。下一阶段不应只因当前 `loc_user` 就把这层接收方身份当成已确认事实。此问题不影响返回的内容身份或 total/items 绑定；归因是标注推断边界，当前原始 unresolved 中未列出此项，本复核也没有篡改它。

**3. 现有五项未决仍限制观察与外发结论，不是单纯效果顺序不确定。**

- `ir_001.effects`：已确认文件读取与字段处理，D014 是否进入 LLM 上下文未决。EM01 支持读取相关完整容器，EM03 不允许由 LLM 发起/调度读取就推导 `model_observe`。既不能认定模型看到了 D014，也不能因当前 events 没有 model_observe 就认定它不可见。
- `ir_003/005/007/009.effects`：网络发送/接收属性未决。工具名不能证明远程通信。当前没有 net_send/net_receive 或 remote 位置，不能读作“已证实无外发”；反过来也不能把搜索工具参数自动记为互联网外发。
- 这四条搜索的模型观察有独立依据：EM02 的工具返回默认进入模型上下文假设。交付的是 D017/D004/D002/D007 完整响应，包含未知剩余部分，而不是只交付 total/items；这符合当前执行模型，依据来自返回路径，不是 `operator` 含 llm 或模型参与调度。没有明示本地隔离、只返回句柄或清洗前置证据可缩小该观察范围。

## 已核准的范围与传播近似

D014 最初是 opaque 文件整体；显式 `select_part` 使其识别 term/from_date/limit，但 `parts_complete=false` 保留其余未知内容。字段需求没有使最初读取范围只剩这三个字段，也没有据此扩大成读取整个运行环境。只在有明确选择的参数使用处和输出字段使用处缩小内容范围，理由充分。

下表中的响应整体、total 和 items 都是独立内容身份。total 的 write 与 items 的 deliver 直接使用相应身份，没有再计算、摘要或清洗；items 的内部字段与条目未知，不能替它补出字段清单或敏感性结论。

| 可选参数路径 | 搜索 IR / 实际内容参数 | 响应整体 | total → count.txt | items → 返回 |
|---|---|---|---|---|
| 两者存在 | ir_003 / D012、D009、D016 | D017 | D003，经 ir_011 | D010，经 ir_012 |
| 仅 from_date | ir_005 / D012、D009 | D004 | D018，经 ir_013 | D006，经 ir_014 |
| 仅 limit | ir_007 / D012、D016 | D002 | D001，经 ir_015 | D008，经 ir_016 |
| 两者缺失 | ir_009 / D012 | D007 | D013，经 ir_017 | D015，经 ir_018 |

`ir_001` 无条件声明可选字段符号，传播后的各分支入口都仍携带 D009/D016；当前没有实际 request 值，也没有用存在标志消除所有符号候选。这是静态路径近似，不能解释为缺失字段实际存在或被发送。判断参数是否使用，应看各分支搜索的实际 inputs；该处确实省略了缺失参数。D011/D005 没有用于净化数据，也没有替代任何原字段。

四个响应及后续写入/返回属于条件候选，不是同时发生的内容集合。`count.txt` 的四次 strong write 分别位于互斥路径；本例并未出现四条路径合流后把它们当作一个确定值的问题。程序通过结构和引文校验，只能支持这些记录可被解释及引用存在；无法证明上述来源或接收方推断正确。

## Data 定位表

下列 D 编号沿用本轮传播报告的短名，完整 ID 可直接在 `propagation/doe-input.json` 查找。

| 短名 | 内容身份 | 完整 Data ID |
|---|---|---|
| D014 | request.json 未知整体 | `data_9c9c8f7c46b4ec216135731d4003e326ec445917b369146b45fd478adb13c59e` |
| D012 | request.term 原值 | `data_95e56c38a88a77a39b2f3df41e69cbae222bdc61045971e2887f269fc24a4c21` |
| D009 | request.from_date 候选原值 | `data_62c06c44f28ee594441cfd805519eda7daa3a7894913e94ff9d595898dfde87d` |
| D016 | request.limit 候选原值 | `data_b0a2bba101493466cf17cd9896a33744a42cc53b4e68168e169c9d62f5c6e418` |
| D011 | from_date 存在标志 | `data_7df6a45755e5fc42ddf027614e7e52e43d3aaefaf60a05f8c6bf510e5a5d4c26` |
| D005 | limit 存在标志 | `data_3ed9e5af62ce54004ad623b152a65d44a76869f7ed5ae530d894b0d1d898b06b` |
| D017 | ir_003 响应整体 | `data_d7f75409cfb212dd3daf3f33a08e49447b1ce05985d6e83423d7cb7c9390fa01` |
| D003 | ir_003 响应 total | `data_26157b7b4b467efc117f0d8402bc282d8c5fdd3a7275ec973f7d6bb9cf7eb7d7` |
| D010 | ir_003 响应 items | `data_7b9c53fc5cc25b6c09b534982f77b2122fef0e02e3a930b78a805d4f449d19da` |
| D004 | ir_005 响应整体 | `data_3482304f01e661f48598f6274ec6ef83afb5a0daa0b31fa9d04cf3c46455f975` |
| D018 | ir_005 响应 total | `data_f1a1c5ab9763a3494915f8df01718ca09a203e35899cec11b1e5e359c6f46f40` |
| D006 | ir_005 响应 items | `data_4ac38378dd42296724970198fda552a08241b7521f38f0d9cf8dc1a7374ad326` |
| D002 | ir_007 响应整体 | `data_24c9ed3679406222d320368fb6975c894175976cbf82818630572205dac6fc80` |
| D001 | ir_007 响应 total | `data_22c449dd17a3149d9305d52b16c99b23efd82c050191019f70546e1fe87a6771` |
| D008 | ir_007 响应 items | `data_58d2329547a795e880dd6d78cdbb47fa91f03f60f423feec899ecaa89207a72b` |
| D007 | ir_009 响应整体 | `data_520ebc7705c72f97c4e62bcb0afdbd5db8a44aab4a33a1f6436c4823682cd820` |
| D013 | ir_009 响应 total | `data_97081ab0e58d9fdb1960e5e178e4c43b97c98909dd8f40220a6d24cc725db10f` |
| D015 | ir_009 响应 items | `data_a9b762f6b9969ba6db70215a9338fbdf3c43f00237b55fd73654cf9e6bc1e766` |

本轮没有具体 request/response 实例，Data 的敏感性标注为空也不表示不敏感。下一阶段可以使用这里已验证的字段流转与条件路径，但必须保留响应的未知整体、来源建模缺口、文件模型可见性与搜索网络未决，并区分“返回值”与“直接用户输出”的证据强度。
