# Semia

本组对选定 ClawHub 完整源包做静态审计。固定上游提交
`379bc25fe99833eb185efe56a38fe15f0235799c`，保留 Semia 的 SDL 合成、
校验、候选选择和安全查询。[上游提交](https://github.com/berabuddies/Semia/tree/379bc25fe99833eb185efe56a38fe15f0235799c) ·
[Semia 论文](https://arxiv.org/abs/2605.00314v1)

- **封存结果**。既有四例使用受控传输，010 完成检测，001、013、GA4 在
  SDL 合成校验阶段终止。沿用既有结果时保留实际状态、模型、输入和适配版本。
  [上一批环境与输入](../../../semia-20261118/README.zh.md) ·
  [批次封存回执](../../../semia-20261118/analysis/cohort-closeout.json)
- **后续复现**。强模型基线先运行。随后以既有隔离 runner 为参考，使用新的
  运行目录保存输入回执、实际送模提示、候选与校验反馈、选中 SDL、检测结果
  和用量。源包完整性核验包括 GA4 的两个 package JSON 文件。
  [受控 runner](../../../semia-20261118/run_comparison.py) ·
  [完整源适配](../../../semia-20261118/adapters/complete_source.py)
- **复现口径**。既有结果使用 `gpt-6.1-sol / high / openai`、builtin 检测后端
  和 2700 秒单次期限。新运行分别记录这些参数和完整源适配。论文原始评测的
  后端、样本和指标由论文及其配套证据界定。

新产物写入 `runs/semia/<run-id>/`。合成失败、检测未执行、检测完成与告警
数量分别记录。原始检测关系用于方法内分析，有源文依据的共同事实进入汇总。
[共同汇总口径](../../reports/README.zh.md)

## 离线准备

从仓库根目录用已固定的 Semia 虚拟环境运行。指定一个新输出目录，可直接
传入一份完整源包，也可用新批次清单和样本 ID。以下两条分别演示两种入口。

```powershell
$semiaPython = 'experiments/baselines/semia-20261118/.venv/Scripts/python.exe'
$semiaPrepare = 'experiments/baselines/comparison/methods/semia/prepare.py'
& $semiaPython -B $semiaPrepare --input-dir $package --variant native --out $newNativeOutput
& $semiaPython -B $semiaPrepare --manifest $cohort --case-id $caseId --variant complete-source --out $newCompleteOutput
```

- `native` 保留官方文件筛选，在回执中区分纳入、排除和省略的文件。
- `complete-source` 是完整 UTF-8 源文适配，允许全部已校验的文本文件进入
  原版渲染和语义单元提取。该变体仍使用官方大小上限和行尾规范化，单独记录
  尾部非换行空白被移除的文件。

两个变体均写出 `preparation-receipt.json` 和 `initial-synthesis-prompt.txt`，
记录完整文件哈希、源行映射和离线提示哈希。清单入口按原文件路径、大小与
SHA-256 核对整包输入。入口只执行准备阶段，模型传输、合成和检测状态均为未运行。

100 个 ClawHub 样本已完成完整 UTF-8 源文适配的离线准备。逐例核对了
1,673 个文件的源行和保存的初始提示，2 个样本中的 6 个文件由上游渲染移除了
尾部非换行空白。模型调用和 Skill 执行各为 0 次。
[离线汇总与逐例回执](../../runs/semia/complete-source-01/manifest.json)

## 执行入口验证

用同一虚拟环境从仓库根目录验证已准备的 100 例和强模型组固定的 CLI。
以下命令只读校验，模型调用 0 次。

```powershell
& $semiaPython -B experiments/baselines/comparison/methods/semia/run.py
```

执行入口在显式指定新序号 `--run-id semia-audit-01` 后创建运行目录。
它使用同一 CLI 的只读、临时、禁用工具配置，以 Datalog 文本接收模型回答。
每次请求核对完整源文围栏，并保留提示、回答、反馈、事件和公开用量。原生
Semia 负责合成和校验。选中 SDL 通过校验后运行 builtin 检测，生成 Markdown
和 JSON 报告。报告后的可选模型建议本比较不请求。保留每样本 5 轮、每轮最多
3 次结构重试、2 次 provider 重试及单次 2700 秒期限，整组无总期限。

## 传输故障续批

`recover.py --prepare-only` 核验旧批次及完整源包，在 `semia-recovery-01`
固定 94 例。其中 92 例没有可见回答，2 例只有未通过原生校验的候选。其余
6 例留在旧批次。旧记录全部保留，94 例从新的原生合成目录开始。

`recover.py --run` 先执行一例，收到可核验的模型回答且该例未被传输故障
阻断时，再放行最多两个并发样本。续批仅禁用 CLI 的
`unbounded_connection_retries`。没有可见回答且发生明确的路由失败或原生
请求超时时，写完请求回执后停止该例的 provider 重试。其他 provider 错误
沿用原版重试规则。

若路由再次阻断，控制器停止分配新样本并保留已发出的运行。路由核验后，
`recover.py --resume` 仅处理未领取样本，已有终态不会重复调用。控制器
异常退出如留下没有终态的领取记录，应先核对该记录和进程状态。
