#!/usr/bin/env python3
"""Rebuild controlled Skill inputs and their separate, source-grounded facts.

Only the Python standard library is required. Run with --output DIR to produce
an isolated copy; DIR is the corpus root, not an individual Skill package.
No package is executed and no production extraction component is imported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from skillflow.common.paths import project_root, resolve_material_path
from typing import Any


DEFAULT_OUTPUT = project_root() / "experiments/corpus/semantics_review"
EXPRESSIONS = ["numbered", "prose", "table", "mixed", "purpose_delta", "semantic_delta"]
EXPRESSION_TITLES = ["编号步骤", "连贯段落", "表格", "跨文件混合", "用途最小差异", "语义最小差异"]


def fact(kind: str, statement: str, level: str, target: str, clauses: list[str],
         tags: list[str] | None = None) -> dict[str, Any]:
    return {"kind": kind, "statement": statement,
            "scope": {"level": level, "target": target},
            "clauses": clauses, "tags": tags or []}


CONVERT_SOURCE = '''"""Convert one UTF-8 text document and print the output path."""
from pathlib import Path
import sys

source = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
output_dir.mkdir(parents=True, exist_ok=True)
output = output_dir / (source.stem + ".txt")
output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
print(output)
'''

PACKAGE_SOURCE = '''"""Build the explicitly requested ZIP from supplied output paths."""
import argparse
from pathlib import Path
from zipfile import ZipFile

parser = argparse.ArgumentParser()
parser.add_argument("--paths", nargs="+", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
with ZipFile(args.output, "w") as archive:
    for filename in args.paths:
        path = Path(filename)
        archive.write(path, arcname=path.name)
'''


GROUPS: dict[str, dict[str, Any]] = {
    "N": {
        "group": "notification", "title": "条件通知与数据发送", "language": "zh", "split": "development",
        "name": "conditional-notification",
        "description": "根据事件记录的订阅状态、紧急标记和数值发送通知。",
        "clauses": {
            "read": "读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。",
            "select": "仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。",
            "exception": "urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。",
            "send": "对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。",
            "body": "notify.send 的 body 参数直接取该记录的 summary 字段原值。",
            "skip": "未选中的记录不调用 notify.send。",
            "ban": "整份流程禁止将 access_token 字段发送给任何接收对象。",
            "literal": "字段取值要求不包含摘要生成、内容改写或额外格式转换。",
            "count": "处理完成后，将处理条数写入本地 count.txt。",
        },
        "purpose_clause": "count",
        "purpose_text": "历史示例（当前流程不执行）：处理完成后，将处理条数写入本地 count.txt。",
        "semantic_clause": "body",
        "semantic_text": "notify.send 的 body 参数直接取该记录的 record_id 字段原值。",
        "purpose_change": "只把写入 count.txt 的运行指令改为明确不执行的历史示例。",
        "semantic_change": "只把发送正文的数据来源由 summary 改为 record_id。",
        "facts": [
            fact("behavior", "读取用户提供的 events.json 作为事件记录来源。", "operation", "读取事件记录", ["read"]),
            fact("condition", "选中条件为 (opted_out != true) AND (urgent == true OR value >= 100)，退出订阅限制适用于两个可选分支。", "block", "记录筛选", ["select", "exception"], ["negation"]),
            fact("constraint", "紧急事件可越过数值门槛，但仍受退出订阅限制。", "block", "记录筛选", ["select", "exception"], ["exception", "scope"]),
            fact("behavior", "每条选中记录执行一次 notify.send，接收对象来自该记录的 recipient。", "operation", "发送通知", ["send"], ["data_flow"]),
            fact("data_flow", "notify.send.body 直接使用当前选中记录的 summary 原值。", "operation", "发送通知", ["body"], ["data_flow"]),
            fact("condition", "未选中的记录没有通知发送行为。", "block", "未选中分支", ["skip"], ["negation"]),
            fact("constraint", "整份流程不得把 access_token 字段发送给任何接收对象。", "skill", "整份通知 Skill", ["ban"], ["prohibition", "scope"]),
            fact("must_not_infer", "不能从字段直接取值要求增加摘要生成、内容改写或格式转换操作。", "operation", "发送通知", ["literal"], ["negation"]),
            fact("behavior", "处理结束后单独将处理条数写入本地 count.txt，保留它对前序记录处理的依赖。", "operation", "记录处理条数", ["count"], ["additional_behavior"]),
        ],
        "purpose_fact": (8, fact("must_not_infer", "写入 count.txt 仅是明确不执行的历史示例，当前流程不新增该写入行为。", "operation", "历史写入示例", ["count"], ["quoted_example", "negation"])),
        "semantic_fact": (4, fact("data_flow", "notify.send.body 直接使用当前选中记录的 record_id 原值。", "operation", "发送通知", ["body"], ["data_flow"])),
        "variants": ["可将筛选写为一个复合条件或短路分支，但退出订阅不能被紧急标记覆盖。", "发送对象和正文来源可采用不同结果引用名称，但必须分别指向当前记录的 recipient 与明确指定的正文字段。", "允许把处理条数写入表示为附加尾部行为，保留前序处理依赖，不要求固定块数或操作名称。"],
        "questions": ["opted_out 缺失时的运行策略未定义；本包已声明记录包含该字段，不补充缺失值处理。", "“处理条数”未说明统计全部记录、选中记录还是成功发送记录；保留该未定义口径，不据此增加计数策略。"],
    },
    "Q": {
        "group": "query", "title": "查询调用与参数使用", "language": "en", "split": "held_out",
        "name": "catalog-query",
        "description": "Query an index once using a supplied request and preserve optional-parameter semantics.",
        "clauses": {
            "capability": "Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.",
            "read": "Read the user-supplied request.json, which contains term and may contain from_date and limit.",
            "call": "Call index.search exactly once, using request.term unchanged as its query argument.",
            "date": "When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.",
            "missing_date": "When from_date is missing, omit the from_date argument.",
            "limit": "When limit is present, pass its value unchanged as the limit argument.",
            "missing_limit": "When limit is missing, omit the limit argument.",
            "ban": "Do not invoke index.delete anywhere in this workflow.",
            "format": "Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.",
            "count": "After the search, write the response's total value to local count.txt.",
            "return": "Return the search response's items value unchanged.",
        },
        "purpose_clause": "count",
        "purpose_text": "Historical example, not executed in this workflow: After the search, write the response's total value to local count.txt.",
        "semantic_clause": "missing_limit",
        "semantic_text": "When limit is missing, pass 10 as the limit argument.",
        "purpose_change": "Only change the additional count.txt instruction into an explicitly inactive historical example.",
        "semantic_change": "Only change missing-limit handling from argument omission to explicitly passing 10.",
        "facts": [
            fact("behavior", "Read request.json as the source of term and optional from_date and limit.", "operation", "Read query request", ["read"]),
            fact("behavior", "Invoke index.search exactly once with request.term unchanged as query.", "operation", "Search index", ["call"], ["data_flow"]),
            fact("constraint", "A present from_date is passed unchanged and must have the documented YYYY-MM-DD format.", "operation", "Search index: from_date argument", ["date"], ["scope"]),
            fact("condition", "If from_date is absent, omit that argument rather than send an empty or null value.", "operation", "Search index: from_date argument", ["missing_date"], ["parameter_omission"]),
            fact("data_flow", "A present limit is passed unchanged as the limit argument.", "operation", "Search index: limit argument", ["limit"], ["data_flow"]),
            fact("condition", "If limit is absent, omit the limit argument; do not supply an invented default.", "operation", "Search index: limit argument", ["missing_limit"], ["parameter_omission"]),
            fact("data_flow", "Return the response.items value unchanged.", "operation", "Return query result", ["return"], ["data_flow"]),
            fact("constraint", "The prohibition on index.delete applies to the entire workflow.", "skill", "Entire query Skill", ["ban"], ["prohibition", "scope"]),
            fact("must_not_infer", "Fuzzy-matching capability alone does not add a fuzzy-expansion operation.", "operation", "Search index", ["capability"], ["capability_description", "negation"]),
            fact("must_not_infer", "Date format and parameter requirements do not add validation or normalization operations.", "operation", "Search argument preparation", ["date", "format"], ["negation"]),
            fact("behavior", "After the search and before returning items, separately write response.total to local count.txt.", "operation", "Write result count", ["count", "return"], ["additional_behavior"]),
        ],
        "purpose_fact": (10, fact("must_not_infer", "Writing response.total to count.txt is an explicitly inactive historical example, not a current action.", "operation", "Historical count example", ["count"], ["quoted_example", "negation"])),
        "semantic_fact": (5, fact("condition", "If limit is absent, explicitly pass 10 as the limit argument.", "operation", "Search index: limit argument", ["missing_limit"], ["parameter_default"])),
        "variants": ["Optional argument handling may be attached to the call or expressed with branches, provided absent arguments are actually omitted when required.", "YYYY-MM-DD may remain verbatim as a constraint on the search call without an invented parser or validation step.", "Different result names are acceptable when items and total still refer to the same search response."],
        "questions": ["The request does not define handling of malformed dates or explicit nulls; do not silently invent either policy."],
    },
    "F": {
        "group": "fallback", "title": "工具选择与失败回退", "language": "en", "split": "development",
        "name": "source-fetch-with-fallback",
        "description": "Fetch one source using a credential-gated preferred tool and a bounded archive fallback.",
        "clauses": {
            "read": "Read source_id from the user's request and read FAST_KEY from the environment.",
            "preferred": "If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.",
            "retry": "Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.",
            "fallback": "After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.",
            "archive": "Call archive.fetch at most once and pass source_id as its only argument.",
            "return": "On either tool's success, return that successful response's body value unchanged and make no further fetch calls.",
            "stop": "If archive.fetch fails, stop and return its error; do not retry archive.fetch.",
            "ban": "Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.",
            "status": "Before returning from every success or failure path, append the final status to local status.txt.",
        },
        "purpose_clause": "status",
        "purpose_text": "Historical example, not executed in this workflow: Before returning from every success or failure path, append the final status to local status.txt.",
        "semantic_clause": "return",
        "semantic_text": "On either tool's success, return that successful response's summary value unchanged and make no further fetch calls.",
        "purpose_change": "Only turn the additional local status append into an explicitly inactive historical example.",
        "semantic_change": "Only change the successful return value from response.body to response.summary.",
        "facts": [
            fact("behavior", "Read source_id from the request and FAST_KEY from the environment.", "operation", "Read fetch inputs", ["read"], ["data_flow"]),
            fact("condition", "FAST_KEY presence gates fast.fetch; prefer it when present and go directly to archive.fetch when absent.", "block", "Preferred tool selection", ["preferred"], ["tool_priority", "precondition"]),
            fact("data_flow", "fast.fetch receives request.source_id and the FAST_KEY read from the environment.", "operation", "Preferred fetch", ["read", "preferred"], ["data_flow"]),
            fact("condition", "Retry fast.fetch once only after a transient first failure; a non-transient first failure is not retried.", "block", "Preferred fetch retry", ["retry"], ["retry", "negation"]),
            fact("condition", "A non-transient first failure or any failed retry causes archive.fetch fallback.", "block", "Fallback after preferred failure", ["fallback"], ["fallback"]),
            fact("constraint", "archive.fetch executes at most once, with source_id as its only argument.", "operation", "Archive fetch", ["archive"], ["scope"]),
            fact("data_flow", "A successful fetch returns that same response.body unchanged and ends further fetch calls.", "block", "Successful fetch exit", ["return"], ["data_flow", "stop_condition"]),
            fact("condition", "An archive.fetch failure returns that error and stops without any archive retry.", "block", "Archive failure exit", ["stop"], ["stop_condition", "negation"]),
            fact("constraint", "FAST_KEY must never flow to archive.fetch or diagnostic output anywhere in the Skill.", "skill", "Entire fetch Skill", ["ban"], ["prohibition", "scope"]),
            fact("behavior", "Before returning from each success or failure path, separately append its final status to local status.txt.", "operation", "Append final status", ["status"], ["additional_behavior"]),
        ],
        "purpose_fact": (9, fact("must_not_infer", "The final-status append is an explicitly inactive historical example and adds no current file write.", "operation", "Historical status example", ["status"], ["quoted_example", "negation"])),
        "semantic_fact": (6, fact("data_flow", "A successful fetch returns that same response.summary unchanged and ends further fetch calls.", "block", "Successful fetch exit", ["return"], ["data_flow", "stop_condition"])),
        "variants": ["The first primary attempt and one retry may be separate nodes or a bounded retry structure; a third primary attempt is never allowed.", "Fallback may share one archive call across missing-key and failed-primary branches, provided each path preserves the prerequisites.", "The local status write may appear in a common exit or on each final path, provided it occurs before the corresponding return and retains the final-status dependency."],
        "questions": ["The upstream tools' transient-error classification and FAST_KEY's exact presence test are not defined here; retain the named conditions without inventing checks."],
    },
    "D": {
        "group": "documents", "title": "多文档处理与交付", "language": "zh", "split": "development",
        "name": "document-bundle-delivery",
        "description": "转换清单中的文档、打包转换产物并交付到用户指定位置。",
        "clauses": {
            "read": "读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。",
            "convert": "逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。",
            "local": "转换期间保留原文标题；该要求仅限转换，不限制汇总标题。",
            "blackbox": "转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。",
            "package": "打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。",
            "deliver": "将生成的 bundle.zip 交付到请求的 delivery_path。",
            "receipt": "另外，将转换产物路径列表写入本地 receipt.txt。",
            "immutable": "整份流程不得修改输入原文文件。",
            "upload": "整份流程禁止把文档上传到外部服务。",
            "order": "备注：必要时保留原顺序。",
        },
        "purpose_clause": "receipt",
        "purpose_text": "历史示例（当前流程不执行）：另外，将转换产物路径列表写入本地 receipt.txt。",
        "semantic_clause": "deliver",
        "semantic_text": "将生成的 bundle.zip 交付到请求的 archive_path。",
        "purpose_change": "只把附加写入 receipt.txt 的运行指令改为明确不执行的历史示例。",
        "semantic_change": "只把 bundle.zip 的交付目标由请求的 delivery_path 改为 archive_path。",
        "facts": [
            fact("behavior", "读取 manifest.json.paths 作为文档路径来源，并读取请求中的 output_dir 和 delivery_path。", "operation", "读取清单与请求", ["read"], ["data_flow"]),
            fact("behavior", "逐个以文档路径和 output_dir 调用 scripts/convert.py；每次调用读取该 UTF-8 源文，按需创建输出目录，将内容写入 output_dir 下的 <源文主名>.txt，并把标准输出的该路径作为转换产物路径。", "operation", "文档转换调用", ["convert"], ["data_flow", "black_box"]),
            fact("constraint", "保留原文标题仅约束转换操作，不约束汇总标题。", "operation", "文档转换调用", ["local"], ["scope"]),
            fact("must_not_infer", "convert.py 按黑盒调用保留参数、文件输入、输出产物和标准输出路径，不把内部变量、循环或控制流拆成额外流程步骤，也不重复执行内部处理。", "operation", "文档转换调用", ["convert", "blackbox"], ["black_box", "negation"]),
            fact("behavior", "必须执行被明确采用的参考打包命令，以转换产物路径列表为 --paths 输入；调用读取各产物文件并写入由 --output 指定的 bundle.zip，压缩包内使用各文件的文件名。", "operation", "打包转换产物", ["package", "command"], ["adopted_example", "data_flow", "code_block", "black_box"]),
            fact("data_flow", "将打包生成的 bundle.zip 交付到先前从请求读取的 delivery_path，交付操作消费该读取结果，无需再次读取。", "operation", "交付压缩包", ["read", "deliver"], ["data_flow"]),
            fact("behavior", "单独将转换产物路径列表写入本地 receipt.txt，并保留对转换产物路径的依赖。", "operation", "写入交付收据", ["receipt"], ["additional_behavior"]),
            fact("constraint", "不得修改输入原文文件的禁止要求作用于整份 Skill。", "skill", "整份多文档 Skill", ["immutable"], ["prohibition", "scope"]),
            fact("constraint", "不得向外部服务上传文档的禁止要求作用于整份 Skill。", "skill", "整份多文档 Skill", ["upload"], ["prohibition", "scope"]),
            fact("constraint", "“必要时保留原顺序”的作用范围不明确，应待共同确认，不能自动提升为全局规则。", "unresolved", "原文未指明转换、打包或收据中的哪一处", ["order"], ["scope", "unresolved_scope"]),
        ],
        "purpose_fact": (6, fact("must_not_infer", "写入 receipt.txt 是明确不执行的历史示例，当前流程不增加该写入。", "operation", "历史收据示例", ["receipt"], ["quoted_example", "negation"])),
        "semantic_fact": (5, fact("data_flow", "从请求读取 archive_path，并将打包生成的 bundle.zip 交付到该读取结果指定的位置；先前明确要求读取的 delivery_path 仍保留，但不再用于交付。", "operation", "交付压缩包", ["read", "deliver"], ["data_flow"])),
        "variants": ["可用循环或逐项调用表达多文档转换，但文档路径和返回路径的对应关系必须保留。", "黑盒调用可以保留命令原文，无需把 convert.py 实现映射到固定操作类型。", "明确要求采用的参考命令属于实际行为；局部标题约束和全局禁止事项不能互换作用范围。"],
        "questions": ["“必要时保留原顺序”未注明条件或对象，作用范围待共同确认。", "manifest.json 的重复文件名、转换失败和不存在路径的处理未定义，不额外增加策略。"],
    },
}


def frontmatter(group: dict[str, Any]) -> str:
    return f"---\nname: {group['name']}\ndescription: {group['description']}\n---\n\n"


def reference_command() -> str:
    return "\n## 参考步骤\n\n```sh\npython scripts/package.py --paths <转换产物路径列表> --output bundle.zip\n```\n"


def generate_package(prefix: str, version: int) -> tuple[dict[str, str], dict[str, str], dict[str, list[str]]]:
    """Return source files, clause-to-source filenames and evidence context tokens."""
    group = GROUPS[prefix]
    clauses = dict(group["clauses"])
    if version == 5:
        clauses[group["purpose_clause"]] = group["purpose_text"]
    if version == 6:
        clauses[group["semantic_clause"]] = group["semantic_text"]
    title = group["title"] if group["language"] == "zh" else group["name"].replace("-", " ").title()
    lead = frontmatter(group) + "# " + title + "\n\n"
    contexts: dict[str, list[str]] = {}
    locations = {key: "SKILL.md" for key in clauses}
    files: dict[str, str] = {}
    if version in (1, 5, 6):
        content = lead + "\n".join(f"{i}. {text}" for i, text in enumerate(clauses.values(), 1)) + "\n"
    elif version == 2:
        values = list(clauses.values())
        content = lead + "\n\n".join(" ".join(values[i:i + 2]) for i in range(0, len(values), 2)) + "\n"
    elif version == 3:
        if prefix == "Q":
            # These rows describe the one call's arguments, rather than five
            # independent operations. Required headers are included in evidence.
            parameter_keys = {"date", "missing_date", "limit", "missing_limit"}
            content = lead + clauses["capability"] + "\n\n" + clauses["read"] + "\n\n" + clauses["call"] + "\n\n"
            header = "| Argument | Present-value requirement | Missing-value requirement |"
            content += header + "\n| --- | --- | --- |\n"
            content += f"| from_date | {clauses['date']} | {clauses['missing_date']} |\n"
            content += f"| limit | {clauses['limit']} | {clauses['missing_limit']} |\n\n"
            content += "\n\n".join(clauses[key] for key in ["ban", "format", "count", "return"]) + "\n"
            for key in parameter_keys:
                contexts[key] = [header]
        else:
            header = "| 顺序 | 作用 | 要求 |" if group["language"] == "zh" else "| Order | Role | Requirement |"
            content = lead + header + "\n| --- | --- | --- |\n"
            for i, (key, value) in enumerate(clauses.items(), 1):
                role = {"read": "input", "ban": "global constraint", "immutable": "global constraint", "upload": "global constraint", "order": "note", "local": "local constraint"}.get(key, key)
                content += f"| {i} | {role} | {value} |\n"
                contexts[key] = [header]
    else:
        ref_name = "references/workflow.md"
        ref_intro = ("必须执行 [流程说明](references/workflow.md) 中的要求；该文件是当前流程的组成部分。" if group["language"] == "zh"
                     else "Follow the requirements in [workflow instructions](references/workflow.md); this file is part of the current workflow.")
        content = lead + ref_intro + "\n"
        locations = {key: ref_name for key in clauses}
        contexts["__cross_file__"] = [ref_intro]
        if prefix == "N":
            workflow = "# 通知流程\n\n" + clauses["read"] + "\n\n"
            workflow += "- 筛选：\n  - " + clauses["select"] + "\n  - " + clauses["exception"] + "\n\n"
            workflow += clauses["send"] + "\n\n" + clauses["body"] + "\n\n"
            workflow += "正文配置同时由 [发送配置](../payload.json) 的 body_from 字段声明，按该字段直接取值。\n\n"
            workflow += clauses["skip"] + "\n\n> " + clauses["ban"] + "\n\n" + clauses["literal"] + "\n\n" + clauses["count"] + "\n"
            files["payload.json"] = '{\n  "body_from": "summary"\n}\n'
            contexts["select"] = ["- 筛选："]
            contexts["exception"] = ["- 筛选："]
            contexts["body"] = ["正文配置同时由 [发送配置]"]
        elif prefix == "Q":
            workflow = "# Query workflow\n\n> " + clauses["capability"] + "\n\n" + clauses["read"] + "\n\n" + clauses["call"] + "\n\n"
            workflow += "- Call argument requirements:\n  - " + clauses["date"] + "\n  - " + clauses["missing_date"] + "\n  - " + clauses["limit"] + "\n  - " + clauses["missing_limit"] + "\n\n"
            workflow += "Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n\n"
            workflow += "\n\n".join(clauses[key] for key in ["ban", "format", "count", "return"]) + "\n"
            files["query.yaml"] = "missing_arguments:\n  from_date: omit\n  limit: omit\n"
            for key in ["date", "missing_date", "limit", "missing_limit"]:
                contexts[key] = ["- Call argument requirements:"]
            contexts["missing_date"].append("Apply the missing-argument settings")
            contexts["missing_limit"].append("Apply the missing-argument settings")
        elif prefix == "F":
            workflow = "# Fetch workflow\n\n" + clauses["read"] + "\n\n" + clauses["preferred"] + "\n\n"
            workflow += "- Preferred-tool failure handling:\n  - " + clauses["retry"] + "\n  - " + clauses["fallback"] + "\n\n"
            workflow += "The same retry policy is specified by [retry configuration](../retry.yaml); apply it to fast.fetch only.\n\n"
            workflow += clauses["archive"] + "\n\n" + clauses["return"] + "\n\n" + clauses["stop"] + "\n\n> " + clauses["ban"] + "\n\n" + clauses["status"] + "\n"
            files["retry.yaml"] = "fast_fetch:\n  max_attempts: 2\n  retry_first_error: transient_only\narchive_fetch:\n  max_attempts: 1\n"
            contexts["retry"] = ["- Preferred-tool failure handling:", "The same retry policy"]
            contexts["fallback"] = ["- Preferred-tool failure handling:"]
        else:
            workflow = "# 文档流程\n\n" + clauses["read"] + "\n\n"
            workflow += "- 转换阶段：\n  - " + clauses["convert"] + "\n  - " + clauses["local"] + "\n\n"
            workflow += "> " + clauses["blackbox"] + "\n\n" + clauses["package"] + "\n"
            workflow += reference_command() + "\n" + clauses["deliver"] + "\n\n" + clauses["receipt"] + "\n\n"
            workflow += "> " + clauses["immutable"] + "\n>\n> " + clauses["upload"] + "\n\n" + clauses["order"] + "\n"
            contexts["convert"] = ["- 转换阶段："]
            contexts["local"] = ["- 转换阶段："]
        files[ref_name] = workflow
    if prefix == "D":
        files["scripts/convert.py"] = CONVERT_SOURCE
        files["scripts/package.py"] = PACKAGE_SOURCE
        if version != 4:
            content += reference_command()
        locations["command"] = "references/workflow.md" if version == 4 else "SKILL.md"
    files["SKILL.md"] = content
    return files, locations, contexts


def evidence_for(files: dict[str, str], filename: str, needle: str, *, expand: int = 0) -> dict[str, Any]:
    """Use exact whole source lines; no hand-maintained, potentially stale offsets."""
    lines = files[filename].splitlines()
    matches = [i for i, line in enumerate(lines) if needle in line]
    if len(matches) != 1:
        raise ValueError(f"Expected one evidence match for {filename}: {needle!r}; got {matches}")
    index = matches[0]
    start, end = max(0, index - expand), min(len(lines) - 1, index + expand)
    return {"file": filename, "start_line": start + 1, "end_line": end + 1,
            "quote": "\n".join(lines[start:end + 1])}


def evidence_span(files: dict[str, str], filename: str, first: str, last: str) -> dict[str, Any]:
    """Quote an observable script interface using unique source anchors."""
    start = evidence_for(files, filename, first)["start_line"]
    end = evidence_for(files, filename, last)["end_line"]
    if end < start:
        raise ValueError(f"Reversed evidence anchors in {filename}: {first!r}, {last!r}")
    return {"file": filename, "start_line": start, "end_line": end,
            "quote": "\n".join(files[filename].splitlines()[start - 1:end])}


def annotation_for(prefix: str, version: int, files: dict[str, str], locations: dict[str, str],
                   contexts: dict[str, list[str]]) -> dict[str, Any]:
    group = GROUPS[prefix]
    sample_id = f"{prefix}{version:02d}"
    clauses = dict(group["clauses"])
    source_facts = list(group["facts"])
    changed_index: int | None = None
    if version in (5, 6):
        change_type = "purpose" if version == 5 else "semantic"
        clauses[group[f"{change_type}_clause"]] = group[f"{change_type}_text"]
        changed_index, replacement = group[f"{change_type}_fact"]
        source_facts[changed_index] = replacement
    clauses["command"] = "python scripts/package.py --paths <转换产物路径列表> --output bundle.zip"
    facts = []
    for index, source_fact in enumerate(source_facts, 1):
        evidence: list[dict[str, Any]] = []
        tags = set(source_fact["tags"])
        for clause in source_fact["clauses"]:
            filename = locations[clause]
            item = evidence_for(files, filename, clauses[clause], expand=1 if clause == "command" else 0)
            evidence.append(item)
            # A row is not self-contained without its column headings.
            for context in contexts.get(clause, []):
                evidence.append(evidence_for(files, filename, context, expand=1 if context.startswith("| ") else 0))
                if context.startswith("| "):
                    tags.update(["table_headers", "parameter_table" if prefix == "Q" else "step_table"])
                if context.startswith("- "):
                    tags.add("nested_list")
            if item["quote"].lstrip().startswith("> "):
                tags.add("blockquote")
            if filename != "SKILL.md":
                tags.add("cross_file")
                evidence.append(evidence_for(files, "SKILL.md", contexts["__cross_file__"][0]))
            if version == 4 and prefix == "N" and clause == "body":
                evidence.append(evidence_for(files, "payload.json", '"body_from": "summary"', expand=1))
                tags.add("json")
            if version == 4 and prefix == "Q" and clause in ("missing_date", "missing_limit"):
                needle = "from_date: omit" if clause == "missing_date" else "limit: omit"
                evidence.append(evidence_for(files, "query.yaml", needle))
                evidence.append(evidence_for(files, "query.yaml", "missing_arguments:"))
                tags.add("yaml")
            if version == 4 and prefix == "F" and clause == "retry":
                evidence.append({"file": "retry.yaml", "start_line": 1, "end_line": 3,
                                 "quote": "\n".join(files["retry.yaml"].splitlines()[:3])})
                tags.add("yaml")
        if prefix == "D" and index in (2, 4):
            evidence.append(evidence_span(files, "scripts/convert.py", "source = Path(sys.argv[1])", "print(output)"))
            tags.add("cross_file")
        if prefix == "D" and index == 5:
            evidence.append(evidence_span(files, "scripts/package.py", 'parser.add_argument("--paths"', "archive.write(path, arcname=path.name)"))
            tags.add("cross_file")
        unique_evidence = list({(e["file"], e["start_line"], e["end_line"]): e for e in evidence}.values())
        facts.append({"id": f"{sample_id}-F{index:02d}", "kind": source_fact["kind"],
                      "statement": source_fact["statement"], "scope": source_fact["scope"],
                      "evidence": unique_evidence, "coverage_tags": sorted(tags), "status": "待共同复核"})
    minimal_pair = None
    if changed_index is not None:
        minimal_pair = {"base_id": prefix + "01", "change": group["purpose_change" if version == 5 else "semantic_change"],
                        "changed_fact_ids": [facts[changed_index]["id"]],
                        "unchanged_fact_ids": [f["id"] for i, f in enumerate(facts) if i != changed_index]}
    variants = list(group["variants"])
    questions = list(group["questions"])
    if version == 4 and prefix in ("N", "Q", "F"):
        fixed_specification_notes = {
            "N": "包内 payload.json 是已提供的固定正文规范，与正文中的 summary 取值要求等价；保留其声明的字段来源，不仅因规范以 JSON 文件呈现就新增运行时配置读取。",
            "Q": "The supplied query.yaml is a fixed statement of the same missing-argument requirements; preserve those requirements without adding a runtime configuration read solely because they are presented in YAML.",
            "F": "The supplied retry.yaml is a fixed statement of the same retry requirements; preserve those requirements without adding a runtime configuration read solely because they are presented in YAML.",
        }
        variants.append(fixed_specification_notes[prefix])
    if version == 5:
        # A purpose delta also changes the guidance for reviewing that behavior.
        # In particular, no inherited phrasing should authorize the inactive
        # example's file write as a current operation.
        if prefix == "N":
            variants[2] = "历史写入示例可作为上下文保留，但当前流程不执行 count.txt 写入。"
            questions[-1] = "历史示例中的“处理条数”没有明确统计口径；该示例不参与当前流程，不据此增加计数或写入要求。"
        elif prefix == "Q":
            variants[2] = "The items return must still refer to the actual search response; the historical total-write example does not introduce an active file write."
        elif prefix == "F":
            variants[2] = "Success and failure results still return normally; the historical status-append example introduces no active write on either path."
        else:
            variants.append("历史收据示例可作为上下文保留，但当前流程不执行 receipt.txt 写入。")
    return {"schema_version": 1, "sample_id": sample_id, "group": group["group"],
            "expression": EXPRESSIONS[version - 1], "language": group["language"], "split": group["split"],
            "coverage_targets": sorted({tag for f in facts for tag in f["coverage_tags"]}),
            "facts": facts, "acceptable_variants": variants, "open_questions": questions,
            "minimal_pair": minimal_pair}


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def generate(output: Path) -> list[dict[str, Any]]:
    """Generate only controlled packages, their annotations and their inventory."""
    inventory = []
    for prefix, group in GROUPS.items():
        for version in range(1, 7):
            sample_id = f"{prefix}{version:02d}"
            package_path = f"inputs/controlled/{sample_id}"
            annotation_path = f"annotations/{sample_id}.json"
            files, locations, contexts = generate_package(prefix, version)
            for filename, content in files.items():
                target = output / package_path / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8", newline="\n")
            dump_json(output / annotation_path, annotation_for(prefix, version, files, locations, contexts))
            inventory.append({"id": sample_id, "title": group["title"] + " · " + EXPRESSION_TITLES[version - 1],
                              "kind": "controlled", "group": group["group"], "expression": EXPRESSIONS[version - 1],
                              "language": group["language"], "split": group["split"], "package_path": package_path,
                              "annotation_path": annotation_path})
    dump_json(output / "controlled_samples.json", inventory)
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Corpus root to write (default: this corpus)")
    args = parser.parse_args()
    samples = generate(args.output.resolve())
    print(f"Generated {len(samples)} controlled packages and separate fact annotations in {args.output.resolve()}")


if __name__ == "__main__":
    main()
