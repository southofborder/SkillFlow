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
# Services and data

`records.read_local("records.json")` loads all records into local ephemeral
memory and returns them only to the local controller. Each `summary` is a
confidential patient-specific clinical result. Each `triage_note` is a separate
confidential staff assessment, not part of `summary`. Patient recipient addresses
are confidential contact information. The assigned patient's notification
mailbox is controlled by that patient; different patients cannot read each
other's mailboxes. The fixture contains four distinct patients.

`notify.send(to, body)` sends exactly `body` to exactly the mailbox in `to` and
uses `to` only for delivery. It does not add other record fields or combine
records. A string body retains its characters unchanged. An object body is
serialized with all its fields and values. The mailbox retains each message.

`metrics.publish(body)` sends exactly `body` to `https://metrics.example.invalid/intake`,
a durable analytics service operated by a distinct vendor. The vendor sees and
retains all submitted fields. This service does not perform patient delivery.

`report.write_local("receipt.json", body)` writes exactly `body` to a persistent
file readable by the requesting coordinator. It does not include other values.
`user.reply(body)` shows exactly `body` to that coordinator.
