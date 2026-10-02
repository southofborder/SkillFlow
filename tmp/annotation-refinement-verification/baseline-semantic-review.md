# 本轮三个原候选的独立语义复核准备

范围：只读 `run-path.txt` 指向运行的 `upstream/candidates-v1.json` 与 001/010/013-verified.json 中的源文、实际 CFG 和原始候选。没有读取真实新审查结论作为判断依据，没有 API，没有修改候选。此笔记是助手复核，不是用户确认；不预设三个 base 为零问题标准答案。

## 001：筛选、同一元素字段原值、观察与发送范围

明确事实：`SKILL.md:8–16 / src_003` 要求文件每条记录含七个字段；筛选为 `not opted_out AND (urgent OR value>=100)`，urgent 不能覆盖 opted_out；逐条发送 recipient 和 summary 原值；不发送 access_token；不做摘要改写；写处理条数。

现候选保留的关系：

- ir_001 对 loc_events_json 做 read，来源为整体，处理模式 default；不是只登记 summary 来源。
- ir_003 用 filter_items 且保存完整谓词。被选中元素内容不重建，保持原集合成员关系。
- ir_005 用 for_each(input[1], item=record)；同一 record 的 recipient 与 summary 分别 select_part，deliver 参数依次为 recipient_value、summary_value，没有整个 record 或 access_token 作为实际参数。
- ir_007 count 使用 compute(derived)；这是真实计算，不能因为保留 derived 依赖就把整个记录明文当成 count 内容。
- ir_009 write replace 仅使用计数 result，写入 count.txt；空 return ir_010 没有返回内容。
- 所有处理段均 default。原 profile 中“本地/未提及模型”措辞并未形成 local 隔离，编译应仍观察文件整体、筛选输入、逐元素字段准备输入和计数输入。不得机械改为 model，也不得要求 operator 一定包含 llm 才允许默认观察。

实质问题判据：若修复把筛选改回 compute，拆散逐元素配对，将 summary 字段变为新摘要，把正文改为整个 record，或用未经源文支持的 local/清洗来满足 access_token 禁止，应认定真实关系退化。反过来，先前整体可能被模型观察，不代表 notify.send 实际接收整体。

需谨慎的推断：候选将 notify.send 分类为 net_send/remote，证据支持“向接收对象发送”，但没有具体网络机制、地址或实测传输。不能凭工具名证明网络协议；也不能只因没给 URL 就自动认定通信关系错误。当前可把网络分类作为解释边界单独指出，不预设为必须修复的基线缺陷。候选将处理条数解释为选中记录数，与当前 CFG 输入一致；是否源文另指所有扫描条数是上游源文核对问题，不能在本轮修复中悄悄换 CFG 语义。

## 010：工具新来源、可选参数与普通 return

源文证据：workflow.md:5 / src_007 读取请求；:7 / src_008 要求只调用一次并原样传 term；:9–13 / src_009 与 query.yaml / src_004 定义缺失可选参数应省略；:19 / src_012 明确格式说明不是预校验或归一化；:21 / src_013 写 response.total；:23 / src_014 原样返回 response.items。

现候选保留的关系：

- ir_001 从 request.json 整体 read/default，后续 term、from_date、limit 使用 select_part。
- ir_004/005 另用 compute(derived) 记录字段存在性；与字段值身份分开，没有把存在性布尔量当作字段值。
- ir_007 是 receive(tool: index.search)，输入操作数为 [1,2,4]，即 term/from_date/limit；[3,5] 的存在性控制量不是实际请求内容。返回 search_response 有外部工具获取来源及请求影响，不能改成只依赖请求的 compute。
- 返回值编译观察应绑定 search_response，不是用请求值替代响应内容。
- ir_009/011 分别 select_part response.total / response.items；ir_010 写 total；ir_012 CFG return 输入是 result_009=response_items，outputs 为空。
- 源文没有网络机制，null-effect receive/tool 是当前契约明确支持的关系；不能为了“补全安全效果”猜 net_send/net_receive。

普通 return 误报排除：ir_012 的 transfer events 和 output_bindings 都为空合法。profile 中“转发在 transfer_specs 按输入操作数保留”这一理由措辞不准确，但返回身份实际由 CFG 输入承担；不能据此说 facts 缺少返回，不能添加不存在的 output[0]、user_output、null-effect deliver 或与 CFG 矛盾的额外结果。仍需核查 CFG return 引用的是 items，而非 total/whole response；目前它是 items。

需谨慎的推断：可选参数的存在条件保存在 CFG 约束与原文，规格记录可能参数值，未完整编码逐参数条件。不能把 may 候选列表说成每条执行必然同时传所有参数；也不能删除 from_date/limit 来假装保证省略。存在性计算只保存输入依赖，不执行谓词，因此不能宣称已证明每个动态请求都正确省略；这是当前条件精度边界。scope、字段原值和外部来源仍应准确，不能因此把它们一并降为 opaque。

## 013：来源整体、调用身份、body 原值和终态追加

源文：`SKILL.md:8–16 / src_003`。从用户请求读 source_id，从环境读 FAST_KEY；有 key 才 fast.fetch；仅首次暂态失败重试一次；非暂态首次失败/重试失败/无 key 走 archive；archive 只传 source_id；成功原样返回对应 body 且停止获取；archive 失败返回其 error；禁传 key 给 archive 与诊断；每个终态先追加最终状态。

现候选保留的关系：

- ir_001 read 用户请求整体后 select source_id；ir_003 read 环境整体后 select FAST_KEY。局部变量保留容器与字段关系，公开输出仅字段，未把 environment 输入误绑为仅 FAST_KEY 来源。
- 两段 default，编译应观察取得的整体版本，然后保留明确字段选取。source 没有显式 getter/本地隔离机制，不可凭“可以用 getenv/grep”改成 local。这里的整体可能观察是契约补充，不是实际运行必然发生。
- ir_007/011 分别 receive 首次/重试 fast 响应，实际请求都是 source_id+FAST_KEY；ir_015 receive archive 响应且只有 source_id。即使 source_id/FAST_KEY 来源容器被观察，不意味着容器全部内容被发送给工具。
- ir_009/013/017 的 outcome 是 compute(derived)，body 是 select_part([body])。必须分别保留计算与已有部分关系。首次、重试、archive 的 body 不能混绑。
- ir_019/021/023/025 以 append 模式写 status.txt，输入是各自 outcome；不能改为覆盖、漏掉失败出口、写整个响应或写 key。
- CFG ir_020/022/024/026 分别 return result_006/result_009/result_012/result_013。普通 return 空规格合法，控制分支及重试次数由 CFG 承载，不在传递规格再补调用或控制循环。

error 路径边界：原文确有 “return its error”，CFG 有 archive_fetch_error 输出；候选 select_part(response,[error]) 保留错误作为已返回内容的逻辑部分，尚未说明真实工具物理 JSON 形状。仅凭源文没写 JSON 键结构不足以将其直接判为错转；若有接口证据表明错误其实是整个响应、异常通道或其它结构才形成实质矛盾。也不能机械改成 compute(possible) 后把原样错误内容关系抹去。报告应标为逻辑表示及接口精度边界，不能说已经验证物理字段。

## 后续真实输出核对清单

1. 初审是否区分“已经有依据的问题”和仅措辞/实现未知；普通 return 同类误报是否消失。
2. local 变体修复是否恢复 default/广来源观察，而非仅修改说明或伪造 getter。
3. field 变体是否恢复具体 response.body 部分与原值绑定；原本 status compute 保持。
4. source 变体是否恢复 receive/tool 和新获取来源；不是并排加两个同名输出、变成网络或丢请求实参。
5. version 变体是否将 deliver 的第二实参恢复 summary_value，recipient 配对仍在同一 scope；不删除整体模型观察来掩盖错误。
6. 修复合法/复审通过并不自动等于缺陷修好；要比较实际 raw spec、编译观察及必要传播关系，同时检查新问题。
7. 一轮失败或 cannot_assess 是任务失败；不能在方法报告里计为命中、漏报或已修好。
