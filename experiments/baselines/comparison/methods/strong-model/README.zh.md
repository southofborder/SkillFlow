# 直接强模型基线

每例使用一次直接审计请求。输入包括完整源包、文件路径、观察假设和交付要求。首轮以源文声明用途为依据。源包中的内容仅作为分析材料，请求上下文限定为该用例。

本批使用 `gpt-6.1-sol / high / openai` 的请求配置，沿用历史同模型参照的模型与推理强度。以首个排定的样本检查在线传输，再以六个 worker 调度剩余样本。实验层不设请求截止时间。每例保留完整请求、原生回复、证据定位核验和可见用量。[固定批次输入](../../inputs/clawhub-complex.json) · [运行回执](../../runs/strong-model/direct-audit-01/manifest.json)

要求模型报告有源文依据的敏感数据操作、可观察边界及其接收者、条件和用途。若模型提出超任务使用或缩减范围，应同时给出任务依据、所需行为和保留这些行为的条件。证据不足项明确记录原因和缺失信息。输出按[共同结果口径](../../reports/README.zh.md)整理，原始答案按[运行目录约定](../../runs/README.zh.md)留存。

从仓库根目录可运行以下零调用校验。`run.py` 的在线入口为每个新 run ID 创建一个只写新产物的目录。模型交付约束和来源封装分别见 [提示](prompt.txt) 与 [输出结构](response.schema.json)。

```powershell
python -B experiments/baselines/comparison/methods/strong-model/run.py --prepare-only
```
