# 001-version：助手独立复核

## 结论

**受控的“通知正文错误绑定整个元素”缺陷已实际修复。** 原始候选、修复标注及最终 DOE 的交付参数均已检查；本结论不依赖复审是否报问题。初审命中 1 项问题，一次完整修复后独立复审未报告问题，共 3 次逻辑调用。传播完成，10/10 条 IR 有记录，诊断为空，零 API 重放一致。

## 实际修改

修复前，在同一个 `for_each` 中已经提取 `recipient_value` 和 `summary_value`，但最终 `deliver` 的第二个输入引用了整个 `record`。修复后只把该实参改为 `summary_value`。

去除模型依据文字再作结构比较，除了上述实参变动，所有业务字段均相同。若干引文和理由被修改或补充，但筛选条件、处理模式、字段路径、位置、计数计算、公开结果绑定均未改变。

```text
同一符号元素 record
├─ 契约观察：record
├─ select_part(record, ["recipient"]) → recipient_value
├─ select_part(record, ["summary"])   → summary_value
└─ deliver(recipient_value, summary_value) → notify.send
```

## 最终 DOE 核对

- 原文件整体是 `data_ae9f03f1f871bde7628d46c87ff37ad126a5abf98fe11aefd1c152cebdf9eb1c`，保留 storage 来源，已知组成没有被标成完整列举。
- `filter_items` 产生 `subset_view`，其 base 指向原文件整体，predicate 仍为“仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录”。它没有生成内容改写后的成员。
- `ir_005` 的作用域 collection 指向筛选子集，符号元素为 `data_3c3e28210953bd753e3602ac6856fc31ff2999c8e60495659399a46d5f940803`。作用域实例保存 collection 与 element 的对应关系，没有把不同记录独立组合。
- recipient 为 `data_5b7d4037b2bab5e458cc4dd437022bef2202ece41f73eca6c50870002f7ea797`，summary 为 `data_f044f0da9dff2dfd2df8081142aa65387874d3080888c8086693f7c2a086e8fb`；两者路径拥有完全相同的抽象元素 scope，只在末段分别为 recipient、summary。字段可追溯至原文件中同一个元素。
- `net_send` 的 `deliver.inputs` 是两个有序参数位置：先 recipient Data，后 summary Data。第二个位置没有再引用整个元素；summary 也没有退化成摘要计算。
- 逐元素段的 `model_observe` 仍绑定原元素；文件读取、筛选和计数的默认观察也仍存在。缩小通知参数没有反向撤销模型对较宽内容的契约观察。
- 计数仍从筛选子集产生 derived 计算结果 `data_df0d6a5d80ec3a909264de3cc001e2c3588485364b5064ede5a2e827e6741260`，`count.txt` 的写入只使用该结果，没有把集合或原记录写进文件。

独立 `load_doe_input` 通过；传播重放为 `matched`、0 次调用、差异为空。

## 限制与新增问题检查

未发现本次修复引入的新实质关系问题。符号元素不是实际第零条记录，不代表已枚举真实集合长度；筛选谓词被保留但没有求值。当前可以确认交付的是两个明确字段，而不是整条记录；不能由此进一步宣布 summary 内必然不存在敏感内容，或运行中已经执行隐私保护。模型观察属于统一契约下的静态可能行为，发送与观察的必要性留给 DOE 阶段。

修复过程中部分执行主体依据仍使用“源文未提及模型参与”等措辞。编译后的默认观察未受其影响，且本轮契约明确区分动作执行主体与可能可见性；未据这一措辞单独认定新增的数据关系错误。
