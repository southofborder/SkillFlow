"""FCG analyzer layer: graph builder, id assignment, callsite expansion,
cycle handling, feedback-edge plausibility, node splitting, and the type/
dependency candidate analyzer. Ports of packages/skill-fcg-analyzer/src/analyzer/*
plus src/parser/type-analyzer.js. Node/edge shapes mirror the JS objects
verbatim (camelCase keys preserved at the data boundary)."""
