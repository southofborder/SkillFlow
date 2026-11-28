# Fresh GA4 prelaunch record

The user explicitly authorized one fresh GA4 online test on 2026-11-12 after the previous timeout explanation. This is a new run of the corrected offline-accepted implementation, not a continuation of the failed request or a four-case batch.

- Current implementation: `796240619b140cbb2c521d1ef00fb1dcae81aa0eed7acc6b79f692c194e5f5fa`; an independent read-only audit matched all 194 implementation manifest files.
- GA4: 16 files, byte-identical to the prior complete package; source SHA `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. Download metadata `_meta.json` and `skill-card.md` are excluded, as in the original verified package.
- `gpt-6.1-sol/high/openai`; seven normal requests, two workers, one structural correction per stage, one shared semantic repair, 2700-second native timeout, up to two eligible extra transient attempts. One controller-owned zero-call replay follows the terminal result.
- The old native executable was removed by the installed application update. Current app version: `26.1106.6628.0`; CLI version: `0.167.0-alpha.4.1`; executable SHA `83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f`. Both installed executable copies match. Current flags were checked locally. There were three metadata-only CLI invocations (root: one `exec --help`; independent auditor: `--version` and `exec --help`), zero model probes and zero Skill executions.
- Two preparation attempts stopped before creating a preparation intent or run: system Python lacked the editable package, then the previous executable path was absent. Preparation used the existing accepted-work venv and the current installed CLI; no production code was changed.
- No Python controller was active in the initial process inventory. All four prior controllers and their replays were closed. No old process was resumed.

Preserve all previous sources, artifacts, failures and costs. Freeze production, prompts, transport and executables during the new run and its sole replay. Do not launch additional small cases, probes or resampling. Compare the new result with the prior failure only with the corrected implementation and CLI identities stated explicitly.
