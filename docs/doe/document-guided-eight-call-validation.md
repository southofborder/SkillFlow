# 精简并行八调用：实现与离线验收

日期：2026-10-27。目录：`D:/projects/SkillFlow`。

本轮已实现正常八调用、两个依赖感知 worker、精简 CFG 与扁平 annotation、稀疏统一源文审查，以及单层逐项获取与映射集合输出。保留独立 Task、任务对应／敏感性隔离和原有确定性分析框架。正式入口已经移除环境确认、profile／harness pin 和 usage 回执验收门槛；监控没有额外模型请求。

本轮只有实现和离线验证。新增 Skill 分析与校准模型调用为 **0**；没有执行 Skill，没有续跑或改写 GA4、比较实验等历史运行。下述 fake client 结果验证工程流程，不能替代真实模型的准确性、token 成本或速度成绩。

入口：[现行设计](document-guided-analysis.md) · [八份英文 Prompt 与当前样张](../../examples/document-guided/index.html) · [prepare/run/replay CLI](../../tools/doe/document_guided_pilot.py)。

## 分项交付

| 项目 | 实现结果 | 证据与解释 |
|---|---|---|
| 循环能力 | `read/receive/call` 可用于单层 `for_each`；`yield/output` 成对导出集合 | 保留源 occurrence、顺序、重复、响应版本和每成员候选；空集合无 body 获取，未知集合不被当成一个成员 |
| 填写规模 | CFG 的指令编号／可读名称／context-key 清单由程序生成；annotation 为 segments/ops | 删除模型 operator、operator_evidences、empty_effect_evidences 和 realization status；最近父级证据继承，location 证据内联 |
| 正常请求数 | 恰好 8 个分析逻辑请求 | Task、flow、CFG、processing、任务对应、敏感性、annotation、统一审查；没有 relationships、单独图核对或确认调用 |
| 并行 | 最多 2 个 worker | CFG 不等待 Task；任务对应／敏感性在 processing 后并行；根状态和选用组合由主线程写入 |
| 少量重建 | 一轮共享语义修复，按实际依赖重建 | annotation／Task／CFG／多域正常总数分别为 10／12／14／15；结构纠正和网络传输尝试另计 |
| 监控移除 | 本地被动观察，缺 usage 不影响分析 | 阶段、Task、根结果和 CLI 统计失败不决定语义接受；重放不启动客户端 |

合成样张的 compact JSON UTF-8 大小：CFG wire **850 bytes**，程序展开 candidate **1,045 bytes**；flat annotation **4,596 bytes**，程序展开 backend annotation **6,334 bytes**。这是同一作者样张的序列化体积比较，不是旧／新模型输出实验，也不是实际 tokenizer 或长 Skill 的 token 降幅。

## 语义和恢复检查

- `call` 根据明确 wire 坐标生成 request ID 和一对一 request/response 映射；同参、零参及同值重复成员不会按邻近或 FIFO 猜配。需求 input/self/output 分别对应请求参数／发起动作／响应；约束 phase 省略时为 request。
- 映射集合只从 yield 引入内容；源集合提供成员和基数关系，不把整份输入明文复制进结果。每成员字段需求回到相应 yield，基数需求不扩大为响应内容需求。敏感性与原内容限制保留候选来源，避免同一成员的候选 A 通过汇总数组污染候选 B。
- local body 的内部响应不会因 yield 自动进入模型；真实返回集合必须声明 returns。允许有证据、空 ops 的纯返回路由。
- 审查仅输出真实差异；空 findings 不生成逐项 accepted。annotation 不可用时仍审实际具备的 Task／CFG 和障碍，缺失对象保持未审。
- 真实上游问题可使用同一轮语义修复；单纯能力失败不重采样。未失效的独立失败步骤保留原失败，不因其他域修复而重发。新 annotation 完整编译并绑定新的 Task／CFG 后整体选用；重建失败不混用版本。
- 每阶段最多一次结构纠正；恢复沿原调用链继续，不重置预算。完整答案保存后只做本地复用；尾部空消息不能覆盖它。已退出、无完整答案的暂态网络错误最多额外尝试两次，未知进程状态不重复启动。

## GA4 代表路径

本轮使用源码支持的小夹具贯穿编译、传播、保存、输出和反向需求，没有运行 GA4 Skill：

1. 批次函数：metadata 存在、默认保存的正常完成路径，response notification 形成每成员结果，再进入真实保存和返回集合；未将响应 URL 冒充原始输入 URL。
2. `checkIndexStatus`：正常 status projection、indexed 计算及 URL／对应结果的成员关系。
3. catch 候选：用源码明确的凭据验证常量构造一种 Error，再形成 `String(error)` 候选，与成功记录作为同成员的替代结果；错误内容不来自 URL／response，也没有虚构异常数据接口。

批次及 catch 候选夹具明确保留未建模的 guard、throw/catch、任意 SDK／网络异常、缓存及终止条件。相应结果保留 partial 和 gap；“候选可收集”不等于“异常执行语义完整”。无逐项 catch 的函数只验证正常完成路径，没有添加失败记录后继续的行为。不同 import 来源、配置写入、完整 metadata 需求、接收方区别和分析结果文件的来源关联缺口仍在提示与统一审查范围内。

## 最终验收结果

最终检查前后 `implementation_provenance()` 完全一致，摘要为 `f8aec3198114eabf2a8a1189a60573543117092cce1a0c86def9a2aa3e9f7ee9`。原始日志、JUnit 和前后实现清单保存在[本轮验证目录](../../output/verification/document-guided-eight-call-v4/)。

| 检查 | 原始结果 | 处理及最终状态 |
|---|---|---|
| 调度、Task、结构纠正、恢复及当前样张 | 194 passed；pytest 283.89s | 正常八调用贯穿实际 propagation／DOE；包含真实 Lean 证书归档与零调用重放 |
| 数据、循环、编译、需求、敏感性、限制及后端兼容 | 866 passed、2 failed；pytest 589.51s | 两条失败只检查旧 compiler v9／run v19，当前版本已为 v10／v20 |
| 上述两个兼容文件完整重跑 | 63 passed；pytest 130.96s | 更新两条过时断言，保留全部顺序、原文、输入隔离、恢复、篡改和重放检查 |
| CLI 参数帮助和 whitespace | 通过 | 仅运行 Python 入口 --help，未启动 Codex CLI；针对本轮文件的 CRLF-aware diff --check 通过 |

按 classname/name 去重，并采用修正后对应测试的最新结果，最终相关范围为 **1,062 个不同测试，剩余失败／错误／跳过均为 0**。其中 63 个兼容测试已包含于 868 项范围，不能再相加。上表时间是离线测试时间，且部分检查并行，不能当成模型速度或串行总时间。[机器可读汇总](../../output/verification/document-guided-eight-call-v4/verification.json)保留初次失败和修正说明。

可复现范围及环境见[命令清单](../../output/verification/document-guided-eight-call-v4/commands.json)。后端[文件列表](../../output/verification/document-guided-eight-call-v4/backend-paths.txt)展开了原目录参数，对应同一 868 项范围；当前测试断言已包含上述版本修正。

没有把前期范围过宽、因修复门槛问题而中断的尝试计为通过；其 `pytest.log` 和 `broad-attempt-status.json` 原样保留。新增 partial-review 回归先观测到 3 failed／2 passed，修复后 5 passed，随后已纳入最终 194 项范围，不重复累计。所有试验均为工程 fake client／本地后端检查，不是目标模型语义评分。

主要覆盖：

- 两 worker 的依赖与写入归属、Task 等待点、mapping／sensitivity 并发及输入隔离；
- 完整 CFG、literal、call、for_each、yield、输出绑定、非空 finding 的真实类型与生成格式；
- 重复 URL occurrence、同参／零参工具获取、准确 request/response 配对；
- 空、未知和多候选集合、保存／返回消费最终版本、不展开整批候选积；
- 每成员字段及基数需求、敏感范围、候选隔离和限制保留；
- 一次结构纠正、各语义修复闭包、修复失败一致回退及部分材料审查；
- 不同并行完成顺序、中断 cursor、完整答案本地复用、缺 usage 和 observer 故障；
- 当前 flat wire 贯穿加载、编译、传播、DOE 和零模型调用重放；
- 多语言源文、原始物理行引用以及当前样张 GA4 子目录原字节保持。

## 当前契约与使用

当前文档入口 run/step/annotation v4；内层 annotation run v20、profile v18、runtime v8、processing compiler/mapping v10；Data v5、propagation records v12、propagation run/format v18、demand v6、sensitivity v5。Task v5、Task extraction v3 和已有 CFG 的联合 pipeline v9 保留各自身份。历史版本不迁移、不重新标记。

新运行的命令为：

```powershell
python -m tools.doe.document_guided_pilot prepare --input <Skill> --run-dir <new-directory>
python -m tools.doe.document_guided_pilot run --run-dir <prepared-directory>
python -m tools.doe.document_guided_pilot replay --run-dir <recorded-directory>
```

`run` 可选 `--executable`、`--timeout`、`--retries 0|1|2`。子进程启动参数指定 gpt-6.1-sol／max／openai；没有环境确认模型调用、profile 或 token 验收。当前 CLI 的实际在线投递未在本轮测试。

## 结论边界

本轮证明所选表示、依赖调度和确定性关系已接通，并分别验证了正常调用数、填写字段、并行、恢复和被动监控。它没有测得真实长 Skill 的端到端提速、实际 token 降幅或准确性提升，也没有把旧 GA4 未完成运行改写为新方案成功。

最终审查后移会使晚发现的图问题重建更多下游步骤；同一输入需要的总调用量仍取决于真实纠正和修复次数。共享写入、嵌套循环、通用异常、提前终止及尚无来源绑定的缓存／错误机制维持明确限制。所有现有 gap、需求、敏感性和约束裁决规则继续生效，没有用字段精简放宽 DOE 成功条件。

