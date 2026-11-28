"""Read-only source/run audit; writes derived evidence only beneath analysis/001-audit/."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "pilot/001"
OUT = BASE / "analysis/001-audit"
sys.path.insert(0, str(BASE / "source/packages/semia-core/src"))
from semia_core.checker import CheckOptions, check_program
from semia_core.evidence import align_evidence_text
from semia_core.facts import parse_facts
from semia_core.pipeline import _load_prepare_units


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(name: str, value: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def main() -> None:
    prepared = _load_prepare_units(RUN/"artifacts")
    candidates = []
    for path in sorted((RUN/"artifacts").glob("synthesis_attempt_*.dl")):
        raw = path.read_bytes()
        program = parse_facts(raw.decode("utf-8"))
        check = check_program(program, options=CheckOptions(require_include=True))
        alignment = align_evidence_text(program, prepared)
        errors=[asdict(x) for x in check.errors]
        taint_failed=alignment.evidence_match_rate < 0.1
        if taint_failed:
            errors.append({"code":"EVD020","line":0,"severity":"error",
                           "message":f"evidence_match_rate {alignment.evidence_match_rate:.3f} below taint threshold 0.100; facts reference text not present in prepared_skill.md (possible hallucination or prompt-injection-induced facts)"})
        record = {
            "candidate": path.name, "sha256": sha(raw),
            "basis": "offline_read_only_recheck_of_original_candidate_no_new_model_call",
            "raw_structural_program_valid":check.program_valid,
            "program_valid": check.program_valid and not taint_failed,
            "errors": errors,
            "warnings": [asdict(x) for x in check.warnings],
            "error_codes": dict(Counter(x["code"] for x in errors)),
            "arity_error_messages":dict(Counter(x["message"] for x in errors if x["code"]=="SDL003")),
            "evidence_support_coverage": check.evidence_support_coverage,
            "evidence_match_rate": alignment.evidence_match_rate,
            "reference_unit_coverage": alignment.reference_unit_coverage,
            "evidence_taint_failed": taint_failed,
        }
        save(path.stem+".json", record)
        candidates.append({k: record[k] for k in ["candidate","sha256","program_valid","error_codes",
                                                "arity_error_messages","evidence_match_rate","evidence_support_coverage","reference_unit_coverage"]}
                          | {"errors": len(errors), "warnings": len(check.warnings)})
    calls = []
    for path in sorted((RUN/"transport").glob("call-*/request.json")):
        record = json.loads(path.read_text("utf-8"))
        event_types = Counter()
        event_errors = []
        turn_errors=[]
        for line in (path.parent/"stdout.jsonl").read_text("utf-8",errors="replace").splitlines():
            try: event=json.loads(line)
            except ValueError: continue
            if event.get("type") in {"error","turn.failed"}:turn_errors.append(event)
            if event.get("type") == "item.completed":
                item=event.get("item",{})
                event_types[item.get("type","unknown")]+=1
                if item.get("type") == "error": event_errors.append(item.get("message"))
        calls.append({k:record.get(k) for k in ["id","native_start","returncode","elapsed_seconds","usage","timed_out"]}
                     | {"public_item_types":dict(event_types),"public_item_errors":event_errors,
                        "public_turn_errors":turn_errors,
                        "prompt_sha256":sha((path.parent/"prompt.txt").read_bytes()),
                        "phase":"recommendation" if (path.parent/"prompt.txt").read_text("utf-8").startswith("# Semia Recommendation") else "synthesis",
                        "internal_sampling_retry_lines":[line for line in (path.parent/"stderr.txt").read_text("utf-8",errors="replace").splitlines()
                                                         if "retrying sampling request" in line]})
    finished_path=RUN/"finished.json"
    finished=json.loads(finished_path.read_text("utf-8")) if finished_path.exists() else None
    metadata_path=RUN/"artifacts/synthesis_metadata.json"
    metadata=json.loads(metadata_path.read_text("utf-8")) if metadata_path.exists() else None
    log_path=BASE/"logs/controlled-pilot-001.log"
    terminal_messages=[line for line in log_path.read_text("utf-8",errors="replace").splitlines() if "semia:" in line] if log_path.exists() else []
    runtime=json.loads((RUN/"runtime.json").read_text("utf-8"))
    changed_source=[p for p,h in runtime["source_file_hashes"].items()
                    if sha((BASE/"source"/p).read_bytes()) != h]
    adapter_unchanged=sha((BASE/"run_controlled_pilot.py").read_bytes()) == runtime["adapter_sha256"]
    usages=[c["usage"] for c in calls if c.get("usage")]
    initial_prompt_hash=calls[0]["prompt_sha256"] if calls else None
    totals={key:sum(u.get(key,0) for u in usages) for key in
            ["input_tokens","output_tokens","cached_input_tokens","cache_write_input_tokens","reasoning_output_tokens"]}
    totals["input_plus_output_tokens"]=totals["input_tokens"]+totals["output_tokens"]
    aggregate_errors=Counter()
    aggregate_arity=Counter()
    for candidate in candidates:
        aggregate_errors.update(candidate["error_codes"])
        aggregate_arity.update(candidate["arity_error_messages"])
    final_check_comparison=None
    original_check_path=RUN/"artifacts/synthesis_check.json"
    if finished and candidates and original_check_path.exists():
        original_check=json.loads(original_check_path.read_text("utf-8"))
        save("original-final-synthesis-check.json",original_check)
        final_recheck=json.loads((OUT/Path(candidates[-1]["candidate"]).with_suffix(".json")).read_text("utf-8"))
        final_check_comparison={"candidate":candidates[-1]["candidate"],
                                "original_check_sha256":sha(original_check_path.read_bytes()),
                                "errors_equal":original_check["errors"]==final_recheck["errors"],
                                "warnings_equal":original_check["warnings"]==final_recheck["warnings"],
                                "program_valid_equal":original_check["program_valid"]==final_recheck["program_valid"]}
    result={"observed_at_utc":datetime.now(timezone.utc).isoformat(),"status":"finished" if finished else "running",
            "finished":finished,"candidate_count":len(candidates),"valid_candidates":sum(c["program_valid"] for c in candidates),
            "candidates":candidates,"calls":calls,"known_public_usage":totals,
            "usage_missing_count":sum(c.get("native_start",False) and c.get("usage") is None for c in calls),
            "internal_sampling_retry_log_count":sum(len(c["internal_sampling_retry_lines"]) for c in calls),
            "calls_identical_to_initial_prompt":[c["id"] for c in calls if c["prompt_sha256"]==initial_prompt_hash],
            "new_model_calls_by_audit":0,"skill_executions_by_audit":0,
            "source_file_count_verified":len(runtime["source_file_hashes"]),
            "changed_source_files":changed_source,"adapter_unchanged":adapter_unchanged,
            "synthesis_metadata":metadata,"terminal_messages":terminal_messages,
            "aggregate_error_counts":dict(aggregate_errors),"aggregate_arity_message_counts":dict(aggregate_arity),
            "candidates_without_arity_errors":[c["candidate"] for c in candidates if not c["arity_error_messages"]],
            "final_original_check_comparison":final_check_comparison,
            "downstream_artifacts":{name:(RUN/"artifacts"/name).exists() for name in ["detection_result.json","detection_findings.dl","report.md","recommendation.md"]},
            "accuracy":"not_evaluated","native_failure_vs_structural_rejection":"reported separately"}
    save("summary.json",result)
    rows="\n".join(f"| {c['candidate']} | {c['errors']} | {c['warnings']} | {'通过' if c['program_valid'] else '拒绝'} | {', '.join(f'{k}×{v}' for k,v in c['error_codes'].items())}; {'; '.join(f'{k} × {v}' for k,v in c['arity_error_messages'].items())} |"
                    for c in candidates)
    call_rows="\n".join(f"| {c['id']} | {c['phase']} | {c['returncode'] if c['returncode'] is not None else '进行中'} | {c['elapsed_seconds'] if c['elapsed_seconds'] is not None else '未完成'} | {(c['usage']['input_tokens']+c['usage']['output_tokens']) if c['usage'] else '未知'} |"
                         for c in calls)
    state="已取得完成回执" if finished else "仍在运行；本文件是中途观察，不是最终结果"
    completion=f"完成回执 exit_code={finished['exit_code']}，总耗时 {finished['elapsed_seconds']} 秒；终止消息：{' / '.join(terminal_messages) or '无 semia 终止消息，须查看完整日志'}。" if finished else "尚未取得结束回执。"
    if finished and not result["valid_candidates"] and not any(result["downstream_artifacts"].values()):
        completion += " 合成/校验阶段没有得到有效候选；没有产生检测、报告或推荐结果。这里的检测结果是未运行，不能记成零告警或安全。"
        if metadata:
            completion += f" metadata保留 {len(metadata.get('iterations',[]))} 轮、accepted chain为空、selected_iteration=null，completed=false/stop_reason=null；这是原版在无有效候选时先抛异常、未走成功收尾路径的结果，不代表仍在运行。finished.error=null也不代表成功，应以exit_code和终止消息为准。"
    final_budget_note=(f"最终只有 {sum(bool(c.get('native_start')) for c in calls)} 次原生启动，其中 recommendation={sum(c['phase']=='recommendation' for c in calls)}；未达到60的冻结runner上限，因此60/63差异没有截断本例。" if finished and len(calls)<60 else "尚需最终回执判定该上限是否影响本例。")
    integrity_note=(f"最终原版 synthesis_check 与最后候选离线重核的 errors、warnings、program_valid 均一致；原始check SHA-256为 `{final_check_comparison['original_check_sha256']}`，副本与对照标记保存在analysis目录。" if final_check_comparison and all(final_check_comparison[k] for k in ('errors_equal','warnings_equal','program_valid_equal')) else "最终原版check对照待完成回执后记录，详见summary字段。")
    native_status_note=("20个原生请求均正常退出并各产生1份候选，完整执行5轮×4次候选生成（15次结构重试）；本例未发生上游provider重新调用或2700秒原生超时。原生exit=0只表示文本请求完成，Semia总exit=2表示生成结果均未通过校验。" if finished and len(calls)==20 and len(candidates)==20 and all(c['returncode']==0 for c in calls) and not result['valid_candidates'] else "原生请求状态和结构校验结果分开统计。")
    text=f'''# Semia 001 首例失败机制核查

观察时间（UTC）：{result['observed_at_utc']}。状态：**{state}**。

本核查只读取原始回答、候选、提示、回执及固定源码，用上游纯函数重新检查候选并写到独立 `analysis/001-audit/`，没有模型调用、Skill 执行或 active run 改动。全部重核记录保留候选 SHA-256。报告状态和统计可由 `audit_001.py` 再次只读更新。

适用范围是固定 `379bc25f / v0.1.3` 的 **Semia + controlled transport**，`gpt-6.1-sol / high / openai` 与 builtin 后端。本报告不把此配置的失败外推为所有模型下的 Semia 失败，也不冒称论文原配置复现。精确配置见 [runtime.json](../pilot/001/runtime.json)。

适配差异包括无工具文本调用、每请求独立工作目录、忽略用户/项目配置、记录公开事件，以及将单次timeout从上游默认600秒设为2700秒。builtin是官方支持的本地后端，但本机未完成Soufflé等价性验证。固定源码并不等于原封不动的论文、原生Codex或宿主插件路径复现；本轮结论仅适用于这些已列出的运行条件。

## 当前结果及成本

{completion}

已观察 {len(calls)} 个原生请求目录，{len(candidates)} 个候选，其中 {result['valid_candidates']} 个通过结构校验。已公开 input tokens={totals['input_tokens']}，output tokens={totals['output_tokens']}，合计 **{totals['input_plus_output_tokens']}**；reasoning tokens 是 output 的子计数，不重复相加。缺公开用量的已启动请求有 {result['usage_missing_count']} 个，provider 内部未披露用量仍未知。

全部候选的错误累计为 {dict(aggregate_errors)}；这是重复候选中的出现次数，不能当作独立漏洞数量。逐个参数错误按谓词统计：{dict(aggregate_arity)}。原生内部 sampling retry 日志共 {result['internal_sampling_retry_log_count']} 条，独立于上游provider重试及原生启动次数。

固定源码核验 {result['source_file_count_verified']} 个文件，变更 {len(changed_source)} 个；首例adapter未变={adapter_unchanged}。{integrity_note}

| 请求 | 阶段 | native exit | 耗时／秒 | 已知 input+output tokens |
| --- | --- | ---: | ---: | ---: |
{call_rows}

{native_status_note}

这些是工程首例成本，没有独立 gold，准确率与召回率为 `not_evaluated`。接收到模型回答和引文能够匹配，不等于候选结构有效或隐私结论正确。

表中 native 耗时包含CLI启动、传输/重连、模型处理和进程结束等阶段，不能全部解释为纯模型推理时间。旧SkillFlow参考运行不构成当前同版本、同预算的严格配对结果。

| 原始候选 | errors | warnings | 原版结构校验 | 错误代码 |
| --- | ---: | ---: | --- | --- |
{rows}

## 已证实的失败链

首三份候选分别有 8/12/7 个 error：其中 6/10/5 个是 `action_evidence_text` 或 `call_evidence_text` 的三参数输出，而 schema 要求两个；其余均含 `v_access_token` 缺少 `value_secret_allowed_action`（SDL050）以及 `c_read_events` 同时标注 untrusted 与 secret（SDL061）。首轮 12 个 warning 对应六个错误 sidecar 未命中 core fact 和六个 core fact 缺 typed evidence，不是额外十二个独立语义遗漏。

第5份候选的六个 SDL003 则是**另一类**：`action_param_evidence_text` 期望4参、实给3参；不是 action/call evidence 的额外参数错误。SDL003只是统一错误代码，必须按具体谓词及期望/实际参数数目区分。分析者曾在中途消息中仅凭代码计数把第5份误概括为 entity evidence，已纠正；原始重核 JSON 从始至终保留了正确的逐条 message。

第15、17、19份候选（`synthesis_attempt_3_2.dl`、`synthesis_attempt_4_0.dl`、`synthesis_attempt_4_2.dl`）均已没有 SDL003，warnings=0、evidence_support_coverage=1.0，仍因 SDL050 与 SDL061 两项拒绝。这是原运行内直接观察到的证据：参数语法问题并非唯一阻断因素；它不是额外修正或消融实验，也不能当作语义内容已经全部正确。

1. **提示通则与 schema 特例矛盾。** 首请求 `prompt.txt` 的 Evidence Sidecar 通则要求参数镜像 core fact 并追加引文；但同一提示中的 action/call 示例只给实体 ID 与引文。固定 `schema.py` 的 `_ENTITY_EVIDENCE_ARITIES` 也明确 action/call 为2。模型在首三份回答反复采用了通则自然导出的3参写法。这能证明提示不一致与观察错误相符，尚不能证明它是所有失败的唯一原因。
2. **详细检查结果没有进入纠错输入。** `semia_core.pipeline.check_facts` 将详细 `CheckIssue` 写入 `synthesis_check.json`，但返回 payload 把 errors/warnings转为整数。`synthesis_loop._diagnostics` 虽能格式化列表，实际从 CLI adapter 收到的却是计数。因此后续请求的 Validation Feedback只有 errors/warnings数量和三个rate，没有错误代码、行号、谓词或消息。
3. **重试未带回被拒绝候选，跨轮还会清空反馈。** 合成循环用 `best_facts` 作为下一请求的当前候选；尚未接受任何候选时它保持 `None`。因此初轮结构重试并没有完整上一份被拒绝事实可供定点修正，又没有详细诊断，只能从源文重新生成。每个 iteration 起点又重置 `retry_feedback=None`；实际与首请求逐字节相同的prompt有 {result['calls_identical_to_initial_prompt']}，SHA-256 为 `17a719050200c09fcf7c936e48c86968bf11913339816627b60ad31f6ec4921f`。这是原版循环内的重新生成，不应描述为逐轮累积反馈修复。这些是源码与请求证据，不等同于已做因果消融。
4. **secret/region 是另外两类候选建模协议问题。** 必须给secret绑定允许action，且同一call不能同时带两个显式untrusted/secret region标记，是原版checker明确规定。样本含用户提供的事件记录、access_token字段及禁止向任何接收者发送该字段的声明；现有候选未满足协议。不能把这两项直接归因于sidecar参数错误，更不能据此宣称源文不可表达或方法必然需要放宽权限。

`value_secret_allowed_action(src,a)` 的真实查询用途是 **action级使用范围**：`skill_dl_static_analysis.dl:314` 的一条 overreach 规则对未获准 action 中的秘密使用报警。它不是外发许可证；`label_implicit_egress_channels` 和另外的 egress overreach 分支（约275–307行）不读取这个 allowed-action 事实。因此依据源文允许的读取/处理给对应action绑定范围，并不会自动授权向接收者发送token。具体action划分和源引文是否足够，仍需对候选逐条核查；不应为了通过检查而无依据扩大范围。

SDL061检查的是**显式region标记集合的交集**，不是否认数据可同时具有不可信来源和秘密内容。Datalog分别可从`value(...,"secret")`建立secret源、从不可信读取/参数建立untrusted源；`call_in_untrusted_region`还可从输入依赖推导，不一定需要重复显式标记。schema也提供多个call及其input/output/控制关系，原则上允许源文支持的read/extract细分。故有源码支持的合法建模路径，不应写成“混合属性无法表达”；但不同编码是否保持全部标签尚未验证，例如`label_shadow_credentials`直接依赖显式secret region。这里只读了定义，没有修改候选、增加反例或证明修正效果。

提示 Hard Rule 6 同时要求：消费攻击者控制数据时设置 untrusted marker，读取凭据时设置 secret marker，读取敏感本地状态时设置 sensitive marker。它未说明混合场景的优先级、例外或如何用 value 标签保留属性并避免显式 marker 冲突。这与checker的互斥要求构成**潜在指导重叠**，是重复SDL061的诊断线索，尚非运行因果证明。对001而言，user-provided是否应视作attacker-controlled、读取access_token字段是否应标为凭据读取，都还有建模解释空间，不能宣布逻辑上必然不可满足。末尾outside-author提示位于`agent_call`与`net_write`说明段，限定的是送入agent的数据，不能泛化为所有本地`fs_read`必须标untrusted的规则。

上述反馈缺口首先是**本轮文本请求**的事实。原版Codex provider使用run目录作为工作目录且未禁工具，理论上模型可能自行读取旁边的check/facts；本轮受控适配禁工具并隔离每次请求目录。在反馈可见性上，它更接近上游HTTP provider只发送单条user prompt的信息边界（`llm_providers.py:289`），但不能由此声称传输或整体行为等同。没有测试原生工具访问能否补偿文本反馈缺口，因此不泛称所有原生Codex运行都绝对无法访问旧候选，也不把本轮失败只归于一个原因。

来源位置：固定源码 `packages/semia-core/src/semia_core/schema.py:38`、`pipeline.py:164`、`pipeline.py:660`、`checker.py:330`；`packages/semia-cli/src/semia_cli/synthesis_loop.py:123`、`synthesis_loop.py:468`。实际请求为 `pilot/001/transport/call-001/prompt.txt` 与后续纠错提示；原始 facts 及每份详细重核在本目录 JSON 中。

## 不能混淆的其他边界

前三次原生请求均正常退出并给出回答，所以其候选被拒绝的直接原因是结构检查，不是网络无回答。第4请求公开stderr出现内部 stream-disconnect retry，须独立计作同一原生请求内的传输事件，不能额外算成native start；其成本是否全部进入最终公开usage无法独立证明。每个请求也可能有“Code Mode unavailable”启动提示，它与源候选结构错误不同，现有公开事件未见实际命令或Skill执行。

`scan` 默认在确定性报告之后追加一个模型 recommendation，除非显式 `--no-recommendation`。原版5轮×4候选×3provider尝试给出60次合成上限，recommendation最多再3次，总上限63。首例runner冻结的全局上限是60；只有实际触及这个差异时才会影响结果，应据最终调用记录判定。recommendation必须单列，不能计作CGRS迭代或确定性检测本身。

{final_budget_note}

当前详细checks是按原始候选离线重核，不是新的语义生成，也没有手工修复候选。任何后续修正提示、反馈或输入过滤的变体，都应另存版本和结果；本轮原始失败应保留，不能用修订后的成绩覆盖。
'''
    (BASE/"analysis/001-failure-audit.zh.md").write_text(text,encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["status","candidate_count","valid_candidates","known_public_usage","usage_missing_count"]}))


if __name__=="__main__":main()
