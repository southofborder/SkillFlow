# Interface Copy

Scope: the words inside the design — labels, buttons, errors, empty states, confirmations, microcopy. Text is the highest-density part of an interface and the part most often left to whoever implements it.

**Contents:** [Write the Copy First](#write-the-copy-first) · [Labels and Buttons](#labels-and-buttons) · [Error Messages](#error-messages) · [Empty and Success Copy](#empty-and-success-copy) · [Confirmations](#confirmations) · [Voice Without Costume](#voice-without-costume) · [Mechanics](#mechanics) · [Numbers, Dates and Units](#numbers-dates-and-units) · [Writing for Translation](#writing-for-translation) · [Write It Down](#write-it-down)

**Before writing interface copy**, read `## Brands` in `~/Clawic/data/designer/memory.md` and open any `artifacts/voice-*.md` the `## Boxes` index names; if `brand_file` is set in `config.yaml`, that file overrides the generic register below.

## Write the Copy First

Copy written after the layout gets truncated to fit boxes that were sized for lorem ipsum. Copy written first sizes the boxes.

Practical order: write the screen as a plain paragraph of what the user is being told and asked; cut it to the essential sentence; then lay out around it. If the paragraph cannot be written, the screen does not have a purpose yet, and no amount of layout will supply one.

## Labels and Buttons

| Rule | Bad | Good |
|---|---|---|
| Verb + object on buttons | `Submit` | `Send invitation` |
| The button answers the question in the heading | `Delete this project?` / `Yes` | `Delete this project?` / `Delete project` |
| Name what happens next, not the mechanism | `Process` | `Start import` |
| Nouns for navigation, verbs for actions | `Settings` for a nav item; `Save settings` for the button | — |
| No "click", no "here" | `Click here to learn more` | `How billing works` |
| Field labels are nouns, not sentences | `What is your email address?` | `Email` |
| Toggle labels state what the *on* position does | `Notifications` (on/off ambiguous) | `Email me when a comment is added` |

A cancel button says what is being abandoned when it is ambiguous (`Discard draft` beats `Cancel`), and the pair `Cancel / OK` on a destructive dialog is the classic ambiguity: which one is destructive is a coin flip.

## Error Messages

Three parts, in order: **what happened → why → what to do next.** The third is the one that gets dropped and the only one the user needs.

| Instead of | Write |
|---|---|
| `Invalid input` | `Enter a date after today` |
| `An error occurred` | `We couldn't save your changes. Check your connection and try again.` |
| `Error 4021` | `That invite link has expired. Ask the workspace owner for a new one. (4021)` |
| `Password does not meet requirements` | `Passwords need at least 12 characters. Yours has 8.` |
| `Field required` | `Add a project name so you can find it later` |

Rules:
- **No blame and no fake apology.** "You entered the wrong format" and "Oops! Something went wrong 😅" both fail — one accuses, the other trivialises. State the fact.
- **Say whether it is retryable.** "Try again" on a permanently failed operation costs the user another attempt and their trust.
- **Keep the error id for support, in parentheses, after the human sentence.**
- **Never lose their input** (`components.md`); if you cannot recover it, say so explicitly rather than showing an empty form.
- **Requirements are stated before failure, not after.** A password rule shown only in the error message is a design failure being papered over by copy.

## Empty and Success Copy

- **First-run empty state**: one line saying what this collection is for, then the action. `No projects yet` is a status; `Projects keep related work together. Create your first one.` is an onboarding screen that cost one sentence.
- **No-results state**: echo the query and offer the relaxation. `No results for "invocies"` plus `Search for "invoices" instead?` recovers a typo; `No results` does not.
- **Success messages confirm the specific thing**: `Invitation sent to sam@example.com`, not `Success!`. The specificity is the confirmation.
- **Do not celebrate routine actions.** Confetti on the fourth save is noise; reserve emphasis for genuinely significant milestones or drop it.

## Confirmations

`Delete "Q3 Report"?` / `This deletes the report and its 14 revisions. This cannot be undone.` / buttons `Cancel` and `Delete report`.

Every confirmation contains: the object's name, the consequence in plain terms, whether it is reversible, and a button labelled with the verb. If any of the four is missing, the dialog is asking the user to guess. And if the action *is* reversible, prefer an undo toast to a dialog entirely (`components.md`).

## Voice Without Costume

- **Voice is constant, tone varies with the moment.** The same product is calm in an error, brief in a confirmation, and warmer in an empty state. A single register applied to all three is what makes an interface sound like a chatbot.
- **Three adjectives, each with a "we say / we don't say" pair.** Adjectives alone ("friendly, clear, human") are unenforceable; the pairs are what another writer can actually follow.
- **Humour is a liability in errors, in payments and in anything involving data loss.** Put personality in onboarding, empty states and success — the places where the user is not under pressure.
- **Second person, active voice, present tense.** "You can invite up to 10 people" over "Up to 10 people may be invited."
- **First person plural only for things the product actually does**: "We'll email you when it's ready" is fine; "We think you'll love this" is not, because nobody said it.
- **Target reading level around grade 8-9** for a general audience — not because users are unsophisticated, but because they are scanning while distracted. Domain terms stay when they are the users' own vocabulary; replacing an accountant's "reconciliation" with "matching" makes it worse.

## Mechanics

- **Sentence case for everything** — headings, buttons, labels, menu items. Title Case is slower to scan and forces a per-word judgment nobody makes consistently. Exception: a brand that mandates it, recorded in `brand_file`.
- **No terminal punctuation on labels, buttons, or single-sentence headings**; full stops in body copy and multi-sentence help text.
- **Front-load the meaningful word.** People scan the first two words of a line: `Export as CSV` beats `You can export this data as CSV`.
- **Contractions**, unless the brand register forbids them; their absence reads as legal text.
- **No jargon the user did not bring**: "authenticate", "provision", "utilise", "leverage". Also no internal names — the user does not know what "the orchestrator" is.
- **Consistency over elegance.** One word per concept, everywhere. `Delete`/`Remove`/`Trash` for the same operation is three different mental models.
- **Word count budgets**: button ≤3 words; heading ≤8; empty-state body ≤2 lines; tooltip ≤1 sentence. When a budget is impossible, the interaction is too complex, not the copy.

## Numbers, Dates and Units

- **Absolute dates for anything actionable or auditable**; relative for recency. `2 hours ago` is right in a feed; `Due 14 Mar 2027` is right on an invoice. Never `in 2 days` on a legal deadline.
- **Format dates per the user's locale**, and never render an ambiguous all-numeric date: `03/04` is two different days depending on the reader.
- **Round for humans, keep precision for money**: `1.2k members`, but `1,204.50 USD`.
- **Currency and unit always in the value**, never assumed from the user's guess (`62 USD`, `3 mm`). Currency symbol placement is locale-dependent; the ISO code is unambiguous everywhere.
- **Zero is a state, not a blank.** `0 comments` is information; an empty space is a bug.
- **Pluralisation is a design requirement**: `1 item` / `2 items` needs both strings, and several languages need more than two forms.

## Writing for Translation

- **Short strings expand most.** W3C's guidance puts strings under 10 characters at 100-200% expansion, 11-20 characters at 80-100%, 30-50 at 40-60%, and long paragraphs at roughly 30%. Buttons and labels are therefore the highest-risk strings in the interface.
- **Never assemble sentences from fragments.** `"Delete " + count + " items"` breaks in every language with grammatical gender, case, or a different word order. Use whole strings with named placeholders.
- **Placeholders need context for the translator**: `{count} files moved to {folder}` with a note on what each is.
- **Avoid idiom, puns and culture-specific metaphors** anywhere translation is planned — they either fail or triple the localisation cost.
- **Test with a real long-locale translation and with RTL** before signing off the layout (`layout.md`).

## Write It Down

- **The voice definition, the three adjectives and their say/don't-say pairs, plus the terminology list** → `artifacts/voice-<brand>.md`, its own file, with its `## Boxes` line and a read condition naming the brand.
- **A terminology decision** (one word per concept, and which one won) → the same voice artifact; a scattered glossary is how synonyms come back.
- **A locale that overflows the interface, or a string that cannot be translated cleanly** → `## Pain Points` in `~/Clawic/data/designer/memory.md`, because it will constrain every future layout on that surface.
- **A register the user declares for their brand** → `brand_file` in `config.yaml`, pointing at the long-form file; never inline in the skill's instructions.
