# SkillPrivus

本组按论文 v1 实现静态审计准备，输入采用[同一组 100 个 ClawHub 源包](../../inputs/clawhub-complex.json)。附录 F 提到完整提示位于发布代码库的 `prompts/`，作者仓库地址与提交仍待核实。当前方法标识为 `skillprivus-paper-based-v1`。论文主实验使用 `gpt-oss-120b`，此处尚未配置在线后端。[论文正文与附录](https://arxiv.org/html/2611.26747v1)

1. 筛查是否存在个人数据处理，记录纳入、排除或证据不足。
2. 分别提取声明用途与 `Read`、`Infer`、`Save`、`Send`、`Delete` 操作。操作关联原文件、行范围和依赖片段。
3. 填写情境完整性属性和预期规范，判断 `Violation`、`Ok` 或 `Incomplete`。缺少裁决或必要属性的操作保留为 `Incomplete`。
4. 按论文附录 B 的类别标注潜在危害。归类结果保留对应裁决。
5. 生成可追溯到操作和原文的 Privacy Card，并记录用例终态。

本地重写的提示参照 §3 及附录 B、D–F。筛查和提取均接收完整 UTF-8 源包，进入裁决的内容是声明与带证据的操作。当前确定性实现验证源码哈希、证据位置及裁决覆盖。论文中的本地地址、秘密和共享临时目录复核规则写入裁决提示，独立复核实现待核实作者资料。Privacy Card 为结构化结果，可用于核对事实和依据。[裁决提示](prompts/judgment.txt)

## 离线准备入口

在仓库根目录运行。`prepare` 逐文件验证清单、哈希和完整源码，将筛查材料写入 `runs/skillprivus/<run-id>/cases/<case-id>/requests/`。可重复传入 `--case-id` 只准备指定用例。

```powershell
python experiments/baselines/comparison/methods/skillprivus/prepare.py prepare --run-id paper-based-01
```

后续接入模型时，调用器读取对应 `requests/<stage>.json` 并保留请求回执。将阶段原始 JSON 答案存入同一用例的 `raw/<stage>.json`，再执行 `advance`。验证通过后，程序保存请求和答复的哈希、阶段记录，以及下一阶段请求或终态。例如 `advance --run-id paper-based-01 --case-id <case-id> --stage screening`。

两条命令均离线执行。筛除用例与未完成用例保留各自状态和适用性，完整运行后的零告警取自实际执行阶段。[共同汇总口径](../../reports/README.zh.md)

## 受控同模型入口

[run.py](run.py) 可用 `--prepare-only` 校验 100 个源包、渲染筛查请求和生成阶段输出结构。该命令不启动模型，也不写运行目录。

```powershell
python -B experiments/baselines/comparison/methods/skillprivus/run.py --prepare-only
```

在线入口使用 `skillprivus-paper-based-v1-controlled-codex` 变体，固定请求配置为 `gpt-6.1-sol / high / openai`。默认运行 ID 为 `paper-based-controlled-01`，默认并发为 6。每个实际进入的阶段调用一次，实验层无请求截止时间。首例传输及隔离检查通过后调度余下用例。在线入口当前尚未启动。

新运行保存同批清单和阶段模板、实际提示、CLI 回执、原始结构化答复、阶段记录及用例终态。输出结构的数组阶段用 JSON 对象封装，原始答复与送入阶段验证的答复分别留存。论文 `gpt-oss-120b` 仍需单独核实运行后端。
