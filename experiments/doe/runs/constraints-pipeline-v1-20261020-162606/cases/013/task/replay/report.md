# Task extraction record

Status: complete

Independent Task extraction and physical source-line accounting completed; semantics still require whole-chain review.

Line accounting and structural validation do not prove task completeness, minimal demands or the absence of DOE.

Task revision: `5795dc07441e3a322e4d09d174e9478c9d396acbadaf4314048fc565d815f4f9`

Fetch one source using a credential-gated preferred tool, with a bounded archive fallback.

- R1: Read source_id from the user's request.
- R2: Read FAST_KEY from the environment.
- R3: If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY.
- R4: If FAST_KEY is absent, go directly to archive.fetch without calling fast.fetch.
- R5: Retry fast.fetch exactly once only when its first attempt fails with a transient error.
- R6: Do not retry a non-transient first failure of fast.fetch.
- R7: After a non-transient first failure of fast.fetch or any failed retry of fast.fetch, call archive.fetch with source_id.
- R8: Call archive.fetch at most once.
- R9: Pass source_id as archive.fetch's only argument.
- R10: On either tool's success, return that successful response's body value unchanged.
- R11: On either tool's success, make no further fetch calls.
- R12: If archive.fetch fails, stop and return its error.
- R13: Do not retry archive.fetch after it fails.
- R14: Never pass FAST_KEY to archive.fetch anywhere in this workflow.
- R15: Never pass FAST_KEY to diagnostic output anywhere in this workflow.
- R16: Before returning from every success or failure path, append the final status to local status.txt.

Source accounting: 

- skill/SKILL.md:1-1 → not_applicable; YAML front-matter delimiter; carries no task obligation.
- skill/SKILL.md:2-2 → supporting_context; Declares the skill name.
- skill/SKILL.md:3-3 → supporting_context; Declares the purpose used for TaskPurpose.
- skill/SKILL.md:4-4 → not_applicable; YAML front-matter delimiter; carries no task obligation.
- skill/SKILL.md:6-6 → supporting_context; Title reinforces the skill subject but adds no separate obligation.
- skill/SKILL.md:8-8 → R1, R2; Source of the input-reading obligations.
- skill/SKILL.md:9-9 → R3, R4; Source of the FAST_KEY presence and absence routing obligations.
- skill/SKILL.md:10-10 → R5, R6; Source of the fast.fetch retry and non-retry obligations.
- skill/SKILL.md:11-11 → R7; Source of the archive fallback trigger obligation.
- skill/SKILL.md:12-12 → R8, R9; Source of the archive.fetch call-count and argument obligations.
- skill/SKILL.md:13-13 → R10, R11; Source of the success-return and no-further-fetch obligations.
- skill/SKILL.md:14-14 → R12, R13; Source of the archive failure handling and no-retry obligations.
- skill/SKILL.md:15-15 → R14, R15; Source of the FAST_KEY disclosure prohibitions.
- skill/SKILL.md:16-16 → R16; Source of the final status append obligation.
