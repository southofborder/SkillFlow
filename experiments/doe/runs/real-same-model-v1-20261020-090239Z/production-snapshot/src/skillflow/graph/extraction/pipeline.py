"""Skill extraction and bounded candidate repair."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from skillflow.graph.extraction.candidate import IRAnalysisCandidate
from skillflow.graph.extraction.compiler import CompileResult
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.common.llm.client import LlmClient
from skillflow.graph.extraction.response_parser import parse_candidate_response
from skillflow.graph.extraction.response_parser import response_text
from skillflow.common.inputs.skill_package import SkillPackage
from skillflow.common.inputs.skill_package import load_skill_package
from skillflow.graph.extraction.prompt import build_whole_skill_prompt


class SkillAnalysisResult(BaseModel):
    """Serializable result of one complete or degraded analysis attempt."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    status: Literal["complete", "degraded"]
    cfg: ControlFlowGraph | None = None
    raw_candidate: dict[str, Any] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)
    requires_review: bool
    prompt: str
    raw_response: str | None = None
    attempts: int = 0


def _candidate_dump(candidate: IRAnalysisCandidate) -> dict[str, Any]:
    payload = candidate.model_dump(mode="json")
    for block in payload.get("blocks", []):
        for instruction in block.get("instructions", []):
            for operand in [
                *instruction.get("inputs", []),
                *instruction.get("outputs", []),
            ]:
                if operand.get("type") != "literal":
                    operand.pop("literal_value", None)
    return payload


def _validation_diagnostics(error: ValidationError) -> list[str]:
    return [
        "CANDIDATE_SCHEMA_INVALID at "
        + (".".join(str(part) for part in item["loc"]) or "candidate")
        + f": {item['msg']}"
        for item in error.errors()
    ]


def _compile_diagnostics(result: CompileResult) -> list[str]:
    messages = [
        f"{item.code} at {item.path}: {item.message}" for item in result.diagnostics
    ]
    messages.extend(f"candidate warning: {warning}" for warning in result.warnings)
    return messages


def _repair_prompt(
    original_prompt: str,
    raw_response: str,
    candidate: dict[str, Any],
    diagnostics: list[str],
) -> str:
    return "\n\n".join(
        [
            original_prompt,
            "Repair the previous candidate. Return the complete corrected JSON object only.",
            "Previous raw response:",
            raw_response,
            "Previous parsed candidate:",
            json.dumps(candidate, ensure_ascii=False, indent=2),
            "Deterministic validation errors:",
            json.dumps(diagnostics, ensure_ascii=False, indent=2),
        ]
    )


def _result_from_compilation(
    *,
    prompt: str,
    raw_candidate: dict[str, Any],
    raw_response: str | None,
    attempts: int,
    compiled: CompileResult,
) -> SkillAnalysisResult:
    diagnostics = _compile_diagnostics(compiled)
    if compiled.ok:
        return SkillAnalysisResult(
            status="complete",
            cfg=compiled.cfg,
            raw_candidate=raw_candidate,
            diagnostics=diagnostics,
            requires_review=False,
            prompt=prompt,
            raw_response=raw_response,
            attempts=attempts,
        )
    return SkillAnalysisResult(
        status="degraded",
        cfg=None,
        raw_candidate=raw_candidate,
        diagnostics=diagnostics,
        requires_review=True,
        prompt=prompt,
        raw_response=raw_response,
        attempts=attempts,
    )


def analyze_skill(
    source: str | Path | SkillPackage,
    *,
    client: LlmClient | Any | None = None,
    max_repair_rounds: int = 3,
    candidate: IRAnalysisCandidate | dict[str, Any] | None = None,
) -> SkillAnalysisResult:
    """Analyze a directory or ZIP, optionally compiling a fixed candidate offline."""

    if max_repair_rounds < 0:
        raise ValueError("max_repair_rounds must be non-negative")
    package = source if isinstance(source, SkillPackage) else load_skill_package(source)
    prompt = build_whole_skill_prompt(package)

    if candidate is not None:
        raw_candidate = (
            _candidate_dump(candidate)
            if isinstance(candidate, IRAnalysisCandidate)
            else candidate
        )
        compiled = compile_candidate(raw_candidate, package)
        return _result_from_compilation(
            prompt=prompt,
            raw_candidate=raw_candidate,
            raw_response=None,
            attempts=0,
            compiled=compiled,
        )

    return analyze_skill_with_prompt(
        package,
        initial_prompt=prompt,
        client=client,
        max_repair_rounds=max_repair_rounds,
    )


def analyze_skill_with_prompt(
    source: str | Path | SkillPackage,
    *,
    initial_prompt: str,
    client: LlmClient | Any | None = None,
    max_repair_rounds: int = 3,
    on_attempt: Callable[[dict[str, Any]], None] | None = None,
) -> SkillAnalysisResult:
    """Extract a full candidate with an explicit prompt and bounded structural repair.

    The feedback orchestrator supplies a case-specific prompt here. This function
    shares the ordinary parser/compiler and repair policy; it never modifies a
    previous CFG or treats a structurally complete result as semantic acceptance.
    ``on_attempt`` observes each finished parse/compile before the next request;
    callback failures propagate rather than permitting unrecorded continuation.
    """
    if max_repair_rounds < 0:
        raise ValueError("max_repair_rounds must be non-negative")
    if not isinstance(initial_prompt, str) or not initial_prompt.strip():
        raise ValueError("initial_prompt must be a non-empty string")
    package = source if isinstance(source, SkillPackage) else load_skill_package(source)
    prompt = initial_prompt
    effective_client = client or LlmClient()
    current_prompt = prompt
    latest_candidate: dict[str, Any] = {}
    latest_response: str | None = None
    latest_diagnostics: list[str] = []
    total_attempts = max_repair_rounds + 1

    for attempt in range(1, total_attempts + 1):
        raw_response_value = effective_client.complete(current_prompt)
        latest_response = response_text(raw_response_value)
        parsed = parse_candidate_response(raw_response_value)
        if parsed is None:
            latest_candidate = {}
            latest_diagnostics = [
                "CANDIDATE_JSON_INVALID: LLM response did not contain a JSON object"
            ]
        else:
            latest_candidate = parsed
            try:
                validated_candidate = IRAnalysisCandidate.model_validate(parsed)
            except ValidationError as error:
                latest_diagnostics = _validation_diagnostics(error)
            else:
                compiled = compile_candidate(validated_candidate, package)
                if compiled.ok:
                    if on_attempt is not None:
                        on_attempt(deepcopy({
                            "attempt": attempt, "raw_candidate": latest_candidate,
                            "raw_response": latest_response,
                            "diagnostics": _compile_diagnostics(compiled), "status": "complete",
                            "cfg": compiled.cfg.model_dump(mode="json") if compiled.cfg else None,
                        }))
                    return _result_from_compilation(
                        prompt=prompt,
                        raw_candidate=latest_candidate,
                        raw_response=latest_response,
                        attempts=attempt,
                        compiled=compiled,
                    )
                latest_diagnostics = _compile_diagnostics(compiled)

        if on_attempt is not None:
            on_attempt(deepcopy({
                "attempt": attempt, "raw_candidate": latest_candidate,
                "raw_response": latest_response, "diagnostics": latest_diagnostics,
                "status": "repair_needed", "cfg": None,
            }))
        if attempt <= max_repair_rounds:
            current_prompt = _repair_prompt(
                prompt,
                latest_response or "",
                latest_candidate,
                latest_diagnostics,
            )

    return SkillAnalysisResult(
        status="degraded",
        cfg=None,
        raw_candidate=latest_candidate,
        diagnostics=latest_diagnostics,
        requires_review=True,
        prompt=prompt,
        raw_response=latest_response,
        attempts=total_attempts,
    )
