"""FCG security layer: node profiler (roles/boundary/action steps), data labeler
(ontology-driven sensitivity labels), and the label ontology. Ports of
packages/skill-fcg-analyzer/src/security/*. All 153 ontology regexes compile in
Python re with no JS-only constructs (verified), so label-ontology.json is copied
verbatim. Node/profile shapes mirror the JS objects (snake_case output keys)."""
