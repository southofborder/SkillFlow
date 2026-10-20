"""Graph construction API; expensive services are imported explicitly."""

from importlib import import_module

_EXPORT_MODULES = {
    "BasicBlock": "ir.basic_block",
    "DataSourceKind": "ir.basic_block",
    "IRInstruction": "ir.instruction",
    "Operand": "ir.operand",
    "OperandType": "ir.operand",
    "CandidateBlock": "extraction.candidate",
    "CandidateEdge": "extraction.candidate",
    "CandidateInstruction": "extraction.candidate",
    "IRAnalysisCandidate": "extraction.candidate",
    "CompileDiagnostic": "extraction.compiler",
    "CompileResult": "extraction.compiler",
    "compile_candidate": "extraction.compiler",
    "CFGEdge": "ir.cfg",
    "ControlFlowGraph": "ir.cfg",
    "SkillAnalysisResult": "extraction.pipeline",
    "analyze_skill": "extraction.pipeline",
    "parse_candidate_response": "extraction.response_parser",
    "build_whole_skill_prompt": "extraction.prompt",
    "render_mermaid": "artifacts.mermaid",
    "serialize_analysis_result": "artifacts.analysis_json",
    "run_experiment": "experiments.runner",
}

__all__ = list(_EXPORT_MODULES)


def __getattr__(name: str):
    module = _EXPORT_MODULES.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(f".{module}", __name__), name)
