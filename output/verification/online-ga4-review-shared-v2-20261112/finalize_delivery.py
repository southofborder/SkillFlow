"""Publish reports and close navigation for the sole finished GA4; no analysis."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
OFFLINE = VERIFY.parent / "review-input-size-20261112"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(path, value):
    with path.open("x", encoding="utf-8") as handle:
        if isinstance(value, str):
            handle.write(value)
        else:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")


def main():
    prepared = read(VERIFY / "prepared-run.json")
    run = Path(prepared["run_directory"])
    finish = read(run / "controller-finished.json")
    replay = read(run / "replay-check.json")
    result = read(run / "result.json")
    cost_summary = read(VERIFY / "cost-provenance-audit/final-cost-summary.json")
    cost = read(VERIFY / cost_summary["source_audit"])
    necessities = read(VERIFY / "final-necessity-audit.json")
    source = read(VERIFY / "final-source-coverage.json")
    review = read(VERIFY / "final-review-audit.json")
    delivery = read(VERIFY / "review-delivery-audit.json")
    offline = read(OFFLINE / "offline-acceptance.json")
    regression = read(OFFLINE / "integrated-delivery-measurement.json")
    support = read(run / "doe/audit/demand-support.json")
    doe = read(run / "doe/doe-result.json")
    range_counts = Counter(r["status"] for a in support["input_assessments"] for r in a["ranges"])
    comparisons = [row for sink in doe["sinks"] for row in sink["data_reviews"]]
    conclusions = Counter(row["conclusion"] for row in comparisons)
    assert dict(range_counts) == {k: v for k, v in necessities["input_assessments"]["range_statuses"].items() if v}
    assert dict(conclusions) == necessities["doe"]["conclusions"]
    assert finish["status"] == result["status"] == "partial"
    assert replay["status"] == "matched" and replay["new_native_markers"] == 0
    assert cost["final_observation"] and not cost["issues"] and not cost["warnings"]
    assert cost_summary["status"] == "verified" and cost_summary["native_starts"] == 12
    assert sha(VERIFY / cost_summary["report"]) == cost_summary["report_sha256"]
    assert read(run / "implementation-check.json")["unchanged"]
    assert offline["implementation_sha256"] == prepared["implementation_sha256"]
    previous = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"
    for name, digest in regression["original_artifact_hashes_unchanged"].items():
        assert sha(previous / name) == digest, name
    counts = necessities["input_assessments"]
    summary = {
        "status": "closed_partial_reports_delivered", "recorded_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(run), "analysis_status": result["status"],
        "implementation_sha256": prepared["implementation_sha256"], "source_sha256": prepared["source_sha256"],
        "source_files": 16, "guided_run_identity": "skillflow-document-guided-run-v12", "review_view": "shared-v2",
        "offline_acceptance": {"passed": 511, "skipped": 0, "failed": 0, "whole_repository_run": False},
        "analysis_seconds": finish["analysis_seconds"], "replay": replay,
        "stages": result["stages"], "repair_used": result["repair_used"],
        "review_deliveries": cost["review_deliveries"],
        "review_expected_obligations": 271, "review_expected_scopes": 1045,
        "accepted_contract_checks": 0, "raw_candidate_checks": {"accepted_label": 227, "rejected_label": 43, "unresolved_label": 1},
        "raw_candidate_checks_are_accepted_evidence": False,
        "source_review_failure": "Three missing_field source-input findings used absent_argument, then empty input_range paths after the sole correction; no accepted review and no semantic repair.",
        "source_coverage": source["counts"], "input_assessments": counts,
        "input_findings": necessities["input_findings"],
        "unresolved_reference_buckets": necessities["unresolved_attribution"]["exclusive_diagnostic_reference_buckets"],
        "doe_comparisons": dict(conclusions), "doe_reductions": sum(row["reduction"] is not None for row in comparisons),
        "cost": cost_summary, "known_public_usage": cost["known_public_usage"],
        "returned_model": cost["returned_model"], "provider_billing_cost": cost["provider_billing_cost"],
        "old_artifacts_unchanged": True,
        "causal_boundary": "The original failed request fits after lossless rendering. This fresh run's same material already narrowly fits compact-v1 (1038128); shared-v2 saves 176976 further characters. Online admission alone is not evidence the old format would reject this fresh material.",
        "limitations": result["limitations"],
        "authorization_consumed": True, "additional_models_or_replays_authorized": False,
        "reports": ["assessment.en.md", "assessment.zh.md", "final-cost-provenance.en.md", "final-review-audit.en.md", "final-source-coverage.en.md", "final-necessity-audit.en.md"]}
    create(VERIFY / "run-summary.json", summary)
    english = f"""# Generic review display: GA4 online assessment

The general lossless source-review fix is implemented and offline accepted. This one fresh GA4 run and its sole zero-call replay are **closed**. Both actual source-review requests fit the unchanged input cap and retained complete material. The analysis nevertheless remains **partial** because the review's source-input defect records failed structural validation after its one correction. No deletable input or DOE reduction was established.

## Implementation and scope

The default guided run v12 / shared-v2 presentation applies to every Skill. It selects exact shared JSON values and inventory column tables only when the complete presentation, including its explanation, is shorter. There are no GA4-name, path or IR-count branches. Full source is unchanged. Semantic contracts, actual forward inputs, Task v5 isolation, seven normal requests, two workers and existing budgets remain unchanged.

The accepted implementation is `{prepared['implementation_sha256']}`. Final offline acceptance passed **511 scoped tests, zero skips/failures** in one integrated execution; it was not a whole-repository run. Only review_display.py, source_review.py and runner.py changed in the production inventory. See [design](../../../docs/doe/review-input-size.md), [Chinese design](../../../docs/doe/review-input-size.zh.md) and [acceptance](../review-input-size-20261112/offline-acceptance.json).

## Input-size result and preservation

The prior rejected request had 1,079,505 Unicode codepoints: logical JSON 874,402, complete numbered source 180,825 and instructions/schema/envelope/delimiters 24,278. Annotation (403,839) and the mandatory inventory (244,455) dominated the logical JSON. Local audit metadata was already excluded; there was no duplicate full-fragment delivery. This was an adapter pre-start character-cap rejection, not a connection timeout.

| Material and comparison | Original display | New complete delivery | Saving / headroom |
| --- | ---: | ---: | --- |
| Same historical failed material, offline rendering only | 1,079,505 | 903,775 | 175,730 saved; 144,801 below cap |
| Same fresh material, normal real review | 1,038,128 | 861,152 | 176,976 saved; 187,424 below cap |
| Actual bounded review correction | — | 867,125 | 181,451 below cap |

The cap remains 1,048,576 codepoints. Both real deliveries retained all **271 physical review obligations, 1,045 scopes and 16 complete source files**. Exact expansion matched the original logical payload, including ordering, field types, contract bodies, identities and evidence. The correction retained the complete base prompt and changed only three response records. Initial assembly's 16 gaps, including four unmodeled IR, remained visible; they were not compression omissions. [Delivery proof](review-delivery-audit.en.md), [both-request audit](final-review-audit.en.md).

The fresh material also narrowly fit the old display, so this run's admission alone does not show that the old format would have rejected it. The separate same-material historical rendering regression demonstrates that the original overflow was fixed. Neither roundtrip nor a model process launch proves semantic correctness. Irreducibly large complete material can still exceed a finite cap; it is never truncated.

## Why review was not accepted

The first response proposed 271 contract checks (227 accepted labels, 43 rejected labels, one unresolved), 15 ordinary findings and three source-input findings concerning filters, orderBy and limit at ir_119. These are **raw model proposals, not accepted review evidence**.

Each source finding declared missing_field but used absent_argument. The sole structural correction replaced those records with input_index 0 and an empty field path. The remaining diagnostic was `A missing field must locate its nonempty path within an actual operand`. The stage exhausted its existing one-correction budget and ended structural_failure. Its authoritative receipt contains **zero accepted contract checks and zero accepted source-review findings**. Semantic repair requires an accepted completed review with findings, so it did not run. No extra request, repair budget or resampling was added. [Exact records and hashes](final-review-audit.json).

The terminal failure was therefore a response-location schema failure, not an input-length rejection or a 2,700-second native timeout. Reconnection events did occur separately, as recorded below.

## Coverage and input necessity

The selected CFG remains the initial accepted graph: 237 blocks, 222 edges and 511 IR. Static propagation processed **487/511**, with four unmodeled and 20 blocked positions. Processed status is not executed source coverage or proof of faithful boundary modeling.

| Physical source sites | Represented in CFG | IR processed | Correct boundary in records |
| --- | ---: | ---: | --- |
| 13 remote API calls | 13 | 9 | 6 network sends; 3 processed calls were local-tool substitutes, 4 unmodeled |
| 25 saveResult calls | 25 | 21 | 0 caller-specific persistence boundaries; 21 local-tool deliveries, 4 blocked |

Standalone storage records exist separately at ir_442 and ir_454; they do not instantiate each caller's payload/version. Ten loop structures processed, but successful per-member remote effects are missing in several cases. The Markdown summary writer remains absent. The original unused filters/orderBy reads appear in CFG metadata but are not preserved as distinct compiled field reads. Local diagnostics also remain at some processed positions. Thus this run does not validate complete boundary coverage or the original-read-preservation acceptance example on GA4. [Full source audit](final-source-coverage.en.md).

There are **1,517 input assessments and 3,922 emitted range records**: **1,113 required, 2,809 unresolved, zero deletable**. These are range entries, not disjoint unique fields. Coverage is 1,484 processed assessments, 24 blocked and nine unmodeled. All 116 acquisition projections remain unestablished. All 121 DOE comparisons are no_excess_established; there are no reductions or input modifications. This does not prove every input necessary or the Skill free of DOE.

Unresolved evidence is not attributed solely to review failure: 1,272 entries reference local contract-unavailability diagnostics; 1,430 reference global Task/mapping limitations (656 also reference local issues); 107 have no diagnostic_refs, comprising 87 explicit operand-to-metadata binding gaps and 20 conservative-transfer entries with demand references. There are 177 contract-unavailability diagnostics across 64 IR and 103 operations. Thirty wrong_input findings originate in demand_analysis as expected-original-value relation mismatches; they are not accepted versions of the three raw source findings. The precision and adequacy of these unresolved reasons are not established by compression or replay. [Necessity audit](final-necessity-audit.en.md).

Initial source-only processing audit also found root-only opaque transfer rules and current-argument-only interface evidence. Those quality concerns remain separate from complete delivery and were not repaired in this run. [Initial processing audit](processing-audit.en.md).

## Timing, cost and closure

Requested runtime was gpt-6.1-sol/high/openai, with two workers and the same complete source package. The run started 2026-11-12 22:13:21 China time; the controller closed 2026-11-13 00:33:52. Main analysis took **8,255.173 seconds**. Its sole replay matched in **174.913 seconds**, with **zero new native starts**.

Actual cost for this fresh run is **12 confirmed native starts = seven normal + five structural corrections**; semantic repair and outer retries were zero. Public final usage is complete for all 12: **2,296,735 tokens = 2,054,895 input + 241,840 output**. Cached input 924,416 and reasoning output 8,916 are subsets, not additions. No provider billing amount or public returned-model metadata is available; unreported provider-internal retry usage remains unknown. Prior attempts are not included in this total.

Ten internal CLI retry log lines comprise three TLS peer closes, one WebSocket close, three OS 10054 resets and three internal request timeouts. They are not ten extra native starts and cannot establish an HTTP-attempt total. All 12 native processes returned exit code 0 below the 2,700-second cap; final review failed validation after return. No public tool-execution events appeared. [Complete available cost, stage durations and provenance](final-cost-provenance.en.md).

The controller/wrapper exited. All 199 pinned implementation/transport/renderer files, 16 source files and additional executable/helper pins matched; historical tracked artifacts remain unchanged. No Skill was executed, old run resumed or historical analysis replayed. The generated DOE report's “Offline preparation; zero API calls” describes its deterministic DOE substage, not this 12-request online pipeline.

The single new-run and sole-replay authorizations are consumed. Preserve all failures and raw proposals. No further run or replay was launched. [Machine-readable summary](run-summary.json).
"""
    chinese = """# 源文审查通用修复与 GA4 本轮结果

通用修复已完成并通过离线验收；新一轮 GA4 及唯一零调用重放已关闭。两次真实审查请求都完整送入模型，没有再因长度被拒绝。但最终分析仍为 **partial**，原因是三条源输入缺陷定位记录未通过结构校验，不能把未接纳的候选检查当作已核验契约。

## 通用代码与输入大小

新代码对所有 Skill 默认使用 shared-v2，不按 GA4 名称、路径或 IR 数量特判。共享完全相同的 JSON 值，并以列名和行值表示契约清单；连同格式说明确实更短时才启用，否则保持原 JSON。源文、契约、范围和原始坐标均保留。保持七次正常请求、两个 worker、Task v5 隔离和原有预算。

最终受影响模块集成回归 **511 项通过，零跳过、零失败**，不是一次全仓库测试。原失败请求在同材料离线回归中由 **1,079,505 降至 903,775 字符**，完整保留 16 文件、344 审查项和 1,195 范围。

本轮实际普通审查为 **861,152 字符**，结构纠错为 **867,125 字符**，均低于未改变的 1,048,576 上限；保留全部 **271 个审查项、1,045 个范围和 16 份源文**。本轮同材料旧展示为 1,038,128，也会勉强低于上限，因此线上成功进入模型不能单独证明旧格式本轮必然失败；原超限修复的证明来自前面的同材料离线回归。本轮新展示另外节省 176,976 字符。

## 为何最终仍是 partial

模型首次答复提出 271 条契约检查、15 条普通发现和 3 条源输入发现。后三条均把 missing_field 写成 absent_argument；唯一结构纠错后又给出空字段路径，仍违反“缺失字段必须定位到真实输入中的非空路径”。因此 **0 条契约检查被正式接纳**，也没有进入语义修复。原答复中 227 个 accepted 标签不是通过审查的证据。

传播处理 **487/511 条 IR**，4 条未建模、20 条受阻。源文核对显示：13 个实际远程 API 位置只有 6 个记录了相应网络边界；另有 3 个被表示为本地工具、4 个未建模。25 个保存调用中，21 个只记录本地工具传递、4 个受阻；调用处均未建立持久化边界。独立存储函数的记录不能替代各调用位置及成员版本的持久化事实。总结写入和部分成功循环分支的远程副作用也有覆盖缺口。

最终 1,517 项输入评估包含 3,922 条范围记录：**1,113 required、2,809 unresolved、0 deletable**。121 项 DOE 比较均为 no_excess_established，没有删除修改或 DOE 缩减。30 条 wrong_input 来自反向需求计算中的关系不匹配，不能当作那 3 条未被接纳的源文发现。未决同时来自审查不可用、全局 Task／映射限制、局部覆盖和绑定缺口，并非全部由审查失败造成；也不能据此断言所有输入都必要。

## 实际用量与封存

2026-11-12 22:13 启动，2026-11-13 00:33 关闭。主分析 **8,255.173 秒**，唯一重放 **174.913 秒**、结果一致、零新增启动。实际 **12 次原生模型启动＝7 次正常＋5 次结构纠错**，语义修复和外层重试均为 0。12 次最终公开用量全部可见，共 **2,296,735 tokens**；未公开的服务端内部重试成本仍未知。

日志另有 10 条 CLI 内部重试，其中 3 条 request timed out；没有原生进程触及 2,700 秒超时。最终失败原因是返回结果的定位结构校验，不是输入长度或原生进程超时。实现、传输、执行程序及 16 份源文哈希保持一致，未执行 Skill，未重放历史运行，也未增加实验。

本轮授权和唯一重放已用完。报告保留全部失败证据；当前后续阻碍是审查定位格式及已发现的建模覆盖问题。

证据：[英文总报告](assessment.en.md)、[机器摘要](run-summary.json)、[输入与审查核对](final-review-audit.en.md)、[源文覆盖](final-source-coverage.en.md)、[必要性评估](final-necessity-audit.en.md)、[完整可见用量](final-cost-provenance.en.md)、[通用设计](../../../docs/doe/review-input-size.zh.md)。
"""
    create(VERIFY / "assessment.en.md", english)
    create(VERIFY / "assessment.zh.md", chinese)
    state = read(VERIFY / "continuation-state.json")
    state.update(status="closed_reports_delivered", analysis_status="partial", replay=replay,
                 actual_native_starts=12, known_public_tokens=2296735, reports=summary["reports"],
                 instructions="Closed. The sole new run and sole zero-call replay are consumed. Preserve raw evidence. No further model run, probe, Skill execution, historical replay/resume, resampling or frozen artifact rewrite is authorized by this completed task.")
    (VERIFY / "continuation-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    offline_state = read(OFFLINE / "continuation-state.json")
    offline_state.update(status="offline_accepted_online_followup_closed", online_followup_status="partial",
                         online_followup_summary=str((VERIFY / "run-summary.json").relative_to(PROJECT)),
                         new_model_starts_in_online_followup=12)
    (OFFLINE / "continuation-state.json").write_text(json.dumps(offline_state, indent=2) + "\n", encoding="utf-8")
    headline = ("Shared-v2 GA4 CLOSED (2026-11-13): generic lossless source-review display passed 511/511 current scoped tests (not a whole-repository run). "
                f"Implementation {prepared['implementation_sha256']} remained frozen. Sole new run {run.relative_to(PROJECT).as_posix()} and sole zero-call replay are CLOSED. "
                "Review deliveries 861152/867125 chars retained all 271 obligations,1045 scopes and16 source files; no input rejection. "
                "Result partial: 3 missing_field records still had empty paths after one correction, so 0 accepted contract checks and no semantic repair. "
                "Propagation487/511 (4unmodeled,20blocked); source-faithful direct remote boundaries6/13 and caller storage boundaries0/25. "
                "1517 input assessments:1113 required/2809 unresolved/0deletable range entries;121 DOE comparisons all no_excess_established. "
                "Actual12 native starts=7normal+5corrections,2296735 known public tokens, all final usages visible; outer retries0. Replay matched174.913s/0new starts. "
                "Read output/verification/online-ga4-review-shared-v2-20261112/assessment.en.md, assessment.zh.md and run-summary.json. "
                "This launch/replay authorization is consumed: no extra model run/probe/replay, Skill execution, historical resume, frozen artifact rewrite or staged-worktree import. "
                "Earlier active notes below are consumed history.\n\n")
    agents = PROJECT / "AGENTS.md"
    agents.write_text(headline + agents.read_text(encoding="utf-8"), encoding="utf-8")
    navigation = {
        "docs/current-version.md": "Latest result (2026-11-13): the generic shared-v2 display is offline accepted (511 scoped passes), and its sole new GA4/replay are closed. Complete review deliveries fit the unchanged cap, but review failed source-input field-location validation; analysis remains partial, with zero deletable ranges or DOE reductions. Actual cost: 12 native starts and 2,296,735 known public tokens; replay matched with zero new starts. See [English assessment](../output/verification/online-ga4-review-shared-v2-20261112/assessment.en.md), [Chinese assessment](../output/verification/online-ga4-review-shared-v2-20261112/assessment.zh.md) and [summary](../output/verification/online-ga4-review-shared-v2-20261112/run-summary.json). The one-run/replay authorization is consumed; earlier active notes below are history.\n\n",
        "docs/research-chat-handoff.md": "Latest closure (2026-11-13): shared-v2 generic review delivery and offline acceptance are complete. The sole fresh GA4 and replay are closed, partial, with no deletable input. Input size is fixed; three malformed missing-field findings prevented accepted source review. See [current version](current-version.md) and `output/verification/online-ga4-review-shared-v2-20261112/run-summary.json`. No extra run/replay, old resume, Skill execution or frozen artifact rewrite is authorized by this closure. Earlier active notes are history.\n\n",
        "docs/README.md": "2026-11-13 最新结果：[通用源文审查展示修复](doe/review-input-size.zh.md)通过 511 项分范围测试；新 GA4 与唯一零调用重放已关闭。完整审查请求均未超限，但三条字段定位格式错误使审查未被接纳，最终仍为 partial，未建立可删除输入。见[本轮中文报告](../output/verification/online-ga4-review-shared-v2-20261112/assessment.zh.md)。本轮启动／重放授权已用完，下列活动描述保留为历史。\n\n"}
    for name, paragraph in navigation.items():
        path = PROJECT / name
        contents = path.read_text(encoding="utf-8")
        title, rest = contents.split("\n", 1)
        path.write_text(title + "\n\n" + paragraph + rest.lstrip("\n"), encoding="utf-8")
    report_names = summary["reports"] + ["run-summary.json", "final-review-audit.json", "final-source-coverage.json", "final-source-coverage-closed-binding.json", "final-necessity-audit.json", "review-delivery-audit.json", cost_summary["source_audit"]]
    create(VERIFY / "delivery-seal.json", {"sealed_at": datetime.now(timezone.utc).isoformat(),
        "reports": {name: sha(VERIFY / name) for name in report_names},
        "run_receipts": {name: sha(run / name) for name in ("result.json", "selection.json", "controller-finished.json", "replay-check.json", "implementation-check.json", "metrics.json", "review/result.json", "doe/doe-result.json")},
        "offline_acceptance_sha256": sha(OFFLINE / "offline-acceptance.json"), "historical_artifacts_unchanged": True})
    print(json.dumps({"status": state["status"], "native_starts": 12, "known_public_tokens": 2296735,
                      "input_ranges": dict(range_counts), "doe": dict(conclusions), "replay": replay}, indent=2))


if __name__ == "__main__":
    main()
