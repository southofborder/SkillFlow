# Sink 收紧、可选参数与 DOE 对照：三例完成结果

本轮三例均完成一次联合标注、观察编译、确定性传播和零 API 重放。001 修正了无依据网络分类；010 保留了可选参数原值、出现条件和同一请求绑定；013 本次获得合法 JSON。助手逐例复核未发现新的实质关系问题。以下是统一契约下的静态可能行为，不是执行日志或 DOE 结论。

| 样例 | 标注／传播 | IR 记录 | Data | Sink 位置 | 主要变化 |
|---|---|---:|---:|---:|---|
| 001 / N01 | complete / complete | 10 | 6 | 6 | notify.send 为 tool/recipient/null，external_tool 等级 2；recipient 与 summary 保持同一元素的原字段。来源整体观察未被工具参数范围替换。 |
| 010 / Q04 | complete / complete | 12 | 22 | 12 | query、from_date、limit 保留原字段；两项 when 独立控制加入／省略，形成四种候选请求；交付与获取使用同一实际 Data 绑定。旗标不在请求内容中。 |
| 013 / F01 | complete / complete | 26 | 20 | 16 | 上轮完整返回有多余括号，未形成 DOE；本轮严格解析通过。环境整体与 FAST_KEY 选择分开，首次／重试／回退来源及 body 原字段保持，archive 直接参数只有 source_id。 |

## 逐例审查入口

001：[数据与边界审查](cases/001/propagation/report.html) · [DOE 变化对照](cases/001/doe-input-change.html) · [DOE 原始事实](cases/001/propagation/doe-input.json) · [助手逐项复核](cases/001/assistant-review.md) · [标注与边界属性](cases/001/annotation/report.md) · [原始标注](cases/001/annotation/audit/raw-annotation.json) · [本次既有 CFG](cases/001/selected-analysis.json)

010：[数据与边界审查](cases/010/propagation/report.html) · [DOE 变化对照](cases/010/doe-input-change.html) · [DOE 原始事实](cases/010/propagation/doe-input.json) · [助手逐项复核](cases/010/assistant-review.md) · [标注与边界属性](cases/010/annotation/report.md) · [原始标注](cases/010/annotation/audit/raw-annotation.json) · [本次既有 CFG](cases/010/selected-analysis.json)

013：[数据与边界审查](cases/013/propagation/report.html) · [DOE 变化对照](cases/013/doe-input-change.html) · [DOE 原始事实](cases/013/propagation/doe-input.json) · [助手逐项复核](cases/013/assistant-review.md) · [标注与边界属性](cases/013/annotation/report.md) · [原始标注](cases/013/annotation/audit/raw-annotation.json) · [本次既有 CFG](cases/013/selected-analysis.json)

## DOE 文件增加什么

```text
DOE 顶层业务区、Data 外层和证据边界：保持不变
records[IR].events[].atomic_ops[]
├─ build.members[]                    仅 build 适用
│  ├─ path                            构造字段位置
│  ├─ value_input_index               原值槽；确定省略时 null
│  └─ when_input_index                控制槽；无条件时 null
└─ 条件观察.when_input_index           控制槽，不能算作观察载荷

locations.access_scope / retention    继续保留
sink_boundaries                       继续保留类型、等级、目标和操作坐标
```

成员映射不复制 Data ID。inputs 仍为按参数顺序排列的候选集合；控制影响成员出现，不代表控制明文成为请求内容。010 的四种请求形状是静态候选，不表示实际执行了四次工具调用。

## 工程验收与复核边界

- 全套 2493 项回归通过；最后一次报告展示修正后，受影响的 158 项回归再次通过，含逐元素条件观察的展示测试。
- 三例恰好 3 次逻辑调用、3 次 HTTP 尝试、0 次传输重试。请求模型 deepseek-v4-flash，实际返回 deepseek-flash；实际请求均启用 JSON Output，完成原因均为 stop。
- 三份 DOE 独立加载有效；离线重放阻断在线客户端和网络连接，0 API、0 网络尝试，三个最终文件的摘要保持不变。
- 11513 个历史／冻结文件与 49 个受保护源码文件的摘要保持不变；三例源包和选定 CFG 与 bootstrap 绑定一致。
- 传播诊断三例均为空。未运行额外模型审查或自动修复；助手复核不冒充人工确认。
- 多余括号、重复键、非布尔条件、歧义请求和其他无效输入仍严格拒绝，不通过截断、修 JSON 或择优重跑形成成功。

保留的正常近似包括：统一契约下可能的模型观察、工具默认外部接收、未知布尔条件的出现／省略候选、分支 may 汇合和不透明计算的 possible 依赖。等级只描述边界性质；这些结果不证明真实执行发生，也不判断敏感性、必要性或 DOE。013 不把上轮“未生成文件”解释成“上轮没有 sink”。

[机器验收记录](verification.json) · [重放核验](replay-verification.json) · [历史保护](preservation.json) · [调用与状态](summary.json)

## 离线复查

```powershell
$env:PYTHONPATH='packages/skill-ir/src'
python -m skill_ir.propagation replay --run-dir <本例 propagation 目录>
```

三例整体重放也可使用 tools/run_tightening_pilot.py replay --run-dir <本运行目录>。重放不读取 API key，不创建在线客户端。当前版本拒绝旧格式，历史文件只按原字节对照，不迁移。
