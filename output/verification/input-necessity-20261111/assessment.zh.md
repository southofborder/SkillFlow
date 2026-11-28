# 字段级输入必要性：离线验收

状态：**通过**。

当前保存收据按测试标识去重、按测试进程启动时间选择最新结果：**2810 项通过，2 项跳过，0 项未解决失败**。这不是一次全仓全绿执行。
较早启动的长测试在修正复验之后才结束，不会覆盖较晚启动的新进程复验结果。所有初次失败收据仍然保留。

## 交付行为

- processing 生成 Task 隔离的字段级输出—输入契约，末尾源文审查逐契约确认，程序据所需输出确定性回传需求。
- 无需求范围在完成语义核验及适用限制保持检查后判为可删除；覆盖非敏感输入，保留实际前向读取、来源和观察。
- 工具接口必需范围与额外实参分开；整值要求保持整值，可选字段保留存在性及存在时的值。
- 删除影响与反向需求使用同一契约；同一字段的其他输出、控制及消费者需求会汇总保留。
- 所选 source、CFG、annotation、review 与审查回执绑定；旧回执不可用于修复后的契约。
- 多余、错误、缺失输入独立列示；未决保留具体受影响范围、缺失关系及证据。

## 验收证据

逐项对应见 [coverage matrix](input-necessity-coverage.md) 和 [machine-readable receipt](offline-acceptance.json)。

主要覆盖三输入主例、部分字段及整槽删除、不同输出的需求组合、条件及成员关系、工具整值/可选/额外字段、错误和缺失字段、限制保持、局部缺口、旧审查身份拒绝、FIFO/LIFO 一致性，以及注入七答复的保存/修复/重放流程。

## 保留的失败与修正

初始集成检查包含环境依赖缺失、旧协议断言和在并行修改期间触发的实现身份差异。真实实现问题包括跨循环推导的缺口传播、局部契约诊断影响范围，以及新版 JSON schema 的 propertyNames 渲染；均有专项修正与复验。
冻结后的集成检查为 1,777 通过、16 失败、1 跳过；16 项分别是 12 项 tokenizer 版本不符及 4 项旧无契约用例仍期待完整结果，已在相应范围复验通过。生产代码没有为消除这些预期差异而放宽契约检查。

| 保留收据 | 通过 | 失败 | 跳过 |
| --- | ---: | ---: | ---: |
| `constraint-sensitivity-initial.xml` | 76 | 2 | 0 |
| `audit-formal.xml` | 62 | 14 | 0 |
| `integrated-initial.xml` | 1639 | 134 | 1 |
| `independent-review-initial.xml` | 2 | 1 | 0 |
| `propagation-initial.xml` | 1034 | 13 | 1 |
| `compatibility-rerun.xml` | 52 | 1 | 0 |
| `historical-sample-rerun.xml` | 2 | 1 | 0 |
| `historical-sample-final.xml` | 2 | 1 | 0 |
| `fixture-compatibility-initial.xml` | 59 | 1 | 0 |
| `historical-sample-final-v2.xml` | 3 | 1 | 0 |
| `integrated-frozen.xml` | 1777 | 16 | 1 |

## 实现与边界

实现 SHA-256：`09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`。
Python 源文件集合 SHA-256：`861a3464984eb1a49c07c9f05144dd32b9586151e665cc0485c649b0864295ad`。

正常七次语义请求、两个 worker、现有结构修正和共享修复预算保持；Task 职责不变。身份升级覆盖 annotation、编译映射、source review、guided run、demand 和 DOE。历史产物未迁移或重写。

语义正确性仍依赖源文及独立审查，不是自然语言等价或全局最小性的形式化证明。错误字段的意图不能凭变量名猜测；没有表达的接口裁剪能力不能被推定。数组重索引、未支持限制及真实源文缺口保留边界。系统不自动改写或执行 Skill。

离线验收期间没有真实模型请求、Skill 执行或历史运行重放。用户已另行授权在此后启动唯一的新 GA4 → 001 → 010 → 013 批次；新目录及实际结果记录在相邻的 online-input-necessity-20261111 目录。
