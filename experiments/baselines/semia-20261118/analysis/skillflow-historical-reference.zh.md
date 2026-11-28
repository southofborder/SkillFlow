# SkillFlow 历史同源工程参照

2026-11-18，仅只读提取 `input-manifest.json` 绑定的四个 parent run。未运行模型、Skill、旧 pipeline、回放或测试。130 个实际读取文件在提取结束后哈希保持一致。

四例的冻结源包均与本次 Semia 输入逐文件字节一致，共21文件；各次原生 `launch.json` 的命令均请求 `gpt-6.1-sol / high / openai`。这支持“同模型请求配置、同源包”的工程参考，**不构成当前统一 SkillFlow 版本、同 CLI、同预算的配对性能实验**。模型实际由服务端如何路由不能仅从公开 argv 独立证明。

| case | 历史实现／run identity | 新原生开始 | 已知公开 tokens | 分析耗时（秒） | 传播 | DOE |
| --- | --- | ---: | ---: | ---: | --- | --- |
| 001 | `09f5f9…`／v10 | 12 | 337,253 | 923.249 | complete；17/17 processed | partial；18 项均 no_excess_established；0 非空 reduction |
| 010 | `09f5f9…`／v10 | 11 | 316,571 | 923.444 | complete；20/20 processed | partial；135 项均 no_excess_established；0 非空 reduction |
| 013 | `09f5f9…`／v10 | 12 | 393,374 | 1,317.207 | complete；25/25 processed | partial；14 项均 no_excess_established；0 非空 reduction |
| GA4 | `3ebfb4…`／v17 | 10 | 2,226,933＋未知请求用量 | 8,247.331 | incomplete；470 processed／4 unmodeled／15 blocked，共489 IR | partial；295 项均 no_excess_established；0 非空 reduction |

每项数值的具体原文件、JSON pointer 和聚合规则都保存在 [机器参照](skillflow-historical-reference.json)。表中耗时取各 run 的 `controller-finished.json#/analysis_seconds`，不包括终端回放；原生数与 tokens 取 `metrics.json`；传播按 `propagation/manifest.json#/coverage` 的实际状态计数；DOE 按 `doe/doe-result.json#/sinks/*/data_reviews` 计数。已记录的零 reduction 意味着没有产出非空缩减建议，不能推出不存在过度暴露。传播 processed 也不等于语义正确。

小三例 `total_usage_known=true`、`unknown_usage_requests=0` 仅在历史公开计量口径内成立；GA4 明确 `total_usage_known=false`、1 个未知用量请求。cached input 是 input 的子集、reasoning output 是 output 的子集，没有重复相加。未知 provider 内部用量不补成零。`metrics.json` 的原生 wall span 和 request duration 总和另有原字段保留，不能与表中分析耗时混用。

模型一致之外，以下差异必须保留：

- 小三例的实现 SHA 为 `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`，protocol 标记 `historical_answers_imported=false`；`inherited_initial_stages` 字段没有记录，JSON 保留 null／field_not_recorded，没有强行补零。最终选中 revised annotation，Task 和 CFG 仍为原始选择。
- GA4 的实现 SHA 为 `3ebfb40a0053f0e3dc84aa4c7877b116445749b478b912910b8a9d192d787af6`，继承 task／flow／graph，四个 fresh normal stages 为 processing／task-correspondence／sensitivity／review。10 个新 logical calls 加3个继承 logical calls得到13；表中10次原生和2,226,933 tokens只算本 run 的新 transport。上游303,082 tokens在 `restart-accounting.json#/parent_upstream_cost_not_new/total_tokens`，未加入本次新成本。
- GA4 的 revision-graph 为 `request_failure`，依赖 revision stages 为 `skipped`，没有把未运行阶段写成零完成量。原 Task／CFG／annotation 保持一组选择。四例全部最终 status=partial，不能用前三例传播 complete 掩盖 DOE 的 partial。

| CLI 记录 | 固定的历史可执行文件 SHA256 |
| --- | --- |
| 小三例 SkillFlow | `4f91ae86895ff124760d70ed1630e2354ca874765c9bb61ae524b600327efc17` |
| GA4 SkillFlow | `83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f` |
| 本次 Semia 首例 | `094d4db493de22025712cc5963854e7654b7c97f4cee795e3e986270a0f4f6b4` |

三个 CLI 身份不同。历史 SkillFlow 有两个 worker 和七阶段／修订机制，Semia 有自己的 CGRS 与推荐预算；因此本表不作快慢或方法优劣排名。

必要性评估也保留原状态：001／010／013／GA4 分别有53／67／92／2004个 input assessment；range 的 required 数为393／340／318／497，unresolved 数为58／201／1004／3078；四例实际都没有 deletable range。来源为各 run 的 `doe/audit/demand-support.json#/input_assessments`。一个 assessment 可有多个 range，这些数字不能当作独立样本数，也不直接等于检测精度或召回率。

可用于本轮的是：检查相同源材料在两个系统中产生了哪些表示／接口差异，观察端到端可用性及其成本。正式效果比较仍需冻结同一当前 SkillFlow 版本、共同预算与威胁假设，并建立独立标签。历史记录的未决、继承身份、失败和未知成本都继续保留。
