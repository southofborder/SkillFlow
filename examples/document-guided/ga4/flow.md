Historical prose notes from the earlier document prototype. These are not current typed fragment targets, accepted GA4 responses, or complete reference answers.

# Flow — assistant-authored development notes

This document is not an accepted model response or a reference answer.

- The package offers independent capabilities; do not serialize every exported function into one task (skill/SKILL.md:29-51).
- The selected path imports the Search Console helper under its actual alias, calls page performance first and country performance second, then returns their combined object (skill/scripts/src/index.ts:1-45,278-296).
- Each helper has a separate query and response. Both queries can save their own result; the wrapper also saves the combined result. Keep three writes, not one (skill/scripts/src/api/searchConsole.ts:89-175; skill/scripts/src/index.ts:285-295).
- Saving is followed by reading the saved JSON and producing a Markdown summary in the declared workflow (skill/SKILL.md:53-64).
- Unresolved: clicks versus impressions ranking language and Search Console versus GA4 date formats differ. Do not choose an interpretation silently (skill/SKILL.md:85-112; skill/references/api-reference.md:197-253; skill/scripts/src/api/searchConsole.ts:48-83).
