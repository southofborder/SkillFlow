# Pre-upgrade verification receipts

These three bundles were exported only after the then-current read-only loaders
validated the original annotation and backward-demand runs. They preserve the
old identities, accepted-response provenance, compiled material, forward facts,
Task and demand result as evidence for an explicit offline reconstruction.

`tools/doe/reconstruct_sensitivity_inputs.py` pins each bundle's byte SHA-256.
It authors a new current-format candidate without rewriting the old response or
enabling an old-format production parser. Source, processing, observation and
sink relationships must remain equal, and demand equality permits only a change
in the listing order of goals attached to their new lexical sites.

`historical-sha256.json` records 346 files across the frozen Task, demand and
propagation baselines. The files under those original run directories remain
unchanged. These receipts and the subsequent sensitivity declarations are not
new model calls, gold labels, or evidence of exhaustive sensitivity coverage.
