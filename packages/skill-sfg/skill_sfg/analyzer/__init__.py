"""SFG analyzer layer: graph builder, id assignment, callsite expansion,
cycle handling, feedback-edge plausibility, node splitting, and the type/
dependency candidate analyzer. Ported from the now-removed JS engine
(packages/skill-fcg-analyzer)/src/analyzer/* plus src/parser/type-analyzer.js.
Node/edge shapes mirror the original JS objects verbatim (camelCase keys
preserved at the data boundary)."""
