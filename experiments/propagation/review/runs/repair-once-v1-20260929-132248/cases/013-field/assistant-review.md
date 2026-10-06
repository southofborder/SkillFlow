# 013-field：助手独立复核

## 结论

**受控的“首次响应 body 原字段关系降为不透明计算”缺陷已实际修复。** 本结论来自原始候选、修复响应和最终 DOE 数据关系的核对。初审命中 1 项问题，执行 1 次完整修复，独立复审未报告问题；共 3 次逻辑调用。传播完成，26/26 条 IR 均有记录，诊断为空，离线重放 `matched`、0 次模型调用。

## 实际修改与保留关系

`ir_009` 的第二个操作由 `compute(input[0], possible)` 改为 `select_part(input[0], ["body"])`，局部输出名 `fast_fetch_first_body` 和 `result_006` 输出绑定保持不变。源文依据仍是“return that successful response's body value unchanged”，修复后的表示保留了该明确字段的原值关系。

同一 IR 的状态分类仍为 `compute`、`derived`，没有被误改成字段取值；它与 body 选取继续是两个不同输出。重试和回退的响应获取、状态分类、body／error 选取及输出绑定没有修改。

另外四个普通 return 的空效果证据，从引用 CFG 中的 `return` 改为引用 EM06 的普通返回边界。这是依据调整；operator、roles、effects、事件及 CFG 返回输入均未改动。其余业务结构没有变化。

## 最终 DOE 核对

| 路径 | 响应身份 | body 部分身份 | 返回结果 |
| --- | --- | --- | --- |
| 首次成功 | `data_4db4b052af4f83026d9f38aba2cb2fc930ba07a593d4d9545090aa332bf95aa0` | `data_4cece14d028e19a13108446c1eed5e0a9777fca23d4a245765c0a0b8d543054a` | `ir_020` 返回 `result_006` |
| 重试成功 | `data_8da431bdc473f8e6e766485922b38b7ce2507a3469023a7ee24b7b3160969297` | `data_789648a1965d6f0cbbf139f11b8b61877c076297dc88771794e3216fecf3d729` | `ir_022` 返回 `result_009` |
| 回退成功 | `data_9cab3f219bab2120ee576370e763de8b2f2f9344baed1ce5e9faea925a1369f8` | `data_bee756a26a31cbfe495b77195c0631dc4b66fce7e8689ac1320addf445852af8` | `ir_024` 返回 `result_012` |

三份 body 的 `origin.part_of` 分别指向本行响应，`origin.path=["body"]`，不是仅有输入依赖的 opaque 计算结果。body 本身内容仍可为 opaque：这表示字段内容未展开，不会取消已知的“属于该响应 body 字段”关系。

首次、重试和回退响应身份互不替换，各自保留工具获取边界。回退失败返回 `result_013`，普通 return 的事件为空，返回身份仍由 CFG 输入承载。

环境仍按默认段读取整体、观察整体再选出 FAST_KEY。环境整体与密钥字段没有混成同一 Data；archive.fetch 的实际参数继续仅为 source_id。首次／重试所用凭据没有被加入 archive 参数。

独立 `load_doe_input` 校验通过；原样字段关系已落实到 Data 和事件记录，不是仅改写模型理由。

## 限制与新增问题检查

未发现本次修复引入的新实质关系问题。工具网络机制未说明时仍使用 tool 获取边界，不补造网络事实。回退 error 的结构化路径沿用原候选对“返回其 error”的表示，不表示已验证真实接口 Schema。模型观察仍是统一抽象运行时契约下的可能行为，不是执行日志。此次复核没有执行 Skill 或进行 DOE 判断，不宣称全图已获语义正确性证明。
