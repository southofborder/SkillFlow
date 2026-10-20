# Proposed exact-stdin engineering calibration amendment

State: **prepared, not executed; awaiting explicit transport amendment**.

The original protocol requires `collaboration.spawn_agent(fork_turns="none")`.
That interface requires the supervisor to embed the complete prompt in a literal
message argument. One manual embedding changed source code, and that stopped
calibration remains preserved as a protocol violation with unknown usage.

The application-bundled CLI is version `0.163.0-alpha.10.2`, distinct from the
older `0.121.0` CLI found on PATH. Its inspected effort type accepts a nonempty
model-advertised string, and `exec -` accepts a complete UTF-8 stdin message.
Neither property proves that the actual requested model and effort will run.

The concrete proposed probe is `proposed-launch.json`. It launches a new CLI
process without resume/fork, passes the saved calibration prompt bytes directly
to stdin, requests exactly `gpt-6.1-sol / ultra / openai`, disables user/project
configuration loading where supported, uses an empty working directory and
read-only execution sandbox, and retains stdout/stderr and the exact launch.
The target message forbids tools, retrieval, execution and delegation. A separate
actual receipt audit must verify fresh context, exact configuration, delivered
content, tool behavior, response attribution and per-response usage. Unknown
usage or mismatched configuration stops continuation; `ultra` is never mapped to
another effort. No credentials are read or exported by this driver.

This would be an engineering feasibility probe only, not a replacement semantic
trial and not one of the 216 formal workflows. The existing failed attempt would
remain visible. No automatic retry would occur. If the probe fails, its failure
and observed cost remain recorded. If it succeeds, a further frozen transport
amendment and the same delivery path for all three methods would still be needed
before the three engineering calibrations and formal gate can pass.

No formal generation is allowed before the selected cases, shared assumptions,
references and two actual-human confirmations are complete and frozen.
