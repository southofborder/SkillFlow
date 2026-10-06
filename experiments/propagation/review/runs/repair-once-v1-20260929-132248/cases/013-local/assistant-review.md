# 013-local：助手独立复核

## 结论

**受控的“无依据局部隔离”缺陷已实际修复。** 这项判断来自原始候选、完整修复响应、编译结果和最终 DOE 数据关系的逐项检查，不以复审没有报问题作为依据。本例初审命中 1 项问题，执行 1 次完整修复，独立复审未报告问题；总计 3 次逻辑调用。传播覆盖 26/26 条 IR，状态为 `complete`，诊断为空，零 API 重放与原结果一致。

## 实际修改

逐字段比较 `refinement/inputs/candidate.json` 与 `refinement/repair/audit/raw-annotation.json`：业务变化仅发生在 `ir_003` 的环境获取处理段。

| 项目 | 修复前 | 修复后 |
| --- | --- | --- |
| 处理方式 | `local` | `default` |
| 段出口回传声明 | 只回传 `fast_key` | 空列表；不再以局部隔离限定可见范围 |
| 依据 | 设想环境其余内容留在本地 | 引用源文缺少局部机制及 EM10 的默认规则 |

其余 profiles、locations、操作、公开输出绑定和各 IR 关系未改变。修复没有通过增加字段或假想保护操作满足审查意见。

编译后的 `ir_003` 为：

```text
read(loc_environment) → environment_content
model_observe(environment_content)
select_part(environment_content, ["FAST_KEY"]) → fast_key
output[0] = fast_key
```

## 最终数据与边界检查

- 环境整体是 `data_0daf6a610305be67bfde3e4e1e0d5bff905767cc685650ce0e78632fcd9a35ef`，来源为 `runtime_context:environment`。内容登记了 FAST_KEY 部分，但 `parts_complete=false`，没有把未知剩余删除。
- `ir_003` 的观察事件直接引用上述环境整体，字段选取的输出为 `data_42111b8716da74f9d2470144b479d7c9827c69c33fcdd8ad3d006a9e3f53ee3a`。后者的 `origin.part_of` 指向环境整体，`origin.path=["FAST_KEY"]`；公开 `result_002` 绑定的是该部分。
- 首次及重试 `fast.fetch` 仍分别使用 source_id 与 FAST_KEY 两个实际参数；环境整体没有被当成工具参数。两次响应是不同 Data，各自保留 `tool:fast.fetch` 获取来源和参数的 possible 依赖。
- `archive.fetch` 的获取操作只有 source_id 一个请求参数，没有新增 FAST_KEY 或环境整体。观察范围恢复并未扩大 archive 的实际参数范围。
- 首次、重试、回退的 body 都保留明确的部分关系，分别指向各自响应；分类仍为计算结果。普通 return 的输入身份保留在 CFG 中，没有为它虚构公开输出或用户交付。
- 各终态写 status.txt 的操作仍使用相应结果分类，不直接使用环境或 FAST_KEY。响应对凭据的 possible 依赖不能被解释为状态中必然包含凭据明文。

独立 `load_doe_input` 检查通过。传播重放记录为 `matched`，`model_calls=0`，差异列表为空。

## 限制及新增问题检查

没有发现本次修复引入的其他实质关系变化。环境整体的观察属于 `skillflow-abstract-runtime-v3` 下的保守可能性，不是实测的整个环境读取或泄露。已知工具获取保持 tool 边界，未据此补造网络发送／接收标签。回退响应的 `error` 部分关系沿用原候选；它是对源文“返回其 error”的当前表示，不意味着已验证真实工具 JSON 接口。

本次检查未执行 Skill、未进行 DOE 必要性或风险判断，也未证明全图语义完全正确。
