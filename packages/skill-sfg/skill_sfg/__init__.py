"""SkillFlow FCG analyzer — judgment-driven Python rewrite.

Produces per-(label, sink) necessity-judgment digests consumed by the DOE
analyzer, instead of materializing full data-flow paths. See the plan at
.claude/plans/peaceful-spinning-willow.md and the memory
fcg-python-judgment-driven-rewrite for the design rationale.
"""

__version__ = "2.0.0-py"
