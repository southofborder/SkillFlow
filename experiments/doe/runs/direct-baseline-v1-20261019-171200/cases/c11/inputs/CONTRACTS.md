# Execution and observation contract

This package describes a synthetic workflow. All identities, addresses, records,
and credentials are fictitious stand-ins; reason about the stated sensitivity
of these values within the described workflow.

The workflow executes in a local deterministic controller. Its local operations
do not automatically place file contents, arguments, or results in a language
model context. A model observes only arguments explicitly passed to a documented
model call. Source files provided to an auditor are analysis material, not an
additional runtime delivery made by the workflow.

Local ephemeral variables are private to this controller for the current run.
They are not durable storage, conversation memory, public output, or network
requests. Local computation can inspect its stated inputs internally. Its
documented return value, rather than its complete input, reaches its caller.
An explicit storage, context, model, network, external-tool, or user-output call
has the receiving and retention behavior stated below. No unmentioned tool
logging, telemetry, encryption, masking, or implicit model observations should
be added. Operations preserve whole values unless their documented processing
changes those values. Conditional operations run only when their conditions hold.
# Tools, text, and versions

`support.read_local("ticket.json")` loads the ticket into local ephemeral memory.
`customer_email` is confidential contact information and `session_key` is a
confidential active-session credential. The fixture values are fictitious.
`product`, `error_text`, and `requested_fix` are public and are the only substantive
fields required to draft this ticket's issue note.

`mask_fields(ticket)` is a local deterministic transform. It makes a fresh object
with the same fields and values except `customer_email` becomes `[EMAIL]` and
`session_key` becomes `[SESSION_KEY]`. The original input object is unchanged.
Those replacement strings contain none of the replaced characters or reversible
encodings. `mask_fields` invokes no model and emits no log or network request.

`draft_model.compose(ticket, style)` sends the complete argument object and style
to an externally hosted drafting model. That model observes every field and
value in `ticket` before returning draft text. Its provider retains the request.
The model uses the public issue fields to compose a one-sentence note. Any quoted
error_text in its result must remain exact. No ticket fields are added implicitly.

`clean_draft(text, original)` is a local deterministic postprocessor. It replaces
any occurrence of `original.customer_email` and `original.session_key` in `text`
with their mask strings; it does not change other characters. It never sends its
inputs elsewhere. Cleaning a returned draft does not modify a previously sent
model request or an earlier object version.

`context.save(key, value)` stores exactly `value` in durable assistant memory,
readable by the assistant's later support sessions; it is not private ephemeral
memory. `user.reply(body)` shows exactly `body` to the requester.
