# Cloud setup without model calls

Run the setup script from a Codex Cloud environment setup command:

```bash
bash tools/cloud/setup.sh
```

It installs this checkout in editable mode and installs pytest. Dependency
downloads may use the package index; setup never invokes a model or an
experiment dispatcher. Set `SKILLFLOW_PYTHON` if the environment uses a different
Python executable. Python 3.10 or later is required by the project.

On any platform, installation and inspection can also be run separately:

```text
python -m pip install -e . pytest
python tools/cloud/preflight.py
python -m pytest tests/cloud -q
```

The inspection command also works from another directory when its script path
or `--project` argument points to this checkout. It identifies the root by the
existing project marker, uses the installed package, and compiles the project's
existing synthetic graph candidate in a temporary directory outside the
checkout. Candidate compilation and Mermaid rendering run with Python network
and model-client guards. The check is an installation smoke test, not a
semantic audit or a replacement for the project regressions.

Setup requires `experiments/configs/cloud-materials-v1.json` and verifies every
declared submitted material file by exact path, byte count and SHA-256:

```text
python tools/cloud/materials.py verify
```

The manifest is an audit of selected material bytes, not a new research format.
It rejects traversal, links, duplicate paths and case collisions. Additional
unlisted files are not removed or interpreted. A mismatch never triggers
automatic migration, restoration or historical resume.

To create a new manifest, first explicitly stage the intended material files.
Then select their repository-relative roots:

```text
python tools/cloud/materials.py create --root experiments/example --manifest experiments/configs/new-cloud-materials.json
```

Creation reads `git ls-files --cached` under those roots and seals the current
working-tree bytes. It does not stage anything and refuses to overwrite an
existing manifest. There is no filename-based exclusion: a submitted raw
archive, receipt, or bytecode file that is frozen source evidence remains
included. Local operational locks and caches must be excluded when choosing
what to submit, without excluding similarly named frozen evidence.

The read-only Codex inventory executes only `codex --version` and `codex --help`.
An explicit binary can be supplied with `--codex-executable`. It does not inspect
authentication files, environment values, or conversation/session contents.
Raw CLI output is not serialized. Successful help/version checks do **not**
establish model availability, authentication, or authority to run experiments.

Lean is optional for this smoke test. Its pinned version is read from
`formal/lean-toolchain`; no toolchain is downloaded and no Lean build is
started. Install that exact toolchain separately before running formal checks.

## Long experiment boundary

The existing `tools/doe/real_comparison/cli_adapter.py` transport binds a specific
Windows executable hash, CLI version, runtime envelopes, and receipt format.
A cloud-host CLI cannot be substituted into old run identities. The preflight
always reports the long-experiment transport as not ready. This is independent
of the offline installation result.

Cloud model authentication, requested model/effort availability, exact input
isolation and receipt accounting must be separately established before any
authorized calibration. Do not copy a local login file, silently switch to a
paid API, change the pinned adapter, run `dispatch-next`, or promote a
calibration into a formal run as part of setup. Setup does not modify research
prompts, evaluation rules, frozen materials or historical manifests.
