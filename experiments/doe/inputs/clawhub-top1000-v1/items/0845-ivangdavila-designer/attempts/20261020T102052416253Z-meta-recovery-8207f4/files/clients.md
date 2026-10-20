# Client and Project Work

Scope: the commercial side of design — briefs, scope, rounds, pricing, change requests, rights and the ending. Most freelance and agency pain is a scoping failure that was visible on day one.

**Contents:** [The Brief](#the-brief) · [Scoping](#scoping) · [Pricing](#pricing) · [Estimating](#estimating) · [The Contract Minimum](#the-contract-minimum) · [Rounds and Change Requests](#rounds-and-change-requests) · [Running the Engagement](#running-the-engagement) · [Difficult Situations](#difficult-situations) · [Closing](#closing) · [Write It Down](#write-it-down)

**Before quoting or scoping**, read the client's file at `~/Clawic/data/projects/<project>.md` and their row in `~/Clawic/data/contacts/contacts.md`. History with a client — how many rounds they actually used last time, how they pay, who really decides — is worth more than any estimate heuristic below.

## The Brief

A brief that permits an estimate contains six things. Missing any one of them is the reason the project overruns:

1. **The business outcome**, measurable — not "a new website" but "reduce demo no-shows" or "look credible to enterprise buyers"
2. **The audience**, specifically — who they are, what they already believe, where they see this
3. **Hard constraints** — brand mandatories, technical platform, legal or compliance requirements, existing systems
4. **The decider**, by name, plus who else must be consulted
5. **The deadline**, and what is driving it — a launch, an event, a print date, a funding round
6. **The budget range**, or at least the order of magnitude

**If the brief is missing items, write it yourself and get it signed.** A one-page brief you drafted and the client approved is worth more than a twenty-page document they wrote, because the act of approving it is where the misunderstandings surface.

The three answers that predict trouble: "we'll know it when we see it", "everyone needs to be happy with it", and "we don't have a budget yet, what do you charge". Each is fixable — ask for reference examples they like and why, insist on one decider, and quote a range — but none of them fixes itself.

## Scoping

Write down what is in and, more usefully, what is **out**:

| Define | Because otherwise |
|---|---|
| Number of deliverables, itemised | "The website" turns out to include an email template and a pitch deck |
| Number of initial concepts | Two becomes five |
| Number of revision rounds, and what a round is | Revisions become continuous |
| File formats and what is handed over | Source files are assumed to be included |
| Who writes the copy | You do, unpaid |
| Who supplies imagery | You buy it, unpaid |
| Who implements, and whether you review the build | You QA it for free (`handoff.md`) |
| Meetings included, and their length | The weekly call becomes a third of the project |
| Timeline, with the client's response deadlines | Their two-week silence becomes your delay |
| What happens if the project pauses | It resumes six months later at the old price |

**A round is a definition, not a number.** State it: one round = one consolidated set of feedback from the client, delivered in one document, within a stated window. Feedback arriving in six separate emails over three weeks is three rounds' worth of work, and it will be unless the definition prevents it.

## Pricing

`pricing_model` in `config.yaml` selects the shape; all four are legitimate:

| Model | Fits | Risk |
|---|---|---|
| Hourly | Undefined scope, ongoing support, discovery | You are penalised for being fast, and the client watches the clock instead of the work |
| Fixed | Well-defined deliverables with a written scope | Every scope gap is yours; requires the discipline of a change-order process |
| Value | The work has a measurable commercial outcome the client can size | Requires access to their numbers and a trust level most engagements do not have |
| Retainer | Ongoing needs, a predictable monthly volume | Scope creep by default; needs a stated capacity ("up to X days a month") and a use-it-or-lose-it rule |

Practices worth holding:
- **Never quote before the brief.** A number given in the first conversation is the number you will be held to.
- **Quote a range while scope is open**, and narrow it once the brief is signed.
- **Deposit before starting** — 50% is a common standard, staged payments on longer projects — and it is a filter as much as cash flow.
- **Rush work is priced as rush work.** A deadline that requires displacing other commitments has a premium; say the number rather than absorbing it.
- **Price the deliverable, not the hours,** on fixed work — and never show an hourly breakdown on a fixed quote, because it invites negotiation on speed rather than value.
- **Currency, tax treatment and payment terms in the quote**, in the value itself (`1,800 EUR`, net 14). Cross-border work adds withholding and VAT questions that should not surface at invoice time.

## Estimating

- **Estimate the tasks, not the project.** Break to items of roughly half a day; the sum is more honest than a single instinct, and it survives challenge.
- **Add the invisible work explicitly**: kickoff, research, revisions, presentation prep, handoff, project management, admin. On most engagements this is a substantial share of the total and it is what gets forgotten.
- **Use your own history.** The last three similar projects are a better estimator than any rule of thumb, and they are the reason every project's estimate versus actual lives in `~/Clawic/data/projects/<project>.md`.
- **Buffer for client response time**, not for your own work. Their approval latency is usually the critical path.
- **Give a range with the assumptions attached**: "8-11 days, assuming copy is supplied and one round of consolidated feedback." The assumptions are what let you renegotiate honestly when they break.

## The Contract Minimum

Even a one-page agreement should carry: scope and deliverables; the number of rounds and what a round is; the timeline including client response deadlines; the fee, schedule and payment terms; late-payment terms; **IP transfer conditional on final payment**; usage rights, and what happens to work from rejected concepts; a portfolio/credit clause; a kill fee if the project is cancelled mid-way (25-50% of the remainder is a common band, scaled to how much was completed); and a termination clause for both sides.

Two specifics designers most often omit: **fonts and stock are licensed to someone** — say whether the client buys them or you pass through the cost, and whether the licence transfers (`typography.md`, `icons.md`); and **source files are a separate deliverable** — decide whether they are included, extra, or withheld, and say so before the last week.

This is a working checklist, not legal advice; a real contract is reviewed by a lawyer in the relevant jurisdiction.

## Rounds and Change Requests

- **A change request is anything outside the signed scope**, including "small" additions. Price it, date it, and get it approved before doing it — even at zero cost, when goodwill is the point, because recording it keeps the baseline visible.
- **The first free extra sets the price of every future one.** Doing one unbilled round to be helpful reframes rounds as free.
- **Consolidate feedback by contract**, not by request: one document, from one person, per round.
- **Contradictory feedback from two stakeholders goes back to the client to resolve**, not to you to arbitrate. Say it plainly and give them a deadline.
- **When scope has grown, say so at the moment it grows**, with the impact on date and cost. Raising it at the deadline is a much worse conversation and it is the same conversation.
- **Track rounds used, visibly** — contracted versus used in `~/Clawic/data/projects/<project>.md`, and said out loud to the client. "This is round two of two; further changes are a change order at the day rate" is a normal sentence and it prevents the awkward one later.

## Running the Engagement

- **Kickoff with the brief, the decider, the schedule and the response deadlines** confirmed out loud.
- **A short written update on a fixed cadence**, even when there is nothing to show. Silence is where clients invent problems.
- **Present work, never send it without context.** Emailing a PDF invites line-by-line reactions with no framing (`critique.md`).
- **Written confirmation of every decision**, in your words, same day. "Confirming: we're going with direction B, and the logo stays as-is."
- **Approval before proceeding to the next phase**, in writing. Verbal approval evaporates when the person who gave it leaves.
- **Log actual time against the estimate** in `~/Clawic/data/projects/<project>.md`, even on fixed-price work. It is the only way the next quote gets better, and it is what tells you which client type is unprofitable.

## Difficult Situations

| Situation | Response |
|---|---|
| "Can you just do a quick mockup so we can see?" (unpaid) | A paid discovery or a paid concept phase, or a portfolio piece with a scoped equivalent. Spec work is unpaid work with a hopeful name |
| Scope has quietly doubled | Stop, restate the original scope, list what has been added, and present the change order before the next deliverable |
| Endless revisions inside the contracted rounds | The rounds are being used on the wrong questions — go back to the brief and the decider (`critique.md`) |
| The decider changes mid-project | Re-approve the brief with the new person before continuing. Their predecessor's approvals do not bind them, and pretending otherwise costs the whole project |
| Payment is late | Stop work at the point stated in the contract, keep it factual, and follow the late-payment terms you wrote |
| Client wants an alternative direction after approving one | It is a new phase with a new fee, unless a brief error caused it |
| Client asks you to copy another brand's work | Decline plainly, explain the trademark and reputational exposure, and offer what the reference actually achieves (`brand.md`) |
| Project goes dark | A stated pause policy: after N weeks the project closes, work to date is invoiced, and restarting is a new engagement at current rates |

## Closing

- **Handover package**: final files in the agreed formats, source files if contracted, the guidelines or spec, licence documentation for every third-party asset, and a short written summary of what was delivered against the brief (`handoff.md`, `brand.md`).
- **Final invoice with the IP transfer clause satisfied** — the transfer happens on payment, and that should be stated on the invoice.
- **A short retrospective, for yourself**: estimated versus actual, rounds used versus contracted, what went wrong, whether this client type is worth repeating.
- **Ask for the testimonial and the portfolio permission at the moment of delivery**, while the outcome is fresh. Two months later the answer is silence.
- **Set a check-in date**. Past clients are the cheapest source of future work, and the follow-up is a calendar entry, not a talent.

## Write It Down

- **The client, their role, preferred channel and who actually decides** → a row in the shared `~/Clawic/data/contacts/contacts.md`. Identity key is the lowercase email, or a handle, or a stable kebab-case name. Read the file first: if the person is already there, update their row in place, never add a second one.
- **The engagement — brief, scope, deliverables, rounds contracted and used, milestones, decisions, estimate versus actual** → `~/Clawic/data/projects/<project>.md`, one file per project from the first one. Close it with `status: done | cancelled — <date>` rather than deleting it; it is the record of what was delivered and the basis of the next estimate.
- **A retainer or a recurring engagement with a monthly fee and a renewal date** → a row in the shared `~/Clawic/data/finances/subscriptions.md` with the amount and its currency in the value (`1,200 EUR/month`), plus a `## Due` row for the renewal.
- **The user's own standing terms** — pricing model, day rate band, deposit percentage, rounds default, response-time expectations → `config.yaml` (`pricing_model` plus free-form keys under a preference area), never re-asked.
- **Never store contract text, bank details, tax identifiers or client credentials** under `~/Clawic/data/`. A signed contract is a file elsewhere on the machine; reference it by name, or by pointer (`file:~/Documents/contracts/acme-2027.pdf`).
