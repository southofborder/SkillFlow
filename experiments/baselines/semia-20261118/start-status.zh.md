# Semia 同模型复刻启动记录

观察时点：2026-11-18 16:14（Asia/Shanghai）。这是一份启动快照，后续完成状态以 `pilot/001/finished.json` 为准；文件尚不存在表示没有完成回执。

用户选定同模型、同一批 Skill 的对照路线。相关工作及比较协议已保存到 [研究入口](../../../docs/research/README.md)。本轮只启动 001 工程首例；010、013、GA4 仅完成输入固定和离线预处理。

固定官方 Semia `v0.1.3 / 379bc25fe99833eb185efe56a38fe15f0235799c`，使用隔离环境和官方 builtin Datalog 后端。292 项 scoped 官方测试中 289 通过、3 跳过、0 失败；没有证明 builtin 与 Soufflé 在任意输入上等价。

真实首例名为 **Semia + controlled transport**：原版提示词、SDL、校验和候选选择保持不变；独立 runner 显式设置 `gpt-6.1-sol / high / openai`，禁用命令执行、插件及相关工具入口，忽略用户配置和项目指令，保存每次完整请求／响应／公开事件及用量。它是同模型工程适配，不是论文原配置复现。适配源码和CLI哈希已保存在 `runtime.json`；实际事件目前未观察到 Skill 执行。

截至观察时点，已经启动 3 次原生模型请求，前 2 次已返回，共 25,498 input + 9,843 output = **35,341 已知公开 tokens**；未完成请求及未公开的 provider 内部用量未知，不能计为零。前两份候选分别被原版校验器以 8、12 项结构错误拒绝。原始候选、纠错输入和前两轮详细检查分别保存在 `artifacts/`、`transport/`、`observations/`；没有手工修正候选再冒充原模型输出。

运行沿用原版 5 个合成 iteration、每轮 3 次结构重试和每次 2 次 provider 重试；每次 native deadline 设置为 2700 秒。最坏原生启动上限为 60；有效候选可提前停止。注意上游 provider retry 捕获全部 `LlmSynthesisError`，并非仅瞬态错误。未修改正在运行的算法或追加其他案例。模型名相同不代表调用预算相同，本轮不作同预算胜负结论。

同源材料核验发现：001、010、013 全部纳入；GA4 输入虽然是同一16文件包，但原版 prepare 排除了 `scripts/package.json` 和 `scripts/package-lock.json`。因此 GA4 暂不启动，完整源适配应另命名、保存差异，不能声称原版默认已经读全。

本轮没有独立 gold 标签，准确率／召回率均为 `not_evaluated`。历史 SkillFlow 输出来自不同实现和继承阶段，不能直接拼成当前版本的公平配对成绩。现有 GA4 运行、封存源文及生产代码未由本轮修改。

首轮只读诊断已定位两项可复查的上游问题：提示词的通则要求 evidence sidecar 镜像 core fact 参数并追加引文，但同一提示词的示例及校验器对 `action_evidence_text`、`call_evidence_text` 要求的是两个参数。首候选有六处相关的三参数错误；另两项错误分别是 secret 缺少 allowed action、同一读取区域同时标为 untrusted 和 secret。第二候选有十处同类参数错误。纠错输入却只包含 errors/warnings 的数量和三个 rate，没有具体错误消息、行号或谓词名。该矛盾与信息缺失已经得到文本证据，尚未通过消融证明它们各自造成多少失败；本次保留原版，不在进行中的试跑里修补。`evidence_match_rate=1.0` 也仅表示引文匹配，不是语义正确率。

运行入口：`run_controlled_pilot.py` 默认仅显示配置，显式 `--run` 才发起模型请求；同一个 case 输出目录已存在时拒绝重复启动。当前 001 已启动，勿再次启动。机器观察记录为 [launch-observation.json](launch-observation.json)；实时回执见 [运行目录](pilot/001/)。
