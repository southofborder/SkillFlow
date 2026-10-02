"""Skill extraction and bounded candidate repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .candidate import IRAnalysisCandidate
from .compiler import CompileResult, compile_candidate
from ..ir.cfg import ControlFlowGraph
from ..llm.client import LlmClient
from .response_parser import parse_candidate_response, response_text
from ..inputs.skill_package import SkillPackage, load_skill_package
from .prompt import build_whole_skill_prompt


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
                    return _result_from_compilation(
                        prompt=prompt,
                        raw_candidate=latest_candidate,
                        raw_response=latest_response,
                        attempts=attempt,
                        compiled=compiled,
                    )
                latest_diagnostics = _compile_diagnostics(compiled)

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
