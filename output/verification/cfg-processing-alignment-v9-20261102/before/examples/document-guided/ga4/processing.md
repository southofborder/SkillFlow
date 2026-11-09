Historical prose notes from the earlier document prototype. These are not current typed fragment targets, accepted GA4 responses, or complete reference answers.

# Processing — assistant-authored development notes

- Page and country requests use distinct dimensions and limits. Preserve their separate response identities and their association with the matching call (skill/scripts/src/api/searchConsole.ts:89-175).
- Query storage defaults to enabled. The returned response is saved before returning to the wrapper; the wrapper separately stores an object containing both responses (skill/scripts/src/api/searchConsole.ts:89-123; skill/scripts/src/index.ts:285-295).
- saveResult writes a wrapper containing metadata (savedAt, category, operation, propertyId, optional extraInfo) and data. The file is not just the raw response (skill/scripts/src/core/storage.ts:10-26,58-95).
- Settings and client construction obtain configuration and credentials; this does not establish that each credential is an explicit application query or saved-result field (skill/scripts/src/config/settings.ts:1-74; skill/scripts/src/core/client.ts:1-133).
- Acquisition and possible observation describe actual ranges. They do not establish a Task demand for the entire returned object. Runtime visibility defaults still apply unless an explicit supported mechanism narrows visibility.
- Unknown SDK internals, runtime filename collision occurrence, date compatibility and ranking semantics remain unresolved; do not invent mechanisms.
