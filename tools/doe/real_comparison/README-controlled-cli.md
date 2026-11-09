# Controlled CLI transport

The current application's installed plugin catalogue appeared in one fresh CLI
session and was absent from two simultaneous sessions. A matching executable,
base instruction hash and model configuration therefore did not establish an
identical common developer harness. The rejected requests remain rejected and
the in-flight calibration implementation remains frozen.

`controlled_cli.py` adds explicit global `--disable plugins`,
`--disable remote_plugin` and `--disable recommended_plugins` arguments. It keeps
the existing executable/version pins, model/effort/provider, ignored user config
and rules, complete stdin delivery, empty working directory, no-tool receipt
checks and single-process/no-retry supervision. It has its own exact argv
validation because the immutable older adapter intentionally accepts only its
original command. No older constants or functions are monkeypatched.

An engineering probe uses `prepare_launch(..., engineering_discovery=True)` and
the separately authorized caller executes that prepared launch. After completion,
`discover_harness(...)` extracts common-text hashes and allowlisted usage without
exporting the answer or hidden reasoning. It checks the remaining runtime,
visible input, tool/history and usage requirements, and always returns
`semantic_acceptance: false`. Discovery does not establish semantic correctness
or authorize a formal comparison.

Semantic requests must instead provide explicit frozen
`base_instructions_sha256` and `developer_segment_sha256` arguments to
`prepare_launch`. Their `inspect_receipt` path rejects engineering launches and
delegates exact hash and receipt checks to the unchanged CLI-v3 inspector. Any
remaining harness drift must fail rather than silently adopting observed hashes
for a semantic answer. Disabling plugin-related feature flags is a controlled
input measure; actual receipt verification remains required.
