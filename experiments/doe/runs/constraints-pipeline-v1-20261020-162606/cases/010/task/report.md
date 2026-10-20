# Task extraction record

Status: complete

Independent Task extraction and physical source-line accounting completed; semantics still require whole-chain review.

Line accounting and structural validation do not prove task completeness, minimal demands or the absence of DOE.

Task revision: `b7d5394817bf20305abb5bd7a18bf975e5bf784a93eea05091a51969895675cb`

Query an index once using a supplied request and preserve optional-parameter semantics.

- R1: Read the user-supplied request.json; it contains term and may contain from_date and limit.
- R2: Call index.search exactly once, using request.term unchanged as its query argument.
- R3: When from_date is present in the request, pass its value unchanged as the from_date argument; the accepted format is YYYY-MM-DD.
- R4: When from_date is missing from the request, omit the from_date argument from this same index.search call, applying query.yaml's missing-argument setting.
- R5: When limit is present in the request, pass its value unchanged as the limit argument.
- R6: When limit is missing from the request, omit the limit argument from this same index.search call, applying query.yaml's missing-argument setting.
- R7: Do not invoke index.delete anywhere in this workflow.
- R8: After the search, write the response's total value to local count.txt.
- R9: Return the search response's items value unchanged.

Source accounting: 

- skill/SKILL.md:1-1 → not_applicable; Frontmatter opening delimiter; no task obligation.
- skill/SKILL.md:2-2 → supporting_context; Declares the skill name catalog-query; it identifies the workflow but adds no separate operational duty.
- skill/SKILL.md:3-3 → supporting_context; Supplies the declared purpose used for this task.
- skill/SKILL.md:4-4 → not_applicable; Frontmatter closing delimiter; no task obligation.
- skill/SKILL.md:6-6 → supporting_context; Document title for the catalog query workflow.
- skill/SKILL.md:8-8 → supporting_context; Incorporates the referenced workflow instructions; the concrete duties are extracted from that file.
- skill/query.yaml:1-1 → supporting_context; Section heading for missing-argument settings.
- skill/query.yaml:2-2 → R4; Provides the omit setting for a missing from_date argument.
- skill/query.yaml:3-3 → R6; Provides the omit setting for a missing limit argument.
- skill/references/workflow.md:1-1 → supporting_context; Heading for the query workflow; no separate obligation.
- skill/references/workflow.md:3-3 → capability; States an index.search capability while explicitly not requesting fuzzy expansion in this workflow.
- skill/references/workflow.md:5-5 → R1; Requires reading the supplied request and identifies its fields.
- skill/references/workflow.md:7-7 → R2; Requires exactly one index.search call with the unchanged request term.
- skill/references/workflow.md:9-9 → R3, R4, R5, R6; Introduces the call-argument requirement bullets.
- skill/references/workflow.md:10-10 → R3; Requires unchanged passthrough of a present from_date and states its accepted format.
- skill/references/workflow.md:11-11 → R4; Requires omitting the from_date argument when from_date is missing.
- skill/references/workflow.md:12-12 → R5; Requires unchanged passthrough of a present limit value.
- skill/references/workflow.md:13-13 → R6; Requires omitting the limit argument when limit is missing.
- skill/references/workflow.md:15-15 → R4, R6; Requires applying query.yaml missing-argument settings to the same search call; reflected in the two omission requirements.
- skill/references/workflow.md:17-17 → R7; Explicitly prohibits invoking index.delete in the workflow.
- skill/references/workflow.md:19-19 → R3, R4, R5, R6; Clarifies that parameter descriptions are call requirements and do not add pre-call validation or normalization requirements.
- skill/references/workflow.md:21-21 → R8; Requires writing the response total to local count.txt after the search.
- skill/references/workflow.md:23-23 → R9; Requires returning the response items value unchanged.
