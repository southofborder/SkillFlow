"""Typed transfer specifications and offline static data propagation.

Lazy public exports keep specification types independent of annotation runners.
"""
from importlib import import_module

_EXPORTS = {
    **{name: "models" for name in (
        "FlowLocation", "FlowState", "StateBinding", "IRFlowRecord", "EffectEvent",
        "AtomicOpRecord", "BuildMemberRecord", "StateChange", "ForEachRecord", "ForEachInstance",
    )},
    **{name: "records" for name in (
        "SCHEMA_VERSION", "PropagationRecordError", "PropagationRecords",
        "cfg_sha256",
    )},
    "propagate": "solver", "PropagationResult": "solver",
    "load_doe_input": "handoff", "load_propagation_run": "runner",
    "IRTransferSpec": "contracts.specs", "ValueRef": "contracts.specs",
    "RawIRTransferSpec": "contracts.specs", "ProcessingSpec": "contracts.specs", "ForEachSpec": "contracts.specs",
}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module(f"{__name__}.{_EXPORTS[name]}"), name)
    globals()[name] = value
    return value
