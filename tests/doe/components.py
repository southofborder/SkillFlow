"""Mutable component fixtures for isolated algorithm tests, never a wire format.

Formal loading tests use real PropagationMaterials. Algorithm tests intentionally
edit individual facts; this test-only owner exposes those components for mutation.
"""
from copy import deepcopy
from skillflow.propagation.loading import PropagationMaterials

class Components(PropagationMaterials):
    def __init__(self, **components): self.parts = deepcopy(components)
    def __eq__(self, other): return isinstance(other, Components) and self.parts == other.parts

def _component(name):
    def get(self): return self.parts[name]
    def set_value(self, value): self.parts[name] = value
    return property(get, set_value)
for _name in ("annotation", "material", "source", "source_metadata", "cfg", "runtime_contract",
              "locations", "actions", "data", "records", "sinks", "status", "coverage", "diagnostics"):
    setattr(Components, _name, _component(_name))

def mutable_components(facts):
    return Components(**{name:getattr(facts,name) for name in
        ("annotation", "material", "source", "source_metadata", "cfg", "runtime_contract",
         "locations", "actions", "data", "records", "sinks", "status", "coverage", "diagnostics")})
