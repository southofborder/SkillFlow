Historical prose notes from the earlier document prototype. These are not current typed fragment targets, accepted GA4 responses, or complete reference answers.

# Sensitivity — assistant-authored development notes

- The source identifies service-account configuration including a private key; classify the actual credential value and its version using the setup and client evidence, not a guessed field in a response (skill/SKILL.md:16-27; skill/scripts/src/config/settings.ts:1-74; skill/scripts/src/core/client.ts:1-133).
- Aggregate analytics dimensions and counts require contextual judgment. This note does not declare every response field sensitive or presume unknown personal identifiers.
- Credential use in client initialization is not proof of credential plaintext in response data or saved metadata. Preserve possible influence separately from explicit content.
- Saved property identifiers and returned analytics should be tied to their actual source and saved version before any final declaration. These notes neither modify processing nor decide DOE.
