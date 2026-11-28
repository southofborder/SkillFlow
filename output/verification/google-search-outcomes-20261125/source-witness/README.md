# Google Search 源码切片离线集成证据

**这是人工提供 CFG、标注和 Task 对应关系的离线集成 witness，不是完整自主在线审计结果。** 本目录独立于在线/历史运行。没有模型调用、HTTP 请求、Skill 执行或历史重放；没有修改生产源码、原始包或任何运行产物。

两文件源码逐字节复制自本次 `document-guided-google-search-outcomes-high-20261125-190529` 的原始包。真实提取的完整 Task 保留不变：R10 要求请求参数分别保持 `q/key/cx/num` 的角色；R11 要求先检查状态再解析；R13 要求输出 `Error: ` 加异常的字符串并退出 1。物理证据来自 `scripts/search.py` 第 6–16、23–28、34–39 行。`source-integrity.json` 给出原始来源与摘要。

切片假设 CLI/env 已校验、结果数省略而采用默认值 5，以及 `requests.get` 已正常返回。随后真实源码第 15 行的 `raise_for_status()` 可正常返回，也可抛出异常；后者经第 37–39 行到达格式化、stdout 和退出。GET 的 transport 异常、JSON 解析、成功输出和其他初始化行为在切片之外；完整 Task 仍保留，其余义务记录范围缺口。

`run_witness.py` 调用当前公共入口 `checked_task`、`prepare_material`、`compile_flat_response`、`propagate`、`materials_from_result` 和 `prepare_joint_sensitivity_review`。前向记录又经 `records.validate()` 校验；反向/DOE 的公开准备入口会核验其结果结构与引用。

结果见 `summary.json`：

- 前向 complete，11 条 IR 全部 processed。状态检查产生两个独立 outcome；正常分支没有异常结果，异常分支的真实异常占位是 opaque，并可到达 stdout。
- 请求 `params.key` 是模拟公开输入 `DEMO_API_KEY_NOT_A_SECRET` 的原始 env 数据身份；在真实 Google 请求边界被追踪为 `key` 字段的 direct 暴露。R10 为该实际输入字段提供明确 value 需求。
- 异常及 `Error: {str(e)}` 诊断保持 opaque。没有把 key 复制或虚构成诊断字段。当前标注下未建立 stdout 的 key 暴露；这不证明真实 Requests 异常文本绝不包含 key。
- R13 使 stdout 的完整 payload 为 required；该输入没有删除建议。26 个输入评估包含 27 个 required 和 85 个 unresolved 范围，0 个 deletable。
- 反向与 DOE 为 partial：完整 Task 的切片外义务、未经独立 source review 的契约、opaque 异常关系仍有明确缺口。Google 的 key 比较为 `no_excess_established`，没有 excess 或缩减结论。

可执行文件、人工 CFG/标注、完整编译映射、前向记录、反向推导、输入评估和 DOE 比较均在本目录。用 bundled Python `-B run_witness.py` 重跑会只更新本目录的离线 witness 文件，不会执行 `search.py`。
