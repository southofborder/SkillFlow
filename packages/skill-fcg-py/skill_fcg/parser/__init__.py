"""Parser layer — faithful Python port of packages/skill-fcg-analyzer/src/parser.

This layer turns a skill directory (SKILL.md + docs + scripts) into the flat
list of tool/action *node objects* the graph layer consumes. Node objects are
kept as plain dicts with the SAME keys as the JS pipeline (including camelCase
ones like ``isCritical``/``startLine``) so the golden node-by-id parity check is
a trivial structural diff and the two implementations read side by side.
"""
