# 传播材料交接

当前传播交接由三份阶段产物及清单构成：`data.json`、`records.json`、`sinks.json`。清单保存上游引用、状态、覆盖和诊断；审计保存原请求种子、有效初始种子、登记身份和技术记录。

旧 `doe-input.json` 总包、独立格式、构造器和加载器已经退役。没有替代总包，也没有旧字段别名。DOE 通过公共只读 `load_propagation_materials()` 加载所需关系，数据及证据不重复保存。

参见 [当前字段树、保留理由与版本](../architecture/field-tightening.md) 和 [正式联合分析链](joint-pipeline.md)。[早期 DOE 输入三例报告](../../experiments/propagation/runs/doe-input-v1-20260924-193407/index.html) 保留当时原始字节和失败记录，不能用新加载器重解释。
