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

`vault.read_local("deploy.json")` returns the local deployment configuration to
the controller. `deploy_token` is a confidential service credential. It is a
fictitious nonfunctional stand-in in this package. `artifact_digest` and `job_id`
are public identifiers; they do not contain or encode the token.

`deploy_proxy.submit(url, job_id, artifact_digest, credential)` is a local proxy.
It sends the three request fields `job_id`, `artifact_digest`, and the complete
credential in an `Authorization` header to the deployment service at the supplied
URL. That service requires the complete current credential to authenticate the
submission. Truncating or replacing it makes authentication fail. The proxy does
not return the credential or request headers, does not log them, and does not
invoke a model. Its response is only `{state, retryable}`. `state` is one of
`accepted`, `busy`, or `rejected`; `retryable` is a Boolean. These public response
fields never echo any part of the credential. A first `busy` response may be
retryable; actual response outcomes are not fixed by this source package.

`runlog.append(body)` appends exactly `body` to a persistent local run log readable
by the operations team. The operations team is distinct from the deployment
service. It receives all appended field values and retains them. The logger
does not automatically add proxy input or headers.

`support.submit(body)` sends exactly `body` to `https://support.example.invalid/debug`,
a separate support vendor. Its employees may read retained requests. It does not
submit or retry deployment jobs and is not needed to authenticate the proxy.
`user.reply(body)` shows exactly `body` to the requesting build owner.
