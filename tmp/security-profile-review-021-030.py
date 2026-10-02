"""Write assistant review notes after manually reading inputs and completed records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "packages/skill-ir/experiments/security_profile/runs/security-profile-20260917"
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
CASES = {case["case_id"]: case for case in MANIFEST["cases"]}
FOCUS = {
    "021": ["已静态阅读 SKILL.md 与 convert.py/package.py 全文；转换读取/写入、ZIP 组合和 receipt 写入均与实际 CFG 对照。", "区分转换脚本 stdout 路径与文档正文；模型看到路径不等于模型看到路径指向的内容。", "纯 dispatch/空 return、禁止外传声明、delivery_path 的实际交付媒介均已列为核对点。"],
    "022": ["完整读取 SKILL.md 引用的 references/workflow.md 与两个脚本，逐条复核 14 条实际 profile 和全部证据。", "ir_007 正确列出 fs_read/fs_write/transform，并依据 stdout 与 EM02 标 model_observe；该观察只支持产物路径，不证明读取整份文档。", "ir_009 正确依据 ZipFile.write 标读取、组合、写入；ir_013 receipt 为 fs_write；禁止外传声明未被变成额外过滤操作。", "dispatch 及无值 return 未硬贴 transform/user_output；未在没有远程依据时补造 net_send。"],
    "023": ["完整阅读三份可读源文件和 12 条 IR；历史 receipt 示例明确不执行，当前图也没有 receipt 写操作。", "转换脚本 stdout 是路径；打包脚本实际读文件并写 ZIP，不能把 handle 当内容。", "交付媒介、隐含模型观察、空 return 与隐私声明/实际动作的区别。"],
    "024": ["完整阅读三份可读源文件和 16 条 IR；实际交付使用 archive_path，不能沿用同名样例的 delivery_path。", "转换/打包脚本读写、receipt.txt 写入，以及路径与正文观察边界。", "未将禁止外传约束当作已经执行的筛选动作。"],
    "025": ["完整阅读 PDF Skill、代理说明和许可证，核对 45 条 IR、条件、约束与嵌入命令；二进制图标仅核验边界。", "PDF 渲染/文本抽取涉及读取与变换，输出 PNG/文档涉及写入；视觉检查的模型观察与本地生成文件分开。", "安装依赖、普通返回、面向用户的缺依赖说明，以及选择文件句柄与读取文件内容的区别。"],
    "026": ["完整阅读 Skill、CLI/workflows 引用、playwright_cli.sh、代理说明、NOTICE、许可证及 SVG 文本，核对 22 条 IR。", "浏览器 open/交互是否实际联网、snapshot/工具 stdout 的模型可见性、截图/trace 写入与路径返回分别核对。", "wrapper 的参数/环境读取与 npx 执行，不把所有 wrapper 命令机械认定为同一种网络效果。"],
    "027": ["完整阅读 Skill、inspect_pr_checks.py 全文、代理说明、许可证及 SVG 文本，核对 28 条 IR；没有执行脚本。", "gh 请求参数发送与 GitHub Actions 日志返回双向效果、脚本提取片段及默认工具结果回传。", "手工 gh api 日志重定向具有文件写入；请求批准不等于实施修复；外部提供商仅报告 URL 的限制不应被标成自动清洗。"],
    "028": ["完整阅读 Skill、三份 Netlify 参考文档、代理说明、许可证及 SVG 文本，核对 40 条 IR 和所有内嵌命令。", "Netlify 登录/建站/部署跨网络边界；部署还涉及本地构建产物读取，不能只标网络发送。", "package.json、netlify.toml、本地依赖、报告 URL 与远端日志内容，以及禁止提交秘密声明与实际操作的区别。"],
    "029": ["完整阅读 Linear Skill、MCP transport 配置、许可证及 SVG 文本，核对 62 条 IR 的全分支。", "明确 streamable_http 远端 MCP；list/get/search 也发送查询，create/update 也返回结果，结果回传模型的隐含观察。", "配置服务地址不等于已经传出业务数据；用户澄清、结果汇总与普通内部控制分别核对。"],
    "030": ["完整阅读 Skill、API 引用、transcribe_diarize.py 全文、代理说明、许可证及 SVG 文本，核对 22 条 IR。", "实际脚本读取音频与 speaker 引用、base64 编码、调用转录 API、格式化与本地写入；默认 stdout 是 Wrote 路径，--stdout 才直接输出正文。", "验证 key 存在与读取 key 值、CLI 返回句柄与后续验证转录正文、禁止贴密钥声明与真实隔离行为的区别。"],
}


def read(case, name):
    return json.loads((ROOT / "cases" / case / name).read_text(encoding="utf-8"))


def source_quote(material, file, quote):
    content = next(item["content"] for item in material["source"]["files"] if item["path"] == file)
    assert quote in content, (file, quote)
    start = content[:content.index(quote)].count("\n") + 1
    return {"file": file, "start_line": start, "end_line": start + quote.count("\n"), "quote": quote}


def graph_ref(material, identifier):
    item = material["instruction_index"][identifier]
    row = next(row for row in material["graph_index"] if row["id"] == item["location"])
    return {"instruction_id": identifier, "location": item["location"], "pointer": row["pointer"]}


def manual_findings(case, result, material):
    if case == "030":
        return [
            {"instruction_id": "ir_013", "field": "effects/evidences", "kind": "证据不足",
             "reason": "CLI 的 model_observe 标签可由工具输出默认回传支持，但说明将 CLI 转录结果和后续初始转录文本直接视为模型可见正文，混淆了产物与返回内容。实际脚本默认把正文写入文件，只打印 Wrote 路径；只有 --stdout 分支打印正文。当前 CFG 给出 output/transcribe/ 且没有明确 --stdout 或单独读取输出文件。ir_015 对正文的校验意图不能反向证明 ir_013/ir_019 已把文件内容回传。",
             "source_evidence": [source_quote(material, "scripts/transcribe_diarize.py", 'if args.stdout:\n            print(output)'), source_quote(material, "scripts/transcribe_diarize.py", 'out_path.write_text(output, encoding="utf-8")\n        print(f"Wrote {out_path}")'), source_quote(material, "SKILL.md", "Validate the output: transcription quality, speaker labels, and segment boundaries")],
             "graph_evidence": [graph_ref(material, identifier) for identifier in ("ir_013", "ir_015", "ir_019")],
             "profile_evidence": {identifier: result["profiles"][identifier] for identifier in ("ir_013", "ir_015", "ir_019")},
             "suggestion": "保留工具返回内容的 model_observe，明确该证据目前支持状态/路径，不把路径所指正文自动纳入观察集合；把实际正文读取机制及输出含义记为边界或未决，留待工具契约与传播阶段解析。不要据此宣称音频、密钥或完整正文都已被 Agent LLM 观察。"},
            {"instruction_id": "ir_011", "field": "effects", "kind": "未决合理",
             "reason": "ensure_openai_sdk_installed 没有固定当前环境是否已安装，模型没有把一次检查强行标成下载与文件写入，而将具体网络/文件效果列为未决。原文安装命令有条件，保留这种不确定性合理。",
             "source_evidence": [source_quote(material, "SKILL.md", "## Dependencies (install if missing)")],
             "graph_evidence": [graph_ref(material, "ir_011")], "profile_evidence": {"profile": result["profiles"]["ir_011"], "unresolved": result["unresolved"]},
             "suggestion": "保留未决，不将空 effects 当成已确定无副作用；实际是否安装及安装契约明确后再收窄。"},
        ]
    if case == "026":
        return [{"instruction_id": "ir_013", "field": "effects", "kind": "未决合理",
                 "reason": "interact_with_element_refs 没有指定具体 click/fill/导航行为，wrapper 的 cli_args 也未固定子命令；模型将是否实际远程通信列为未决，并保留 snapshot 的模型观察、捕获产物的文件写入及 wrapper 返回内容的模型观察，没有把所有浏览器动作都强行标成网络发送。",
                 "source_evidence": [source_quote(material, "SKILL.md", "Interact using refs from the latest snapshot."), source_quote(material, "scripts/playwright_cli.sh", 'cmd+=("$@")')],
                 "graph_evidence": [graph_ref(material, identifier) for identifier in ("ir_013", "ir_021", "ir_022")],
                 "profile_evidence": {"unresolved": result["unresolved"], "wrapper_return": result["profiles"]["ir_022"]},
                 "suggestion": "保留网络效果未决，后续传播不能把 effects 空列表理解成无副作用；具体子命令/URL 类型/工具契约明确后再收窄。模型观察目前只说明返回的 CLI 结果可见，不自动证明其引用的所有网页或截图内容可见。"}]
    if case in {"023", "024"}:
        extract = "ir_003" if case == "023" else "ir_005"
        delivery = "ir_011" if case == "023" else "ir_013"
        destination = "delivery_path" if case == "023" else "archive_path"
        return [
            {"instruction_id": extract, "field": "actor/effects", "kind": "证据不足",
             "reason": "通用 manifest 路径提取没有给出执行实现，却被依据 opcode 直接确定为 " + str(result["profiles"][extract]["actor"]) + "。相同业务步骤在 022/023/024 中分别被定为 runtime/LLM/runtime，model_observe 也随之改变；原文差异是 receipt 是否执行或交付参数改名，没有提供这种执行者差异。没有记录未决，不能据此认定模型是否实际观察 manifest。",
             "source_evidence": [source_quote(material, "SKILL.md", "按其中 paths 列表获取文档路径")],
             "graph_evidence": [graph_ref(material, "ir_001"), graph_ref(material, extract)],
             "profile_evidence": result["profiles"][extract],
             "suggestion": "把执行分配规则固定为显式执行模型/工具契约，或将 actor 及其模型观察影响记为未决；不要用操作名称给同一抽象步骤分配不同实现。"},
            {"instruction_id": delivery, "field": "effects", "kind": "证据不足",
             "reason": f"交付到 {destination} 不足以证明目的地属于本地文件系统，profile 的 fs_write 和本地运行时解释缺少路径类型/交付工具依据；禁止外传声明不构成其执行保证。",
             "source_evidence": [source_quote(material, "SKILL.md", f"将生成的 bundle.zip 交付到请求的 {destination}。")],
             "graph_evidence": [graph_ref(material, delivery)], "profile_evidence": result["profiles"][delivery],
             "suggestion": "保留 sink，并将具体交付效果列为未决；获得媒介/工具依据后再确定 fs_write、net_send 或 user_output。"},
        ]
    if case == "025":
        return [
            {"instruction_id": "ir_027", "field": "actor", "kind": "漏标",
             "reason": "该复合动作既根据缺陷修改文档又重新渲染，profile 已承认 fs_read、fs_write 和渲染效果，却只列 llm。源文渲染路径明确使用 pdftoppm/Poppler，实际文件读写与重新渲染还需要工具或运行时参与；只列 LLM 会把执行职责缩成模型调度。",
             "source_evidence": [source_quote(material, "SKILL.md", "After each meaningful update, re-render pages and verify alignment, spacing, and legibility."), source_quote(material, "SKILL.md", "pdftoppm -png $INPUT_PDF $OUTPUT_PREFIX")],
             "graph_evidence": [graph_ref(material, "ir_013"), graph_ref(material, "ir_027")],
             "profile_evidence": result["profiles"]["ir_027"],
             "suggestion": "对复合 IR 保留模型处理及工具/运行时执行主体，依据当前渲染路径补充相应 actor；不要让 fs_write 被误解为 LLM 本身直接执行。"},
            {"instruction_id": "ir_017", "field": "effects", "kind": "未决合理",
             "reason": "四个安装动作保留本地写入及结果回传，将 net_send/net_receive 外置为未决。原图没有网络仓库、缓存状态或安装工具通信契约，不能仅据安装命令断言每次都发生网络通信。",
             "source_evidence": [source_quote(material, "SKILL.md", "brew install poppler"), source_quote(material, "SKILL.md", "uv pip install reportlab pdfplumber pypdf")],
             "graph_evidence": [graph_ref(material, identifier) for identifier in ("ir_017", "ir_019", "ir_037", "ir_039")],
             "profile_evidence": {"unresolved": result["unresolved"]},
             "suggestion": "保留未决；后续工具契约可描述可能联网与缓存分支，但不得把目前未标网络效果当作确定无网络。"},
            {"instruction_id": "ir_034", "field": "effects", "kind": "证据不足",
             "reason": "最终 delivery_summary 返回被直接套用普通 return 规则清空 effects。EM06 只排除仅凭 opcode 推断用户输出，不能替代检查整个交付上下文。当前原文有交付与总结要求，块也组织了最终交付，至少应解释接收方是否已明确；现有证据只引用 return，没有处理该上下文。",
             "source_evidence": [source_quote(material, "SKILL.md", "Do not deliver until the latest PNG inspection shows zero visual or formatting defects."), source_quote(material, "agents/openai.yaml", "Create, edit, or review this PDF and summarize the key output or changes.")],
             "graph_evidence": [graph_ref(material, "ir_033"), graph_ref(material, "ir_034")],
             "profile_evidence": result["profiles"]["ir_034"],
             "suggestion": "结合原文交付上下文判断最终输出边界；若接收方仍未确定则明确未决，不能仅用 EM06 把所有 return 都当成无用户输出。"},
        ]
    if case != "022":
        return None
    return [
        {"instruction_id": "ir_001", "field": "actor/effects", "kind": "证据不足",
         "reason": "读取 manifest 与后续字段提取没有明确声明由隔离本地程序完成。profile 仅凭 read_manifest_json 名称把执行者确定为 agent_runtime，未说明是否通过工具回传模型，也未记录该分配的不确定性。该假设会影响后续是否建立模型观察边界，不能把没有 model_observe 当作已证明模型不可见。相同执行者推断还出现在 ir_003、ir_005。",
         "source_evidence": [source_quote(material, "references/workflow.md", "读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。")],
         "graph_evidence": [graph_ref(material, identifier) for identifier in ("ir_001", "ir_003", "ir_005")],
         "profile_evidence": {identifier: result["profiles"][identifier] for identifier in ("ir_001", "ir_003", "ir_005")},
         "suggestion": "明确通用读取/字段提取操作的执行分配规则，或将 actor 及相关模型观察记为未决；若采用工具结果默认回传，应为模型观察给出该操作与 EM02 的联合依据。不要根据 opcode 假设本地隔离。"},
        {"instruction_id": "ir_011", "field": "effects", "kind": "证据不足",
         "reason": "delivery_path 的传输媒介和实现没有给出，原文只要求交付到请求的位置。标签 fs_write 以该句为依据，进一步解释为本地放置/写入，超过了文本明确说明的范围。禁止上传声明也不能证明执行机制必然是本地文件系统。sink 角色有依据，但具体效果应保留未知。",
         "source_evidence": [source_quote(material, "references/workflow.md", "将生成的 bundle.zip 交付到请求的 delivery_path。"), source_quote(material, "references/workflow.md", "整份流程禁止把文档上传到外部服务。")],
         "graph_evidence": [graph_ref(material, "ir_011")],
         "profile_evidence": result["profiles"]["ir_011"],
         "suggestion": "保留交付 sink，外置记录交付媒介未决；只有在路径类型或工具契约明确后才确定 fs_write/net_send/user_output，不用约束声明补成实现保证。"},
    ]


def raw_response_findings(case, material):
    """Review rejected text without altering it or treating it as accepted annotation."""
    raw = json.loads(read(case, "calls/annotation/a001/call.json")["response"])
    profiles = raw["profiles"]
    units = {item["id"]: item for item in material["source_index"]}
    files = {item["path"]: item["content"] for item in material["source"]["files"]}
    mismatches = []
    for identifier, profile in profiles.items():
        for evidence in profile["evidences"]:
            if evidence["basis"] != "source":
                continue
            unit = units[evidence["location"]]
            located = "\n".join(files[unit["file"]].splitlines()[unit["start_line"] - 1:unit["end_line"]])
            if evidence["quote"] not in located:
                mismatches.append({"instruction_id": identifier, "evidence": evidence, "actual_unit": unit, "actual_unit_text": located})
    if case == "028":
        return [
            {"instruction_id": "ir_005", "field": "evidences", "kind": "证据不足",
             "reason": "本条仅诊断未接受的原始响应：完整 JSON 覆盖 40 个 IR，但源文引文有 33 处定位错配。首处将登录指示 Wait for user to complete login 定位到 src_062；该单元实际是 SKILL.md 82–91 行的 Git remote/link 代码段，登录指示在第 58 行。文本在完整源文中存在，不能因此忽略错位定位。其余部署引用也存在类似错位。",
             "source_evidence": [source_quote(material, "SKILL.md", "This opens a browser window for OAuth authentication. Wait for user to complete login, then verify with `netlify status` again.")],
             "graph_evidence": [graph_ref(material, "ir_005")],
             "profile_evidence": {"accepted": False, "raw_profile_count": len(profiles), "source_quote_mismatches": mismatches},
             "suggestion": "保持整例 invalid_response 和 0 份接受标注；保留完整响应供定位错误诊断，不人工改引用、不自动重发。下一轮实验如改定位提示需独立运行身份。"},
            {"instruction_id": "ir_027", "field": "effects", "kind": "漏标",
             "reason": "本条仅诊断未接受的原始响应：三种部署动作已列 transformer 角色，并解释本地构建把源项目变成构建产物，但 effects 均缺少 transform。原文明确说明部署流程包含 Builds the project locally；文件读写与网络发送不能完整表达这一实际变换。",
             "source_evidence": [source_quote(material, "SKILL.md", "Builds the project locally")],
             "graph_evidence": [graph_ref(material, identifier) for identifier in ("ir_027", "ir_029", "ir_031")],
             "profile_evidence": {"accepted": False, "raw_profiles": {identifier: profiles[identifier] for identifier in ("ir_027", "ir_029", "ir_031")}},
             "suggestion": "后续独立标注实验应对复合构建/上传动作保留 transform 并给出正确定位；本次不修补已拒收响应。"},
            {"instruction_id": "ir_040", "field": "effects", "kind": "漏标",
             "reason": "本条仅诊断未接受的原始响应：源文明确 After deployment, report to user，且 ir_039 格式化结果由 ir_040 返回，二者都没有 user_output。普通 return 规则不能覆盖这里已经明确的用户接收方；这不是仅凭 return 操作名推测用户输出。",
             "source_evidence": [source_quote(material, "SKILL.md", "After deployment, report to user:")],
             "graph_evidence": [graph_ref(material, "ir_039"), graph_ref(material, "ir_040")],
             "profile_evidence": {"accepted": False, "raw_profiles": {identifier: profiles[identifier] for identifier in ("ir_039", "ir_040")}},
             "suggestion": "后续独立标注应结合明确的用户交付上下文定位 user_output，不能把 EM06 当成所有 return 一律无输出；保持本次原始响应不变。"},
        ]
    return [
        {"instruction_id": "ir_017", "field": "evidences", "kind": "证据不足",
         "reason": "本条仅诊断未接受的原始响应：完整 JSON 覆盖 62 个 IR，但 12 个写调用将 Execute Linear MCP tool calls 错指 src_047。该单元是 SKILL.md 43–44 行 Step 2 的选择工作流/确认标识，所引文字实际位于第 47 行 Step 3。并非该句话不在源文，而是精确定位不匹配，严格拒收有据。",
         "source_evidence": [source_quote(material, "SKILL.md", "Execute Linear MCP tool calls in logical batches:")],
         "graph_evidence": [graph_ref(material, "ir_017")],
         "profile_evidence": {"accepted": False, "raw_profile_count": len(profiles), "source_quote_mismatches": mismatches},
         "suggestion": "保持整例 invalid_response 和 0 份接受标注；不手工替换 src_047，不把已有 JSON 覆盖全部 IR 当作可接受结果。"},
        {"instruction_id": "ir_014", "field": "roles", "kind": "漏标",
         "reason": "本条仅诊断未接受的原始响应：查询动作仅列 source，创建动作仅列 sink，虽然 effects 已承认请求发送和响应接收。例如 ir_014 把 confirmed_identifiers 发到远端并引入问题列表，ir_017 发送创建参数并引入 created cycle；按本轮中性数据边界定义，两类动作都有引入与到达边界的一面，不能仅按业务读/写给单一角色。",
         "source_evidence": [source_quote(material, "SKILL.md", "Read first (list/get/search) to build context."), source_quote(material, "SKILL.md", "Create or update next (issues, projects, labels, comments) with all required fields.")],
         "graph_evidence": [graph_ref(material, "ir_014"), graph_ref(material, "ir_017")],
         "profile_evidence": {"accepted": False, "raw_profiles": {identifier: profiles[identifier] for identifier in ("ir_014", "ir_017")}},
         "suggestion": "后续独立标注按具体请求/返回内容复核多 roles，至少为示例查询补充 sink、创建响应补充 source；不要用 net_send 标签机械映射角色，仍需检查实际输入输出。"},
        {"instruction_id": "ir_034", "field": "effects/roles/actor", "kind": "未决合理",
         "reason": "本条仅诊断未接受的原始响应：suggest_or_apply_redistributions 既可能提出方案，也可能实施变更，原始响应将是否实际网络写入保留未决合理。不过该不确定性还可能影响 tool actor 与 sink role，目前只记在 effects，需要避免把其余字段误看成已完全确定。",
         "source_evidence": [source_quote(material, "SKILL.md", "suggest or apply redistributions")],
         "graph_evidence": [graph_ref(material, "ir_034")],
         "profile_evidence": {"accepted": False, "raw_profile": profiles["ir_034"], "raw_unresolved": raw["unresolved"]},
         "suggestion": "后续独立实验保留行为分支未决，并检查其对 actor、roles 的影响；本次保持拒收状态。"},
    ]


def review(case):
    result_path = ROOT / "cases" / case / "result.json"
    if not result_path.exists():
        return None
    result = read(case, "result.json")
    material = read(case, "inputs/material.json")
    findings = manual_findings(case, result, material)
    call_details = []
    call_path = ROOT / "cases" / case / "calls/annotation/a001/transport.json"
    if call_path.exists():
        for record in json.loads(call_path.read_text(encoding="utf-8")):
            for index, attempt in enumerate(record.get("http_attempts", []), 1):
                stream = attempt.get("stream", {})
                call_details.append({"attempt": index, "status": attempt.get("status"), "http_status": attempt.get("http_status"),
                                     "error_type": attempt.get("error_type"), "error": attempt.get("error"),
                                     "done_received": stream.get("done_received"), "finish_reason": stream.get("finish_reason"),
                                     "received_bytes": stream.get("received_bytes"), "partial_content_chars": len(stream.get("partial_content", ""))})
    if result["status"] not in {"complete", "incomplete"}:
        findings = [{"instruction_id": None, "field": "execution", "kind": "记录失败",
                     "reason": result["reason"] + "；没有经过严格校验接受的整图标注，不能把空 profiles 当作语义漏标，也不能评价该例标注是否正确。",
                     "source_evidence": {"reviewed_files": [f["path"] for f in material["source"]["files"]], "source_sha256": material["source"]["source_sha256"]},
                     "graph_evidence": {"instruction_count": len(material["instruction_index"]), "graph_sha256": result["graph_sha256"]},
                     "profile_evidence": {"status": result["status"], "validation": result["validation"], "counts": result["counts"], "attempts": call_details},
                     "suggestion": "保留本次执行失败和不完整响应，不重发、不补造 profile，不纳入漏标/误标结论；网络条件改善后的另一次实验需要独立运行身份。"}]
        conclusion = "执行记录已复核；本次没有可接受标注，动作安全分类质量无法评价。"
        if case in {"028", "029"}:
            findings.extend(raw_response_findings(case, material))
            conclusion = "完整原始响应因源文引文定位错误而被拒收，接受的 profiles 仍为 0。已逐条阅读未接受候选；以下额外语义观察仅作失败诊断，不作为已接受标注或正确率统计。"
            findings[0]["suggestion"] = "保留本次 invalid_response 与原始完整响应，不手工修引用、不补造已接受 profile，不重发或补跑择优；具体定位错误见后续条目。"
    elif findings is None:
        return None
    else:
        conclusion = ("已逐条复核 22 条标注及 1 项未决。脚本读写、双向网络和编码有依据；正文与路径回传的观察边界需澄清，SDK 安装效果未决合理。" if case == "030" else
                      "已逐条复核 22 条标注及 2 项未决。网络效果未决与未知子命令相符；快照、捕获产物及 wrapper 返回处理未见明确相反证据。这不是通用正确性证明。" if case == "026" else
                      "已逐条复核 45 条标注与 4 项未决。安装网络效果未决合理；复合动作执行主体有遗漏，最终交付的效果解释仍需补充。" if case == "025" else
                      "已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。")
    note = {"case_id": case, "sample_id": CASES[case]["sample_id"], "status_observed": result["status"],
            "review_conclusion": conclusion, "findings": findings, "checked_focus": FOCUS[case],
            "reviewer": "assistant", "user_confirmed": False,
            "review_scope": "静态阅读全部可读源文件、实际 CFG 及已完成的调用/标注记录；没有执行 Skill、调用 API 或修改原始结果。"}
    lines = [f"# {case} · {note['sample_id']} Security Profile 助手复核", "", f"实际执行状态：`{result['status']}`。", "", conclusion,
             "", "本记录是助手复核，尚未由用户确认；不计算标注正确率。", "", "## 已检查内容", ""]
    lines += [f"- {item}" for item in FOCUS[case]]
    lines += ["", "## 发现与建议", ""]
    for index, finding in enumerate(findings, 1):
        lines += [f"### {index}. {finding['kind']} · {finding['instruction_id'] or '整例调用'} · {finding['field']}", "", finding["reason"], "", "建议：" + finding["suggestion"], "",
                  "```json", json.dumps({key: finding[key] for key in ("source_evidence", "graph_evidence", "profile_evidence")}, ensure_ascii=False, indent=2), "```", ""]
    (ROOT / "cases" / case / "assistant-review.md").write_text("\n".join(lines), encoding="utf-8")
    return note


existing_path = ROOT / "review-021-030.json"
existing = {row["case_id"]: row for row in json.loads(existing_path.read_text(encoding="utf-8"))} if existing_path.exists() else {}
for number in range(21, 31):
    case = f"{number:03}"
    if case in existing:
        continue
    note = review(case)
    if note:
        existing[case] = note
        print(case, note["status_observed"], len(note["findings"]))
existing_path.write_text(json.dumps([existing[key] for key in sorted(existing)], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
