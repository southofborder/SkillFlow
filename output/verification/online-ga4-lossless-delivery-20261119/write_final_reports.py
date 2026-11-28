"""Write bounded closeout reports from terminal audits; no analysis execution."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
RUN_REL = "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"
RUN = PROJECT / RUN_REL


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    request = read(HERE / "final-request-audit.json")
    backend = read(HERE / "final-backend-audit.json")
    integrity = read(HERE / "final-integrity.json")
    boundaries = read(HERE / "final-source-boundary-audit.json")
    controller = read(RUN / "controller-finished.json")
    timing = read(RUN / "component-timing.json")
    offline = read(PROJECT / "output/verification/lossless-delivery-20261119/offline-acceptance.json")
    sync = read(HERE / "github-sync.json")
    if (integrity["status"] != "closed" or controller["replay"]["status"] != "matched"
            or controller["replay"]["new_native_markers"] != 0):
        raise ValueError("Expected terminal matched zero-call replay and closed processes")
    delivery_rows = [{"stage": row["stage"], "index": row["index"],
                      "category": row["category"], **row["delivery"]}
                     for row in request["deliveries"]]
    file_sizes = {name: (RUN / "doe" / name).stat().st_size
                  for name in ("doe-result.json", "report.html", "report.md")}
    summary = {
        "identity": "skillflow-ga4-lossless-delivery-closeout-v1",
        "status": "closed",
        "run_directory": RUN_REL,
        "implementation_sha256": offline["implementation_sha256"],
        "github_commit": "2b11000a1679421c578ac59e9f2dae8619ab864a",
        "github_sync": sync,
        "offline": {"latest_distinct_scoped_results": offline["latest_distinct_scoped_results"],
                    "method": offline["method"], "unresolved_failures": 0},
        "policy": offline["policy"],
        "inherited_stages": ["task", "flow", "graph"],
        "inherited_from": "document-guided-ga4-runtime-locality-high-20261117-205158",
        "inherited_parent_known_tokens_excluded": 303082,
        "old_producer_identities_preserved": True,
        "controller": controller,
        "request_counts": request["counts"], "usage": request["usage"],
        "deliveries": delivery_rows,
        "selected_cfg": backend["selected_cfg"], "selection": backend["selection"],
        "initial_cfg_published_unchanged": backend["initial_cfg_published_unchanged"],
        "review": backend["selected_review_receipt"],
        "propagation": backend["propagation"], "demand": backend["demand"], "doe": backend["doe"],
        "boundaries": {key: {name: value for name, value in item.items()
                              if not isinstance(value, (list, dict))}
                       for key, item in boundaries["categories"].items()},
        "component_timing": timing, "integrity": integrity,
        "doe_artifact_bytes": file_sizes,
        "scope": "No extra model probes, Skill execution, historical replay, resampling or second fresh run. Ranges and comparisons count use sites, properties and derivations, not distinct original fields. Public token counters exclude inherited cost; reasoning/cache are subsets. Unreported provider internals are unavailable.",
        "result": "Lossless delivery exercised successfully; GA4 semantic/necessity analysis remains partial with no deletable input established.",
        "followup_implemented": False,
    }
    table = "\n".join(f"| {row['stage']} a{row['index']:03d} | {row['characters']:,} | {row['utf8_bytes']:,} |"
                      for row in sorted(delivery_rows, key=lambda x: (x['stage'], x['index'])))
    english = f"""# GA4 lossless-delivery closeout

Generic lossless input delivery is accepted offline and exercised online. The sole fresh GA4 analysis closed **partial**; it established **no deletable input range**. Its sole controller-owned zero-call replay matched. This run does not establish successful end-to-end field-necessity detection on GA4.

## Delivered implementation and synchronization

Implementation SHA256 `{offline['implementation_sha256']}` is published in [GitHub commit 2b11000](https://github.com/southofborder/SkillFlow/commit/2b11000a1679421c578ac59e9f2dae8619ab864a). The accepted tree equals original local commit 3c7808ec; its original metadata remains on `codex/lossless-local-before-sync-20261119`. Fetch verified the remote tree. Offline evidence has **3,205 latest distinct scoped passes, two reviewed skips, zero unresolved failures** across scoped scans and final rechecks. This is not one whole-repository/all-green execution; original failures remain saved.

Shared value/column encoding covers sensitivity and Task-correspondence normal, structural-correction and full/scoped revision builders. The audit also covers scoped processing and graph inputs. Existing processing/review formats and version-bound historical readers remain explicit. Every real delivery records exact codepoints, UTF-8 bytes, section/prefix totals and digests before native start. Source is complete and validation remains strict.

## Sole run and actual delivery

Run: `{RUN_REL}`. The selected initial **215 blocks / 489 IR / 192 edges**, Task/flow and full **16-file source** came from closed 205158 with old producer identities retained. Seven normal-stage policy means **three inherited plus four fresh normal requests**; two workers and existing correction/shared-repair/2700-second/transport budgets were preserved. No Skill or real GA4 tool was executed.

| Actual request | Characters | UTF-8 bytes |
|---|---:|---:|
{table}

All eight actual preflights match actual delivery size/hash and logical-core digest; all retain the complete selected source. Sensitivity and correspondence completed first try. Under a controlled same-payload expansion, their deliveries are **476,237 vs 1,030,256** and **516,118 vs 1,078,676** characters: savings **554,019** and **562,558**. The latter expanded reference exceeds the 1,048,576-character adapter limit. This changes only JSON encoding, retaining source/instructions; it is not a causal historical latency/token comparison. These two stages did not exercise their correction/revision paths online in this run; those paths have offline evidence.

## Outcome and localized failures

Initial processing retained 483 modeled and six explicitly unmodeled IR after its finite correction. Four validation exclusions remained: ir_167 has undefined output locals; ir_311/329/346 have unsupported nested cases. The model repaired seven evidence references but omitted the authorized three whole records and five binding fields.

Source review covered **431 obligations / 1,929 scopes**. It retained **425 valid checks** (386 accepted, 39 rejected) and **1,911 scope decisions** (1,654 accepted, 257 rejected); six checks/18 scopes have local barriers. Forty-six findings remain (two CFG, 44 annotation). Six mixed wide/narrow scope groups inherited an affected-input list illegal for narrow subjects; the correction changed the target list without splitting the subjects. Other 425 checks and seven original findings were retained. The selected review receipt is bound to the selected original bundle and matches demand.

Shared graph repair returned two region objects where block arrays were required; both updates were locally rejected. Independently, the proposed action split exceeds the signed action-preserving region capability. Scoped processing acknowledged all 27 slots but six rewritten records omitted **24 mandatory attachments** (23 demand_transfer, one tool input_contract). Its builder omitted normal-stage conditional contract rules and existing location definitions from the read-only revision context. The stage failed strict validation; no revised annotation/review was selected. Original Task, CFG, annotation and review stay together.

Propagation: **451 processed / six unmodeled / 32 blocked**, zero typed operation execution faults; two missing_part diagnostics at ir_457/459 retain unrefined failure wrappers on success paths. Compared with parent coverage, four newly excluded roots account for 34 lost positions, while 15 positions are gained: **470 - 34 + 15 = 451**. Implementations/model answers differ across runs; this is not an encoding-only ablation. API **12/13**, save **24/25**, filesystem **7/7** denote source-boundary record reach. Manual audit still finds 13 omitted receiver dependencies and eight underdeclared/inconsistent response projections; reach does not establish semantic correctness.

Demand: **2,175 input assessments**, **2,942 required / 5,077 unresolved / zero deletable range entries**. There are 32 global Task-related blockers, 190 output-selector gaps over 62 IR, and 430 scoped contract-rejection diagnostics. Automatic `input_findings` is empty; independent source-audit findings must not be reported as automatically detected input mismatch results. Five unavailable_required_action diagnostics now demonstrate backward protection activation, without an end-to-end deletion-preservation result.

DOE: **103 sink records, 83,442 comparisons**, all `no_excess_established`, no reductions. This conclusion does not prove every input necessary. Comparison/assessment counts are not counts of unique source fields or actual leaks.

## Candidate scale and publication

Forensics finds 109,448 sensitivity derivations (108,600 possible, 848 direct), versus 912 in the parent. One hundred per-site environment-field credential declarations resolve to the same opaque environment Data; possible influence broadens through opaque computations. Four components of the same dateRange generate three alternatives each, then build emits **81 = 3^4** versions with empty condition bindings. A saved mixed object/default witness violates shared-source branch correlation. The largest sink has **34,668 = 81 x 428** distinct candidates. Candidate IDs/tuples are not literal duplicates; they include conservative and source-infeasible alternatives. These are not observations of plaintext credential leakage.

The backward demand_transfer contract must not erase actual forward reads or possible-flow records. Follow-up should supply source-faithful structured selections, validate seed provenance, introduce source-backed typed guards, and retain receiver/version relations. Shared evidence references and streaming publication should reduce report expansion while preserving every candidate and trace.

Published DOE JSON is **266,059,954 bytes**, HTML **3,938,066,348 bytes**, Markdown **3,697,695,105 bytes**. A single private-memory observation during publication was 19,285,307,392 bytes; it is not a resident/peak/OOM measurement. Measured analysis propagation compute/save: **2.669/126.551s**; DOE load/compute/total: **39.457/487.929/794.504s**; post-compute publication interval: **257.175s**. Nested intervals must not be summed. Replay DOE computation is not separately instrumented, so no exact replay component breakdown is invented.

## Cost, closure and retained evidence

Analysis **4,427.233s**; sole replay **958.102s**, matched, **zero new native starts**, native inventory unchanged. Actual new calls: **eight = four normal + two corrections + two shared-repair requests**. Public final counters: **1,417,149 input + 180,850 output = 1,597,999 tokens**; cached 86,016 and reasoning 35,693 are subsets. Three inherited calls/303,082 parent tokens are excluded. No main Responses retry events, native timeout, outer retry or prestart input rejection were recorded. Nine auxiliary catalog-refresh warnings are separately classified; they do not establish a main-request reconnect. Unreported provider-internal usage is unavailable. Request durations include connection/local/response time, not pure generation.

Integrity checks pass: **223 runtime pins, three executable pins, 16 source files, 83 inherited original files, 103 copied files, 102 parent sealed report/helper files and 36 parent sealed evidence files** unchanged. All ten recorded PIDs are absent. The one launch and one replay authorization is consumed; implementation/helpers remain frozen, and prior runs stay closed.

Bound evidence: [summary](run-summary.json), [requests](final-request-audit.json), [backend](final-backend-audit.json), [integrity](final-integrity.json), [review locality](review-locality-audit.json), [processing revision](revision-processing-audit.json), [candidate forensics](independent-candidate-scale-forensics.en.md), [follow-up proposal in Chinese](followup-plan.zh.md). Follow-up is unimplemented; no second online run is implied.
"""
    chinese = """# 无损交付修复与 GA4 最终结果

本轮通用无损交付修复已完成离线验证、同步 GitHub，并实际进入线上流程。GA4 最终为 **partial**，没有建立可删除输入；唯一一次零调用重放一致。不能据此宣称字段必要性功能已经在 GA4 上端到端成功。

## 代码与验证

代码已同步到 [GitHub 2b11000](https://github.com/southofborder/SkillFlow/commit/2b11000a1679421c578ac59e9f2dae8619ab864a)。原本地提交 3c7808ec 的完整相同树已通过 fetch 核对，原提交另有 codex 分支保留。接受实现 SHA256 为 `6126c7ba84984aec0d20ead0693df291ea3978a4072056dbd6428321bdfd627b`。

离线最新不同测试 **3,205 通过、2 跳过、0 未解决失败**，来自分组扫描和最终复查，不是一轮全仓全部通过；初始失败记录保留。

共享值/列编码已接入敏感性、Task 对应的正常、纠错和完整/局部修订入口，并检查 processing、graph 的局部输入。完整源文、Task 隔离、严格校验和历史协议身份保留。实际发送前记录 Unicode 字符数、UTF-8 字节数、分段/前缀体积及哈希。

## 新 GA4 的实际交付

唯一新运行：`document-guided-ga4-lossless-delivery-high-20261122-211742`。从关闭的 205158 继承 Task/flow、原选定 **215 blocks / 489 IR / 192 edges CFG** 和完整 **16 文件源文**，保留旧 producer。七正常阶段为三个继承、四个新正常请求；两个 worker 及现有纠错/共享修订/2700 秒/传输预算不变。没有执行 Skill 或真实 GA4 工具。

8 次实际交付全部通过 preflight，体积、哈希、逻辑内容一致且全部带完整源文。敏感性正常请求 **476,237 字符**、Task 对应 **516,118 字符**，均首答通过。固定相同逻辑内容只改变 JSON 编码，展开参照分别为 1,030,256、1,078,676 字符，节约 **554,019、562,558 字符**；后者展开参照超过适配器上限。不能把不同模型答复的历史运行当成编码的耗时/token 因果对照。两阶段纠错及修订路径本轮未实际触发，其证据为离线验证。

review 正常/纠错为 **909,828 / 918,793 字符**，graph 局部修订 **194,148**，processing 局部修订 **308,564**。没有输入拒绝、模型超时、主请求重连或外层重试记录。

## 为什么仍然 partial

1. 初始 processing 一次纠错只返回了 7 项 evidence 修正，漏掉获准的 3 条整记录和 5 个输出绑定。ir_167 未绑定局部变量，ir_311/329/346 嵌套 cases 无效；这些位置被严格隔离。最终有 483 个 modeled、6 个明确 unmodeled。
2. 源文审查完整记录 **431 项义务、1,929 个范围**；保留 **425 条有效检查**（386 通过、39 拒绝）及 **1,911 个范围决定**（1,654 通过、257 拒绝）。另 6 条/18 范围局部阻断。其原因是宽、窄主体共组后，影响列表错误落到窄主体；纠错修改了目标列表，未拆开主体。其余 425 条和原有 7 条 finding 保留，最终 46 条 finding（CFG 2、annotation 44）未被共享修订解决。并非整份审查失效。
3. graph 两项 region 补丁返回对象，而协议要求块数组，均未应用。即使纠正封装，当前保留原动作的区域权限也不能表达所提 clock 动作拆分。
4. processing 修订回应全部 27 个槽位，但 6 个改写操作缺 **24 项必需契约**，因此未接受。修订构造器漏带正常路径的条件必填规则，也没带相关既有 location 声明；模型由此把授权视图缺失误称为没有查询边界。完整源文仍在，缺的是修订语义上下文和规则。

原 Task、CFG、annotation 和绑定审查始终成套选中；失败修订未冒用旧审查。缺失语义契约不能用默认值补齐，也不能为提高成功率放宽校验。

传播 **451 已处理 / 6 未建模 / 32 阻断**，类型化操作执行错误为 0；ir_457/459 的两项 missing_part 仍来自成功路径未排除失败包装。与父运行相比，四个新排除根及后继损失 34 个位置，另获得 15 个位置：**470 - 34 + 15 = 451**。实现和模型答复均有差异，这不是仅改变编码的对照实验。

API **12/13**、save **24/25**、filesystem **7/7** 是边界记录到达率。独立源码核对仍有 13 个接收方依赖遗漏和 8 个响应投影关系不足的位置；这些记录不能代表语义正确。

## 删除分析的实际结论

有 **2,175 条输入评估**，范围条目 **2,942 required / 5,077 unresolved / 0 deletable**。仍有 32 项全局 Task 阻碍、62 个 IR 上的 190 项输出选择器缺口，以及 430 项局部契约拒绝诊断。自动 `input_findings` 为空；独立源码审计发现不能冒充系统自动检出的多余/错误输入。5 项 unavailable_required_action 诊断表明反向保护已触发，尚无实际删除后的端到端保持证据。

DOE **103 个 sink 记录、83,442 项比较**均为 `no_excess_established`，没有 reduction；这不等于证明所有输入都必要。范围与比较统计按使用位置、信息属性及推导计数，不是原始字段的去重数量。

## 为什么本地结果规模暴涨

敏感性推导本轮 **109,448** 条（108,600 possible、848 direct），父运行 912 条。有前向记录的 100 项按位置声明的环境凭据标记，定位到同一个 opaque live-environment Data；后续不透明计算按 possible 关系扩散到整个输出。

四个消费同一 dateRange 的组件各有三个候选，构造时得到 **81 = 3⁴** 个版本。保存结果包含同一参数一处走 object、其他处走 default 的不可行混合，且 alternatives 在构造前就没有形式化条件绑定。最大 sink 的 **34,668 = 81 × 428** 个候选有不同 ID，并非重复写同一行；其中包含过近似和不可行组合，不能称为真实凭据泄露。敏感性核心算法与父运行基本一致，这次数据形态触发了既有传播和组合的规模问题。

必须保留原始前向读取和观察。不能直接拿反向 demand_transfer 删除正向事实；应补齐有来源的字段选择、敏感源定位、typed guard、接收方及资源版本关系，再解释必要性和泄露结论。

已发布 JSON **266,059,954 字节**，HTML **3,938,066,348 字节**，Markdown **3,697,695,105 字节**。本地报告反复展开共享证据。单次观察到进程私有内存 19,285,307,392 字节，不是峰值或常驻内存测量，也无 OOM 证据。

测量到传播计算/保存 **2.669 / 126.551 秒**；DOE 加载/计算/总过程 **39.457 / 487.929 / 794.504 秒**，计算结束到发布完成 **257.175 秒**，嵌套区间不能相加。重放 DOE 计算没有独立埋点，不能虚构该部分精确耗时。

## 成本、封存与后续

分析 **4,427.233 秒**；唯一重放 **958.102 秒**、结果一致、0 新模型启动且启动清单未变。新模型启动 **8 次 = 4 正常 + 2 纠错 + 2 共享修订**。公开计数 **1,417,149 input + 180,850 output = 1,597,999 tokens**；缓存 86,016 和 reasoning 35,693 是其中子集。继承的 3 次调用/303,082 tokens 不计新成本。9 项辅助 catalog-refresh 警告单列，不能据此认定主请求重连；没有主 Responses 重试、外层重试、超时或输入超限记录，未披露的供应商内部用量无法得知。

完整性检查确认 **223 个 runtime pins、3 个可执行文件、16 个源文件、83 个继承原文件、103 个复制文件、父运行封存的 102 个报告/辅助文件及 36 个证据文件未变**；10 个记录 PID 均已退出。一次启动与一次重放授权已耗尽，历史运行保持关闭。

后续优先：统一所有入口的条件协议和只读依赖；把已知校验失败纳入实际修订范围并核验编辑能力；保持分支关联和源/接收方身份；以引用和流式发布消除报告重复展开。这些是建议，本轮没有追加实现或线上实验。

详见 [英文结果](assessment.en.md)、[结构化汇总](run-summary.json)、[修订和运行时后续方案](followup-plan.zh.md)、[独立规模取证](independent-candidate-scale-forensics.en.md)、[最终完整性检查](final-integrity.json)。
"""
    outputs = {"run-summary.json": json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
               "assessment.en.md": english, "assessment.zh.md": chinese}
    if any((HERE / name).exists() for name in outputs):
        raise ValueError("A final report already exists")
    for name, text in outputs.items():
        with (HERE / name).open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    state = read(HERE / "continuation-state.json")
    state.update(status="closed", analysis_status=controller["status"],
                 analysis_seconds=controller["analysis_seconds"], replay=controller["replay"],
                 dispatch_consumed=True, replay_consumed=True,
                 next="No restart, extra replay, Skill execution, probes, resampling, automatic follow-up implementation or new online run. Read the sealed result and unimplemented follow-up proposal; wait for new explicit instructions.")
    (HERE / "continuation-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "written", "reports": list(outputs)}))


if __name__ == "__main__":
    main()
