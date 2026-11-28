# Initial processing protocol audit

The sole new run is `document-guided-ga4-processing-correction-high-20261117-110830`. Its saved protocol and manifest specify seven normal semantic requests, two workers, one structural correction per stage, one shared semantic repair, a 2700-second native deadline and two additional eligible transient native attempts. The selected configuration is gpt-6.1-sol/high/openai. Guided run v15, step v12, fragments v7, complete shared-output grammar, bounded raw diagnostics and causal dependency correction are recorded.

All 16 frozen source files match the protocol's individual SHA-256 pins, totaling 155,170 bytes. The raw run-protocol file matches its prepared-run pin. The adjacent JSON binds the inspected protocol, manifest, preparation and source snapshot files.

Processing has not yet been audited. Prompt delivery size, output size, contract count and validation status are **not measured**, not zero. The processing-ready/closure notification will trigger passive inspection of the saved prompt, raw response and validation records. This preliminary audit makes no claim about processing, propagation, field necessity or DOE coverage.

Network retry and usage reconciliation is owned by the separate transport audit. Native elapsed time and public host-observation intervals do not establish model-only generation time or first-token timing. No project validator, analysis, backend, replay, Skill, CLI or model was executed for this report; only standard-library file reads and hashes were used. No frozen or run file was edited.
